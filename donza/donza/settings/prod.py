from donza.settings.base import *

ALLOWED_HOSTS = ["secretariaat.ldpdonza.be"]
DEBUG = False
STATIC_ROOT = '/home/tim/static'
MEDIA_ROOT = '/home/tim/media'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp-relay.gmail.com'
EMAIL_PORT = 587