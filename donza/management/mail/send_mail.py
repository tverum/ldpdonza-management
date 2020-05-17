import datetime
from datetime import timedelta

from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template

from ..models import Betaling


def lidgeld_mail(pk):
    plaintext = get_template('mail/lidgeld.txt')
    htmly = get_template('mail/lidgeld.html')

    betaling = Betaling.objects.get(pk=pk)
    lid = betaling.lid
    datum_versturen = datetime.date.today().strftime('%d-%m-%Y')
    datum_verval = (datetime.date.today() + timedelta(days=40)).strftime('%d-%m-%Y')
    d = {
        'betaling': betaling,
        'lid': lid,
        'datum_versturen': datum_versturen,
        'datum_verval': datum_verval,
    }

    subject, from_email, to = "Inschrijvingsgeld {} LDP Donza, seizoen '20-'21".format(
        lid), 'tim.vanerum@gmail.com', 'vanerum.tim@icloud.com'
    text_content = plaintext.render(d)
    html_content = htmly.render(d)
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
