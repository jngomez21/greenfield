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
