---
feature: <slug>
state: not-started
methodology_version: "<X.Y>"
updated: <YYYY-MM-DD>
updated_by: "@<user>"
# feature_flag:
#   name: <flag-name>
#   envs: { pruebas: OFF, qa: OFF, main: OFF }
---
<!--
  PLANTILLA AI-DLC — status.md (canonical: .agents/templates/spec/)
  Materializa el progreso real de la feature. Lo actualiza el Service
  Agent al cerrar cada task (/spec-implement) o el dev a mano si
  commitea fuera del flujo. Formato YAML simple parseable por
  spec-lint y /spec-status. El frontmatter va SIEMPRE primero.

  REGLAS (§6 Lifecycle):
  - `state` se DERIVA de las tasks (algoritmo §6). Si declaración y
    derivación divergen, spec-lint lo reporta como drift (W4).
  - Task `blocked` REQUIERE `blocked_by:` con causa concreta.
  - `updated` = fecha del último commit que tocó este archivo.
  - `methodology_version` = versión AI-DLC con la que se autoreó la
    spec (/spec-new la toma de `.ai-dlc-version` al root). spec-lint
    la usa para NO aplicar retroactivamente reglas posteriores
    (linteo versionado). /spec-amend y los bugs B/C que re-tocan
    requirements la suben a la versión actual — migración al re-tocar,
    nunca en bloque por un upgrade.
  - feature_flag: omitir el bloque entero si la feature no usa flag.
  - Estados de task: pending | blocked | in-progress | done |
    deployed:<env> | cancelled. Estados de feature: not-started |
    in-progress | partial-deploy-<env> | feature-complete | live |
    cancelled | legacy.
-->

# Status

## Gates

<!-- Firma por commit dedicado tipo `sign` (ver AGENTS.md § Gates).
     G2 requiere: checklist de requirements completa + 0
     OPEN_QUESTIONS abiertas + 0 [NEEDS CLARIFICATION] + design.md
     resuelto (lo produce /spec-design) + /spec-verify --pre-g2 sin
     CRITICALs. -->

| Gate | Qué firma | Estado |
|---|---|---|
| G2 — requirements + design | tech lead | pending |
| G3 — code review (por PR) | 1+ reviewer | pending |
| G4 — QA sign-off | QA | pending |
| G5 — Ops sign-off (pre-prod) | Ops + tech lead | pending |

## Tasks

T1: pending |
T2: pending |

## Dependencies snapshot

<!-- Omitir si no hay D-N. -->
D1 (<título corto>): NEGOTIATING

## Notas

- <YYYY-MM-DD>: spec creada con /spec-new.
