<!--
  PLANTILLA AI-DLC — tasks.md (canonical: .agents/templates/spec/)
  Se llena DESPUÉS de que design.md esté firmado. Es el desglose
  ejecutable que /spec-implement recorre.

  GUARDRAILS de derivación:
  - Organizar por FASES: Setup → Foundational (bloqueante) → una fase
    por slice (P1, P2... de requirements.md) → Polish. Implementar
    sólo Setup + Foundational + P1 debe dar algo desplegable a
    `pruebas` (MVP — alimenta partial-deploy, §3.10).
  - Cada task cita los R*.* que cubre y las D-N de las que depende.
    Una task sin R*.* es sospechosa (¿es chore?).
  - Marcar [P] sólo si la task es PARALELIZABLE dentro de su fase:
    toca archivos distintos y no depende de otra task de la misma
    fase. Sin [P] = secuencial en el orden listado.
  - Tasks bloqueadas por dependencias externas: `[D1=LIVE]` — quedan
    `blocked` en status.md con blocked_by.
  - Cada fase cierra con un CHECKPOINT: condición observable de que
    la fase está completa (tests verdes del slice, build OK, etc.).
  - Tamaño: S (< 1h), M (media jornada), L (1+ día). Una task L
    probablemente deba partirse.
-->
# Tasks: Gestión de tareas personales

> Derivado de `design.md` firmado en G2 (`0fa9a7b`). Ninguna task es `[P]`:
> T5–T8 y T10 comparten `tasks/router.py` y `tasks/service.py`.

## Fase 0 — Setup

## T1 — Scaffolding, dependencias aprobadas y toolchain [M]
- **Cubre**: — (chore; habilita todas)
- **Archivos**: `pyproject.toml`, `uv.lock`, `.python-version`, `.gitignore`, `.env.example`, `compose.yaml`, `src/greenfield/__init__.py`, `tests/__init__.py`
- **Acceptance**:
  - [x] Python 3.13 fijado; `uv sync` instala sólo las dependencias de `design.md` § *Dependencias nuevas*
  - [x] `pip-audit` sin vulnerabilidades conocidas (condición del OK de G2: si reporta alguna, parar y consultar) — 2026-09-25: "No known vulnerabilities found", 76 paquetes en `uv.lock`
  - [x] `ruff check`, `ruff format --check` y `mypy src/` en verde; `pytest` ejecuta y, con 0 tests, el umbral de cobertura (85 %) falla como se esperaba: se exige desde T2

**Checkpoint fase 0**: toolchain verde sobre el esqueleto vacío.

## Fase 1 — Foundational (bloqueante para todos los slices)

## T2 — Configuración, BD, modelo y migración 0001 [M]
- **Cubre**: R1.2, R2.2, R2.4, R2.5, R2.6 (restricciones de BD de respaldo)
- **Archivos**: `src/greenfield/config.py`, `src/greenfield/db.py`, `src/greenfield/tasks/models.py`, `migrations/`, `alembic.ini`, `tests/conftest.py`, `tests/integration/test_migrations.py`
- **Acceptance**:
  - [ ] `alembic upgrade head` y `downgrade base` corren sobre Postgres de testcontainers
  - [ ] Tests de los `CHECK` y del default de `status` (`# Derived from R2.2`, `R2.4`, `R2.5`, `R2.6`)
  - [ ] Lint + mypy limpios

## T3 — Autenticación JWT y app base [M] [D1: MOCK]
- **Cubre**: R1.1
- **Archivos**: `src/greenfield/auth.py`, `src/greenfield/main.py`, `tests/conftest.py` (emisor de tokens), `tests/integration/test_auth.py`, `tests/unit/test_auth.py`
- **Acceptance**:
  - [ ] Token ausente, mal formado, expirado, con otra `aud`/`iss`, `alg=none` o `HS256` → 401 + `WWW-Authenticate: Bearer` (`# Derived from R1.1`)
  - [ ] Token válido → `sub` disponible para los endpoints

## T4 — Errores RFC 9457 y access log [S]
- **Cubre**: R3.2, NFR2
- **Archivos**: `src/greenfield/errors.py`, `src/greenfield/access_log.py`, `src/greenfield/main.py`, `tests/unit/test_errors.py`
- **Acceptance**:
  - [ ] `NotFoundError` → 404, `RequestValidationError` → 422 con `errors[{field, message}]`, excepción no controlada → 500 genérico; todos `application/problem+json`
  - [ ] Access log con método, ruta, status, duración y `sub`, sin cuerpo

**Checkpoint fase 1**: la app arranca; una petición sin token da 401; migración aplicada en tests; cobertura ≥ 85 %.

## Fase 2 — Slice P1 (MVP)

## T5 — Crear tarea: `POST /v1/tasks` [M]
- **Cubre**: R1.2, R2.1, R2.2, R2.3, R2.4, R2.5, R2.6, R2.7, R2.8
- **Archivos**: `src/greenfield/tasks/schemas.py`, `src/greenfield/tasks/service.py`, `src/greenfield/tasks/router.py`, `tests/integration/tasks/test_create.py`, `tests/unit/tasks/test_schemas.py`
- **Acceptance**:
  - [ ] 201 + `Location`; 422 por campo en cada validación; `extra="forbid"`
  - [ ] Tests con `# Derived from R2.x` por requisito

## T6 — Consultar y listar: `GET /v1/tasks/{id}`, `GET /v1/tasks` [M]
- **Cubre**: R1.3, R1.4, R3.1, R3.2, R3.3, R3.4, R3.5, R3.6, R3.7, R3.8
- **Archivos**: `service.py`, `router.py`, `schemas.py` (`Page[T]`), `tests/integration/tasks/test_read.py`
- **Acceptance**:
  - [ ] Tarea ajena, inexistente o ID inválido → mismo 404
  - [ ] Paginación 50/1–100 con `total`; orden `created_at DESC, id DESC`; filtro por estado; listado vacío

## T7 — Actualizar: `PATCH /v1/tasks/{id}` [M]
- **Cubre**: R1.3, R4.1, R4.2, R4.3, R4.4, R4.5, R4.6, R4.7
- **Archivos**: `service.py`, `router.py`, `schemas.py` (`TaskUpdate`), `tests/integration/tasks/test_update.py`
- **Acceptance**:
  - [ ] Ausente = no cambia; `null` quita `description`/`due_date`; `null` en `title`/`status` → 422 sin cambios
  - [ ] `updated_at` avanza sólo si hay modificación; transición libre de estados; última escritura gana

## T8 — Eliminar: `DELETE /v1/tasks/{id}` [S]
- **Cubre**: R1.3, R5.1, R5.2
- **Archivos**: `service.py`, `router.py`, `tests/integration/tasks/test_delete.py`
- **Acceptance**:
  - [ ] 204; luego GET/PATCH/DELETE → 404; ID inexistente o inválido → 404

## T9 — Prueba independiente de P1 y NFR2 [S]
- **Cubre**: R1.1, R1.2, R1.3, R1.4, NFR2
- **Archivos**: `tests/integration/test_slice_p1.py`
- **Acceptance**:
  - [ ] Prueba independiente de P1 (usuarios A y B, `requirements.md` § Slices) pasa de punta a punta
  - [ ] Ningún log del recorrido contiene título, descripción ni token (`caplog`)

**Checkpoint fase 2**: P1 verde y cobertura ≥ 85 %. Desplegable a `pruebas` cuando se resuelvan el runtime y D1 (hallazgo V1).

## Fase 3 — Slice P2

## T10 — Pendientes: `GET /v1/tasks/pending` [M]
- **Cubre**: R6.1, R6.2, R6.3, R6.4, R6.5, R6.6
- **Archivos**: `service.py` (`list_pending`), `router.py`, `schemas.py` (`PendingTaskRead`), `tests/unit/tasks/test_overdue.py`, `tests/integration/tasks/test_pending.py`
- **Acceptance**:
  - [ ] Sólo `pending`/`in_progress`; orden `due_date ASC NULLS LAST, created_at, id`; `is_overdue` con `today` inyectado (UTC); `overdue=true`; paginación

## T11 — Prueba independiente de P2 [S]
- **Cubre**: R6.1, R6.2, R6.3, R6.4, R6.5, R6.6
- **Archivos**: `tests/integration/test_slice_p2.py`
- **Acceptance**:
  - [ ] Prueba independiente de P2 (`requirements.md` § Slices) pasa

**Checkpoint fase 3**: P2 verde y cobertura ≥ 85 %.

## Fase final — Polish

## T12 — Script k6 de NFR1 [S]
- **Cubre**: NFR1
- **Archivos**: `tests/load/tasks.js`, `tests/load/README.md`
- **Acceptance**:
  - [ ] Siembra 10 usuarios × 1.000 tareas; thresholds `p(95)<300` (operaciones individuales) y `p(95)<500` (listados)

## T13 — Medir NFR1 en `pruebas` [S] [D1=LIVE]
- **Cubre**: NFR1
- **Acceptance**:
  - [ ] Corrida k6 contra `pruebas` con tokens reales del IdP y thresholds en verde
