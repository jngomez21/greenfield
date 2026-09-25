# Testing

> **Servicio**: `greenfield`
> **Estado**: completo (bootstrap 2026-09-25)

## Niveles obligatorios

- **Unit**: reglas de negocio de `service` sin BD cuando la lógica lo permita
  (validaciones, transiciones de estado, cálculo de vencimiento).
- **Integration**: cada endpoint vía `TestClient` contra **PostgreSQL real**
  (la base indicada en `TEST_DATABASE_URL`), con auth incluida (tokens firmados en la fixture).
  Es el nivel principal para un CRUD.
- **Sin e2e ni load** por ahora: no hay UI y no hay NFR de carga. Si un `R*.*`
  declara una NFR medible de rendimiento, se agrega el nivel correspondiente.

Cada `R*.*` declara en `requirements.md` qué nivel lo cubre.

## Cobertura mínima

- **≥ 85 % de líneas** sobre `src/` (`pytest --cov=greenfield --cov-fail-under=85`).
- **100 % de los `R*.*`** con al menos un test que los cite (lo verifica `/spec-verify`).
- Exclusiones permitidas: `main.py` (wiring) y `migrations/`. Nada más.

## Frameworks

- `pytest`, `pytest-cov`.
- `fastapi.testclient.TestClient` (usa `httpx`).
- PostgreSQL 18 real vía `TEST_DATABASE_URL` (sin contenedores, AMD-001). La fixture aplica las
  migraciones al inicio y vacía las tablas entre tests. **Se niega a correr si el nombre de la base
  no termina en `_test`**: protege contra vaciar una base con datos reales por error de configuración.

## Convención `# Derived from R*.*`

Cada test declara el `R*.*` que cubre en un comentario justo antes del `def`:

```python
# Derived from R1.2 (título obligatorio)
def test_crear_tarea_sin_titulo_devuelve_422(client, auth_headers): ...
```

Esto permite a `/spec-verify` cruzar tests ↔ requirements y detectar tests
huérfanos (sin `R*.*` válido tras un amendment) o `R*.*` sin cobertura.

## Política de mocks

- **BD propia: nunca se mockea** → PostgreSQL real de `TEST_DATABASE_URL`.
- **IdP: no se llama en tests** → par de llaves generado por la fixture y JWKS
  servido localmente o inyectado vía `dependency_overrides`.
- Terceros futuros (si aparecen como `D-N`): doble explícito con la regla
  *Ready to unmock* (§6 del methodology).

## Estructura de archivos

```
tests/
├── conftest.py
├── unit/<modulo>/test_<tema>.py
└── integration/<modulo>/test_<endpoint>.py
```

Nombres de test descriptivos en español: `test_<accion>_<condicion>_<resultado>`.

## TDD vs test-after

**Tests primero** para reglas de negocio y para cada `R*.*` de comportamiento
(es el default de `/spec-implement`). Test-after aceptable para wiring
(`main.py`, `config.py`, `db.py`).

## CI gates de tests

- En cada PR: `ruff check`, `ruff format --check`, `mypy src/`,
  `pytest` (unit + integration) con el umbral de cobertura y `pip-audit`.
- La promoción a `pruebas`/`qa`/`main` exige esos mismos checks en verde más los
  gates de `repo-config.yaml > environments[].gate`.
- El proveedor de CI (GitHub Actions / Azure Pipelines) se decide junto con el
  deploy target.
