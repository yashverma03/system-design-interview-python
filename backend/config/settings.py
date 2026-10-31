import os
from pathlib import Path

from dotenv import load_dotenv
from utils.env import get_env

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / '.env')

SECRET_KEY = get_env('DJANGO_SECRET_KEY')
DEBUG = os.getenv('DJANGO_DEBUG', '').lower() == 'true'
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# REST APIs don't use trailing slashes
APPEND_SLASH = False

INSTALLED_APPS = [
  'django.contrib.contenttypes',
  'django.contrib.auth',
  'corsheaders',
  'rest_framework',
  'user',
]

MIDDLEWARE = [
  'middlewares.request_logging.RequestLoggingMiddleware',
  'corsheaders.middleware.CorsMiddleware',
  'django.middleware.security.SecurityMiddleware',
  'django.middleware.common.CommonMiddleware',
  'middlewares.csrf_exempt.CsrfExemptMiddleware',
  'django.middleware.csrf.CsrfViewMiddleware',
  'middlewares.jwt_auth.JWTAuthMiddleware',
]

ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.postgresql',
    'NAME': get_env('DB_DATABASE'),
    'USER': get_env('DB_USERNAME'),
    'PASSWORD': get_env('DB_PASSWORD'),
    'HOST': get_env('DB_HOST'),
    'PORT': get_env('DB_PORT'),
  }
}

# Redis (used by utils/redis_client.py, not wired anywhere yet)
REDIS_HOST = get_env('REDIS_HOST')
REDIS_PORT = int(get_env('REDIS_PORT'))

CORS_ALLOWED_ORIGINS = [o for o in os.getenv('CORS_ALLOWED_ORIGINS', '').split(',') if o]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
  'EXCEPTION_HANDLER': 'utils.exception_handler.custom_exception_handler',
  'DEFAULT_AUTHENTICATION_CLASSES': [],
  'DEFAULT_PERMISSION_CLASSES': [],
  'DEFAULT_RENDERER_CLASSES': ['rest_framework.renderers.JSONRenderer'],
}

JWT_SECRET_KEY = get_env('JWT_SECRET_KEY')
JWT_EXPIRY_DAYS = int(get_env('JWT_EXPIRY_DAYS'))

LOGGING = {
  'version': 1,
  'disable_existing_loggers': False,
  'formatters': {
    'verbose': {'format': '{levelname} {asctime} {module} {message}', 'style': '{'},
  },
  'handlers': {
    'console': {'class': 'logging.StreamHandler', 'formatter': 'verbose'},
  },
  'root': {'handlers': ['console'], 'level': 'INFO'},
}
