# specs/

> Cada feature de este repo vive en `specs/<feature-slug>/` y sigue la
> estructura del methodology AI-DLC (§6).
>
> Crea una feature con `/spec-new <slug>` — el Service Agent genera la
> estructura completa (desde las plantillas de `.agents/templates/spec/`)
> con entrevista guiada. Después: `/spec-clarify` para resolver
> ambigüedades, `/spec-design` para llenar `design.md` —requisito de
> G2— y la firma G2 antes de implementar.

## Estructura de una feature

```
specs/<feature-slug>/
├── requirements.md     ← EARS R1.1..R*.* + slices P1/P2/P3 + Dependencies
│                          + Tests strategy + ## Clarifications + OPEN_QUESTIONS
├── design.md           ← arquitectura, contratos, decisiones (DEC-N),
│                          complejidad justificada
├── tasks.md            ← fases Setup → Foundational → P1 → P2 → … → Polish,
│                          [P] paralelizables, checkpoints
├── status.md           ← state + tabla Gates + lifecycle + commit hashes
├── checklists/
│   └── requirements.md ← "unit tests del requirements" — G2 exige todo [x]
├── bugs.md             ← BUG-NNN (taxonomía A/B/C/D/E)
├── amendments.md       ← AMD-NNN (cambios post-aprobación) + HANDOFF-NNN
├── rollout-plan.md     ← fases de despliegue (canary → 50% → 100%)
└── mocks/              ← mocks de servicios externos, opcional
```

## Convenciones obligatorias (§5 + §6 del methodology)

- Requirements **siempre** en formato EARS.
- Cada `R*.*` declara su nivel de test (`Tests: unit, integration` etc.).
- Ambigüedad: máx 3 marcadores `[NEEDS CLARIFICATION]` inline;
  `OPEN_QUESTIONS` con `owner:` y `due:`. Ambos en 0 para firmar G2.
- Cada test cita su requirement con `// Derived from R*.*`.
- Cada commit cita su `R*.*` (y su work item si hay tracker):
  `feat(scope): T<n> - <desc> [R<x>.<y>] AB#<wi-id>`.
- Tasks **no** se ejecutan fuera de orden; las bloqueadas se resuelven
  primero (o se justifican explícitamente con `blocked_by:`).
- Cambios post-aprobación van por `/spec-amend`, NO por edición directa.
- `scripts/spec-lint.{sh,ps1}` valida lo mecánico — correrlo antes de
  commitear cambios a specs.

## Lifecycle

Estados de feature (`state:` en `status.md`, §6 del methodology):
`not-started | in-progress | partial-deploy-<env> | feature-complete |
live | cancelled | legacy`. El estado se **deriva** de las tasks
(algoritmo §6 — implementado en `spec-lint`, warning W4 si hay drift).

Estados de task: `pending | blocked | in-progress | done |
deployed:<env> | cancelled`.

Ver §6 del methodology *Lifecycle de feature y task*.
