import os
from collections.abc import Iterator
from pathlib import Path
from urllib.parse import urlsplit

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import Engine, create_engine, text

ROOT = Path(__file__).resolve().parents[1]

TEST_AUTH_ENV = {
    "AUTH_ISSUER": "https://idp.test/",
    "AUTH_AUDIENCE": "greenfield-api",
    "AUTH_JWKS_URL": "https://idp.test/.well-known/jwks.json",
}


def ensure_test_database(url: str | None) -> str:
    """Devuelve la URL sólo si apunta a una base `*_test`; las pruebas la vacían."""
    if not url:
        raise ValueError("Falta TEST_DATABASE_URL (ver README.md § Configuración).")
    database = urlsplit(url).path.lstrip("/")
    if not database.endswith("_test"):
        # No se muestra la URL completa: lleva la clave.
        raise ValueError(
            f"TEST_DATABASE_URL apunta a la base '{database}', que no termina en '_test'. "
            "Las pruebas vacían las tablas: se aborta para no borrar datos reales."
        )
    return url


def _read_dotenv(name: str) -> str | None:
    env_file = ROOT / ".env"
    if not env_file.exists():
        return None
    for line in env_file.read_text(encoding="utf-8").splitlines():
        key, sep, value = line.partition("=")
        if sep and key.strip() == name:
            return value.strip()
    return None


def alembic_config(url: str) -> Config:
    cfg = Config(str(ROOT / "alembic.ini"))
    cfg.set_main_option("sqlalchemy.url", url.replace("%", "%%"))
    return cfg


@pytest.fixture(scope="session")
def test_database_url() -> str:
    try:
        url = ensure_test_database(
            os.environ.get("TEST_DATABASE_URL") or _read_dotenv("TEST_DATABASE_URL")
        )
    except ValueError as exc:
        pytest.exit(str(exc), returncode=2)
    # La app lee su configuración del entorno: en pruebas apunta a la base *_test.
    os.environ["DATABASE_URL"] = url
    for key, value in TEST_AUTH_ENV.items():
        os.environ.setdefault(key, value)
    return url


@pytest.fixture(scope="session")
def engine(test_database_url: str) -> Iterator[Engine]:
    command.upgrade(alembic_config(test_database_url), "head")
    eng = create_engine(test_database_url)
    yield eng
    eng.dispose()


@pytest.fixture
def db(engine: Engine) -> Engine:
    """Base limpia para cada test que la use."""
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE tasks"))
    return engine
