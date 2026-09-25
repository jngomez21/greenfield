# Tech stack

> **Servicio**: `greenfield`
> **Estado**: completo (bootstrap 2026-09-25). Deploy target `TBD` a propósito — ver abajo.

> El Service Agent se **negará a generar código** mientras este archivo
> tenga un `TODO` **que no cuelgue de nada** — lenguaje, framework,
> persistencia o testing sin decidir. Razón: sin eso, los `design.md`
> salen genéricos y los tests no pueden trazar a las convenciones
> reales.
>
> **Un `TODO` que cuelga de una `D-N` aceptada en G2 con `MOCK` y
> `Ready to unmock` no bloquea**: bloquea producción, no el trabajo
> contra el doble. Si bloqueara, una spec cuyo stack espera a un
> tercero no llegaría nunca al código. La tabla está en
> `/spec-implement`.

## Lenguaje y framework

- **Python 3.13**.
- **FastAPI** (API HTTP/JSON) sobre **Uvicorn**. Validación y schemas con
  **Pydantic v2** (viene con FastAPI). El OpenAPI lo genera FastAPI; no se
  mantiene a mano.

## Persistencia

- **PostgreSQL 18** (subido desde 17 en AMD-001 de `gestion-tareas`: misma versión en desarrollo, pruebas y despliegue).
- **SQLAlchemy 2.x** (ORM, estilo 2.0 con `Mapped[...]`), driver **psycopg 3**.
- **Alembic** para migraciones. Todo cambio de esquema pasa por una migración
  versionada; nunca `create_all()` fuera de tests.
- Sin cache. Se agrega cuando una métrica lo justifique.

## Build y package manager

- **uv** (gestión de dependencias y entornos). `pyproject.toml` como fuente
  única; **`uv.lock` se commitea**.
- Sin bundler (no aplica).
- Imagen de contenedor: `Dockerfile` multi-stage cuando se decida el deploy target.

## Tests

- **pytest**, con `fastapi.testclient.TestClient` para la API.
- Integración contra un **PostgreSQL 18 real** indicado en `TEST_DATABASE_URL` (en local, el servidor
  instalado en la máquina; en CI, un servicio PostgreSQL del pipeline). Sin contenedores: el proxy
  corporativo bloquea la descarga de imágenes de Docker Hub (AMD-001).
- Detalle de política en `stack/testing.md`.

## Lint y formato

- **ruff** para lint y formato (`ruff check` + `ruff format`).
- Tipado: anotaciones obligatorias en código de `src/`; chequeo con **mypy**
  en modo `strict` sobre `src/`.

## Deploy target

`TBD` — igual que `repo-config.yaml > runtime.type`. No bloquea desarrollo ni
tests locales; se resuelve antes de la primera promoción a `pruebas`. Local:
instancia PostgreSQL 18 propia del desarrollador (`initdb` con los binarios ya instalados,
datos en `%LOCALAPPDATA%\greenfield\pgdata`, puerto **5433**, sin permisos de administrador), con
las bases `greenfield` (ejecución manual) y `greenfield_test` (pruebas). Se arranca con `pg_ctl`
(ver `README.md`).

## Versiones pineadas

| Componente | Versión |
|---|---|
| Python | 3.13.x |
| PostgreSQL | 18.x |
| FastAPI | última 0.x estable al crear `pyproject.toml`, fijada en `uv.lock` |
| SQLAlchemy | 2.x |
| Alembic | 1.x |
| psycopg | 3.x |
| PyJWT (con `cryptography`) | 2.x — validación de JWT, ver `stack/security.md` |

Las versiones exactas viven en `uv.lock`. Añadir una dependencia nueva requiere
OK explícito (AGENTS.md § *Dependencias nuevas*).
