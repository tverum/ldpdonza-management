import datetime
from datetime import timedelta

from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template

from email.mime.image import MIMEImage

from ..models import Betaling


def lidgeld_mail(pk):
    plaintext = get_template('mail/lidgeld.txt')
    htmly = get_template('mail/lidgeld.html')

    betaling = Betaling.objects.get(pk=pk)
    lid = betaling.lid
    datum_versturen = datetime.date.today().strftime('%d-%m-%Y')
    datum_verval = (datetime.date.today() + timedelta(days=40)).strftime('%d-%m-%Y')
    to = []
    if lid.moeder.email:
        to.append(lid.moeder.email)
    if lid.vader.email:
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
    msg.content_subtype = 'html'
    msg.mixed_subtype = 'related'

    with open(image_path, mode='rb') as f:
        image = MIMEImage(f.read())
        msg.attach(image)
        image.add_header('Content-ID', '<%s>' % image_name)
    msg.send()

    betaling.status = 'mail_sent'
    betaling.mails_verstuurd = str(datetime.date.today())
    betaling.save()
