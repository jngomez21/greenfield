# Patterns

> **Servicio**: `greenfield`
> **Estado**: completo (bootstrap 2026-09-25)

## Naming

### Archivos

`snake_case.py` (PEP 8).

### Funciones / métodos

`snake_case`.

### Clases / tipos / interfaces

`PascalCase`, sin prefijos (`Task`, `TaskCreate`, `TaskRead`). Los schemas
Pydantic llevan el sufijo del uso: `<Entidad>Create`, `<Entidad>Update`,
`<Entidad>Read`.

### Variables / constantes

`snake_case`; constantes de módulo en `UPPER_SNAKE_CASE`.

### API HTTP

- Recursos en plural y kebab-case: `/tasks`, `/tasks/{task_id}`.
- Campos JSON en `snake_case`.
- Fechas y horas en ISO 8601. Los instantes (`created_at`, …) siempre en UTC y
  con zona horaria (`timestamptz` en BD, `datetime` aware en Python).
- IDs: UUID.

## Imports

Absolutos desde el paquete (`from greenfield.tasks import service`). Orden y
agrupado automáticos con `ruff` (regla `I`).

## Convención de commits

Sin tracker (`repo-config.yaml > trackers: []`):

```
<type>(greenfield): T<n> - <desc> [R<x>.<y>]
```

`type` ∈ `feat`, `fix`, `test`, `refactor`, `docs`, `chore`, `spec`, `sign`.
Los commits que no implementan una task (bootstrap, tooling) omiten `T<n>` y
los `R*.*`. Mensajes en español neutro.

## Branching

Viene de `repo-config.yaml > environments` + `promotion_path`
(`pruebas → qa → main`). Rama por feature `feat/<slug>` (worktree por feature,
§6 del methodology). Sin `push --force` a ramas de ambiente.

## Organización de tests

Directorio aparte `tests/` (ver `stack/testing.md`), archivos `test_*.py`, y
cada test lleva `# Derived from R<x>.<y>` en la línea anterior a su `def`.

## Logging

- `logging` de la stdlib, a stdout. Niveles: `DEBUG` (sólo local), `INFO`
  (arranque, requests), `WARNING`, `ERROR` (excepciones no manejadas).
- Formato texto en local; JSON cuando se defina el deploy target.
- **No se loguea**: tokens, headers `Authorization`, ni el contenido de las
  entidades de usuario (títulos o descripciones de tareas). Sí se permiten IDs
  (`task_id`, `sub`).

## Error reporting

N/A hasta que se defina el deploy target: los errores no manejados se loguean
en `ERROR` con stack trace. La herramienta (Sentry, App Insights, …) se decide
junto con el runtime.
