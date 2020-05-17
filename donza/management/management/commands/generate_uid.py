from django.core.management.base import BaseCommand

from ...main.utils import generate_uid
from ...models import Lid


class Command(BaseCommand):
    help = ""

    def handle(self, **options):
        generate_uids()


def generate_uids():
    lid_qs = Lid.objects.filter(uid=None)
    for lid in lid_qs:
        lid.uid = generate_uid()
        lid.save()
