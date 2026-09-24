# `.agents/templates/` — plantillas de artefactos AI-DLC

Plantillas que los slash commands copian y llenan. Son territorio
AI-DLC (`role: owned` en el manifiesto `.ai-dlc-version`): el
`--upgrade` las reemplaza con la versión nueva del methodology. Lo que
el equipo llena vive en `specs/<feature>/` (`role: user`, nunca tocado).

| Plantilla | La usa | Destino |
|---|---|---|
| `spec/requirements.md` | `/spec-new` | `specs/<feature>/requirements.md` |
| `spec/design.md` | `/spec-new` (esqueleto; se llena tras aprobar requirements) | `specs/<feature>/design.md` |
| `spec/tasks.md` | `/spec-new` (vacío hasta firmar design) | `specs/<feature>/tasks.md` |
| `spec/status.md` | `/spec-new` | `specs/<feature>/status.md` |
| `spec/checklist-requirements.md` | `/spec-new` (la adapta a la feature) | `specs/<feature>/checklists/requirements.md` |

Los comentarios HTML dentro de cada plantilla son **guardrails para el
agente** — instrucciones de llenado y reglas de calidad. Se conservan
en los archivos generados (no renderizan en markdown y guían
amendments futuros).

**No editar las plantillas para una feature puntual** — se editan vía
PR al template AI-DLC (o entre adopciones, aceptando divergencia que
`--upgrade` reportará). Para necesidades de una sola feature, el
agente adapta el contenido *generado*, no la plantilla.
