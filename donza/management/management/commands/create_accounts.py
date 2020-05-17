import json
import os

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from guardian.models import UserObjectPermission

from ...models import Lid, Functie, PloegLid, Ploeg


class Command(BaseCommand):
    help = ""

    def handle(self, **options):
        generate_coaches_accounts()


def generate_coaches_accounts():
    functie_coach = Functie.objects.get(functie="Coach")
    coaches = Lid.objects.filter(functies__functie=functie_coach)

    entries = []
    for coach in coaches:
        username = '{}{}'.format(coach.voornaam.replace(" ", "").lower(), coach.familienaam.replace(" ", "").lower())
        password = '{}{}'.format(coach.voornaam[::-1].replace(" ", "").lower(),
                                 coach.familienaam[::-1].replace(" ", "").lower())
        try:
            coach_user = User.objects.create_user(
                username,
                coach.email,
                password
            )
        except Exception:
            coach_user = User.objects.get_by_natural_key(username)

        ploegen = [Ploeg.objects.get(ploeg_id=ploeglid.ploeg.ploeg_id) for ploeglid in PloegLid.objects.filter(
            lid=coach, functie=functie_coach)]
        if ploegen:
            entries.append((coach.voornaam, coach.familienaam, username, coach.email, password,))
        for ploeg in ploegen:
            UserObjectPermission.objects.assign_perm('view_ploeg', coach_user, obj=ploeg)

    keys = ("Voornaam", "Familienaam", "Username", "Email", "Passwoord",)
    dictionairy = [dict(zip(keys, entry)) for entry in entries]
    with open(os.path.join(settings.BASE_DIR, "coaches.json"), 'w') as outfile:
        json.dump(dictionairy, outfile)
