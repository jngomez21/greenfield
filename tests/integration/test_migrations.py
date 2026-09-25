import uuid
from contextlib import contextmanager
from datetime import UTC, datetime

import pytest
from alembic import command
from sqlalchemy import Engine, inspect, text
from sqlalchemy.exc import DataError, IntegrityError

from greenfield.db import get_session
from greenfield.tasks.models import Task
from tests.conftest import alembic_config

INSERT = text(
    "INSERT INTO tasks (id, owner_sub, title, description, status, created_at, updated_at) "
    "VALUES (:id, :owner, :title, :description, :status, now(), now())"
)


def _row(**overrides: object) -> dict[str, object]:
    row: dict[str, object] = {
        "id": uuid.uuid4(),
        "owner": "user-a",
        "title": "Pagar arriendo",
        "description": None,
        "status": "pending",
    }
    row.update(overrides)
    return row


def test_migracion_baja_y_sube_de_nuevo(engine: Engine, test_database_url: str) -> None:
    cfg = alembic_config(test_database_url)
    command.downgrade(cfg, "base")
    assert "tasks" not in inspect(engine).get_table_names()
    command.upgrade(cfg, "head")
    indexes = {ix["name"] for ix in inspect(engine).get_indexes("tasks")}
    assert {"ix_tasks_owner_created", "ix_tasks_owner_pending"} <= indexes


# Derived from R2.2
def test_bd_asigna_pending_si_no_se_indica_estado(db: Engine) -> None:
    with db.begin() as conn:
        conn.execute(
            text(
                "INSERT INTO tasks (id, owner_sub, title, created_at, updated_at) "
                "VALUES (:id, 'user-a', 'x', now(), now())"
            ),
            {"id": uuid.uuid4()},
        )
        assert conn.execute(text("SELECT status FROM tasks")).scalar_one() == "pending"


# Derived from R1.2
def test_bd_exige_dueno(db: Engine) -> None:
    with pytest.raises(IntegrityError), db.begin() as conn:
        conn.execute(INSERT, _row(owner=None))


# Derived from R2.4
@pytest.mark.parametrize(
    ("title", "error"), [("   ", IntegrityError), ("x" * 201, DataError), (None, IntegrityError)]
)
def test_bd_rechaza_titulo_vacio_o_largo(db: Engine, title: str | None, error: type) -> None:
    with pytest.raises(error), db.begin() as conn:
        conn.execute(INSERT, _row(title=title))


# Derived from R2.4
def test_bd_acepta_titulo_de_200_caracteres_multibyte(db: Engine) -> None:
    with db.begin() as conn:
        conn.execute(INSERT, _row(title="ñ" * 200))


# Derived from R2.5
def test_bd_rechaza_descripcion_de_mas_de_2000_caracteres(db: Engine) -> None:
    with pytest.raises(DataError), db.begin() as conn:
        conn.execute(INSERT, _row(description="x" * 2001))


# Derived from R2.6
def test_bd_rechaza_estado_desconocido(db: Engine) -> None:
    with pytest.raises(IntegrityError), db.begin() as conn:
        conn.execute(INSERT, _row(status="done"))


def _task() -> Task:
    now = datetime.now(UTC)
    return Task(
        id=uuid.uuid4(),
        owner_sub="user-a",
        title="x",
        status="pending",
        created_at=now,
        updated_at=now,
    )


def _count(engine: Engine) -> int:
    with engine.connect() as conn:
        return conn.execute(text("SELECT count(*) FROM tasks")).scalar_one()


def test_get_session_confirma_si_no_hay_error(db: Engine) -> None:
    with contextmanager(get_session)() as session:
        session.add(_task())
    assert _count(db) == 1


def test_get_session_revierte_si_hay_error(db: Engine) -> None:
    with pytest.raises(RuntimeError), contextmanager(get_session)() as session:
        session.add(_task())
        session.flush()
        raise RuntimeError("falla a mitad de la transacción")
    assert _count(db) == 0
