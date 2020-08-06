import json
import os

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from guardian.models import UserObjectPermission

from ...models import Lid, Functie, PloegLid, Ploeg
from ...mail.send_mail import mail_w_attachment


class Command(BaseCommand):
    help = ""

    def handle(self, **options):
        print("Generating accounts for coaches...")
        coaches_acc = generate_accounts("Coach")

        print("Generating accounts for ploegverantwoordelijken...")
        pv_acc = generate_accounts("Ploegverantwoordelijke")

        print("Writing to file...")
        filename = "coaches.json"
        write_to_file(filename, coaches_acc + pv_acc)

        print("Mailing to admin...")
        mail_to_admin(filename)


def generate_accounts(functie):
    """
    Genereer accounts voor een specifieke functies
    :param functie: de functie waarvoor accounts moeten gegenereerd worden. String-type
    :return: een lijst van gegenereerde accounts
    """
    functie = Functie.objects.get(functie=functie)
    leden = Lid.objects.filter(functies__functie=functie)

    entries = []

    for lid in leden:
        # check of de coach/ploegverantwoordelijke toegewezen is aan een ploeg
        ploegen = [Ploeg.objects.get(ploeg_id=ploeglid.ploeg.ploeg_id) for ploeglid in PloegLid.objects.filter(
            lid=lid, functie=functie)]

        # indien niet, genereer geen account voor dit lid
        if not ploegen:
            continue

        username = '{}{}'.format(lid.voornaam.replace(" ", "").lower(), lid.familienaam.replace(" ", "").lower())
        password = '{}{}'.format(lid.voornaam[::-1].replace(" ", "").lower(),
                                 lid.familienaam[::-1].replace(" ", "").lower())
        try:
            user = User.objects.create_user(
                username,
                lid.email,
                password
            )
        except IntegrityError as e:
            print("Account was al gecreëerd voor de persoon: {} {}".format(lid.voornaam, lid.familienaam))
            print(e)
            # Account was al gecreëerd voor deze persoon
            continue

        ploegen = [Ploeg.objects.get(ploeg_id=ploeglid.ploeg.ploeg_id) for ploeglid in PloegLid.objects.filter(
            lid=lid, functie=functie)]

        entries.append((lid.voornaam, lid.familienaam, username, lid.email, password,))
        for ploeg in ploegen:
            UserObjectPermission.objects.assign_perm('view_ploeg', user, obj=ploeg)

    return entries


def write_to_file(filename, entries):
    """
    Schrijf de gegenereerde accounts naar een file weg
    :param filename: de filename waar de accounts naar moeten weggeschreven worden
    :param entries: de gegenereerde accounts
    :return: None
    """
    keys = ("Voornaam", "Familienaam", "Username", "Email", "Passwoord",)
    dictionairy = [dict(zip(keys, entry)) for entry in entries]
    with open(os.path.join(settings.BASE_DIR, filename), 'w') as outfile:
        json.dump(dictionairy, outfile)


def mail_to_admin(filename):
    """
    Mail het bestand met accounts naar de admin, verwijder het bestand
    :param filename: de file die moet gemaild worden
    :return:
    """
    from_email = settings.NOREPLY
    to_email = [admin[1] for admin in settings.ADMINS]
    filename = os.path.join(settings.BASE_DIR, filename)

    print("Mailing file to {}".format(to_email))
    mail_w_attachment(from_email=from_email, to_email=to_email, filename=filename)
    print("File mailed!")

    print("Removing accounts file")
    os.remove(filename)
    print("File Removed!")