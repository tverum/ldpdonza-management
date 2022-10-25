import os

from django.conf import settings

from management.mail.send_mail import mail_w_attachment


def mail_to_admin(filename):
    """
    Mail het bestand met accounts naar de admin, verwijder het bestand
    :param filename: de file die moet gemaild worden
    :return:
    """
    from_email = settings.NOREPLY
    to_email = [admin[1] for admin in settings.ADMINS]
    reply_to = None
    filename = os.path.join(settings.BASE_DIR, filename)
    subject = "Accounts Secretariaat"
    message = "Hierbij de gegenereerde accounts voor de coaches en de ploegverantwoordelijken"

    print("Mailing file to {}".format(to_email))
    mail_w_attachment(
        from_email=from_email,
        to_email=to_email,
        filename=filename,
        subject=subject,
        message=message,
        reply_to=reply_to,
    )
    print("File mailed!")

    print("Removing accounts file")
    os.remove(filename)
    print("File Removed!")
