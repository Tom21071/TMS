import os
from datetime import timedelta
from pathlib import Path

import certifi
import urllib3
from celery.schedules import crontab

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "django-insecure-maqhf0s46-be2a754#_g46ubqj@t6e%p8e(pt_1i%j@pvh4(61"

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third party apps
    "rest_framework",
    "rest_framework.authtoken",
    "drf_spectacular",
    "django_minio_backend.apps.DjangoMinioBackendConfig",
    # Local apps
    "apps.users",
    "apps.task",
    "django_celery_results",
    "django.contrib.sites",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.github",
]

CELERY_BROKER_URL = os.getenv("REDIS_URL")
CELERY_RESULT_BACKEND = "django-db"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "UTC"
CELERY_BEAT_SCHEDULE = {
    "email-weekly-top20-report": {
        "task": "notifications.tasks.send_weekly_top20_reports",
        "schedule": crontab(minute="*"),
    }
}
MINIO_CONSISTENCY_CHECK_ON_START = True

STORAGES = {
    "default": {
        "BACKEND": "django_minio_backend.models.MinioBackend",
    },
    "staticfiles": {  # -- OPTIONAL
        "BACKEND": "django_minio_backend.models.MinioBackendStatic",
    },
}

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"
MINIO_USE_HTTPS = False
MINIO_USE_SSL = False
MINIO_URL_EXPIRY_HOURS = timedelta(days=1)  # Default is 7 days (longest) if not defined
MINIO_CONSISTENCY_CHECK_ON_START = True
MINIO_PRIVATE_BUCKETS = [
    "django-backend-dev-private",
]
MINIO_PUBLIC_BUCKETS = [
    "django-backend-dev-public",
]
MINIO_POLICY_HOOKS: list[tuple[str, dict]] = []
# MINIO_MEDIA_FILES_BUCKET = 'my-media-files-bucket'  # replacement for MEDIA_ROOT
# MINIO_STATIC_FILES_BUCKET = 'my-static-files-bucket'  # replacement for STATIC_ROOT
MINIO_BUCKET_CHECK_ON_SAVE = True  # Default: True // Creates bucket if missing, then save

MINIO_WEBHOOK_TOKEN = "Fs46gG"
ALLOWED_HOSTS = ["*"]
# Custom HTTP Client (OPTIONAL)

timeout = timedelta(minutes=5).seconds
ca_certs = os.environ.get("SSL_CERT_FILE") or certifi.where()
MINIO_HTTP_CLIENT: urllib3.poolmanager.PoolManager = urllib3.PoolManager(
    timeout=urllib3.util.Timeout(connect=timeout, read=timeout),
    maxsize=10,
    cert_reqs="CERT_REQUIRED",
    ca_certs=ca_certs,
    retries=urllib3.Retry(total=5, backoff_factor=0.2, status_forcelist=[500, 502, 503, 504]),
)
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
]

SITE_ID = 1
LOGIN_REDIRECT_URL = "/api/auth/github/callback"

SOCIAL_AUTH_GITHUB_KEY = "Ov23lid6bSPW9eynAt8V"
SOCIAL_AUTH_GITHUB_SECRET = "2a2b337ddaaf7fc06d88ac920657ef786623363f"

SOCIALACCOUNT_PROVIDERS = {
    "github": {
        "APP": {
            "client_id": "Ov23lid6bSPW9eynAt8V",
            "secret": "2a2b337ddaaf7fc06d88ac920657ef786623363f",
            "key": "",
        }
    }
}

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "sqlite3": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    },
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "postgres",
        "USER": "postgres",
        "PASSWORD": "postgres",
        "HOST": os.getenv("POSTGRES_HOST"),
        "PORT": "5432",
    },
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
# EMAIL_HOST = "localhost"
# EMAIL_PORT = 1025
# EMAIL_USE_TLS = False
# EMAIL_HOST_USER = ""
# EMAIL_HOST_PASSWORD = ""

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "ttomson979@gmail.com"
EMAIL_HOST_PASSWORD = "jsfejipbuyyaipnx"

STATIC_URL = "static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

SPECTACULAR_SETTINGS = {
    "TITLE": "TMS",
    "DESCRIPTION": "Task Management System API",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": True,
}
ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.getenv("REDIS_URL"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

DJANGO_REDIS_IGNORE_EXCEPTIONS = False
CACHE_TTL = 60
