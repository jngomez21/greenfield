import uuid
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, text

from tests.conftest import AuthHeaders, InsertTask


def _delete(client: TestClient, auth: AuthHeaders, tid: Any, sub: str = "user-a") -> Any:
    return client.delete(f"/v1/tasks/{tid}", headers=auth(sub))


def _rows(db: Engine, tid: uuid.UUID) -> int:
    with db.connect() as conn:
        return conn.execute(
            text("SELECT count(*) FROM tasks WHERE id = :id"), {"id": tid}
        ).scalar_one()


# Derived from R5.1
def test_eliminar_borra_la_tarea_de_forma_permanente(
    client: TestClient, auth: AuthHeaders, insert_task: InsertTask, db: Engine
) -> None:
    tid = insert_task()
    response = _delete(client, auth, tid)
    assert response.status_code == 204
    assert response.content == b""
    assert _rows(db, tid) == 0  # borrado físico, sin borrado lógico


# Derived from R5.2
def test_tarea_eliminada_ya_no_existe_para_ninguna_operacion(
    client: TestClient, auth: AuthHeaders, insert_task: InsertTask
) -> None:
    tid = insert_task()
    _delete(client, auth, tid)
    assert client.get(f"/v1/tasks/{tid}", headers=auth()).status_code == 404
    assert client.patch(f"/v1/tasks/{tid}", json={"title": "x"}, headers=auth()).status_code == 404
    assert _delete(client, auth, tid).status_code == 404


# Derived from R5.2
@pytest.mark.parametrize("tid", [uuid.uuid4(), "abc"])
def test_eliminar_inexistente_o_id_invalido_es_404(
    client: TestClient, auth: AuthHeaders, tid: Any
) -> None:
    response = _delete(client, auth, tid)
    assert response.status_code == 404
    assert response.json()["detail"] == "La tarea no existe."


# Derived from R1.3
def test_no_se_puede_eliminar_una_tarea_ajena(
    client: TestClient, auth: AuthHeaders, insert_task: InsertTask, db: Engine
) -> None:
    tid = insert_task(owner="user-a")
    response = _delete(client, auth, tid, sub="user-b")
    assert response.status_code == 404
    assert response.json() == _delete(client, auth, uuid.uuid4(), sub="user-b").json()
    assert _rows(db, tid) == 1
