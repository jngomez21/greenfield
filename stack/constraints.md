# Constraints

> **Servicio**: `greenfield`
> **Estado**: completo (bootstrap 2026-09-25)

> Lo que está **prohibido o desaconsejado** en este repo. Anti-patrones
> específicos del proyecto. Cada constraint con justificación corta
> (sin "porque sí" — siempre hay una razón concreta).

## Librerías / dependencias prohibidas

- **`python-jose`**: sin mantenimiento activo y con CVEs históricos. Usar PyJWT.
- **`passlib` / hashing de contraseñas propio**: el servicio no gestiona
  contraseñas (auth delegada al IdP, `stack/security.md`).
- **Otro ORM u otro gestor de paquetes** (Tortoise, Peewee, poetry, pip-tools):
  duplican lo que ya hacen SQLAlchemy y uv.
- Toda dependencia nueva requiere OK explícito (AGENTS.md § *Dependencias nuevas*).

## Patterns desaconsejados

- **SQL armado concatenando strings**: siempre el ORM o `text()` con parámetros
  bind. Evita inyección SQL.
- **Devolver modelos ORM como respuesta**: siempre un schema `*Read`. Evita
  filtrar columnas internas (`owner_sub`).
- **Queries a recursos de usuario sin filtrar por `owner_sub`**: es un fallo de
  autorización (IDOR).
- **`datetime.now()` / `utcnow()` sin zona**: usar `datetime.now(UTC)`. Los
  naive rompen las comparaciones de fechas límite.
- **`except Exception: pass`** o tragarse errores sin loguear ni relanzar.
- **Repository/interfaces con una sola implementación**: ver
  `stack/architecture.md`.

## Cosas que NO se deben hacer

- `git push --force` a `main`, `qa` o `pruebas`.
- Deshabilitar o marcar `skip` tests para que pase CI.
- `--no-verify` en commits.
- Editar una migración de Alembic ya mergeada: se crea una nueva.
- Commitear `.env` o credenciales.

## Restricciones de runtime / infra

- La configuración entra sólo por variables de entorno (12-factor): nada de
  valores por ambiente hardcodeados.
- El servicio no guarda estado en memoria entre requests (debe poder escalar
  horizontalmente).

## Anti-patrones del methodology aplicados aquí

- **Código antes de G2**: no se escribe código de producción sin requirements +
  design firmados.
- **Lógica improvisada**: si la spec es ambigua, se para y se pregunta (§3.12).
