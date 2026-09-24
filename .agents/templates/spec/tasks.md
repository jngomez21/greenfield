<!--
  PLANTILLA AI-DLC — tasks.md (canonical: .agents/templates/spec/)
  Se llena DESPUÉS de que design.md esté firmado. Es el desglose
  ejecutable que /spec-implement recorre.

  GUARDRAILS de derivación:
  - Organizar por FASES: Setup → Foundational (bloqueante) → una fase
    por slice (P1, P2... de requirements.md) → Polish. Implementar
    sólo Setup + Foundational + P1 debe dar algo desplegable a
    `pruebas` (MVP — alimenta partial-deploy, §3.10).
  - Cada task cita los R*.* que cubre y las D-N de las que depende
    (`[R4.1, D2]`). Una task sin R*.* es sospechosa (¿es chore?).
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
# Tasks: <Feature>

## Fase 0 — Setup

## T1 — <preparación: scaffolding, config, deps aprobadas> [S]
- **Cubre**: —
- **Archivos**: <paths>
- **Acceptance**:
  - [ ] <criterio observable>

**Checkpoint fase 0**: <ej. el proyecto compila con la estructura nueva>

## Fase 1 — Foundational (bloqueante para todos los slices)

<!-- Sólo lo que TODOS los slices necesitan: schema base, auth,
     routing. Si un solo slice lo usa, va en la fase de ese slice. -->

## T2 — <infraestructura común> [M]
- **Cubre**: R1.1
- **Archivos**: <paths>
- **Acceptance**:
  - [ ] Tests passing (`// Derived from R1.1`)
  - [ ] Lint clean

**Checkpoint fase 1**: <condición>

## Fase 2 — Slice P1 (MVP)

## T3 — <task> [M] [P]
- **Cubre**: R1.2
- **Archivos**: <paths — distintos de T4 para que [P] sea válido>
- **Acceptance**:
  - [ ] Tests passing (`// Derived from R1.2`)

## T4 — <task> [M] [P]
- **Cubre**: R2.1
- **Archivos**: <paths>
- **Acceptance**:
  - [ ] <criterio>

## T5 — <integración del slice> [S]
- **Cubre**: R1.*, R2.*
- **Acceptance**:
  - [ ] Prueba independiente de P1 (de requirements.md) pasa end-to-end

**Checkpoint fase 2**: P1 desplegable a `pruebas` por sí solo —
candidato a primera promoción (`/spec-promote --to pruebas`).

## Fase 3 — Slice P2

## T6 — <task> [M] [R3.1, D1]
...

## T7 — <integración real con D1> [M] [D1=LIVE]
<!-- queda blocked en status.md: blocked_by: D1=LIVE -->

**Checkpoint fase 3**: <prueba independiente de P2>

## Fase final — Polish

## T8 — <docs, hardening, limpieza de mocks, performance> [S]
- **Cubre**: NFR1
- **Acceptance**:
  - [ ] <criterio>
