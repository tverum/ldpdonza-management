from os import terminal_size
from typing import Sequence
from django.conf import settings

from django.core import mail
from django.core.exceptions import ImproperlyConfigured
from ..models import Functie, Lid, PloegKenmerk, PloegLid, Seizoen
from .send_mail import send_mail_template


def determine_group(group: str, seizoen: Seizoen) -> Sequence[Lid]:
    """
    [Bepaal de group op basis van de tag gegeven in de form]

    Args:
        group (str): [de group tag gegeven in de form]
        seizoen (Seizoen): [het seizoen waarvoor de mails moeten verstuurd worden. Belangrijk bij het bepalen van de actieve leden]

    Returns:
        [Sequence[Lid]]: [alle leden die binnen de groep vallen]
    """
    if group == "active-ladies":
        kenmerk = PloegKenmerk.objects.get(kenmerk="Dames")
        ploegleden = PloegLid.objects.filter(
            functie=Functie.objects.get(functie="Speler"),
            ploeg__seizoen=seizoen,
            ploeg__kenmerken=kenmerk
        )
        leden = [pl.lid for pl in ploegleden]
        return list(set(leden))
    elif group == "active-men":
        kenmerk = PloegKenmerk.objects.get(kenmerk="Heren")
        ploegleden = PloegLid.objects.filter(
            functie=Functie.objects.get(functie="Speler"),
            ploeg__seizoen=seizoen,
            ploeg__kenmerken=kenmerk
        )
        leden = [pl.lid for pl in ploegleden]
        return list(set(leden))
    elif group == "bovenbouw-heren":
        kenmerk_bovenbouw = PloegKenmerk.objects.get(kenmerk="Bovenbouw")
        kenmerk_heren = PloegKenmerk.objects.get(kenmerk="Heren")
        ploegleden = PloegLid.objects.filter(
            functie=Functie.objects.get(functie="Speler"),
            ploeg__seizoen=seizoen,
            ploeg__kenmerken=kenmerk_bovenbouw
        ).filter(
            ploeg__kenmerken=kenmerk_heren
        )
        leden = [pl.lid for pl in ploegleden]
        return list(set(leden))
    elif group == "bovenbouw-dames":
        kenmerk_bovenbouw = PloegKenmerk.objects.get(kenmerk="Bovenbouw")
        kenmerk_dames = PloegKenmerk.objects.get(kenmerk="Dames")
        ploegleden = PloegLid.objects.filter(
            functie=Functie.objects.get(functie="Speler"),
            ploeg__seizoen=seizoen,
            ploeg__kenmerken=kenmerk_bovenbouw
        ).filter(
            ploeg__kenmerken=kenmerk_dames
        )
        leden = [pl.lid for pl in ploegleden]
        return list(set(leden))
    elif group == "onderbouw":
        kenmerk = PloegKenmerk.objects.get(kenmerk="Onderbouw")
        ploegleden = PloegLid.objects.filter(
            functie=Functie.objects.get(functie="Speler"),
            ploeg__seizoen=seizoen,
            ploeg__kenmerken=kenmerk
        )
        leden = [pl.lid for pl in ploegleden]
        return list(set(leden))
    elif group == "senioren":
        kenmerk = PloegKenmerk.objects.get(kenmerk="Senioren")
        ploegleden = PloegLid.objects.filter(
            functie=Functie.objects.get(functie="Speler"),
            ploeg__seizoen=seizoen,
            ploeg__kenmerken=kenmerk
        )
        leden = [pl.lid for pl in ploegleden]
        return list(set(leden))
    elif group == 'all-active':
        ploegleden = PloegLid.objects.filter(
            functie=Functie.objects.get(functie="Speler"), ploeg__seizoen=seizoen)
        leden = [pl.lid for pl in ploegleden]
        return list(set(leden))
    else:
        raise NotImplementedError


def retrieve_mails(leden: Sequence[Lid], incl_ouders: bool) -> Sequence[str]:
    """
    [Haal de e-mailadressen op waarvoor de mails moeten verstuurd worden]

    Args:
        leden (Sequence[Lid]): [de leden waarvoor de mails moeten opgehaald worden]
        incl_ouders (bool): [boolean die aangeeft of de ouder-mailadressen mee moeten opgehaald worden]

    Returns:
        Sequence[str]: [een lijst van e-mailadressen waarnaar de mail moet verstuurd worden]
    """
    mails = []
    for lid in leden:
        mails.append(lid.email)

        if incl_ouders:
            if lid.moeder:
                mails.append(lid.moeder.email)
            if lid.vader:
                mails.append(lid.vader.email)

    return mails


def group_mail(group: str, mail_template: str, subject: str, reply: str, seizoen: Seizoen) -> None:
    """
    [Send a mail to a given group identified by the group tag 'group']

    Args:
        group (str): [the group tag of the group]
        mail_template (str): [the location of the mail template to be sent]
        subject (str): [the subject of the mail]
        reply (str): [the reply adress of the subject]
        seizoen (Seizoen): [the current seizoen, for which the group should be determined]
    """
    # Retrieve the leden based on the group tag and retrieve the adresses of the group.
    leden = determine_group(group=group, seizoen=seizoen)
    mails = retrieve_mails(leden=leden, incl_ouders=True)

    # Send mail from no-reply to all the mailadresses.
    from_email = 'no-reply@ldpdonza.be'
    for mail in mails:
        send_mail_template(mail_template,
                           mail_template.replace('html', 'txt'),
                           {},
                           [mail],
                           from_email,
                           subject,
                           [reply]
                           )
