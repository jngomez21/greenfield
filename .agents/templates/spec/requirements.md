---
feature: <slug>
modality: code                  # code | config-only | data-migration | catalog-only | docs-only | refactor-only (§6)
initiative: NONE                # opcional — slug/URL sólo si pertenece a una Initiative
owner: <team-o-@persona>
status: draft                   # draft | in-review | approved | in-implementation | done
                                # Quién produce cada transición:
                                #   draft            /spec-new
                                #   in-review        el owner, al pedir revisión de la spec
                                #   approved         firma de G2 (commit `sign`)
                                #   in-implementation  /spec-implement, en su primera task
                                #   done             firma de G5 (§6 Lifecycle)
# work_items:                   # opcional — sólo si repo-config.yaml declara tracker (§13)
#   feature_id: <id-owner>
---
<!--
  PLANTILLA AI-DLC — requirements.md (canonical: .agents/templates/spec/)
  El Service Agent la copia a specs/<feature>/requirements.md durante
  /spec-new y la llena con la entrevista. Las notas en comentarios HTML
  son guardrails para el agente: se CONSERVAN en la spec generada (no
  renderizan y guían amendments futuros). El frontmatter YAML va
  SIEMPRE primero en el archivo (los parsers lo exigen).

  GUARDRAILS (obligatorios al llenar):
  - ✅ QUÉ necesita el usuario y POR QUÉ. ❌ CÓMO se implementa
    (nada de stack, librerías, endpoints internos, estructura de
    código — eso va en design.md).
  - Una acción por requirement. Si tiene "y", dividirlo.
  - NFRs medibles: "rápido" ❌ → "p99 < 500ms" ✅.
  - Casos negativos explícitos (qué hacer ante error/abuso/límite).
  - Cada R*.* debe ser TESTEABLE y NO AMBIGUO: si no puedes escribir
    un test que lo verifique, o admite dos interpretaciones razonables,
    reescribirlo o marcarlo.
  - Ambigüedad: marcar inline con [NEEDS CLARIFICATION: <pregunta
    concreta + opciones>]. MÁXIMO 3 en toda la spec — si necesitas
    más, la captura de intención fue insuficiente: volver a conversar
    con el dev antes de seguir. /spec-clarify los resuelve.
  - NO inventar: lo que no se sabe se marca, no se asume (§3.12).
-->

# Feature: <Nombre>

> *(Opcional)* Parte de [Initiative: <name>](<url>) — omitir si es self-contained.

## Contexto

<!-- Por qué existe esta feature: problema, usuario primario, valor. -->

## Stakeholders

- <PM>
- <Tech lead>
- <Compliance/Legal — si aplica>

## Métricas de éxito

<!-- Medibles y agnósticas de tecnología, verificables sin leer código.
     ✅ "el usuario completa el flujo en < 2 min", "tasa de error < 0.5%"
     ❌ "la API responde 200", "el componente usa cache" -->
- <KPI 1>
- <KPI 2>

## Slices priorizados

<!-- Partir la feature en rebanadas INDEPENDIENTES por prioridad.
     P1 = el MVP: lo mínimo que entrega valor observable y es
     desplegable solo (alimenta partial-deploy, §3.10). P2/P3 son
     aditivos — no pueden ser prerequisito de P1.
     Cada slice declara cómo se prueba SIN las demás. Las tasks de
     tasks.md se organizan por slice. -->

### P1 — <nombre del slice> (MVP)
- **Por qué esta prioridad**: <valor que entrega solo>
- **Prueba independiente**: <cómo se valida sin P2/P3>
- **Cubre**: R1.*, R2.*

### P2 — <nombre del slice>
- **Por qué esta prioridad**: <...>
- **Prueba independiente**: <...>
- **Cubre**: R3.*

## Requisitos funcionales

<!-- EARS (§5): WHEN / WHILE / WHERE / IF-THEN / THE SYSTEM SHALL.
     Numeración estable R<grupo>.<n> — nunca renumerar; las R*.* se
     citan en commits, tests y PRs. Cada R*.* declara `Tests:` con
     niveles: unit | integration | e2e | contract | load |
     accessibility | security | none (este último con justificación). -->

### R1 — <Categoría> [P1]

**R1.1** WHEN <trigger>, THE SYSTEM SHALL <acción observable>.
         Tests: unit, integration

**R1.2** IF <condición de error>, THEN THE SYSTEM SHALL <manejo>.
         Tests: unit

### R2 — <Categoría> [P1]

...

## Requisitos no funcionales

**NFR1** THE SYSTEM SHALL <atributo medible> (<umbral, ej. p99 < 500ms>).
         Tests: load

## Dependencies

<!-- Omitir si no hay dependencias externas. Formato D-N (§6):
     todo lo que la feature necesita y aún no existe. -->

### D1 — <título corto>
- **Tipo**: humana | técnica | externa | disciplina
- **Estado**: NEGOTIATING | AGREED | IMPLEMENTED | LIVE
- **Contrato**: <path/URL versionado — con `id` Y `version`>
- **Owner**: <equipo o disciplina> / <@persona>
- **Tracking**: <URL al work item del proveedor — si aplica>
- **ETA**: <informativo>
- **Implementability**: <sólo si Tipo = disciplina y Estado ∈ {AGREED,
  IMPLEMENTED}: confirmado <YYYY-MM-DD> por @<usuario> — salvedades:
  <...>. Un contrato `derived: true` NO lleva este campo: nunca pasa
  por el implementability check (§16)>
- **Estrategia**: MOCK | BLOCK | PIN | WORKAROUND | NONE
  <!-- NONE = la dependencia ya está LIVE al declararse (contrato
       `derived: true` de brownfield). Sin mock y sin Ready to unmock. -->
- **Mock**: `mocks/<nombre>.mock.<ext>` <!-- si aplica: un contrato de
  diseño puede mockearse con un placeholder o un wireframe, sin archivo -->
- **Ready to unmock**: <condición observable>

<!-- CONDICIONAL — el tipo `disciplina` y el campo `Implementability`
     dependen de `disciplines` en repo-config.yaml. Si el repo NO la
     declara, **borrar de esta plantilla** el valor `disciplina` de la
     enumeración de `Tipo`, la línea `Implementability` y este bloque
     de guardrail: una feature de un repo sin disciplinas no debe ver
     ninguno de los tres (§17 *métrica de control*).

     `Tipo: disciplina` (v0.27) = algo vinculante que produce otra
     disciplina: diseño (`DS-*`/`DC-*`/`DF-*`), cumplimiento (`POL-*`),
     operaciones, datos. Ver §6 *Dependencias de otras disciplinas*.
     IMPORTANTE: declararla con este tipo es lo que activa la sección
     condicional del checklist de esa disciplina. Si se escribe
     `técnica` para un contrato de diseño, el gate de diseño
     desaparece en silencio. -->

## Fuera de scope

<!-- Explícito: lo que alguien podría asumir que entra y NO entra. -->
- <X>

## Dependencias internas

<!-- Opcional: otras features de este repo. -->
- Depende de: <feature>
- Bloquea: <feature>

## Clarifications

<!-- Registro persistente de decisiones que cambiaron la spec. NO
     borrar entradas — son la memoria de por qué la spec dice lo que
     dice. Dos orígenes:
       - /spec-clarify: sesión de preguntas estructuradas.
       - /contract-new: R*.* que aparecieron al escribir un contrato de
         disciplina. CONDICIONAL — si repo-config.yaml no declara
         `disciplines`, BORRAR estas tres líneas al generar la spec.
         Si la declara: encabezar la sesión con el `id` del contrato.
     Formato por sesión: -->

### Session <YYYY-MM-DD>
- Q: <pregunta> → A: <respuesta final>

## OPEN_QUESTIONS

<!-- Preguntas que NO se pudieron resolver en la sesión. Toda entrada
     abierta BLOQUEA el gate G2 (status no puede pasar a approved), y
     también PARA `/spec-design`.

     Por eso, antes de dejar una aquí: ¿es una pregunta o es una `D-N`?
     Si ya sabes QUÉ construir y lo que falta es CON QUÉ, va a
     `Dependencies` con su estrategia, no aquí — y si está en las dos
     listas, ciérrala aquí citando su `D-N`. Ver §6 *Una `D-N` y una
     `OPEN_QUESTION` no son lo mismo*.
     owner y due son obligatorios — spec-lint lo verifica.

     Formato, UNA sola línea por pregunta:

         - [ ] <pregunta> — owner: @<persona>, due: <YYYY-MM-DD>

     El ejemplo vive dentro de este comentario a propósito. Fuera de él
     sería una pregunta abierta de verdad: `spec-lint` la contaría y
     [E8] bloquearía la spec al llegar a `approved`, sin que nadie la
     haya escrito. Una spec recién creada tiene CERO preguntas
     abiertas, y esta sección arranca vacía. -->
