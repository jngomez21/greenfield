"""Prueba independiente del slice P1 (requirements.md § Slices priorizados)."""

import logging
import uuid

import pytest
from fastapi.testclient import TestClient

from tests.conftest import AuthHeaders

TITLE = "TITULO-SENSIBLE-P1"
DESCRIPTION = "DESCRIPCION-SENSIBLE-P1"


# Derived from R1.1, R1.2, R1.3, R1.4, NFR2
def test_prueba_independiente_p1_usuarios_a_y_b(
    client: TestClient, auth: AuthHeaders, caplog: pytest.LogCaptureFixture
) -> None:
    a, b = auth("user-a"), auth("user-b")
    with caplog.at_level(logging.DEBUG):
        # A crea una tarea con fecha límite y la consulta.
        created = client.post(
            "/v1/tasks",
            json={"title": TITLE, "description": DESCRIPTION, "due_date": "2026-12-01"},
            headers=a,
        )
        assert created.status_code == 201
        url = f"/v1/tasks/{created.json()['id']}"
        assert client.get(url, headers=a).json()["due_date"] == "2026-12-01"

        # A cambia el estado y la ve en su listado filtrado.
        assert client.patch(url, json={"status": "in_progress"}, headers=a).status_code == 200
        listed = client.get("/v1/tasks", params={"status": "in_progress"}, headers=a).json()
        assert [t["id"] for t in listed["items"]] == [created.json()["id"]]

        # B no puede verla, listarla, modificarla ni eliminarla en ningún momento.
        assert client.get(url, headers=b).status_code == 404
        assert client.get("/v1/tasks", headers=b).json()["total"] == 0
        assert client.patch(url, json={"status": "completed"}, headers=b).status_code == 404
        assert client.delete(url, headers=b).status_code == 404
        assert client.get(url, headers=a).json()["status"] == "in_progress"

        # A la elimina.
        assert client.delete(url, headers=a).status_code == 204
        assert client.get(url, headers=a).status_code == 404

    # NFR2: nada del contenido ni de las credenciales llega a los logs.
    for secret in (TITLE, DESCRIPTION, a["Authorization"], b["Authorization"]):
        assert secret.split()[-1] not in caplog.text
    access = [r.getMessage() for r in caplog.records if r.name == "greenfield.access"]
    assert len(access) == 11
    assert any("sub=user-b" in line for line in access)


# Derived from R1.1
@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("POST", "/v1/tasks"),
        ("GET", "/v1/tasks"),
        ("GET", f"/v1/tasks/{uuid.uuid4()}"),
        ("PATCH", f"/v1/tasks/{uuid.uuid4()}"),
        ("DELETE", f"/v1/tasks/{uuid.uuid4()}"),
    ],
)
def test_todos_los_endpoints_exigen_token(client: TestClient, method: str, path: str) -> None:
    response = client.request(method, path, json={"title": "x"})
    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"
    assert response.headers["content-type"] == "application/problem+json"
