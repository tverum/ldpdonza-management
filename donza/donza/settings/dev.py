from donza.settings.base import *

DEBUG = True

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'vanerum.tim@gmail.com'
EMAIL_HOST_PASSWORD = 'AA135Tim'

# only for development purposes
# CHANNEL_LAYERS = {
#     "default": {
#        "BACKEND": "channels.layers.InMemoryChannelLayer"
#    }
#}

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}
