# noinspection PyUnresolvedReferences
from .base import *

DEBUG = True

ALLOWED_HOSTS = ["localhost"]

SERVER_EMAIL = 'vanerum.tim@gmail.com'
NOREPLY = 'vanerum.tim@gmail.com'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'vanerum.tim@gmail.com'
EMAIL_HOST_PASSWORD = 'AA135Tim'

SITE_ID = 1
