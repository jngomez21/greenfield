import os
import time
import uuid
from collections.abc import Callable, Iterator
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import jwt
import pytest
from alembic import command
from alembic.config import Config
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient
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
    # Asignación incondicional: los tokens de prueba se firman con estos iss/aud.
    os.environ.update(TEST_AUTH_ENV)
    return url


@pytest.fixture(scope="session")
def engine(test_database_url: str) -> Iterator[Engine]:
    command.upgrade(alembic_config(test_database_url), "head")
    eng = create_engine(test_database_url)
    yield eng
    eng.dispose()


MakeToken = Callable[..., str]


@pytest.fixture(scope="session")
def signing_key() -> rsa.RSAPrivateKey:
    """Llave del IdP de prueba (D1 en MOCK): se genera en cada corrida, nunca se guarda."""
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


@pytest.fixture(scope="session")
def make_token(signing_key: rsa.RSAPrivateKey) -> MakeToken:
    """Emite un JWT válido para `sub`; cada claim se puede sobrescribir o quitar (valor None)."""

    def _make(
        sub: str | None = "user-a", *, key: Any = None, algorithm: str = "RS256", **claims: Any
    ) -> str:
        now = int(time.time())
        payload: dict[str, Any] = {
            "sub": sub,
            "iss": TEST_AUTH_ENV["AUTH_ISSUER"],
            "aud": TEST_AUTH_ENV["AUTH_AUDIENCE"],
            "iat": now,
            "exp": now + 300,
        }
        payload.update(claims)
        payload = {k: v for k, v in payload.items() if v is not None}
        return jwt.encode(payload, signing_key if key is None else key, algorithm=algorithm)

    return _make


@pytest.fixture
def db(engine: Engine) -> Engine:
    """Base limpia para cada test que la use."""
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE tasks"))
    return engine


@pytest.fixture
def client(db: Engine, signing_key: rsa.RSAPrivateKey) -> Iterator[TestClient]:
    """La app real sobre la base *_test, con el IdP sustituido por la llave de prueba."""
    from greenfield.auth import get_key_resolver
    from greenfield.main import create_app

    app = create_app()
    public_key = signing_key.public_key()
    app.dependency_overrides[get_key_resolver] = lambda: lambda token: public_key
    with TestClient(app) as c:
        yield c


InsertTask = Callable[..., uuid.UUID]


@pytest.fixture
def insert_task(db: Engine) -> InsertTask:
    """Inserta una tarea directo en BD, con `created_at` controlable (orden y empates)."""

    def _insert(
        owner: str = "user-a",
        title: str = "x",
        status: str = "pending",
        due_date: date | None = None,
        created_at: datetime | None = None,
        task_id: uuid.UUID | None = None,
    ) -> uuid.UUID:
        task_id = task_id or uuid.uuid4()
        ts = created_at or datetime.now(UTC)
        with db.begin() as conn:
            conn.execute(
                text(
                    "INSERT INTO tasks (id, owner_sub, title, status, due_date, created_at, "
                    "updated_at) VALUES (:id, :owner, :title, :status, :due_date, :ts, :ts)"
                ),
                {
                    "id": task_id,
                    "owner": owner,
                    "title": title,
                    "status": status,
                    "due_date": due_date,
                    "ts": ts,
                },
            )
        return task_id

    return _insert


AuthHeaders = Callable[..., dict[str, str]]


@pytest.fixture
def auth(make_token: MakeToken) -> AuthHeaders:
    """`auth("user-b")` → headers con un Bearer válido para ese usuario."""
    return lambda sub="user-a": {"Authorization": f"Bearer {make_token(sub)}"}
