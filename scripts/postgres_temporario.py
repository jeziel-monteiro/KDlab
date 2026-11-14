"""PostgreSQL privado para validação local, sem usar o banco configurado do usuário."""

from contextlib import contextmanager
import os
from pathlib import Path
import secrets
import subprocess
import tempfile
import time

import psycopg


def _docker(*argumentos, endpoint=None, **kwargs):
    ambiente = os.environ.copy()
    comando = ["docker"]
    if endpoint:
        comando.extend(["--host", endpoint])
        ambiente.pop("DOCKER_HOST", None)
        ambiente.pop("DOCKER_CONTEXT", None)
    return subprocess.run([*comando, *argumentos], env=ambiente, check=True, **kwargs)


@contextmanager
def postgres_temporario(imagem="postgres:17"):
    contexto = os.environ.get("DOCKER_CONTEXT")
    endpoint = None if contexto else os.environ.get("DOCKER_HOST")
    if not endpoint:
        endpoint = _docker(
            "context", "inspect", "--format", "{{.Endpoints.docker.Host}}",
            capture_output=True, text=True,
        ).stdout.strip()
    if not endpoint.startswith("unix://"):
        raise RuntimeError("A validação exige Docker local por socket Unix.")

    nome = "kdlab-bl02-" + secrets.token_hex(6)
    with tempfile.TemporaryDirectory(prefix="kdlab-bl02-") as diretorio:
        socket = Path(diretorio) / "socket"
        socket.mkdir()
        socket.chmod(0o1777)
        criado = False
        try:
            _docker(
                "run", "--detach", "--rm", "--pull=never", "--name", nome,
                "--label", "io.kdlab.validacao=bl02", "--network", "none",
                "--user", "postgres", "--memory", "512m", "--cpus", "1",
                "--mount", f"type=bind,source={socket},target=/run/kdlab-socket",
                "--entrypoint", "/bin/sh", imagem, "-ec",
                "initdb -D /tmp/kdlab-pgdata --auth=trust --username=kdlab "
                ">/tmp/kdlab-init.log; "
                "exec postgres -D /tmp/kdlab-pgdata "
                "-c listen_addresses='' -c unix_socket_directories=/run/kdlab-socket "
                "-c shared_buffers=32MB -c max_connections=40",
                endpoint=endpoint, stdout=subprocess.DEVNULL,
            )
            criado = True
            limite = time.monotonic() + 30
            while True:
                try:
                    with psycopg.connect(
                        host=str(socket), dbname="postgres", user="kdlab", autocommit=True,
                    ) as conexao:
                        versao = conexao.execute("SELECT version()").fetchone()[0]
                        conexao.execute("CREATE DATABASE kdlab")
                    break
                except psycopg.OperationalError:
                    if time.monotonic() >= limite:
                        _docker("logs", "--tail", "30", nome, endpoint=endpoint)
                        raise RuntimeError("O PostgreSQL temporário não ficou pronto.")
                    time.sleep(0.2)
            print(f"Banco temporário: {versao}", flush=True)
            print(f"Imagem: {imagem}; sem rede; 1 CPU / 512 MiB", flush=True)
            ambiente = os.environ.copy()
            ambiente.update({
                "DJANGO_SETTINGS_MODULE": "kdlab.settings",
                "DJANGO_SECRET_KEY": secrets.token_urlsafe(64),
                "DJANGO_DEBUG": "1",
                "DJANGO_ALLOWED_HOSTS": "localhost,127.0.0.1,testserver",
                "DJANGO_STATIC_ROOT": str(Path(diretorio) / "static"),
                "POSTGRES_DB": "kdlab", "POSTGRES_USER": "kdlab",
                "POSTGRES_PASSWORD": "", "POSTGRES_HOST": str(socket), "POSTGRES_PORT": "5432",
                "PYTHONDONTWRITEBYTECODE": "1",
            })
            yield ambiente
        finally:
            if criado:
                _docker("rm", "--force", nome, endpoint=endpoint, stdout=subprocess.DEVNULL)
                print("PostgreSQL da validação removido.", flush=True)
