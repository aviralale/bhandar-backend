from pathlib import Path
import os
import environ
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()

environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

SECRET_KEY = env("SECRET_KEY")

DEBUG = env.bool("DEBUG", default=False)

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

INSTALLED_APPS += [
    'accounts',
    'rest_framework',
    'djoser',
]

# REST framework configuration
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
}

# * JWT SETTINGS
SIMPLE_JWT = {
    "AUTH_HEADER_TYPES": ("JWT",),
    "ACCESS_TOKEN_LIFETIME": timedelta(days=20),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": None,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
}

# Djoser configuration
DJOSER = {
    "LOGIN_FIELD": "username",
    "USER_CREATE_PASSWORD_RETYPE": True,
    "PASSWORD_RESET_CONFIRM_URL": "/password-reset/confirm/{uid}/{token}",
    "USERNAME_RESET_CONFIRM_URL": "/username-reset/confirm/{uid}/{token}",
    "ACTIVATION_URL": "/activate/{uid}/{token}",
    "SEND_ACTIVATION_EMAIL": True,
    "SEND_CONFIRMATION_EMAIL": True,
    "PASSWORD_CHANGED_EMAIL_CONFIRMATION": True,
    "SET_PASSWORD_RETYPE": True,
    "PASSWORD_RESET_SHOW_EMAIL_NOT_FOUND": True,
    "TOKEN_MODEL": None,  #!TO DELETE USER
    "SERIALIZERS": {
        "user_create": "accounts.serializers.UserCreateSerializer",
        "user": "accounts.serializers.UserSerializer",
        "user_delete": "djoser.serializers.UserDeleteSerializer",
        "current_user": "accounts.serializers.UserSerializer",
    },
    "EMAIL": {
        "activation": "accounts.email.ActivationEmail",
        "confirmation": "accounts.email.ConfirmationEmail",
        "password_reset": "accounts.email.PasswordResetEmail",
        "password_changed_confirmation": "accounts.email.PasswordChangedConfirmationEmail",
        "username_changed_confirmation": "accounts.email.UsernameChangedConfirmationEmail",
        "username_reset": "accounts.email.UsernameResetEmail",
    },
}

# CORS settings
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_HEADERS = env.list("CORS_ALLOW_HEADERS")

# *USER MODEL
AUTH_USER_MODEL = "accounts.User"

# EMAIL CONF
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_HOST_USER = env("EMAIL_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_PW")
EMAIL_USE_TLS = True

# ? NAMINGS
EMAIL_FRONTEND_SITE_NAME = "भण्डारण"
EMAIL_FRONTEND_DOMAIN = "localhost:3000"
EMAIL_FRONTEND_PROTOCOL = "http"


# * MEDIA
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
