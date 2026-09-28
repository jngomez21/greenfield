# greenfield

Servicio de gestión de tareas personales (API HTTP). Metodología AI-DLC: ver `AGENTS.md`;
spec activa en `specs/gestion-tareas/`.

## Desarrollo local

Requisitos: [uv](https://docs.astral.sh/uv/) (instala Python 3.13 solo) y los binarios de
PostgreSQL 18 en `C:\Program Files\PostgreSQL\18\bin`.

### Arrancar la base de datos (después de cada reinicio del equipo)

En una ventana de PowerShell propia (no hace falta ser administrador), y dejarla abierta:

```powershell
& "C:\Program Files\PostgreSQL\18\bin\pg_ctl.exe" start -D "$env:LOCALAPPDATA\greenfield\pgdata" -l "$env:LOCALAPPDATA\greenfield\pg.log"
```

Debe terminar en `servidor iniciado`. Para detenerla: el mismo comando con `stop` en lugar de
`start` (sin `-l ...`).

### Configuración

Copiar `.env.example` a `.env` y completar las claves. `.env` nunca se commitea.
`TEST_DATABASE_URL` debe apuntar a una base cuyo nombre termine en `_test`: las pruebas la vacían.

### Comandos

```powershell
uv sync                 # dependencias
uv run pytest           # pruebas + cobertura (umbral 85 %)
uv run ruff check       # lint
uv run ruff format      # formato
uv run mypy             # tipos
uv run pip-audit        # vulnerabilidades conocidas
```

Para levantar el servicio a mano: `uv run uvicorn greenfield.main:app --env-file .env`
(requiere las variables `AUTH_*` de Keycloak; ver `docs/keycloak.md`).

## Despliegue (Render)

Proyecto de práctica desplegado en [Render](https://render.com) (AMD-002). Todo está
declarado en `render.yaml`: el servicio `greenfield-pruebas` (rama `pruebas`, construido
desde el `Dockerfile`) y su base PostgreSQL `greenfield-pruebas-db`.

1. Configurar Keycloak siguiendo `docs/keycloak.md` y anotar el *issuer*.
2. En Render: **New → Blueprint**, conectar el repositorio de GitHub y elegir la rama
   `pruebas`. Render lee `render.yaml` y propone crear el servicio y la base.
3. Cuando lo pida, cargar `AUTH_ISSUER` y `AUTH_JWKS_URL` (las demás variables vienen del
   Blueprint; `DATABASE_URL` la inyecta Render).
4. Render despliega en cada push a `pruebas` una vez que la CI de GitHub pasa. Al arrancar,
   el contenedor aplica las migraciones y luego levanta `uvicorn`.
5. Verificar: `GET https://<servicio>.onrender.com/health` → `{"status":"ok"}`.

Los nombres de campos de `render.yaml` siguen la documentación de Render de 2026-09; si el
Blueprint marca alguno como inválido, compararlo con la referencia actual de Render.
