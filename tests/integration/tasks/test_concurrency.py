"""Carreras entre requests sobre la misma tarea (hallazgos del code review)."""

import re
import threading
from datetime import date

import pytest
from sqlalchemy import Engine, event
from sqlalchemy.orm import Session

from greenfield.errors import NotFoundError
from greenfield.tasks import service
from tests.conftest import InsertTask

BLOCK_CHECK_SECONDS = 0.5


def _run_in_thread(target: object) -> tuple[threading.Thread, dict[str, object]]:
    outcome: dict[str, object] = {}

    def runner() -> None:
        try:
            outcome["result"] = target()  # type: ignore[operator]
        except Exception as exc:  # noqa: BLE001 — se inspecciona en el test
            outcome["error"] = exc

    thread = threading.Thread(target=runner)
    thread.start()
    return thread, outcome


# Derived from R4.7
def test_update_espera_a_la_transaccion_en_curso_y_gana_la_ultima(
    db: Engine, insert_task: InsertTask
) -> None:
    """T1 cambia el título a 'A' sin confirmar; T2 manda 'X' (el valor viejo) y debe ganar."""
    tid = insert_task(title="X")
    with Session(db) as s1:
        service.update(s1, "user-a", tid, {"title": "A"})  # fila bloqueada, sin commit

        def t2() -> None:
            with Session(db) as s2:
                service.update(s2, "user-a", tid, {"title": "X"})
                s2.commit()

        thread, outcome = _run_in_thread(t2)
        thread.join(BLOCK_CHECK_SECONDS)
        assert thread.is_alive(), "T2 debió esperar el bloqueo de T1"
        s1.commit()
        thread.join()
    assert "error" not in outcome
    with Session(db) as s3:
        assert service.get(s3, "user-a", tid).title == "X"


# Derived from R4.6, R5.2
@pytest.mark.parametrize("second", ["update", "delete"])
def test_operacion_sobre_tarea_borrada_en_paralelo_es_404_y_no_500(
    db: Engine, insert_task: InsertTask, second: str
) -> None:
    tid = insert_task()
    with Session(db) as s1:
        service.delete(s1, "user-a", tid)  # borrado sin confirmar

        def other() -> None:
            with Session(db) as s2:
                if second == "update":
                    service.update(s2, "user-a", tid, {"due_date": date(2026, 12, 1)})
                else:
                    service.delete(s2, "user-a", tid)
                s2.commit()

        thread, outcome = _run_in_thread(other)
        thread.join(BLOCK_CHECK_SECONDS)
        s1.commit()
        thread.join()
    assert isinstance(outcome.get("error"), NotFoundError), outcome


# Derived from NFR1 (code review: el índice parcial exige el literal en la consulta)
def test_pendientes_usa_literal_completed_para_el_indice_parcial(
    db: Engine, insert_task: InsertTask
) -> None:
    statements: list[str] = []

    def capture(conn, cursor, statement, parameters, context, executemany) -> None:  # type: ignore[no-untyped-def]
        statements.append(statement)

    event.listen(db, "before_cursor_execute", capture)
    try:
        with Session(db) as session:
            service.list_pending(session, "user-a", date(2026, 10, 10), False, 50, 0)
    finally:
        event.remove(db, "before_cursor_execute", capture)
    # `!=` y `<>` son el mismo operador en PostgreSQL; lo que importa es el literal, no un bind.
    assert statements and all(re.search(r"(<>|!=) 'completed'", s) for s in statements)
