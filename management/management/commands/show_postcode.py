from django.core.management.base import BaseCommand

from ...models import *


class Command(BaseCommand):
    help = ""

    def handle(self, **options):

        postcode = int(input("Geef de postcode op van welke de leden moeten gefilterd worden"))
        functie_speler = Functie.objects.get(functie="Speler")

        # Iterereer over alle betalingen
        for lid in Lid.objects.filter(postcode=postcode):

            ploegen = PloegLid.objects.filter(lid=lid, functie=functie_speler)

            # Als het lid in kwestie geen ploeg heeft, sla over
            if not ploegen:
                continue

            if len(ploegen == 1):
                print("{} {} -> {}".format(lid.voornaam, lid.familienaam, ploegen.ploeg))
            else:
                ploegen = [ploeg.ploeg for ploeg in ploegen]
                ploegen = "[" + ",".join(ploegen) + "]"
                print("{} {} -> {}".format(lid.voornaam, lid.familienaam, ploegen))
