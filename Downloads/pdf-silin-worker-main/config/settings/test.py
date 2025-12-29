"""Testing settings.
With these settings, tests run faster.
"""

from .base import *  # noqa: F403
from .base import env

# Base
DEBUG = False
SECRET_KEY = env("DJANGO_SECRET_KEY", default="7lEaACt4wsCLf4BmdG5QbuHTMYUGir2Gc1v8w9iXwwlIviI2")
TEST_RUNNER = "django.test.runner.DiscoverRunner"


# Cache
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": ""
    }
}

# Passwords
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# Templates
TEMPLATES[0]["OPTIONS"]["debug"] = DEBUG  # NOQA
TEMPLATES[0]["OPTIONS"]["loaders"] = [  # NOQA
    (
        "django.template.loaders.cached.Loader",
        [
            "django.template.loaders.filesystem.Loader",
            "django.template.loaders.app_directories.Loader",
        ],
    )
]
