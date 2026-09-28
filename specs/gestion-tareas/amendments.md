# Amendments: gestion-tareas

## AMD-001 — Pruebas contra PostgreSQL 18 local en lugar de testcontainers (2026-09-25)
- Motivo: el proxy corporativo (`wsaprd.syc.loc:3128`) responde `407 Proxy Authentication Required` al descargar capas de imágenes de Docker Hub, así que testcontainers no puede levantar PostgreSQL. El dev ya tiene PostgreSQL 18.6 instalado como servicio de Windows. Fuente: restricción de infraestructura (red corporativa), detectada al arrancar T2.
- Decisiones: (1) las pruebas de integración usan la base de `TEST_DATABASE_URL`, que debe terminar en `_test`; la fixture aplica migraciones y vacía tablas entre tests. (2) el stack sube de PostgreSQL 17 a 18 para usar la misma versión en desarrollo, pruebas y despliegue (nada desplegado todavía; el diseño no usa nada exclusivo de la 17). (3) se retiran `testcontainers` y `compose.yaml`.
- Autor: @jngomez21 vía Service Agent.
- R*.* afectadas: ninguna (el comportamiento del servicio no cambia).
- Artefactos cambiados: `stack/tech-stack.md`, `stack/testing.md`, `stack/architecture.md`, `design.md` (§ Arquitectura, Componentes, Dependencias nuevas, Despliegue, Configuración), `pyproject.toml`/`uv.lock`, `.env.example`.
- Tasks afectadas: T1 (`done`; sus artefactos `compose.yaml` y `testcontainers` se retiran aquí), T2 (fixture y acceptance modificados).
- Actualización 2026-09-25: se desconoce la clave del superusuario del servidor instalado y el usuario de Windows no es administrador (no se puede restablecer). Se usa una **instancia propia** creada con los mismos binarios de PostgreSQL 18.6 (`%LOCALAPPDATA%\greenfield\pgdata`, puerto 5433), arrancada por el dev con `pg_ctl`. Rol `greenfield` sin superusuario, dueño de `greenfield` y `greenfield_test`. Claves generadas al azar: la de la app sólo en `.env`; la del superusuario local en `%LOCALAPPDATA%\greenfield\admin-password.txt`.
- PR de spec: #1 (fusionada en `pruebas`, `d545bf0`)
- PR de implementación: #1

## AMD-002 — Runtime Render + Keycloak gestionado como IdP (2026-09-28)
- Motivo: resolver el hallazgo V1 (runtime sin decidir) y concretar D1 para poder desplegar en `pruebas`, correr T13 y avanzar a G4/G5. El proyecto es **de práctica**: se despliega pero no tendrá usuarios reales. Fuente: decisión del dev (negocio/alcance).
- Decisiones (DEC-12, DEC-13): (1) runtime **Render**, servicio web desde `Dockerfile`, Blueprint `render.yaml`, por ahora sólo el ambiente `pruebas`; (2) base **PostgreSQL de Render** (plan gratuito; que caduque es aceptable); (3) IdP **Keycloak gestionado** con plan gratuito (realm `greenfield`, cliente `greenfield-api` con *audience mapper*); (4) migraciones en el arranque del contenedor; (5) CI en GitHub Actions como gate del despliegue.
- Autor: @jngomez21 vía Service Agent. Alcance aprobado por el dev el 2026-09-28.
- R*.* afectadas: ninguna (el comportamiento del servicio no cambia). D1: `NEGOTIATING` → `AGREED`.
- Artefactos cambiados: `design.md` (§ Componentes, Decisiones DEC-12/DEC-13, Despliegue, Configuración), `requirements.md` (D1), `repo-config.yaml` (`runtime`), `stack/tech-stack.md`, `stack/security.md`.
- Tasks afectadas: nuevas T14 (`/health` + `DATABASE_URL` de Render), T15 (`Dockerfile` + `render.yaml`), T16 (CI), T17 (guía de Keycloak). T13 sigue bloqueada hasta que el despliegue y D1 estén vivos.
- PR de spec: — (rama `feat/gestion-tareas`)
- PR de implementación: —
