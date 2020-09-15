import datetime
import os
from datetime import timedelta
from email.mime.image import MIMEImage

from django.conf import settings
from django.core.mail import EmailMessage
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template

from ..models import Betaling, Lid
from ..utils import render_to_pdf_file


def lidgeld_mail(pk):
    plaintext = get_template('mail/lidgeld.txt')
    htmly = get_template('mail/lidgeld.html')

    betaling = Betaling.objects.get(pk=pk)
    lid = betaling.lid
    datum_versturen = datetime.date.today().strftime('%d-%m-%Y')
    datum_verval = (datetime.date.today() + timedelta(days=40)).strftime('%d-%m-%Y')
    to = []
    if lid.moeder:
        to.append(lid.moeder.email)
    if lid.vader:
        to.append(lid.vader.email)
    if lid.email:
        to.append(lid.email)

    d = {
        'betaling': betaling,
        'lid': lid,
        'datum_versturen': datum_versturen,
        'datum_verval': datum_verval,
        'emailadressen': to,
    }

    image_path = "management/static/management/images/signature.png"
    image_name = "signature"

    subject, from_email = "Inschrijvingsgeld {} LDP Donza, seizoen '20-'21".format(
        lid), 'no-reply@ldpdonza.be'
    text_content = plaintext.render(d)
    html_content = htmly.render(d)

    msg = EmailMultiAlternatives(subject, text_content, from_email, to, reply_to=['pol@ldpdonza.be'])
    msg.attach_alternative(html_content, "text/html")
    msg.mixed_subtype = 'related'

    with open(image_path, mode='rb') as f:
        image = MIMEImage(f.read())
        msg.attach(image)
        image.add_header('Content-ID', '<%s>' % image_name)
    msg.send()

    betaling.status = 'mail_sent'
    betaling.mails_verstuurd = str(datetime.date.today())
    betaling.save()


def send_herinnering(pk):
    """
    Stuur een betalingsherinnering voor een bepaalde betaling
    :param pk: de betalingsinstantie waarvoor de herinnering moet gegenereerd worden
    :return: None
    """
    plaintext = get_template('mail/herinnering.txt')
    htmly = get_template('mail/herinnering.html')

    betaling = Betaling.objects.get(pk=pk)
    lid = betaling.lid
    datum_verval = (datetime.date.today() + timedelta(days=21)).strftime('%d-%m-%Y')
    datum_vorige_mail = betaling.mails_verstuurd.split(";")[-1]
    to = []
    if lid.moeder:
        to.append(lid.moeder.email)
    if lid.vader:
        to.append(lid.vader.email)
    if lid.email:
        to.append(lid.email)

    d = {
        'betaling': betaling,
        'lid': lid,
        'datum_verval': datum_verval,
        'datum_vorige_mail': datum_vorige_mail,
        'emailadressen': to,
    }

    image_path = "management/static/management/images/signature.png"
    image_name = "signature"

    subject, from_email = "HERINNERING: Inschrijvingsgeld {} LDP Donza, seizoen '20-'21".format(
        lid), 'no-reply@ldpdonza.be'
    text_content = plaintext.render(d)
    html_content = htmly.render(d)

    msg = EmailMultiAlternatives(subject, text_content, from_email, to, reply_to=['pol@ldpdonza.be'])
    msg.attach_alternative(html_content, "text/html")
    msg.mixed_subtype = 'related'

    with open(image_path, mode='rb') as f:
        image = MIMEImage(f.read())
        msg.attach(image)
        image.add_header('Content-ID', '<%s>' % image_name)
    msg.send()

    betaling.status = 'mail_sent'
    betaling.mails_verstuurd += ";" + str(datetime.date.today())
    betaling.save()


def bevestig_betaling(pk):
    """
    Bevestig een bepaalde betaling en verstuur de mutualiteitsformulieren etc.
    :param pk: de betaling die bevestigd moet worden
    :return: None
    """
    filename = "temp.pdf"
    temp = os.path.join(settings.BASE_DIR, filename)
    betaling = Betaling.objects.get(pk=pk)
    lid = betaling.lid
    seizoen = betaling.seizoen
    datum_betaling = betaling.aflossingen.split(";")[-1]
    datum_afgifte = datetime.date.today()
    context = {
        'betaling': betaling,
        'lid': lid,
        'seizoen': seizoen,
        'datum_betaling': datum_betaling,
        'datum_afgifte': datum_afgifte,
    }
    render_to_pdf_file('pdf/betalingsbevestiging.html', temp, context)
    mail_w_attachment("vanerum.tim@gmail.com", ["vanerum.tim@gmail.com"], temp, "Test", "Test")


def mail_w_attachment(from_email, to_email, filename, subject, message):
    """
    Verstuur een mail met een attachment gespecifieerd in filename
    :param from_email: het emailadres van waarop te sturen
    :param to_email: de emailadressen waarnaar te sturen
    :param filename: de file die moet verstuurd worden
    :param subject: het onderwerp dat aan de mail moet meegegeven worden
    :param message: de body van het bericht
    :return: None
    """
    msg = EmailMessage(subject,
                       message,
                       from_email,
                       to_email)

    msg.content_subtype = "html"
    msg.attach_file(filename)
    msg.send()
