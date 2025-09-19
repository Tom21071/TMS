from unittest.mock import MagicMock

import celery.app.task
from celery import current_app

from . import settings as base_settings

# Все таски выполняются синхронно и не требуют брокера
current_app.conf.task_always_eager = True
current_app.conf.task_eager_propagates = True

# Либо глобальный мок, если нужно отключить совсем:

celery.app.task.Task.apply_async = MagicMock(return_value=None)

# 🚀 Наследуем боевые настройки
SECRET_KEY = base_settings.SECRET_KEY
INSTALLED_APPS = base_settings.INSTALLED_APPS
MIDDLEWARE = base_settings.MIDDLEWARE
TEMPLATES = base_settings.TEMPLATES

# 🚀 SQLite in-memory вместо Postgres
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# 🔇 Отключаем Elasticsearch
ELASTICSEARCH_DSL = {}

try:
    from unittest.mock import MagicMock

    import elasticsearch

    elasticsearch.Elasticsearch = MagicMock()
except ImportError:
    pass

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]


class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None


MIGRATION_MODULES = DisableMigrations()

# Минимальные настройки для django-minio-backend
MINIO_ENDPOINT = "localhost:9000"
MINIO_ACCESS_KEY = "dummy"
MINIO_SECRET_KEY = "dummy"
MINIO_USE_HTTPS = False

# ✅ Фейковые бакеты для тестов
MINIO_PRIVATE_BUCKETS = ["test-private"]
MINIO_PUBLIC_BUCKETS = ["test-public"]

# 🔑 Наследуем важные настройки
SECRET_KEY = base_settings.SECRET_KEY
INSTALLED_APPS = base_settings.INSTALLED_APPS
MIDDLEWARE = base_settings.MIDDLEWARE
TEMPLATES = base_settings.TEMPLATES
ROOT_URLCONF = base_settings.ROOT_URLCONF  # 👈 ОБЯЗАТЕЛЬНО!
REST_FRAMEWORK = base_settings.REST_FRAMEWORK  # 👈 если у тебя DRF
