# atenda_chat/asgi.py

import os

import django
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from dotenv import load_dotenv

from chamados.routing import \
    websocket_urlpatterns  # importa suas rotas websocket

load_dotenv()
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.settings")
django.setup()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
