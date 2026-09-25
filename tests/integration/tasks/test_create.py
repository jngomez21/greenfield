import uuid
from datetime import UTC, date, datetime, timedelta
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, text

from tests.conftest import AuthHeaders


def _post(client: TestClient, auth: AuthHeaders, body: dict[str, Any], sub: str = "user-a") -> Any:
    return client.post("/v1/tasks", json=body, headers=auth(sub))


def _fields(response: Any) -> list[str]:
    return [e["field"] for e in response.json()["errors"]]


# Derived from R2.1
def test_crear_devuelve_201_con_la_tarea_completa_y_location(
    client: TestClient, auth: AuthHeaders
) -> None:
    before = datetime.now(UTC)
    response = _post(client, auth, {"title": "Pagar arriendo"})
    assert response.status_code == 201
    task = response.json()
    assert set(task) == {
        "id",
        "title",
        "description",
        "status",
        "due_date",
        "created_at",
        "updated_at",
    }
    uuid.UUID(task["id"])
    assert task["title"] == "Pagar arriendo"
    assert task["description"] is None
    assert task["due_date"] is None
    created = datetime.fromisoformat(task["created_at"])
    assert created.tzinfo is not None and created >= before - timedelta(seconds=1)
    assert task["updated_at"] == task["created_at"]
    assert response.headers["Location"].endswith(f"/v1/tasks/{task['id']}")


# Derived from R1.2
def test_crear_registra_al_usuario_autenticado_como_dueno(
    client: TestClient, auth: AuthHeaders, db: Engine
) -> None:
    task_id = _post(client, auth, {"title": "x"}, sub="user-b").json()["id"]
    with db.connect() as conn:
        owner = conn.execute(
            text("SELECT owner_sub FROM tasks WHERE id = :id"), {"id": task_id}
        ).scalar_one()
    assert owner == "user-b"


# Derived from R2.2
def test_crear_sin_estado_asigna_pending(client: TestClient, auth: AuthHeaders) -> None:
    assert _post(client, auth, {"title": "x"}).json()["status"] == "pending"


# Derived from R2.3
def test_crear_guarda_descripcion_estado_y_fecha_limite(
    client: TestClient, auth: AuthHeaders
) -> None:
    body = {
        "title": "Declaración de renta",
        "description": "Reunir certificados",
        "status": "in_progress",
        "due_date": "2026-10-15",
    }
    task = _post(client, auth, body).json()
    assert {k: task[k] for k in body} == body


# Derived from R2.4, R2.5 (code review: PostgreSQL no admite U+0000 en texto)
@pytest.mark.parametrize(
    ("body", "field"),
    [({"title": "a\u0000b"}, "title"), ({"title": "x", "description": "d\u0000"}, "description")],
)
def test_crear_rechaza_caracter_nulo_con_422_y_no_500(
    client: TestClient, auth: AuthHeaders, body: dict[str, Any], field: str
) -> None:
    response = _post(client, auth, body)
    assert response.status_code == 422
    assert _fields(response) == [field]


# Derived from R2.4
@pytest.mark.parametrize("title", ["x" * 200, "ñ" * 200])
def test_crear_acepta_titulo_de_200_caracteres(
    client: TestClient, auth: AuthHeaders, title: str
) -> None:
    assert _post(client, auth, {"title": title}).status_code == 201


# Derived from R2.4
@pytest.mark.parametrize(
    "body",
    [{}, {"title": ""}, {"title": "   "}, {"title": "\t\n"}, {"title": "x" * 201}, {"title": 5}],
)
def test_crear_rechaza_titulo_invalido(
    client: TestClient, auth: AuthHeaders, body: dict[str, Any]
) -> None:
    response = _post(client, auth, body)
    assert response.status_code == 422
    assert _fields(response) == ["title"]


# Derived from R2.5
def test_crear_limite_de_descripcion(client: TestClient, auth: AuthHeaders) -> None:
    assert _post(client, auth, {"title": "x", "description": "d" * 2000}).status_code == 201
    response = _post(client, auth, {"title": "x", "description": "d" * 2001})
    assert response.status_code == 422
    assert _fields(response) == ["description"]


# Derived from R2.6
@pytest.mark.parametrize("status", ["done", "PENDING", "pendiente", "", None])
def test_crear_rechaza_estado_invalido(client: TestClient, auth: AuthHeaders, status: Any) -> None:
    response = _post(client, auth, {"title": "x", "status": status})
    assert response.status_code == 422
    assert _fields(response) == ["status"]


# Derived from R2.7
@pytest.mark.parametrize(
    "due_date", ["2026-02-30", "01/10/2026", "2026-10-01T00:00:00", "2026-1-5", 20261001, ""]
)
def test_crear_rechaza_fecha_limite_invalida(
    client: TestClient, auth: AuthHeaders, due_date: Any
) -> None:
    response = _post(client, auth, {"title": "x", "due_date": due_date})
    assert response.status_code == 422
    assert _fields(response) == ["due_date"]


# Derived from R2.8
def test_crear_acepta_fecha_limite_pasada(client: TestClient, auth: AuthHeaders) -> None:
    past = (date.today() - timedelta(days=30)).isoformat()
    response = _post(client, auth, {"title": "x", "due_date": past})
    assert response.status_code == 201
    assert response.json()["due_date"] == past


# Derived from R1.2
@pytest.mark.parametrize("field", ["owner_sub", "id", "created_at", "otro"])
def test_crear_rechaza_campos_no_permitidos(
    client: TestClient, auth: AuthHeaders, field: str
) -> None:
    response = _post(client, auth, {"title": "x", field: "valor"})
    assert response.status_code == 422
    assert _fields(response) == [field]
