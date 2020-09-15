from django.core.management.base import BaseCommand

from ...models import *


class Command(BaseCommand):
    help = ""

    def handle(self, **options):
        # Iterereer over alle betalingen
        for betaling in Betaling.objects.all():
            lid = betaling.lid
            ploegen = PloegLid.objects.filter(lid=lid)

            # Als het lid in kwestie geen ploeg heeft, print de naam
            if not ploegen:
                print(lid)
