"""@package docstring
Documentatie voor betalingen.

Omvat alle functies voor het genereren van betalingen, versturen van e-mails etc.
"""
from ..models import Betaling


def no_payment(lid):
    return Betaling.objects.filter(lid=lid).count() == 0


def bereken_bedrag(lid):
    pass


def get_type(lid):
    pass


def gestructureerde_mededeling(lid):
    return "gestructureerde mededeling"


def genereer_betaling(lid):
    origineel_bedrag = bereken_bedrag(lid)
    gestructureerde_mededeling = gestructureerde_mededeling(lid)
    type = get_type(lid)



def genereer_betalingen(leden):
    leden_todo = list(filter(no_payment, leden))

    for lid in leden_todo:
        genereer_betaling(lid)


