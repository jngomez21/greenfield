import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from fastapi.testclient import TestClient

from tests.conftest import AuthHeaders, InsertTask


def _create(client: TestClient, auth: AuthHeaders, sub: str = "user-a", **body: Any) -> Any:
    body.setdefault("title", "Tarea")
    return client.post("/v1/tasks", json=body, headers=auth(sub)).json()


def _list(client: TestClient, auth: AuthHeaders, sub: str = "user-a", **params: Any) -> Any:
    return client.get("/v1/tasks", params=params, headers=auth(sub))


# Derived from R3.1
def test_consultar_tarea_propia_devuelve_todos_sus_campos(
    client: TestClient, auth: AuthHeaders
) -> None:
    created = _create(client, auth, description="d", status="in_progress", due_date="2026-11-02")
    response = client.get(f"/v1/tasks/{created['id']}", headers=auth())
    assert response.status_code == 200
    assert response.json() == created


# Derived from R1.3
def test_tarea_ajena_responde_igual_que_una_inexistente(
    client: TestClient, auth: AuthHeaders
) -> None:
    ajena = _create(client, auth, sub="user-b")["id"]
    response_ajena = client.get(f"/v1/tasks/{ajena}", headers=auth("user-a"))
    response_inexistente = client.get(f"/v1/tasks/{uuid.uuid4()}", headers=auth("user-a"))
    assert response_ajena.status_code == response_inexistente.status_code == 404
    assert response_ajena.json() == response_inexistente.json()
    assert response_ajena.headers["content-type"] == response_inexistente.headers["content-type"]


# Derived from R3.2
@pytest.mark.parametrize("task_id", ["abc", "123", "00000000-0000-0000-0000-00000000000z"])
def test_identificador_con_formato_invalido_no_existe(
    client: TestClient, auth: AuthHeaders, task_id: str
) -> None:
    response = client.get(f"/v1/tasks/{task_id}", headers=auth())
    assert response.status_code == 404
    assert response.json()["detail"] == "La tarea no existe."


# Derived from R3.3
def test_listado_ordena_por_creacion_desc_y_desempata_por_id(
    client: TestClient, auth: AuthHeaders, insert_task: InsertTask
) -> None:
    t0 = datetime(2026, 9, 1, tzinfo=UTC)
    viejo = insert_task(created_at=t0)
    nuevo = insert_task(created_at=t0 + timedelta(hours=2))
    empate = sorted(
        [insert_task(created_at=t0 + timedelta(hours=1)) for _ in range(3)], reverse=True
    )
    ids = [t["id"] for t in _list(client, auth).json()["items"]]
    assert ids == [str(nuevo), *map(str, empate), str(viejo)]


# Derived from R3.4
def test_listado_filtra_por_estado(
    client: TestClient, auth: AuthHeaders, insert_task: InsertTask
) -> None:
    en_curso = insert_task(status="in_progress")
    insert_task(status="pending")
    insert_task(status="completed")
    page = _list(client, auth, status="in_progress").json()
    assert [t["id"] for t in page["items"]] == [str(en_curso)]
    assert page["total"] == 1


# Derived from R3.5
def test_filtro_de_estado_invalido_es_422(client: TestClient, auth: AuthHeaders) -> None:
    response = _list(client, auth, status="done")
    assert response.status_code == 422
    assert [e["field"] for e in response.json()["errors"]] == ["status"]


# Derived from R3.6
def test_sin_tareas_devuelve_listado_vacio(client: TestClient, auth: AuthHeaders) -> None:
    response = _list(client, auth)
    assert response.status_code == 200
    assert response.json() == {"items": [], "total": 0, "limit": 50, "offset": 0}


# Derived from R3.7
def test_paginacion_por_defecto_50_con_total(
    client: TestClient, auth: AuthHeaders, insert_task: InsertTask
) -> None:
    for _ in range(55):
        insert_task()
    primera = _list(client, auth).json()
    assert (len(primera["items"]), primera["total"], primera["limit"]) == (50, 55, 50)
    resto = _list(client, auth, limit=10, offset=50).json()
    assert (len(resto["items"]), resto["total"], resto["offset"]) == (5, 55, 50)
    todas = _list(client, auth, limit=100).json()
    assert len(todas["items"]) == 55
    ids = [t["id"] for t in primera["items"]] + [t["id"] for t in resto["items"]]
    assert len(set(ids)) == 55  # sin repetidos ni huecos entre páginas


# Derived from R3.8
@pytest.mark.parametrize(
    ("params", "field"),
    [
        ({"limit": 0}, "limit"),
        ({"limit": 101}, "limit"),
        ({"offset": -1}, "offset"),
        ({"limit": "abc"}, "limit"),
    ],
)
def test_parametros_de_paginacion_invalidos_son_422(
    client: TestClient, auth: AuthHeaders, params: dict[str, Any], field: str
) -> None:
    response = _list(client, auth, **params)
    assert response.status_code == 422
    assert [e["field"] for e in response.json()["errors"]] == [field]


# Derived from R1.4
def test_listado_solo_incluye_tareas_propias(
    client: TestClient, auth: AuthHeaders, insert_task: InsertTask
) -> None:
    propia = insert_task(owner="user-a")
    insert_task(owner="user-b")
    insert_task(owner="user-b", status="in_progress")
    page = _list(client, auth, sub="user-a").json()
    assert [t["id"] for t in page["items"]] == [str(propia)]
    assert page["total"] == 1
    assert _list(client, auth, sub="user-a", status="in_progress").json()["total"] == 0
