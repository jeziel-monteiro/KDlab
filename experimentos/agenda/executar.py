"""Cria seu próprio PostgreSQL efêmero, executa a prova e remove o container."""

import argparse
import os
from pathlib import Path
import secrets
import subprocess
import sys
import tempfile
import time


IMAGEM_PADRAO = "postgres:17"


def docker(*args, endpoint=None, **kwargs):
    comando = ["docker"]
    ambiente = os.environ.copy()
    if endpoint:
        # Fixar o daemon já verificado, inclusive se o contexto mudar no meio.
        comando.extend(["--host", endpoint])
        ambiente.pop("DOCKER_HOST", None)
        ambiente.pop("DOCKER_CONTEXT", None)
    return subprocess.run([*comando, *args], check=True, env=ambiente, **kwargs)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--imagem", default=IMAGEM_PADRAO)
    parser.add_argument("--rodadas", type=int, default=100)
    parser.add_argument("--concorrentes", type=int, default=20)
    args = parser.parse_args()
    if args.rodadas < 1 or args.concorrentes < 2:
        parser.error("Use ao menos uma rodada e dois concorrentes.")
    import django
    import psycopg

    contexto = os.environ.get("DOCKER_CONTEXT")
    endpoint = None if contexto else os.environ.get("DOCKER_HOST")
    if not endpoint:
        endpoint = docker(
            "context", "inspect", "--format", "{{.Endpoints.docker.Host}}",
            capture_output=True, text=True,
        ).stdout.strip()
    if not endpoint.startswith("unix://"):
        parser.error("A prova exige Docker local por socket Unix; não usa hosts remotos.")

    nome = "kdlab-bl01-" + secrets.token_hex(6)
    with tempfile.TemporaryDirectory(prefix="kdlab-bl01-") as diretorio:
        socket = Path(diretorio) / "socket"
        socket.mkdir()
        # O diretório pai permanece 0700; só a subpasta montada é compartilhada.
        socket.chmod(0o1777)
        criado = False
        try:
            docker(
                "run", "--detach", "--rm", "--pull=never", "--name", nome,
                "--label", "io.kdlab.experimento=bl01", "--network", "none",
                "--user", "postgres", "--memory", "512m", "--cpus", "1",
                "--mount", f"type=bind,source={socket},target=/run/kdlab-socket",
                "--entrypoint", "/bin/sh", args.imagem, "-ec",
                "initdb -D /tmp/kdlab-pgdata --auth=trust --username=kdlab_prova "
                ">/tmp/kdlab-init.log; "
                "exec postgres -D /tmp/kdlab-pgdata "
                "-c listen_addresses='' -c unix_socket_directories=/run/kdlab-socket "
                "-c shared_buffers=32MB -c max_connections=40",
                endpoint=endpoint,
                stdout=subprocess.DEVNULL,
            )
            criado = True
            limite = time.monotonic() + 30
            while True:
                try:
                    with psycopg.connect(host=str(socket), dbname="postgres", user="kdlab_prova") as conn:
                        versao = conn.execute("SELECT version()").fetchone()[0]
                    break
                except psycopg.OperationalError:
                    if time.monotonic() >= limite:
                        docker("logs", "--tail", "30", nome, endpoint=endpoint)
                        raise RuntimeError("O PostgreSQL temporário não ficou pronto.")
                    time.sleep(0.2)
            print(f"Python: {sys.version.split()[0]}; Django: {django.get_version()}; psycopg: {psycopg.__version__}", flush=True)
            print(f"Banco: {versao}", flush=True)
            print(f"Imagem: {args.imagem}; rede: nenhuma; limite: 1 CPU / 512 MiB", flush=True)
            print(f"Rodadas: {args.rodadas}; concorrentes na aprovação: {args.concorrentes}", flush=True)
            ambiente = os.environ.copy()
            ambiente.update({
                "KDLAB_PROVA_SOCKET": str(socket),
                "KDLAB_PROVA_RODADAS": str(args.rodadas),
                "KDLAB_PROVA_CONCORRENTES": str(args.concorrentes),
                "PYTHONDONTWRITEBYTECODE": "1",
            })
            resultado = subprocess.run(
                [sys.executable, "manage.py", "test", "agenda_prova", "--verbosity", "2", "--noinput"],
                cwd=Path(__file__).resolve().parent,
                env=ambiente,
            )
            return resultado.returncode
        finally:
            if criado:
                docker("rm", "--force", nome, endpoint=endpoint, stdout=subprocess.DEVNULL)
                print("PostgreSQL temporário removido.", flush=True)


if __name__ == "__main__":
    sys.exit(main())
