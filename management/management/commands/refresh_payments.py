from django.core.management.base import BaseCommand

from ...models import *


class Command(BaseCommand):
    help = ""

    def handle(self, **options):
        # Iterereer over alle betalingen
        for betaling in Betaling.objects.filter(status='mail_sent'):
            if betaling.origineel_bedrag == betaling.afgelost_bedrag:
                betaling.status = 'betaald'
                betaling.save()
