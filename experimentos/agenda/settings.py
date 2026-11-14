"""Configuração exclusiva da prova; banco e socket fornecidos pelo executor."""

import os

SECRET_KEY = "somente-experimento-local-sem-sessoes-ou-http"
INSTALLED_APPS = ["django.contrib.postgres", "agenda_prova"]
USE_TZ = True
TIME_ZONE = "America/Manaus"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "postgres",
        "USER": "kdlab_prova",
        "HOST": os.environ["KDLAB_PROVA_SOCKET"],
        "PORT": "5432",
        "CONN_MAX_AGE": 0,
        "TEST": {"NAME": "kdlab_bl01_test"},
        "OPTIONS": {
            "connect_timeout": 5,
            "options": "-c statement_timeout=15000 -c lock_timeout=10000",
        },
    }
}
