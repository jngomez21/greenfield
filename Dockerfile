# Imagen del servicio (AMD-002). Se construye en Render, no en la máquina local.
FROM python:3.13-slim AS build
COPY --from=ghcr.io/astral-sh/uv:0.12.19 /uv /bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never
WORKDIR /app
# Dependencias primero (capa cacheable), luego el proyecto; sin dependencias de desarrollo.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY src ./src
RUN uv sync --frozen --no-dev --no-editable

FROM python:3.13-slim
RUN useradd --system --uid 10001 app
WORKDIR /app
COPY --from=build /app/.venv /app/.venv
COPY alembic.ini ./
COPY migrations ./migrations
ENV PATH="/app/.venv/bin:$PATH" PORT=8000
USER app
EXPOSE 8000
# DEC-13: migraciones y luego el servidor, en el puerto que asigne Render.
CMD ["sh", "-c", "alembic upgrade head && exec uvicorn greenfield.main:app --host 0.0.0.0 --port ${PORT}"]
