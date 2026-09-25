# Amendments: gestion-tareas

## AMD-001 — Pruebas contra PostgreSQL 18 local en lugar de testcontainers (2026-09-25)
- Motivo: el proxy corporativo (`wsaprd.syc.loc:3128`) responde `407 Proxy Authentication Required` al descargar capas de imágenes de Docker Hub, así que testcontainers no puede levantar PostgreSQL. El dev ya tiene PostgreSQL 18.6 instalado como servicio de Windows. Fuente: restricción de infraestructura (red corporativa), detectada al arrancar T2.
- Decisiones: (1) las pruebas de integración usan la base de `TEST_DATABASE_URL`, que debe terminar en `_test`; la fixture aplica migraciones y vacía tablas entre tests. (2) el stack sube de PostgreSQL 17 a 18 para usar la misma versión en desarrollo, pruebas y despliegue (nada desplegado todavía; el diseño no usa nada exclusivo de la 17). (3) se retiran `testcontainers` y `compose.yaml`.
- Autor: @jngomez21 vía Service Agent.
- R*.* afectadas: ninguna (el comportamiento del servicio no cambia).
- Artefactos cambiados: `stack/tech-stack.md`, `stack/testing.md`, `stack/architecture.md`, `design.md` (§ Arquitectura, Componentes, Dependencias nuevas, Despliegue, Configuración), `pyproject.toml`/`uv.lock`, `.env.example`.
- Tasks afectadas: T1 (`done`; sus artefactos `compose.yaml` y `testcontainers` se retiran aquí), T2 (fixture y acceptance modificados).
- PR de spec: — (rama `feat/gestion-tareas`, aún sin PR)
- PR de implementación: —
