import os
from datetime import date

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from weasyprint import HTML

from management.models import Seizoen


def render_to_pdf_file(template_src, request, context_dict=None):
    """
    Render a HTML-template to a pdf
    :param template_src: the source template to render to pdf
    :param request: the request uri to create base_url with
    :param context_dict: the context dictionairy.
    :return:
    """
    if context_dict is None:
        context_dict = {}
    html_string = render_to_string(template_src, context_dict)
    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    result = html.write_pdf()
    return result


def link_callback(url):
    """
    Convert HTML URIs to absolute system paths
    So xhtml2pdf can access those resources
    """
    s_url = settings.STATIC_URL
    s_root = settings.STATIC_ROOT
    m_url = settings.MEDIA_URL
    m_root = settings.MEDIA_ROOT

    if url.startswith(m_url):
        path = os.path.join(m_root, url.replace(m_url, ""))
    elif url.startswith(s_url):
        path = os.path.join(s_root, url.replace(s_url, ""))
    else:
        return dict(url)

    # make sure that file exists
    if not os.path.isfile(path):
        raise Exception(
            "media URI must start with %s or %s" % (s_url, m_url)
        )  # TODO: make this into a more specific error
    return dict(path)


def get_current_seizoen(request) -> Seizoen:
    """
    Retrieve the current seizoen.
    If the seizoen is saved in the session, retrieve it.
    Otherwise retrieve the currently active seizoen.
    If no active seizoen, choose highest start datum
    :param request: access to the session variables
    :return: the current seizoen object
    """
    today = date.today()
    if request and "seizoen" in request.session:
        pk = request.session["seizoen"]
        if pk:
            # If a seizoen is stored in the session, retrieve this seizoen
            return Seizoen.objects.get(pk=pk)
    try:
        # If there is an active seizoen, select it
        seizoen = Seizoen.objects.get(
            startdatum__lte=today, einddatum__gte=today
        )
    except ObjectDoesNotExist:
        # Default to the highest startdatum
        seizoen = Seizoen.objects.order_by("-startdatum").first()

    if not seizoen:
        return Seizoen()
    else:
        return seizoen
