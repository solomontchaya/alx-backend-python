os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'messaging_app.settings')
import os
from django.core.asgi import get_asgi_application

# Set the correct settings module for the Django-Middleware-0x03 project
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Django-Middleware-0x03.settings')

application = get_asgi_application()
