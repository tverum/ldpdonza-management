ALLOWED_HOSTS = ["secretariaat.ldpdonza.be", "localhost"]
DEBUG = False
STATIC_ROOT = "/home/tim/static"
MEDIA_ROOT = "/home/tim/media"

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_USE_TLS = True
EMAIL_HOST = "smtp-relay.gmail.com"
EMAIL_PORT = 587

SERVER_EMAIL = "secretariaat-admin@ldpdonza.be"
NOREPLY = "no-reply@ldpdonza.be"
