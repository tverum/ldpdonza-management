"""@package docstring
Documentatie voor ledenbeheer.

Omvat alle functies voor het importeren, wijzigen en verwijderen van leden
"""

import io
import csv
import datetime
import re

from django.contrib import messages

from ..models import Ouder, Lid, Functie, MAN, VROUW, ANDER
from .utils import generate_uid

GSM_PATTERN = r"0(\d{3})/(\d+)"
ADRES_PATTERN = r"(\d+)(.*)"


def import_from_csv(csv_file, request):
    """
    Importeer leden van een csv-file
    :param csv_file: de geuploade csv-file
    :param request: de request waarbij de csv-filie geupload is
    :return: None
    """
    # set up the filestream
    data_set = csv_file.read().decode('UTF-8')
    io_string = io.StringIO(data_set)

    keys = []
    for index, row in enumerate(csv.reader(io_string, delimiter=';', quotechar="|")):
        if index == 0:
            # something is messed up with the first column of the csv file
            keys = [key.strip() for key in row]
        else:
            values = [value.strip() for value in row]
            row = dict(zip(keys, values))
            try:
                geboortedatum = format_geboortedatum(row)
                gescheiden = True if row["Gescheiden ouders?"] else False

                ouder_1, _ = Ouder.objects.get_or_create(
                    gsmnummer=row["Gsm Mama"],
                    email=row["Email Mama"]
                )
                ouder_2, _ = Ouder.objects.get_or_create(
                    gsmnummer=row["Gsm Papa"],
                    email=row["Email Papa"]
                )

                gsm_nummer = format_gsm_nummer(row)

                if row["Geslacht"] == "Male":
                    geslacht = MAN
                elif row["Geslacht"] == "Female":
                    geslacht = VROUW
                else:
                    geslacht = ANDER

                update_lid(geboortedatum, gescheiden, gsm_nummer, geslacht, ouder_1, ouder_2, row)

            except Exception as e:
                if row["Voornaam"] and row["Familienaam"]:
                    messages.error(request, """
                    <p>Probleem bij het processen van rij {}: {} {}</p>
                    <p>{}</p>
                    """.format(index + 1, row["Voornaam"], row["Familienaam"], e))


def update_lid(geboortedatum, gescheiden, gsm_nummer, geslacht, ouder_1, ouder_2, row):
    """
    Update het lid in de database
    :param geboortedatum: geboortedatum in correct format
    :param gescheiden: boolean die aanduidt of er gescheiden ouders zijn
    :param gsm_nummer: correct geformat gsmnummer
    :param geslacht: correct geformat geslacht
    :param ouder_1:
    :param ouder_2:
    :param row: row van de CSV-reader
    :return: None
    """

    # Fetch het lid van de database, add functie en save
    lid, created = get_lid(geboortedatum, gescheiden, gsm_nummer, geslacht, ouder_1, ouder_2, row)

    # Update de velden
    lid_update_functies(lid, row)
    lid_update_familieleden(lid)

    # Alleen de uid updaten als het een nieuw record is
    if created:
        lid_update_uid(lid)

    # Sla op
    lid.save()


def lid_update_uid(lid):
    """
    Update the uid of the lid
    :param lid:
    :return:
    """
    lid.uid = generate_uid()


def lid_update_familieleden(lid):
    """
    Update de familieleden van het lid.
    Gebeurt op basis van het adres. Mensen die op hetzelfde adres wonen worden verondersteld om tot hetzelfde gezin te behoren
    :param lid: Het lid dat moet geupdate worden
    :return: None
    """
    # selecteer alle leden die op hetzelfde adres wonen, met uitzondering van het lid zelf
    familieleden = Lid.objects.filter(
        straatnaam_en_huisnummer=lid.straatnaam_en_huisnummer,
        postcode=lid.postcode
    ).exclude(
        club_id=lid.club_id
    )
    for familielid in familieleden:
        lid.familieleden.add(familielid.club_id)


def lid_update_functies(lid, row):
    """
    Voeg de functies van het lid toe. Pas ook eventuele flags aan op basis van de functie.
    :param lid: Het lid dat geupdate moet worden
    :param row: Row van de csv-reader
    :return:
    """
    # Retrieve de functie, of creëer indien die nog niet bestaat
    if not row["Functie"]:
        return
    functie, _ = Functie.objects.get_or_create(
        functie=row["Functie"]
    )
    lid.functies.add(functie)

    # Alleen spelers gelden als sportieve leden en moeten lidgeld betalen
    if functie.functie == "Speler":
        lid.sportief_lid = True
        lid.betalend_lid = True


def get_lid(geboortedatum, gescheiden, gsm_nummer, geslacht, ouder_1, ouder_2, row):
    """
    Creëer het lid indien het nog niet bestaat, anders, fetch het uit de database.
    :param geboortedatum: Correct geformatte geboortedatum
    :param gescheiden: Boolean die aanduidt of er sprake is van gescheiden ouders
    :param gsm_nummer: Correct geformat gsmnummer
    :param geslacht: Correct geformat geslacht
    :param ouder_1: Ouder instantie
    :param ouder_2: Ouder instantie
    :param row: Row van de csv-reader
    :return: Lid instantie met bepaalde velden reeds ingevuld.
    """
    return Lid.objects.get_or_create(
        voornaam=row["Voornaam"],
        familienaam=row["Familienaam"],
        straatnaam_en_huisnummer=row["Straat + nummer"],
        postcode=row["Postcode"],
        gemeente=row["Gemeente"],
        geboortedatum=geboortedatum,
        gsmnummer=gsm_nummer,
        geslacht=geslacht,
        email=row["Jouw email"],
        gescheiden_ouders=gescheiden,
        extra_informatie=row["Extra info"],
        rekeningnummer=row["Rekeningnummer"],
        moeder_id=ouder_1.ouder_id,
        vader_id=ouder_2.ouder_id,
    )


def format_gsm_nummer(row):
    """
    Format het gsm-nummer op een consistente manier
    :param row: de row van de csv-reader
    :return: Het gsmnummer in het correcte formaat.
    """
    gsm_match = re.match(GSM_PATTERN, row["Jouw gsm"])
    if gsm_match:
        gsm_nummer = "+32{}{}".format(gsm_match.group(1), gsm_match.group(2))
    else:
        gsm_nummer = ""
    return gsm_nummer


def format_geboortedatum(row):
    """
    Format de geboortedatum op een consistente manier
    :param row: de row van de csv-reader
    :return: De geboortedatum in het correcte formaat
    """
    # parse the birthdate to the correct format
    geboortedatum = datetime.datetime.strptime(
        row["Geboortedatum"], '%d/%m/%Y').strftime('%Y-%m-%d') if row["Geboortedatum"] else None
    return geboortedatum
