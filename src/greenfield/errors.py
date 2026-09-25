"""Excepciones de dominio y respuestas de error RFC 9457 (application/problem+json)."""

import logging
from collections.abc import Mapping
from http import HTTPStatus
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("greenfield.errors")

PROBLEM_JSON = "application/problem+json"
_LOCATIONS = {"body", "query", "path", "header", "cookie"}


class NotFoundError(Exception):
    """La tarea no existe o no pertenece al usuario: misma respuesta en ambos casos (R1.3)."""


def problem(
    status: int,
    *,
    detail: str | None = None,
    errors: list[dict[str, str]] | None = None,
    headers: Mapping[str, str] | None = None,
) -> JSONResponse:
    body: dict[str, Any] = {
        "type": "about:blank",
        "title": HTTPStatus(status).phrase,
        "status": status,
    }
    if detail:
        body["detail"] = detail
    if errors is not None:
        body["errors"] = errors
    return JSONResponse(body, status_code=status, media_type=PROBLEM_JSON, headers=headers)


def _field(error: dict[str, Any]) -> str:
    if error.get("type") == "json_invalid":
        return "body"
    parts = [str(p) for p in error.get("loc", ()) if p not in _LOCATIONS]
    return ".".join(parts) or "body"


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(NotFoundError)
    async def not_found(request: Request, exc: NotFoundError) -> JSONResponse:
        return problem(404, detail="La tarea no existe.")

    @app.exception_handler(RequestValidationError)
    async def validation(request: Request, exc: RequestValidationError) -> JSONResponse:
        errors = [{"field": _field(e), "message": str(e.get("msg", ""))} for e in exc.errors()]
        return problem(422, detail="La petición no es válida.", errors=errors)

    @app.exception_handler(StarletteHTTPException)
    async def http_error(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        detail = exc.detail if isinstance(exc.detail, str) else None
        return problem(exc.status_code, detail=detail, headers=exc.headers)

    @app.exception_handler(Exception)
    async def unhandled(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Error no controlado en %s %s", request.method, request.url.path)
        return problem(500, detail="Error interno del servidor.")
