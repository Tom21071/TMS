from . import settings as base_settings

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
