import environ

from django.core.asgi import get_asgi_application

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

from apps.chat import routing as chat_routing

env = environ.Env()
environ.Env.read_env(".env")

# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()


application = ProtocolTypeRouter({
    "http": django_asgi_app,
    # Just HTTP for now. (We can add other protocols later.)

    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(URLRouter(chat_routing.websocket_urlpatterns))
    )
})
