from fastapi.testclient import TestClient
from sqlalchemy import Engine, event


def test_health_responde_sin_token_y_sin_tocar_la_bd(client: TestClient, db: Engine) -> None:
    """Health check de Render (AMD-002): liveness puro, no depende de la BD ni del IdP."""
    statements: list[str] = []

    def capture(conn, cursor, statement, parameters, context, executemany) -> None:  # type: ignore[no-untyped-def]
        statements.append(statement)

    event.listen(db, "before_cursor_execute", capture)
    try:
        response = client.get("/health")
    finally:
        event.remove(db, "before_cursor_execute", capture)
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert statements == []
