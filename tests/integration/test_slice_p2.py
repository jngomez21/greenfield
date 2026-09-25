"""Prueba independiente del slice P2 (requirements.md § Slices priorizados)."""

from datetime import UTC, date, datetime, timedelta

from fastapi.testclient import TestClient

from greenfield.tasks.router import get_today
from tests.conftest import AuthHeaders, InsertTask

T0 = datetime(2026, 9, 1, tzinfo=UTC)


def _preload(insert_task: InsertTask, today: date) -> dict[str, str]:
    """Tareas en los tres estados, con y sin fecha límite, algunas vencidas."""
    d = timedelta(days=1)
    ids = {
        "vencida_pendiente": insert_task(status="pending", due_date=today - 3 * d, created_at=T0),
        "vencida_en_curso": insert_task(status="in_progress", due_date=today - d, created_at=T0),
        "vence_hoy": insert_task(status="pending", due_date=today, created_at=T0),
        "futura_en_curso": insert_task(status="in_progress", due_date=today + 2 * d, created_at=T0),
        "sin_fecha": insert_task(status="pending", created_at=T0),
        "completada_vencida": insert_task(status="completed", due_date=today - 5 * d),
        "completada_sin_fecha": insert_task(status="completed"),
        "ajena_vencida": insert_task(owner="user-b", due_date=today - 3 * d),
    }
    return {name: str(task_id) for name, task_id in ids.items()}


def _check_p2(client: TestClient, auth: AuthHeaders, ids: dict[str, str]) -> None:
    pending = client.get("/v1/tasks/pending", headers=auth()).json()
    assert [(t["id"], t["is_overdue"]) for t in pending["items"]] == [
        (ids["vencida_pendiente"], True),
        (ids["vencida_en_curso"], True),
        (ids["vence_hoy"], False),
        (ids["futura_en_curso"], False),
        (ids["sin_fecha"], False),
    ]
    overdue = client.get("/v1/tasks/pending", params={"overdue": "true"}, headers=auth()).json()
    assert [t["id"] for t in overdue["items"]] == [
        ids["vencida_pendiente"],
        ids["vencida_en_curso"],
    ]
    assert overdue["total"] == 2
    # P2 es aditivo: el listado general de P1 sigue incluyendo las completadas.
    assert client.get("/v1/tasks", headers=auth()).json()["total"] == 7


# Derived from R6.1, R6.2, R6.3, R6.4
def test_prueba_independiente_p2_con_hoy_fijo(
    client: TestClient, auth: AuthHeaders, insert_task: InsertTask
) -> None:
    today = date(2026, 10, 10)
    client.app.dependency_overrides[get_today] = lambda: today  # type: ignore[attr-defined]
    _check_p2(client, auth, _preload(insert_task, today))


# Derived from R6.3
def test_prueba_independiente_p2_con_el_reloj_real_en_utc(
    client: TestClient, auth: AuthHeaders, insert_task: InsertTask
) -> None:
    _check_p2(client, auth, _preload(insert_task, datetime.now(UTC).date()))
