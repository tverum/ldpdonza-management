"""
ASGI config for donza project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/asgi/
"""

import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'donza.settings.dev')

import django
django.setup()

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from reactor.urls import websocket_urlpatterns  # <- for Django Reactor

import django.urls

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(URLRouter(
        websocket_urlpatterns, # <- For Django Reactor
    ))
})
