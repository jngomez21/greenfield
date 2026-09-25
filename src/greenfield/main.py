"""Punto de entrada: `uvicorn greenfield.main:app --env-file .env`."""

from fastapi import APIRouter, FastAPI


def create_app() -> FastAPI:
    app = FastAPI(title="greenfield", version="0.1.0")
    api = APIRouter(prefix="/v1")  # los routers de dominio se registran aquí (T5+)
    app.include_router(api)
    return app


app = create_app()
