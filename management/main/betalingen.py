"""@package docstring
Documentatie voor betalingen.

Omvat alle functies voor het genereren van betalingen, versturen van e-mails etc.
"""
import csv
import io

import chardet
from django.contrib import messages
from django.core.mail import mail_admins

from ..models import Betaling, Functie, PloegLid


def no_payment(lid, seizoen):
    """
    Filter die aangeeft of er voor een lid reeds een betaling is.
    :param lid: het lid waarvoor de betaling moet gegenereerd worden
    :param seizoen: het seizoen waarvoor de betalingen gegenereerd worden
    :return: boolean die aangeeft of er al betalingen zijn voor dit lid.
    """
    return Betaling.objects.filter(lid=lid, seizoen=seizoen).count() == 0


def oldest(lid, familieleden, seizoen):
    """
    Check of het lid in kwestie het oudst spelende lid is van de familie
    :param lid: lid waarvoor de betaling gegenereerd wordt
    :param familieleden: familieleden in de db waarvoor 'spelend_lid' == True
    :param seizoen: het seizoen in kwestie
    :return: flag voor oudste lid in de familie
    """
    for fl in familieleden:
        if not has_team(fl, seizoen):
            continue
        if fl.geboortedatum > lid.geboortedatum:
            return False
    return True


def has_team(lid, seizoen):
    """
    Filter die aangeeft of een lid een ploeg heeft in een bepaald seizoen.
    :param lid: Het lid waarvoor gecheckt moet worden
    :param seizoen: Het seizoen waarvoor betalingen gegenereerd worden
    :return: True als het lid een ploeg heeft in het seizoen in kwestie.
    """
    ploegleden = PloegLid.objects.filter(lid=lid).all()

    # filter alleen ploegen van dit seizoen
    ploegen = [
        ploeglid
        for ploeglid in ploegleden
        if ploeglid.ploeg.seizoen == seizoen
    ]

    return len(ploegen) != 0


def get_discount(lid, seizoen):
    """
    Bereken de discount voor het lid.
    Regels:
    - 0 als het lid het enigste is van de familie (obv. adres)
    - 0 als het lid het oudste is van de spelende familieleden
    - 50 als het lid niet het oudste is.
    :param lid: het lid waarvoor de discount moet berekend worden
    :param seizoen: het seizoen waarvoor de discount moet berekend worden
    :return: het bedrag dat afgetrokken moet worden
    """
    familieleden = [
        lid
        for lid in lid.familieleden.all()
        if lid.sportief_lid and has_team(lid, seizoen)
    ]
    if not familieleden:
        return 0
    elif oldest(lid, familieleden, seizoen):
        return 0
    else:
        return 50


def bereken_bedrag(lid, seizoen):
    """
    Bereken het te betalen bedrag voor een lid in een gegeven seizoen
    :param lid: het lid waarvoor de betaling berekend moet worden
    :param seizoen: het seizoen waarvoor de betalingen gegenereerd worden
    :return: het bedrag dat het lid moet betalen
    """
    functie = Functie.objects.get(functie="Speler")
    ploegen = [
        ploeglid.ploeg
        for ploeglid in PloegLid.objects.filter(lid=lid, functie=functie)
        if ploeglid.ploeg.seizoen == seizoen
    ]
    # als het lid niet in een ploeg zit, moet er geen lidgeld betaald worden
    if not ploegen:
        return 0
    lidgeldklassen = [ploeg.lidgeldklasse for ploeg in ploegen]
    bedragen = [lidgeldklasse.lidgeld for lidgeldklasse in lidgeldklassen]

    bedrag = max(bedragen)
    discount = get_discount(lid, seizoen)
    return bedrag - discount


def get_type(lid):
    """
    Betaal het type betaling dat geldt voor het lid.
    Mogelijkheden zijn:
    - 'facturatie': Hierbij betaalt het lid zijn/haar lidgeld via sponsoring.
        Hier moeten geen herinneringsmails voor gestuurd worden.
    - 'afbetaling': Hierbij betaalt het lid zijn/haar lidgeld in schijven.
        Hier moeten geen herinneringsmails voor verstuurd worden.
    - 'normaal': Lidgeld wordt eenmalig betaald.
    :param lid: het lid waarvoor de betaling gegenereerd moet worden.
    :return:
    """
    if lid.facturatie:
        return "facturatie"
    elif lid.afbetaling:
        return "afbetaling"
    else:
        return "normaal"


def mededeling(lid, seizoen):
    """
    Genereer gestructureerde mededeling op basis van uid en seizoen
    Mededeling wordt random gegenereerd bij aanmaak van het lid
    :param lid: het lid waarvoor de mededeling gegenereerd moet worden
    :param seizoen: het seizoen waarvoor de mededeling moet gegenereerd worden
    :return:
    """
    # begin met de berekening van het getal
    berekening = (
        lid.uid + seizoen.startdatum.year * seizoen.einddatum.year
    ) % (10**10)
    # voeg nullen toe indien nodig
    start_nul = "0" * (10 - len(str(berekening)))
    # bereken controlegetal
    # indien controlegetal = 0 --> 97
    # indien controlegetal < 10, voeg een nul toe
    laatste_twee = berekening % 97
    additionele_nul = ""
    if laatste_twee == 0:
        laatste_twee = 97
    elif laatste_twee < 10:
        additionele_nul = "0"

    # construeer de uiteindelijke gestructureerde mededeling
    resultaat = (
        start_nul + str(berekening) + additionele_nul + str(laatste_twee)
    )
    return "***{}/{}/{}***".format(
        resultaat[:3], resultaat[3:7], resultaat[7:]
    )


def genereer_betaling(lid, seizoen):
    """
    Genereer een openstaande betaling voor een lid.
    Er vanuitgaande dat het lid geen openstaande betalingen heeft
    (Zou elders moeten gefilterd zijn)
    :param lid: het lid waarvoor de betaling gegenereerd moet worden
    :param seizoen: het seizoen waarvoor de betaling gegenereerd moet worden
    :return: None
    """
    origineel_bedrag = bereken_bedrag(lid, seizoen)
    if origineel_bedrag <= 0:
        return
    ge_mededeling = mededeling(lid, seizoen)
    betalings_type = get_type(lid)
    status = "draft"

    Betaling.objects.create(
        origineel_bedrag=origineel_bedrag,
        afgelost_bedrag=0,
        lid=lid,
        seizoen=seizoen,
        mededeling=ge_mededeling,
        type=betalings_type,
        status=status,
    )


def genereer_betalingen(leden, seizoen):
    """
    Genereer de betalingen voor de geselecteerde leden
    :param leden: de lijst met leden
    :param seizoen: het seizoen in kwestie
    """
    # filter alle leden waarvoor er reeds een betaling bestaat
    leden_todo = list(filter(lambda c_lid: no_payment(c_lid, seizoen), leden))
    for lid in leden_todo:
        genereer_betaling(lid, seizoen)


def check_keys(keys):
    """
    Check dat alle benodigde keys aanwezig zijn in de csv file
    :param keys:
    :return:
    """
    required_keys = [
        "bedrag",
        "credit",
        "debet",
        "gestructureerde mededeling",
        "afschriftnummer",
    ]
    return all(x.lower() in keys for x in required_keys)


def check_encoding(csv_file):
    """
    Detecteer de encoding van een csv_file
    :param csv_file:
    :return:
    """
    result = chardet.detect(csv_file.read(-1))
    # Reset the file pointer
    csv_file.seek(0)
    return result["encoding"]


def registreer_betalingen(csv_file, request):
    """
    Registreer betalingen van csv
    :param csv_file: de geuploade csv-file
    :param request: de request waarbij de csv-filie geupload is
    :return: None
    """
    csv_file = request.FILES["file"]
    # set up the filestream
    encoding = check_encoding(csv_file)

    data_set = csv_file.read().decode(encoding)
    io_string = io.StringIO(data_set)
    keys = []

    for index, aflossing in enumerate(
        csv.reader(io_string, delimiter=";", dialect=csv.excel_tab)
    ):
        if index == 0:
            # haal de kolomnamen uit de csv-file
            keys = [key.strip().lower() for key in aflossing]

            # check dat de correcte kolomnamen aanwezig zijn in de file
            if not check_keys(keys):
                # indien niet, error
                messages.error(
                    request, "CSV-bestand bevat niet de correcte headers"
                )
                return
        else:
            # haal de values uit de row
            values = [value.strip() for value in aflossing]
            aflossing = dict(zip(keys, values))
            try:
                # filter op de gestructureerde mededeling
                g_mededeling = aflossing["gestructureerde mededeling"]
                if not g_mededeling:
                    # als de gestructureerde mededeling leeg is, niet van belang
                    continue

                betaling = Betaling.objects.filter(mededeling=g_mededeling)

                # alleen wanneer er maar 1 betaling is die filtert
                if len(betaling) == 1:
                    betaling[0].los_af(aflossing)
                elif len(betaling) == 0:
                    messages.warning(
                        request,
                        "Geen record gevonden voor betaling {}".format(
                            aflossing["omschrijving"]
                        ),
                    )
                else:
                    messages.warning(
                        request,
                        "Meerdere betalingsrecords gevonden voor mededeling {}".format(
                            aflossing["gestructureerde mededeling"]
                        ),
                    )
                    mail_admins(
                        "Meerdere records voor mededeling {}".format(
                            g_mededeling
                        ),
                        """
                    Meerdere records voor mededeling {}.
                    Tijdens het verwerken van aflossing: {},
                    werden meerdere betalingsrecords met mededeling {} gevonden.
                    """.format(
                            g_mededeling, aflossing, g_mededeling
                        ),
                    )
            except Exception as e:
                messages.error(
                    request,
                    """
                <p>Probleem bij het processen van afschrift {}</p>
                <p>{}</p>
                """.format(
                        aflossing["afschriftnummer"], e
                    ),
                )
                raise e
