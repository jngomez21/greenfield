# Architecture

> **Servicio**: `greenfield`
> **Estado**: completo (bootstrap 2026-09-25)

## Estilo arquitectónico

**Layered simple, organizado por módulo de dominio** (router → service → ORM).
Es un servicio CRUD pequeño: Hexagonal o Clean Architecture añadirían puertos y
adaptadores con una sola implementación cada uno. Si aparece un segundo
adaptador real (otra BD, otra cola), se extrae la interfaz en ese momento y se
registra en un ADR.

## Estructura de carpetas

```
src/greenfield/
├── main.py          # crea la app FastAPI y registra los routers
├── config.py        # settings leídos de variables de entorno
├── db.py            # engine, sessionmaker y dependencia get_session
├── auth.py          # dependencia get_current_user (valida el JWT)
├── errors.py        # excepciones de dominio + handlers HTTP
└── <modulo>/        # un paquete por módulo de dominio (ej. tasks/)
    ├── router.py    # endpoints HTTP: parseo, auth, códigos de estado
    ├── service.py   # reglas de negocio; recibe la Session
    ├── models.py    # modelos ORM SQLAlchemy
    └── schemas.py   # schemas Pydantic de entrada/salida
migrations/          # Alembic (env.py + versions/)
tests/
├── conftest.py      # fixtures: Postgres (testcontainers), client, tokens
├── unit/
└── integration/
```

## Capas y boundaries

- `router` importa `service` y `schemas`. **No** contiene reglas de negocio ni
  queries.
- `service` importa `models` y `errors`. **No** importa FastAPI ni conoce HTTP.
- `models` no importa nada de las capas de arriba.
- Un módulo no importa el `service` de otro módulo sin una decisión documentada.
- Los schemas Pydantic (API) y los modelos ORM (BD) son tipos distintos: nunca
  se devuelve un modelo ORM directamente como respuesta.

## Inyección de dependencias

Con el `Depends` de FastAPI (`get_session`, `get_current_user`). En tests se
sustituyen con `app.dependency_overrides`. Sin contenedor DI.

## Manejo de errores

- `service` lanza **excepciones de dominio** (`NotFoundError`,
  `ValidationError`, …) definidas en `errors.py`.
- `errors.py` registra exception handlers que las traducen a HTTP con cuerpo
  **RFC 9457** (`application/problem+json`).
- Errores no esperados → 500 genérico, sin stack trace en la respuesta
  (se loguea).
- Prohibido tragarse excepciones en silencio.

## Concurrencia / async

- Endpoints **síncronos** (`def`, no `async def`) con SQLAlchemy síncrono:
  FastAPI los ejecuta en su threadpool. Es más simple y alcanza para la carga
  esperada. Se migra a async si una NFR de throughput lo exige (ADR).
- Una transacción por request: la dependencia `get_session` hace commit si todo
  sale bien y rollback si hay excepción.
- Sin reintentos ni colas por ahora (no hay integraciones salientes).

## ADRs

`docs/adr/NNNN-<titulo>.md` (formato MADR corto), creados cuando haga falta el
primero. Este archivo no se sobrescribe por decisiones posteriores.
