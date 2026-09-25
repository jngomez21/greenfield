"""Punto de entrada: `uvicorn greenfield.main:app --env-file .env`."""

from fastapi import APIRouter, FastAPI

from greenfield.access_log import configure_logging, register_access_log
from greenfield.config import get_settings
from greenfield.errors import register_error_handlers
from greenfield.tasks.router import router as tasks_router


def create_app() -> FastAPI:
    configure_logging(get_settings().log_level)  # falla al arrancar si falta configuración
    app = FastAPI(title="greenfield", version="0.1.0")
    register_error_handlers(app)
    register_access_log(app)
    api = APIRouter(prefix="/v1")
    api.include_router(tasks_router)
    app.include_router(api)
    return app


app = create_app()
