---
feature: gestion-tareas
state: in-progress
methodology_version: "0.170"
updated: 2026-09-25
updated_by: "@jngomez21"
---
<!--
  PLANTILLA AI-DLC â€” status.md (canonical: .agents/templates/spec/)
  Materializa el progreso real de la feature. Lo actualiza el Service
  Agent al cerrar cada task (/spec-implement) o el dev a mano si
  commitea fuera del flujo. Formato YAML simple parseable por
  spec-lint y /spec-status. El frontmatter va SIEMPRE primero.

  REGLAS (Â§6 Lifecycle):
  - `state` se DERIVA de las tasks (algoritmo Â§6). Si declaraciÃ³n y
    derivaciÃ³n divergen, spec-lint lo reporta como drift (W4).
  - Task `blocked` REQUIERE `blocked_by:` con causa concreta.
  - `updated` = fecha del Ãºltimo commit que tocÃ³ este archivo.
  - `methodology_version` = versiÃ³n AI-DLC con la que se autoreÃ³ la
    spec (/spec-new la toma de `.ai-dlc-version` al root). spec-lint
    la usa para NO aplicar retroactivamente reglas posteriores
    (linteo versionado). /spec-amend y los bugs B/C que re-tocan
    requirements la suben a la versiÃ³n actual â€” migraciÃ³n al re-tocar,
    nunca en bloque por un upgrade.
  - feature_flag: omitir el bloque entero si la feature no usa flag.
  - Estados de task: pending | blocked | in-progress | done |
    deployed:<env> | cancelled. Estados de feature: not-started |
    in-progress | partial-deploy-<env> | feature-complete | live |
    cancelled | legacy.
-->

# Status

## Gates

<!-- Firma por commit dedicado tipo `sign` (ver AGENTS.md Â§ Gates).
     G2 requiere: checklist de requirements completa + 0
     OPEN_QUESTIONS abiertas + 0 [NEEDS CLARIFICATION] + design.md
     resuelto (lo produce /spec-design) + /spec-verify --pre-g2 sin
     CRITICALs. -->

| Gate | QuÃ© firma | Estado |
|---|---|---|
| G2 â€” requirements + design | tech lead | âœ… signed 2026-09-25 by jngomez@syc.com.co (commit d0007d9) |
| G3 â€” code review (por PR) | 1+ reviewer | pending |
| G4 â€” QA sign-off | QA | pending |
| G5 â€” Ops sign-off (pre-prod) | Ops + tech lead | pending |

## Tasks

T1: done | commit c4c8c38 | 2026-09-25
T2: done | commit 31b86e0 | 2026-09-25
T3: done | commit f6ae361 | 2026-09-25
T4: done | commit 142f9c6 | 2026-09-25
T5: pending |
T6: pending |
T7: pending |
T8: pending |
T9: pending |
T10: pending |
T11: pending |
T12: pending |
T13: blocked | blocked_by: D1=LIVE y runtime de `pruebas` sin decidir (hallazgo V1)

## Dependencies snapshot

D1 (Proveedor de identidad OIDC): NEGOTIATING

## Notas

- 2026-09-25: spec creada con /spec-new en `feat/gestion-tareas` (base `pruebas`). Quedan 2 `[NEEDS CLARIFICATION]` (paginaciÃ³n del listado, zona horaria de "hoy") para `/spec-clarify`. `tasks.md` no se crea todavÃ­a: vacÃ­o dispara `[E10]` en spec-lint v0.170 (contradice a `/spec-new`); lo deriva `/spec-implement` tras G2.
- 2026-09-25: `/spec-clarify` (UTC, paginaciÃ³n, Ãºltima escritura gana, supuestos confirmados) y `/spec-design` (API `/v1` en inglÃ©s, tabla `tasks`, JWT, k6). `/spec-verify --pre-g2`: 0 CRITICAL, 0 HIGH; V2 y V3 aplicados, V1 (runtime sin decidir) aceptado como bloqueante de `/spec-promote`, no de implementaciÃ³n.
- 2026-09-25: **G2 firmado** por jngomez@syc.com.co sobre `d0007d9` (self-approval: dev y tech lead son la misma persona). Dependencias nuevas de `design.md` Â§ *Dependencias nuevas* aprobadas **con condiciÃ³n**: `pip-audit` sin vulnerabilidades conocidas. Si aparece alguna, se para y se consulta antes de continuar.
- 2026-09-25: fase 0 cerrada (T1). `pip-audit`: sin vulnerabilidades conocidas (76 paquetes); condiciÃ³n del OK de dependencias cumplida. `cryptography/cobblestone.py` revisado: idÃ©ntico al de `pyca/cryptography` upstream (mÃ³dulo legÃ­timo de la v50). Pendiente para T2: motor de contenedores para testcontainers (la instalaciÃ³n de Podman por winget terminÃ³ con 1602, cancelada).
- 2026-09-25: Podman 6.0.2 quedÃ³ operativo (mÃ¡quina `podman-machine-default`), pero el proxy corporativo responde 407 al bajar imÃ¡genes de Docker Hub. **AMD-001**: pruebas contra PostgreSQL 18 local (`TEST_DATABASE_URL`, base `*_test`) y stack a PostgreSQL 18; se retiran testcontainers y `compose.yaml`. Ver `amendments.md`. T2 espera a que el dev cree el rol y las bases en pgAdmin.
- 2026-09-25: fase 1 cerrada (T2â€“T4). 43 tests en verde, cobertura 99 %, ruff y mypy limpios. Pendientes seÃ±alados: (a) los `message` por campo de los 422 salen en inglÃ©s (texto de Pydantic), el resto de mensajes de error en espaÃ±ol; (b) Starlette sugiere `httpx2` para `TestClient` (aviso, no error; serÃ­a dependencia nueva); (c) con `AUTH_*` vacÃ­as en `.env` la app no arranca a mano hasta configurar D1 (diseÃ±o: falla al arrancar sin configuraciÃ³n).
