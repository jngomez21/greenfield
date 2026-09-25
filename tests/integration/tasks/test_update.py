import uuid
from datetime import UTC, date, datetime
from itertools import permutations
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine
from sqlalchemy.orm import Session

from greenfield.tasks import service
from tests.conftest import AuthHeaders, InsertTask

PAST = datetime(2026, 9, 1, 12, 0, tzinfo=UTC)


@pytest.fixture
def task_id(insert_task: InsertTask) -> uuid.UUID:
    """Tarea de user-a creada en el pasado, para ver avanzar `updated_at`."""
    return insert_task(title="Original", due_date=date(2026, 10, 1), created_at=PAST)


def _patch(client: TestClient, auth: AuthHeaders, tid: Any, body: Any, sub: str = "user-a") -> Any:
    return client.patch(f"/v1/tasks/{tid}", json=body, headers=auth(sub))


def _get(client: TestClient, auth: AuthHeaders, tid: Any, sub: str = "user-a") -> Any:
    return client.get(f"/v1/tasks/{tid}", headers=auth(sub)).json()


# Derived from R4.1
def test_solo_cambian_los_campos_enviados(
    client: TestClient, auth: AuthHeaders, task_id: uuid.UUID
) -> None:
    before = _get(client, auth, task_id)
    after = _patch(client, auth, task_id, {"title": "Nuevo título"}).json()
    assert after["title"] == "Nuevo título"
    for field in ("id", "description", "status", "due_date", "created_at"):
        assert after[field] == before[field]


# Derived from R4.2
def test_modificar_actualiza_updated_at_y_devuelve_la_tarea_resultante(
    client: TestClient, auth: AuthHeaders, task_id: uuid.UUID
) -> None:
    response = _patch(client, auth, task_id, {"status": "in_progress"})
    assert response.status_code == 200
    after = response.json()
    assert datetime.fromisoformat(after["updated_at"]) > PAST
    assert after["created_at"] == _get(client, auth, task_id)["created_at"]
    assert after == _get(client, auth, task_id)


# Derived from R4.2
@pytest.mark.parametrize("body", [{}, {"title": "Original", "due_date": "2026-10-01"}])
def test_sin_modificacion_real_no_toca_updated_at(
    client: TestClient, auth: AuthHeaders, task_id: uuid.UUID, body: dict[str, Any]
) -> None:
    before = _get(client, auth, task_id)
    response = _patch(client, auth, task_id, body)
    assert response.status_code == 200
    assert response.json() == before


# Derived from R4.3
@pytest.mark.parametrize(
    ("origen", "destino"), list(permutations(["pending", "in_progress", "completed"], 2))
)
def test_transicion_libre_entre_estados(
    client: TestClient, auth: AuthHeaders, insert_task: InsertTask, origen: str, destino: str
) -> None:
    tid = insert_task(status=origen)
    assert _patch(client, auth, tid, {"status": destino}).json()["status"] == destino


# Derived from R4.4
def test_nulo_quita_descripcion_y_fecha_limite(
    client: TestClient, auth: AuthHeaders, task_id: uuid.UUID
) -> None:
    _patch(client, auth, task_id, {"description": "algo"})
    after = _patch(client, auth, task_id, {"description": None, "due_date": None}).json()
    assert after["description"] is None
    assert after["due_date"] is None


# Derived from R4.5
@pytest.mark.parametrize(
    ("body", "field"),
    [
        ({"description": "no debe guardarse", "title": ""}, "title"),
        ({"description": "no debe guardarse", "title": "   "}, "title"),
        ({"description": "no debe guardarse", "title": None}, "title"),
        ({"description": "no debe guardarse", "status": None}, "status"),
        ({"description": "no debe guardarse", "status": "done"}, "status"),
        ({"description": "no debe guardarse", "due_date": "2026-02-30"}, "due_date"),
        ({"description": "x" * 2001}, "description"),
        ({"description": "no debe guardarse", "owner_sub": "user-b"}, "owner_sub"),
    ],
)
def test_cambios_invalidos_se_rechazan_sin_modificar_nada(
    client: TestClient, auth: AuthHeaders, task_id: uuid.UUID, body: dict[str, Any], field: str
) -> None:
    before = _get(client, auth, task_id)
    response = _patch(client, auth, task_id, body)
    assert response.status_code == 422
    assert [e["field"] for e in response.json()["errors"]] == [field]
    assert _get(client, auth, task_id) == before


# Derived from R4.6
@pytest.mark.parametrize("tid", [uuid.uuid4(), "abc"])
def test_actualizar_inexistente_o_id_invalido_es_404(
    client: TestClient, auth: AuthHeaders, tid: Any
) -> None:
    assert _patch(client, auth, tid, {"title": "x"}).status_code == 404


# Derived from R1.3
def test_no_se_puede_actualizar_una_tarea_ajena(
    client: TestClient, auth: AuthHeaders, task_id: uuid.UUID
) -> None:
    before = _get(client, auth, task_id)
    response = _patch(client, auth, task_id, {"title": "hackeado"}, sub="user-b")
    assert response.status_code == 404
    assert response.json() == _patch(client, auth, uuid.uuid4(), {"title": "x"}).json()
    assert _get(client, auth, task_id) == before


# Derived from R4.7
def test_dos_actualizaciones_del_mismo_campo_gana_la_ultima(
    client: TestClient, auth: AuthHeaders, task_id: uuid.UUID
) -> None:
    _patch(client, auth, task_id, {"title": "Primera"})
    _patch(client, auth, task_id, {"title": "Segunda"})
    assert _get(client, auth, task_id)["title"] == "Segunda"


# Derived from R4.7
def test_actualizaciones_concurrentes_intercaladas_sin_error_de_conflicto(
    db: Engine, task_id: uuid.UUID
) -> None:
    """Dos transacciones abiertas a la vez: cada una sólo escribe lo que cambió (DEC-9)."""
    with Session(db) as s1, Session(db) as s2:
        service.get(s1, "user-a", task_id)  # s1 lee la tarea (status=pending)...
        service.update(s2, "user-a", task_id, {"status": "completed"})
        s2.commit()  # ...s2 la cambia y confirma...
        service.update(s1, "user-a", task_id, {"description": "desde el celular"})
        s1.commit()  # ...y s1 escribe con su copia vieja sin pisar el status de s2
    with Session(db) as s3:
        task = service.get(s3, "user-a", task_id)
        assert (task.description, task.status) == ("desde el celular", "completed")

    with Session(db) as s1, Session(db) as s2:
        service.update(s1, "user-a", task_id, {"title": "A"})
        s1.commit()
        service.update(s2, "user-a", task_id, {"title": "B"})
        s2.commit()
    with Session(db) as s3:
        assert service.get(s3, "user-a", task_id).title == "B"
