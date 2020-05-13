from donza.settings.base import *

ALLOWED_HOSTS = ["secretariaat.ldpdonza.be"]
DEBUG = False
STATIC_ROOT = '/home/tim/static'
MEDIA_ROOT = '/home/tim/media'

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True