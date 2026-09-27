"""Fixtures dos testes E2E: sobe o servidor uvicorn com banco isolado."""
import os
import socket
import subprocess
import sys
import time

import httpx
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _porta_livre() -> int:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    porta = s.getsockname()[1]
    s.close()
    return porta


@pytest.fixture(scope="session")
def base_url(tmp_path_factory):
    porta = _porta_livre()
    db_path = tmp_path_factory.mktemp("db") / "test.db"

    env = dict(os.environ)
    env["DATABASE_URL"] = f"sqlite:///{db_path}"

    # popula o banco de teste
    subprocess.run(
        [sys.executable, "seed.py", "--reset"],
        cwd=ROOT, env=env, check=True, capture_output=True,
    )

    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app",
         "--host", "127.0.0.1", "--port", str(porta)],
        cwd=ROOT, env=env,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )

    url = f"http://127.0.0.1:{porta}"
    # aguarda o servidor responder
    for _ in range(50):
        try:
            httpx.get(url, timeout=1)
            break
        except Exception:
            time.sleep(0.2)
    else:
        proc.terminate()
        raise RuntimeError("Servidor não subiu a tempo")

    yield url

    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
