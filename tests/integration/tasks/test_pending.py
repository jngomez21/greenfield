from datetime import UTC, date, datetime, timedelta
from typing import Any

import pytest
from fastapi.testclient import TestClient

from greenfield.tasks.router import get_today
from tests.conftest import AuthHeaders, InsertTask

TODAY = date(2026, 10, 10)
T0 = datetime(2026, 9, 1, tzinfo=UTC)


@pytest.fixture
def pending_client(client: TestClient) -> TestClient:
    client.app.dependency_overrides[get_today] = lambda: TODAY  # type: ignore[attr-defined]
    return client


def _pending(client: TestClient, auth: AuthHeaders, sub: str = "user-a", **params: Any) -> Any:
    return client.get("/v1/tasks/pending", params=params, headers=auth(sub))


def _ids(response: Any) -> list[str]:
    return [t["id"] for t in response.json()["items"]]


# Derived from R6.1
def test_pendientes_son_pending_e_in_progress_propias(
    pending_client: TestClient, auth: AuthHeaders, insert_task: InsertTask
) -> None:
    pendiente = insert_task(status="pending", created_at=T0)
    en_curso = insert_task(status="in_progress", created_at=T0 + timedelta(hours=1))
    insert_task(status="completed")
    insert_task(owner="user-b", status="pending")
    response = _pending(pending_client, auth)
    assert response.status_code == 200
    assert _ids(response) == [str(pendiente), str(en_curso)]
    assert response.json()["total"] == 2


# Derived from R6.2
def test_orden_por_fecha_limite_sin_fecha_al_final_y_desempates(
    pending_client: TestClient, auth: AuthHeaders, insert_task: InsertTask
) -> None:
    sin_fecha = insert_task(created_at=T0)
    tarde = insert_task(due_date=TODAY + timedelta(days=5), created_at=T0)
    temprano = insert_task(due_date=TODAY - timedelta(days=3), created_at=T0 + timedelta(hours=2))
    mismo_dia_viejo = insert_task(due_date=TODAY, created_at=T0)
    mismo_dia_nuevo = insert_task(due_date=TODAY, created_at=T0 + timedelta(hours=1))
    empate_total = sorted(
        insert_task(due_date=TODAY + timedelta(days=1), created_at=T0) for _ in range(3)
    )
    assert _ids(_pending(pending_client, auth)) == [
        str(temprano),
        str(mismo_dia_viejo),
        str(mismo_dia_nuevo),
        *map(str, empate_total),
        str(tarde),
        str(sin_fecha),
    ]


# Derived from R6.3
def test_cada_pendiente_indica_si_esta_vencida(
    pending_client: TestClient, auth: AuthHeaders, insert_task: InsertTask
) -> None:
    vencida = insert_task(due_date=TODAY - timedelta(days=1))
    hoy = insert_task(due_date=TODAY)
    sin_fecha = insert_task()
    items = {t["id"]: t for t in _pending(pending_client, auth).json()["items"]}
    assert items[str(vencida)]["is_overdue"] is True
    assert items[str(hoy)]["is_overdue"] is False
    assert items[str(sin_fecha)]["is_overdue"] is False
    assert set(items[str(hoy)]) == {
        "id",
        "title",
        "description",
        "status",
        "due_date",
        "created_at",
        "updated_at",
        "is_overdue",
    }


# Derived from R6.4
def test_filtro_solo_vencidas(
    pending_client: TestClient, auth: AuthHeaders, insert_task: InsertTask
) -> None:
    vencida_1 = insert_task(due_date=TODAY - timedelta(days=10))
    vencida_2 = insert_task(due_date=TODAY - timedelta(days=1), status="in_progress")
    insert_task(due_date=TODAY - timedelta(days=5), status="completed")  # no es pendiente
    insert_task(due_date=TODAY)
    insert_task(due_date=TODAY + timedelta(days=1))
    insert_task()
    response = _pending(pending_client, auth, overdue="true")
    assert _ids(response) == [str(vencida_1), str(vencida_2)]
    assert response.json()["total"] == 2
    assert all(t["is_overdue"] for t in response.json()["items"])
    assert _pending(pending_client, auth, overdue="false").json()["total"] == 5


# Derived from R6.5
def test_sin_pendientes_devuelve_listado_vacio(
    pending_client: TestClient, auth: AuthHeaders, insert_task: InsertTask
) -> None:
    insert_task(status="completed")
    response = _pending(pending_client, auth)
    assert response.status_code == 200
    assert response.json() == {"items": [], "total": 0, "limit": 50, "offset": 0}


# Derived from R6.6
def test_pendientes_paginadas_con_total(
    pending_client: TestClient, auth: AuthHeaders, insert_task: InsertTask
) -> None:
    for i in range(55):
        insert_task(due_date=TODAY + timedelta(days=i))
    first = _pending(pending_client, auth).json()
    rest = _pending(pending_client, auth, limit=10, offset=50).json()
    assert (len(first["items"]), first["total"]) == (50, 55)
    assert (len(rest["items"]), rest["offset"]) == (5, 50)
    assert rest["items"][-1]["due_date"] == (TODAY + timedelta(days=54)).isoformat()


# Derived from R6.6
@pytest.mark.parametrize(
    ("params", "field"),
    [
        ({"limit": 0}, "limit"),
        ({"limit": 101}, "limit"),
        ({"offset": -1}, "offset"),
        ({"overdue": "quizas"}, "overdue"),
        ({"offset": 10**20}, "offset"),  # code review: fuera de bigint daba 500
    ],
)
def test_parametros_invalidos_de_pendientes_son_422(
    pending_client: TestClient, auth: AuthHeaders, params: dict[str, Any], field: str
) -> None:
    response = _pending(pending_client, auth, **params)
    assert response.status_code == 422
    assert [e["field"] for e in response.json()["errors"]] == [field]


# Derived from R1.1
def test_pendientes_exige_token(pending_client: TestClient) -> None:
    assert pending_client.get("/v1/tasks/pending").status_code == 401
