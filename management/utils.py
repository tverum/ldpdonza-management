import os

from django.conf import settings
from django.template.loader import get_template
from xhtml2pdf import pisa


def render_to_pdf_file(template_src, target_filename, context_dict={}):
    """
    Render a HTML-template to a pdf
    :param template_src: the source template to render to pdf
    :param target_filename: the filename to write the pdf to
    :param context_dict: the context dictionairy.
    :return:
    """
    template = get_template(template_src)
    html = template.render(context_dict)
    with open(target_filename, 'wb+') as outputfile:
        pisa_status = pisa.CreatePDF(html,
                                     dest=outputfile,
                                     link_callback=link_callback)
    return pisa_status.err


def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those
    resources
    """
    sUrl = settings.STATIC_URL
    sRoot = settings.STATIC_ROOT
    mUrl = settings.MEDIA_URL
    mRoot = settings.MEDIA_ROOT

    if uri.startswith(mUrl):
        path = os.path.join(mRoot, uri.replace(mUrl, ""))
    elif uri.startswith(sUrl):
        path = os.path.join(sRoot, uri.replace(sUrl, ""))
    else:
        return uri

    # make sure that file exists
    if not os.path.isfile(path):
        raise Exception(
            'media URI must start with %s or %s' % (sUrl, mUrl)
        )
    return path
