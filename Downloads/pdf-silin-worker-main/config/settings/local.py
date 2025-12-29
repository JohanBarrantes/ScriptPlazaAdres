"""Development settings."""

from .base import *  # noqa: F403
from .base import env
from constants import EmptyStringDiff

# Base
DEBUG = True

# Security
SECRET_KEY = env('DJANGO_SECRET_KEY', default='SGGc#4bjwisketyx3ha4ezv%y=yp1yolb7g7$1z_q!*p9')
ALLOWED_HOSTS = [
    'localhost',
    '0.0.0.0',
    '127.0.0.1',
    "template-converter",
    "template-generator",
    "10.7.7.25",
    "10.7.7.22",
    "10.7.7.15",
    "template-develop.jikkosoft.dev",
    "template-develop.jikkosoft.local",
    "template-develop.jikkosoft.com",
    "pdf-develop.jikkosoft.dev",
    "pdf-develop.jikkosoft.local",
    "pdf-develop.jikkosoft.com"
]

# Cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': EmptyStringDiff
    }
}

# Templates
TEMPLATES[0]['OPTIONS']['debug'] = DEBUG  # noqa: F405

# django-extensions
INSTALLED_APPS += ['django_extensions']  # noqa: F405
