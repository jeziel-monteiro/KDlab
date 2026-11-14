"""Gera configuração de desenvolvimento sem sobrescrever arquivos existentes."""

import os
from pathlib import Path
import secrets


def main():
    destino = Path(__file__).resolve().parent.parent / ".env"
    conteudo = (
        "# Configuração local de desenvolvimento. Não versionar.\n"
        f"DJANGO_SECRET_KEY={secrets.token_urlsafe(64)}\n"
        "DJANGO_DEBUG=1\n"
        "DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1\n"
        "POSTGRES_DB=kdlab\n"
        "POSTGRES_USER=kdlab\n"
        f"POSTGRES_PASSWORD={secrets.token_urlsafe(32)}\n"
        "POSTGRES_HOST=127.0.0.1\n"
        "POSTGRES_PORT=5432\n"
    )
    try:
        descritor = os.open(destino, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        print("O .env já existe e foi preservado.")
        return
    with os.fdopen(descritor, "w") as arquivo:
        arquivo.write(conteudo)
    print(".env de desenvolvimento criado com permissão 0600. Nenhum segredo foi exibido.")


if __name__ == "__main__":
    main()
