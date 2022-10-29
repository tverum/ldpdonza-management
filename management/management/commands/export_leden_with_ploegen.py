import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from management.management.commands.mail_to_admin import mail_to_admin
from management.models import PloegLid


class Command(BaseCommand):
    help = ""

    def handle(self, **options):
        ploegleden = PloegLid.objects.all()

        leden = [
            (
                ploeglid.lid.familienaam,
                ploeglid.lid.voornaam,
                ploeglid.lid.straatnaam_en_huisnummer,
                ploeglid.lid.gemeente,
                ploeglid.lid.postcode,
                ploeglid.ploeg.naam,
                ploeglid.functie.functie,
            )
            for ploeglid in ploegleden
        ]

        print("Writing to file...")
        filename = "ploegleden.json"
        write_to_file(filename, leden)

        print("Mailing to admin...")
        mail_to_admin(filename)


def write_to_file(filename, entries):
    """
    Schrijf de gegenereerde accounts naar een file weg
    :param filename: de filename voor wegschrijven
    :param entries: de gegenereerde accounts
    :return: None
    """
    keys = (
        "Familienaam",
        "Voornaam",
        "Straatnaam en Huisnummer",
        "Gemeente",
        "Postcode",
        "Ploeg",
        "Functie",
    )
    dictionairy = [dict(zip(keys, entry)) for entry in entries]
    with open(os.path.join(settings.BASE_DIR, filename), "w") as outfile:
        json.dump(dictionairy, outfile)
