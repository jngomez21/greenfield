"""Logging y access log: una línea por request, nunca el cuerpo ni los headers (NFR2)."""

import logging
import time
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response

logger = logging.getLogger("greenfield.access")


def configure_logging(level: str) -> None:
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s %(name)s %(message)s")


def register_access_log(app: FastAPI) -> None:
    @app.middleware("http")
    async def access_log(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        start = time.perf_counter()
        status_code = 500  # si la app lanza, el cliente recibe un 500
        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        finally:
            logger.info(
                "%s %s %s %.1fms sub=%s",
                request.method,
                request.url.path,
                status_code,
                (time.perf_counter() - start) * 1000,
                getattr(request.state, "sub", "-"),
            )
