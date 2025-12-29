"""Base settings to build other settings files upon."""

import environ
from constants import EmptyString, EmptyStringDiff

ROOT_DIR = environ.Path(__file__) - 3
APPS_DIR = ROOT_DIR.path('converter')

env = environ.Env()

# Base
DEBUG = env.bool('DJANGO_DEBUG', False)

# Language and timezone
TIME_ZONE = 'America/Bogota'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
USE_I18N = True
USE_I10N = True
USE_TZ = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'sqlite.db',
    }
}
# URLs
ROOT_URLCONF = 'config.urls'

# WSGI
WSGI_APPLICATION = 'config.wsgi.application'

# Apps
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'django_filters',
    'corsheaders'
]

LOCAL_APPS = [
    'converter.apps.ConverterAppConfig'
]
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# Passwords
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
]

AUTH_PASSWORD_VALIDATORS = []

# Middlewares
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]

# Static files
STATIC_ROOT = str(ROOT_DIR('staticfiles'))
STATIC_URL = '/static/'
STATIC_DIRS = [
    str(APPS_DIR.path('static'))
]
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# Media
MEDIA_ROOT = str(APPS_DIR('media'))
MEDIA_URL = '/media/'

# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            str(APPS_DIR.path('templates')),
        ],
        'OPTIONS': {
            'debug': DEBUG,
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Security
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# Admin
ADMIN_URL = 'admin/'
ADMINS = [
    ("""Sebastian Granda Gallego""", 'sebastian.granda@jikkosoft.com')
]
MANAGERS = ADMINS


# Django REST Framework
REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'converter.exceptions.exception_handler.drf_default_with_modifications_exception_handler',
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_PAGINATION_CLASS':
        'rest_framework.pagination.LimitOffsetPagination',
        'PAGE_SIZE': 20
}

# CORS
CORS_ORIGIN_ALLOW_ALL = True

ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default=['localhost', '0.0.0.0', '127.0.0.1'])

# 64 MB maximum request size
DATA_UPLOAD_MAX_MEMORY_SIZE = 67108864

# AWS
AWS_ACCESS_KEY = env('AWS_ACCESS_KEY', default=EmptyStringDiff)
AWS_SECRET_ACCESS = env('AWS_SECRET_ACCESS', default=EmptyStringDiff)
AWS_REGION = env('AWS_REGION', default=EmptyStringDiff)
S3_BUCKET = env('S3_BUCKET', default=EmptyStringDiff).split('/')[0]
S3_SUBFOLDER = "pdf/"
AWS_GENERATOR_QUEUE = env('AWS_GENERATOR_QUEUE', default=EmptyStringDiff)
TIME_POLLING = env('TIME_POLLING', default=20)
DOWNLOAD_FOLDER = env('DOWNLOAD_FOLDER', default='/app/converter/templates/download_files/')
CONVERTED_FOLDER = env('CONVERTED_FOLDER', default='/app/converter/templates/converted_files/')
BARCODES_FOLDER = env('BARCODES_FOLDER', default='/app/converter/templates/barcodes/')
MAX_NUMBER_OF_MESSAGES = env('MAX_NUMBER_OF_MESSAGES', default=10)
REDIS_HOST = env('REDIS_HOST', default=EmptyStringDiff)
REDIS_PORT = int(env('REDIS_PORT', default=0))

# Process
NUMBER_OF_PROCESSES = int(env('NUMBER_OF_PROCESSES', default=1))

# Document Management Api
DOCUMENT_MANAGEMENT_URL = env('DOCUMENT_MANAGEMENT_URL', default=EmptyString)

# Auth2 silin api
AUTH2_URL = env('AUTH2_URL', default=EmptyString)

# Timeouts
VISIBILITY_TIMEOUT = int(env('VISIBILITY_TIMEOUT', default=30))
CACHE_TIMEOUT = int(env('CACHE_TIMEOUT', default=60))

# Signature keys jwt
ACCESS_SECRET = env('ACCESS_SECRET', default=EmptyStringDiff)
PUBLIC_RSA = env('PUBLIC_RSA', default=EmptyStringDiff)

# Application client credentials flow
APPLICATION_ID = env('PDF_WORKER_ID', default=EmptyStringDiff)
APPLICATION_SECRET = env('PDF_WORKER_SECRET', default=EmptyStringDiff)
