import datetime
import tempfile
from datetime import timedelta
from email.mime.image import MIMEImage
from typing import Sequence

from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import get_template, render_to_string

from ..models import Betaling
from ..utils import render_to_pdf_file


def send_mail_template(
    html_template: str,
    txt_template: str,
    context: dict,
    to: Sequence[str],
    from_email: str,
    subject: str,
    reply_to=None,
):
    """
    Send the mail using a template
    :param template: the template to render
    :param context: the context to render in the template
    :param to: the recipients of the mail
    :param from_email: from where the mail is sent
    :param subject: the subject of the mail
    :param reply_to: to who should the mail be answered
    :return:
    """
    html = get_template(html_template)
    plaintext = get_template(txt_template)
    html_content = html.render(context)
    text_content = plaintext.render(context)

    msg = EmailMultiAlternatives(
        subject, text_content, from_email, to, reply_to=[reply_to]
    )
    msg.attach_alternative(html_content, "text/html")
    msg.mixed_subtype = "related"
    msg.send()


def lidgeld_mail(pk):
    plaintext = get_template("mail/lidgeld.txt")
    htmly = get_template("mail/lidgeld.html")

    betaling = Betaling.objects.get(pk=pk)
    lid = betaling.lid
    datum_versturen = datetime.date.today().strftime("%d-%m-%Y")
    datum_verval = (datetime.date.today() + timedelta(days=40)).strftime(
        "%d-%m-%Y"
    )
    to = []
    if lid.moeder:
        to.append(lid.moeder.email)
    if lid.vader:
        to.append(lid.vader.email)
    if lid.email:
        to.append(lid.email)

    d = {
        "betaling": betaling,
        "lid": lid,
        "datum_versturen": datum_versturen,
        "datum_verval": datum_verval,
        "emailadressen": to,
    }

    image_path = "management/static/management/images/signature.png"
    image_name = "signature"

    subject, from_email = (
        "Inschrijvingsgeld {} LDP Donza, seizoen '20-'21".format(lid),
        "no-reply@ldpdonza.be",
    )
    text_content = plaintext.render(d)
    html_content = htmly.render(d)

    msg = EmailMultiAlternatives(
        subject, text_content, from_email, to, reply_to=["pol@ldpdonza.be"]
    )
    msg.attach_alternative(html_content, "text/html")
    msg.mixed_subtype = "related"

    with open(image_path, mode="rb") as f:
        image = MIMEImage(f.read())
        msg.attach(image)
        image.add_header("Content-ID", "<%s>" % image_name)
    msg.send()

    betaling.status = "mail_sent"
    betaling.mails_verstuurd = str(datetime.date.today())
    betaling.save()


def send_herinnering(pk):
    """
    Stuur een betalingsherinnering voor een bepaalde betaling
    :param pk: de betalingsinstantie voor herinnering
    """
    plaintext = get_template("mail/herinnering.txt")
    htmly = get_template("mail/herinnering.html")

    betaling = Betaling.objects.get(pk=pk)
    lid = betaling.lid
    datum_verval = (datetime.date.today() + timedelta(days=21)).strftime(
        "%d-%m-%Y"
    )
    datum_vorige_mail = betaling.mails_verstuurd.split(";")[-1]
    to = []
    if lid.moeder:
        to.append(lid.moeder.email)
    if lid.vader:
        to.append(lid.vader.email)
    if lid.email:
        to.append(lid.email)

    d = {
        "betaling": betaling,
        "lid": lid,
        "datum_verval": datum_verval,
        "datum_vorige_mail": datum_vorige_mail,
        "emailadressen": to,
    }

    image_path = "management/static/management/images/signature.png"
    image_name = "signature"

    subject, from_email = (
        "HERINNERING: Inschrijvingsgeld {} LDP Donza, seizoen '20-'21".format(
            lid
        ),
        "no-reply@ldpdonza.be",
    )
    text_content = plaintext.render(d)
    html_content = htmly.render(d)

    msg = EmailMultiAlternatives(
        subject, text_content, from_email, to, reply_to=["pol@ldpdonza.be"]
    )
    msg.attach_alternative(html_content, "text/html")
    msg.mixed_subtype = "related"

    with open(image_path, mode="rb") as f:
        image = MIMEImage(f.read())
        msg.attach(image)
        image.add_header("Content-ID", "<%s>" % image_name)
    msg.send()

    betaling.status = "mail_sent"
    betaling.mails_verstuurd += ";" + str(datetime.date.today())
    betaling.save()


def bevestig_betaling(pk, request):
    """
    Bevestig een bepaalde betaling en verstuur de mutualiteitsformulieren etc.
    :param pk: de betaling die bevestigd moet worden
    :param request: request object, required to authenticate the user
    """
    betaling = Betaling.objects.get(pk=pk)
    lid = betaling.lid
    seizoen = betaling.seizoen
    datum_betaling = betaling.aflossingen.split(",")[-1]

    subject = "Betalingsbevestiging en attest mutualiteit voor {} {}".format(
        lid.voornaam, lid.familienaam
    )
    context = {
        "lid": lid,
        "seizoen": seizoen,
    }
    message = render_to_string("mail/betalingsbevestiging.html", context)

    to = []
    if lid.moeder:
        to.append(lid.moeder.email)
    if lid.vader:
        to.append(lid.vader.email)
    if lid.email:
        to.append(lid.email)

    from_email = "no-reply@ldpdonza.be"
    reply_to = ["secretariaat@ldpdonza.be"]

    # reverse betaling datum
    datum_betaling = "-".join(list(datum_betaling.split("/")))
    datum_afgifte = datetime.date.today()
    context = {
        "betaling": betaling,
        "lid": lid,
        "seizoen": seizoen,
        "datum_betaling": datum_betaling,
        "datum_afgifte": datum_afgifte,
    }
    result = render_to_pdf_file(
        "pdf/betalingsbevestiging.html", request, context
    )
    with tempfile.NamedTemporaryFile(
        delete=True, prefix="ldpdonza", suffix=".pdf"
    ) as output:
        output.write(result)
        output.flush()
        mail_w_attachment(
            from_email,
            to,
            output.name,
            subject=subject,
            message=message,
            reply_to=reply_to,
        )

    betaling.status = "voltooid"
    betaling.save()


def mail_w_attachment(
    from_email, to_email, filename, subject, message, reply_to
):
    """
    Verstuur een mail met een attachment gespecifieerd in filename
    :param from_email: het emailadres van waarop te sturen
    :param to_email: de emailadressen waarnaar te sturen
    :param filename: de file die moet verstuurd worden
    :param subject: het onderwerp dat aan de mail moet meegegeven worden
    :param message: de body van het bericht
    :param reply_to: het reply-to adres voor de mail
    :return: None
    """
    msg = EmailMessage(
        subject, message, from_email, to_email, reply_to=reply_to
    )

    msg.content_subtype = "html"
    msg.attach_file(filename)
    msg.send()
