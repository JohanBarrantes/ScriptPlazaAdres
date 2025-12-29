"""
ASGI config for converter project.
It exposes the ASGI callable as a module-level variable named ``application``.
For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""

import os
import sys

from django.core.asgi import get_asgi_application

# This allows easy placement of apps within the interior
# converter directory.
app_path = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), os.pardir))
sys.path.append(os.path.join(app_path, 'converter'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

application = get_asgi_application()
