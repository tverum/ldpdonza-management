"""
Development settings
"""
DEBUG = True

ALLOWED_HOSTS = ["localhost"]

# --- Mail settings ---
SERVER_EMAIL = 'vanerum.tim@gmail.com'
NOREPLY = 'vanerum.tim@gmail.com'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'vanerum.tim@gmail.com'
EMAIL_HOST_PASSWORD = 'AA135Tim'

SITE_ID = 1

# --- Static and Media roots ---
STATIC_ROOT = '/Users/timvanerum/projects/ldpdonza-management/management/static'
MEDIA_ROOT = '/Users/timvanerum/projects/ldpdonza-management/management/media'
