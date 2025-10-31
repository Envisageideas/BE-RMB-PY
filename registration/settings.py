import os
from pathlib import Path

# ----------------------------------------
# Base configuration
# ----------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-secret-key")
DEBUG = True
ALLOWED_HOSTS = ["*"]

# ----------------------------------------
# Installed apps
# ----------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
    
    # Local apps
    'users.apps.UsersConfig',
]


# ----------------------------------------
# Middleware
# ----------------------------------------
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # Must be before CommonMiddleware
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ----------------------------------------
# URLs and templates
# ----------------------------------------
ROOT_URLCONF = "registration.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# ----------------------------------------
# Database
# ----------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# ----------------------------------------
# Authentication and passwords
# ----------------------------------------
AUTH_PASSWORD_VALIDATORS = []

# ----------------------------------------
# Localization
# ----------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ----------------------------------------
# Static and media files
# ----------------------------------------
STATIC_URL = "static/"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ----------------------------------------
# Django REST Framework
# ----------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
}

# ----------------------------------------
# CORS (Frontend access)
# ----------------------------------------
CORS_ALLOW_ALL_ORIGINS = True  # For local dev only
CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = [
     "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# ----------------------------------------
# Security for iframe and embedding
# ----------------------------------------
# Allow embedding Django pages/files in iframe

X_FRAME_OPTIONS = "ALLOWALL"
SECURE_CROSS_ORIGIN_OPENER_POLICY = None
# ----------------------------------------
# Debug info
# ----------------------------------------
print(f"📁 MEDIA_ROOT: {MEDIA_ROOT}")
print(f"🌐 MEDIA_URL: {MEDIA_URL}")
