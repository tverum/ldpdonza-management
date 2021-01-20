import json
import os

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from guardian.models import UserObjectPermission

from .utils import mail_to_admin
from ...models import Lid, Functie, PloegLid, Ploeg
from ...mail.send_mail import send_mail_template


class Command(BaseCommand):
    help = """
    Maak accounts aan voor de coaches & ploegafgevaardigden.
    """

    def add_arguments(self, parser):
        """
        Add arguments to the command
        :param parser: the parser that is used in parsing the command
        """
        # Named (optional) arguments
        parser.add_argument('-p', '--send-mails-pa',
                            action='store_true', help="Stuur mails naar de PAs")
        parser.add_argument('-c', '--send-mails-coaches',
                            action='store_true', help="Stuur mails naar de Coaches")
        parser.add_argument('-m', '--mailadressen', nargs='+',
                            help="Stuur mails voor de opgegeven mailadressen")

    def handle(self, *args, **kwargs):

        print("Args: {}".format(args))
        print("Kwargs: {}".format(kwargs))

        send_mails_pa = kwargs['send_mails_pa']
        send_mails_coaches = kwargs['send_mails_coaches']
        mailadressen = kwargs['mailadressen']

        self.stdout.write(self.style.SUCCESS(
            "Generating accounts for coaches..."))
        coaches_acc = generate_accounts("Coach")

        self.stdout.write(self.style.SUCCESS(
            "Generating accounts for ploegverantwoordelijken..."))
        pv_acc = generate_accounts("Ploegverantwoordelijke")

        self.stdout.write(self.style.SUCCESS("Writing to file..."))
        filename = "accounts.json"
        write_to_file(filename, coaches_acc + pv_acc)

        self.stdout.write(self.style.SUCCESS("Mailing to admin..."))
        mail_to_admin(filename)

        if send_mails_pa:
            send_mails(pv_acc)
        if send_mails_coaches:
            send_mails(coaches_acc)
        if mailadressen:
            entries = [entry for entry in (
                coaches_acc + pv_acc) if entry[3] in mailadressen]
            send_mails(entries)


def send_mails(entries):
    """
    Send account email to the list of people
    :param entries:
    :return:
    """
    mail_template = "mail/accountmail.html"
    from_email = "no-reply@ldpdonza.be"
    reply_to = ["vanerum.tim@gmail.com", ]
    subject = "Account Ledenportaal LDP Donza"

    raise NotImplementedError


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

        username = '{}{}'.format(lid.voornaam.replace(
            " ", "").lower(), lid.familienaam.replace(" ", "").lower())
        password = '{}{}'.format(lid.voornaam[::-1].replace(" ", "").lower(),
                                 lid.familienaam[::-1].replace(" ", "").lower())
        try:
            user = User.objects.create_user(
                username,
                lid.email,
                password
            )
        except IntegrityError as e:
            print("Account was al gecreëerd voor de persoon: {} {}".format(
                lid.voornaam, lid.familienaam))
            user = User.objects.get_by_natural_key(username)
            if user.check_password(password):
                entries.append((lid.voornaam, lid.familienaam,
                                username, lid.email, password, False))
            else:
                entries.append((lid.voornaam, lid.familienaam,
                                username, lid.email, password, True))
            # Account was al gecreëerd voor deze persoon
            continue

        ploegen = [Ploeg.objects.get(ploeg_id=ploeglid.ploeg.ploeg_id) for ploeglid in PloegLid.objects.filter(
            lid=lid, functie=functie)]

        entries.append((lid.voornaam, lid.familienaam,
                        username, lid.email, password, False))
        for ploeg in ploegen:
            UserObjectPermission.objects.assign_perm(
                'view_ploeg', user, obj=ploeg)

    return entries


def write_to_file(filename, entries):
    """
    Schrijf de gegenereerde accounts naar een file weg
    :param filename: de filename waar de accounts naar moeten weggeschreven worden
    :param entries: de gegenereerde accounts
    :return: None
    """
    keys = ("Voornaam", "Familienaam", "Username",
            "Email", "Passwoord", "Aangepast")
    dictionairy = [dict(zip(keys, entry)) for entry in entries]
    with open(os.path.join(settings.BASE_DIR, filename), 'w') as outfile:
        json.dump(dictionairy, outfile)
