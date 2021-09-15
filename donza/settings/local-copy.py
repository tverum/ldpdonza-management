ALLOWED_HOSTS = ["127.0.0.1", "localhost"]
DEBUG = True
STATIC_ROOT = '/home/tim/Projects/ldpdonza-management/static'
MEDIA_ROOT = '/home/tim/Projects/ldpdonza-management/media'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp-relay.gmail.com'
EMAIL_PORT = 587

SERVER_EMAIL = 'vanerum.tim@gmail.com'
NOREPLY = "no-reply@ldpdonza.be"