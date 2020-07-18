"""
ASGI config for donza project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/asgi/
"""

import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'donza.settings')

import django
django.setup()

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

# importeer de websocket urls die gebruikt worden door reactor
from reactor.urls import websocket_urlpatterns

import django.urls

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(URLRouter(
        # declare de websocket url patterns gebruikt door Django Reactor
        websocket_urlpatterns,
    ))
})
