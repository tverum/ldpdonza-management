from django.core.management.base import BaseCommand

from ...models import Functie, Lid, PloegLid


class Command(BaseCommand):
    help = ""

    def handle(self, **options):

        postcode = int(input("Geef de postcode waarop gefilterd moet worden"))
        functie_speler = Functie.objects.get(functie="Speler")

        # Iterereer over alle betalingen
        for lid in Lid.objects.filter(postcode=postcode):

            ploegen = PloegLid.objects.filter(lid=lid, functie=functie_speler)

            # Als het lid in kwestie geen ploeg heeft, sla over
            if not ploegen:
                continue

            ploegen = [str(ploeg.ploeg) for ploeg in ploegen]
            ploegen = "[" + ",".join(ploegen) + "]"
            print("{} {} -> {}".format(lid.voornaam, lid.familienaam, ploegen))
