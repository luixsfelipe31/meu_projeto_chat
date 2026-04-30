"""
ASGI config for projeto project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""
import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack # Use AuthMiddlewareStack para garantir
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projeto.settings')
django.setup()

import usuarios.routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack( # Mudamos para Auth para ser mais robusto
        URLRouter(
            usuarios.routing.websocket_urlpatterns
        )
    ),
})