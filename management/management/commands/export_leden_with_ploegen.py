import os
import json

from django.core.management.base import BaseCommand
from django.conf import settings

from management.models import PloegLid
from management.management.commands.utils import mail_to_admin

class Command(BaseCommand):
    help = ""

    def handle(self, **options):

        ploegleden = PloegLid.objects.all()

        leden = [(
            ploeglid.lid.familienaam,
            ploeglid.lid.voornaam,
            ploeglid.lid.straatnaam_en_huisnummer,
            ploeglid.lid.gemeente,
            ploeglid.lid.postcode,
            ploeglid.ploeg.naam
        ) for ploeglid in ploegleden]

        print("Writing to file...")
        filename = "ploegleden.json"
        write_to_file(filename, leden)

        print("Mailing to admin...")
        mail_to_admin(filename)


def write_to_file(filename, entries):
    """
    Schrijf de gegenereerde accounts naar een file weg
    :param filename: de filename waar de accounts naar moeten weggeschreven worden
    :param entries: de gegenereerde accounts
    :return: None
    """
    keys = (
        "Familienaam",
        "Voornaam",
        "Straatnaam en Huisnummer",
        "Gemeente",
        "Postcode",
        "Ploeg"
    )
    dictionairy = [dict(zip(keys, entry)) for entry in entries]
    with open(os.path.join(settings.BASE_DIR, filename), 'w') as outfile:
        json.dump(dictionairy, outfile)