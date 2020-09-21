import os

from django.conf import settings
from django.template.loader import get_template, render_to_string
from weasyprint import HTML, default_url_fetcher


def render_to_pdf_file(template_src, target_filename, request, context_dict={}):
    """
    Render a HTML-template to a pdf
    :param template_src: the source template to render to pdf
    :param target_filename: the filename to write the pdf to
    :param context_dict: the context dictionairy.
    :return:
    """
    html_string = render_to_string(template_src, context_dict)
    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    result = html.write_pdf()
    return result


def link_callback(url):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those
    resources
    """
    sUrl = settings.STATIC_URL
    sRoot = settings.STATIC_ROOT
    mUrl = settings.MEDIA_URL
    mRoot = settings.MEDIA_ROOT

    if url.startswith(mUrl):
        path = os.path.join(mRoot, url.replace(mUrl, ""))
    elif url.startswith(sUrl):
        path = os.path.join(sRoot, url.replace(sUrl, ""))
    else:
        return dict(url)

    # make sure that file exists
    if not os.path.isfile(path):
        raise Exception(
            'media URI must start with %s or %s' % (sUrl, mUrl)
        )
    return dict(path)
