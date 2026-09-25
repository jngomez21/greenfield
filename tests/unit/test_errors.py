import logging
from collections.abc import Iterator

import pytest
from fastapi import FastAPI, HTTPException, Request
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field

from greenfield.access_log import register_access_log
from greenfield.errors import NotFoundError, register_error_handlers

PROBLEM = "application/problem+json"


class Body(BaseModel):
    title: str = Field(max_length=5)


@pytest.fixture
def client() -> Iterator[TestClient]:
    app = FastAPI()
    register_error_handlers(app)
    register_access_log(app)

    @app.get("/missing")
    def missing() -> None:
        raise NotFoundError

    @app.get("/limit")
    def limit(limit: int) -> dict[str, int]:
        return {"limit": limit}

    @app.post("/body")
    def body(request: Request, payload: Body) -> dict[str, str]:
        request.state.sub = "user-a"
        return {"ok": "sí"}

    @app.get("/unauthorized")
    def unauthorized() -> None:
        raise HTTPException(
            401, "Credenciales ausentes o inválidas.", {"WWW-Authenticate": "Bearer"}
        )

    @app.get("/boom")
    def boom() -> None:
        raise RuntimeError("detalle interno que no debe salir")

    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


# Derived from R3.2
def test_not_found_es_problem_json_404(client: TestClient) -> None:
    response = client.get("/missing")
    assert response.status_code == 404
    assert response.headers["content-type"] == PROBLEM
    assert response.json() == {
        "type": "about:blank",
        "title": "Not Found",
        "status": 404,
        "detail": "La tarea no existe.",
    }


def test_validacion_es_422_e_identifica_el_campo(client: TestClient) -> None:
    response = client.post("/body", json={"title": "demasiado largo"})
    assert response.status_code == 422
    assert response.headers["content-type"] == PROBLEM
    problem = response.json()
    assert problem["title"] == "Unprocessable Content"  # frase de RFC 9110
    assert [e["field"] for e in problem["errors"]] == ["title"]
    assert all(e["message"] for e in problem["errors"])


def test_validacion_de_query_identifica_el_parametro(client: TestClient) -> None:
    problem = client.get("/limit", params={"limit": "abc"}).json()
    assert [e["field"] for e in problem["errors"]] == ["limit"]


def test_json_mal_formado_se_reporta_en_body(client: TestClient) -> None:
    response = client.post(
        "/body", content=b"{no es json", headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 422
    assert [e["field"] for e in response.json()["errors"]] == ["body"]


def test_http_exception_conserva_status_y_headers(client: TestClient) -> None:
    response = client.get("/unauthorized")
    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"
    assert response.headers["content-type"] == PROBLEM
    assert response.json()["detail"] == "Credenciales ausentes o inválidas."


def test_ruta_inexistente_tambien_es_problem_json(client: TestClient) -> None:
    response = client.get("/no-existe")
    assert response.status_code == 404
    assert response.headers["content-type"] == PROBLEM


def test_error_no_controlado_es_500_generico_y_se_loguea(
    client: TestClient, caplog: pytest.LogCaptureFixture
) -> None:
    with caplog.at_level(logging.ERROR):
        response = client.get("/boom")
    assert response.status_code == 500
    assert response.headers["content-type"] == PROBLEM
    assert "detalle interno" not in response.text
    assert "detalle interno" in caplog.text  # el detalle queda sólo en el log


# Derived from NFR2
def test_access_log_registra_metadatos_sin_el_cuerpo(
    client: TestClient, caplog: pytest.LogCaptureFixture
) -> None:
    with caplog.at_level(logging.INFO, logger="greenfield.access"):
        client.post("/body", json={"title": "SECRO"}, headers={"Authorization": "Bearer TOKEN-X"})
    line = next(r.getMessage() for r in caplog.records if r.name == "greenfield.access")
    assert line.startswith("POST /body 200 ")
    assert "sub=user-a" in line
    assert "SECRO" not in caplog.text
    assert "TOKEN-X" not in caplog.text


def test_access_log_sin_usuario_autenticado(
    client: TestClient, caplog: pytest.LogCaptureFixture
) -> None:
    with caplog.at_level(logging.INFO, logger="greenfield.access"):
        client.get("/missing")
    line = next(r.getMessage() for r in caplog.records if r.name == "greenfield.access")
    assert line.startswith("GET /missing 404 ")
    assert line.endswith("sub=-")
