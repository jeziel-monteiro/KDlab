"""Verifica migrações, configuração, estáticos e testes em PostgreSQL efêmero."""

import argparse
from pathlib import Path
import subprocess
import sys

import django
import psycopg

from postgres_temporario import postgres_temporario


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--imagem", default="postgres:17")
    args = parser.parse_args()
    raiz = Path(__file__).resolve().parent.parent
    print(f"Python {sys.version.split()[0]}; Django {django.get_version()}; psycopg {psycopg.__version__}", flush=True)
    with postgres_temporario(args.imagem) as ambiente:
        comandos = [
            ["makemigrations", "--check", "--dry-run"],
            ["check"],
            ["collectstatic", "--noinput", "--verbosity", "0"],
            ["test", "apps", "--settings", "kdlab.settings_test", "--verbosity", "2", "--noinput"],
        ]
        for argumentos in comandos:
            print("\nExecutando: manage.py " + " ".join(argumentos), flush=True)
            resultado = subprocess.run(
                [sys.executable, "manage.py", *argumentos], cwd=raiz, env=ambiente,
            )
            if resultado.returncode:
                return resultado.returncode
    return 0


if __name__ == "__main__":
    sys.exit(main())
