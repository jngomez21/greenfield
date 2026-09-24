---
name: spec-design
description: Llenar design.md desde requirements aprobados — el paso de Fase 3 que habilita firmar G2
argument-hint: <slug>
model-class: redaccion   # design.md desde requirements sin ambiguedad
---

# `/spec-design <feature-slug>` — Diseño técnico de la spec

> **Argumentos:** `$ARGUMENTS` — si el token aparece sin sustituir, los
> argumentos son el texto con el que se invocó el comando.

Sigue el protocolo §7 (AGENTS.md). Convierte `requirements.md` en el
**cómo**: arquitectura, componentes, modelo de datos, contratos
consumidos y decisiones. Es el paso entre `/spec-clarify` y G2, y sin
él **el gate no se puede firmar** — G2 firma *requirements + design*, y
`/spec-verify --pre-g2` falla con CRITICAL si `design.md` sigue siendo
el esqueleto de la plantilla.

Es la **Fase 3 (Planning)** del ciclo (§4). `tasks.md` no se llena
aquí: se deriva del diseño ya firmado, en `/spec-implement`.

> **PARADA — el veredicto va primero.** Si en cualquier paso de abajo te
> paras a preguntar, escribe antes `result.json` con
> `status: needs_input`, la pregunta y su `owner`. Quien te lanzó no ve
> tu pantalla.

1. **CONTEXT** — leer `requirements.md` completo (incluidas
   `Dependencies` y `## Clarifications`), `design.md` actual, y
   `stack/` entero: `tech-stack.md`, `architecture.md`, `patterns.md`,
   `constraints.md`, `security.md`, `testing.md`.
   - Si `requirements.md` tiene `[NEEDS CLARIFICATION]` o
     `OPEN_QUESTIONS` abiertas: **parar**. Diseñar sobre requirements
     ambiguos produce diseño que hay que rehacer.

     **Antes de parar, mirar si la pregunta ya está recogida por una
     `D-N`.** Una ambigüedad promovida a dependencia con estrategia
     declarada (`MOCK`, `PIN`, `WORKAROUND`) **ya no es una pregunta
     abierta**: se sabe contra qué se construye, y lo que falta es el
     dato, que lleva la `D-N` con su `owner` y su `Ready to unmock`.
     Cerrarla en `OPEN_QUESTIONS` citando su `D-N` y seguir.

     Se midió: siete preguntas del cliente vivían en las dos listas a la
     vez y dejaban la spec **inalcanzable mientras la contraparte
     tardara** — con `design.md` de requisito para G2. Ver §6 *Una `D-N`
     y una `OPEN_QUESTION` no son lo mismo*.

     **No se promueve** si la respuesta cambiaría *qué* se construye en
     vez de *con qué*: un mock no sustituye una decisión de
     comportamiento. Ahí sí se para.

     Distinguir a dónde rutear:
     - `OPEN_QUESTION` que espera el `id` de un contrato de disciplina
       → **`/contract-new <tipo> <id>`**. `/spec-clarify` no la puede
       cerrar: su dueño es la disciplina, no el dev presente.
     - Cualquier otra ambigüedad → **`/spec-clarify`**.
   - Si `status: approved` o posterior: **parar**. Cambiar el diseño de
     una spec firmada es `/spec-amend`, no esto.
   - Si la `modality` es `config-only` o `docs-only` (§6): `design.md`
     puede ser un párrafo o omitirse. Confirmarlo con el dev y no
     forzar la estructura completa.

2. **DERIVAR, no inventar** — cada elemento del diseño debe poder
   rastrearse a un `R*.*`, a un NFR o a una restricción de `stack/`.
   Recorrer en este orden:

   | Sección | Qué se decide | De dónde sale |
   |---|---|---|
   | Arquitectura | Dónde vive cada pieza; qué capas se tocan | `stack/architecture.md` + los `R*.*` |
   | Componentes | Qué se crea, qué se modifica, qué se reutiliza | Los `R*.*`, y lo que ya existe en el repo |
   | Modelo de datos | Entidades, campos, migraciones | Los `R*.*` que persisten algo |
   | Contratos consumidos | `D-N` con `id` + `version`: APIs, eventos, y contratos de disciplina si el repo declara `disciplines` | Sección `Dependencies` de `requirements.md` |
   | Criterios que bajan a test | Cada `acceptance_criteria` **automático** del contrato citado se agrega al `Tests:` de la `R*.*` que lo consume (§12 *G4*) | Los contratos de la `D-N` |
   | Decisiones | Alternativas consideradas y por qué esta | La conversación con el dev |
   | Complejidad justificada | Lo que existe sin `R*.*` que lo pida, con su razón | Explícito, o no debería estar |

   **Reutilizar antes que crear.** Antes de proponer un componente
   nuevo, buscar en el repo si ya existe algo que lo cubra. Un diseño
   que duplica lo existente es más caro de mantener que uno feo.

3. **PREGUNTAR lo que decide el humano** — máximo **5 preguntas** por
   tanda, una a la vez, con opciones tabuladas y una recomendada.
   Preguntar sólo lo que cambia la arquitectura, el modelo de datos o
   el costo. Lo que `stack/` ya decide **no se pregunta**: se aplica y
   se cita.

4. **ANTI-OVERENGINEERING** — antes de escribir, pasar cada componente
   por: *¿qué `R*.*` lo pide?* El que no responda va a
   `Complejidad justificada` con su razón, o se elimina. Es el mismo
   criterio que `/spec-verify --pre-g2` aplica después (check 6): mejor
   resolverlo aquí que en el gate.

5. **ESCRIBIR** `design.md` desde `.agents/templates/spec/design.md`,
   conservando los guardrails en comentarios.

   **Secciones condicionales**: la plantilla marca de qué capacidad
   depende cada una. Si `repo-config.yaml` **no** declara esa capacidad
   —típicamente `disciplines`—, **borrar la sección entera**. Si la
   declara pero no aplica a esta feature, marcarla `N/A — <razón>`.
   Dejar en pie una sección de una capacidad no declarada le cobra a la
   feature un artefacto que su repo no usa, y el check 0 de
   `--pre-g2` obliga a resolverla para firmar G2. Registrar en
   `Conflicts resolved` cualquier conflicto cross-spec que
   `/spec-new` hubiera detectado y dejado abierto.

6. **CERRAR** (§7) — reportar qué se decidió, qué quedó pendiente y el
   siguiente paso: `/spec-verify --pre-g2` y, si sale limpio, la firma
   de G2.

   **Restricciones**:
   - **No se escribe código.** Ni siquiera de ejemplo, más allá de
     firmas o esquemas que el diseño necesite declarar.
   - **No se llena `tasks.md`.** Se deriva en `/spec-implement`, del
     diseño ya firmado. Descomponer en tareas un diseño que aún puede
     cambiar en G2 es trabajo que se tira.
   - **No se firma G2.** El comando prepara el gate; firmarlo es del
     tech lead.

## Contrato de salida — `result.json`

**Al terminar, siempre, escribe `result.json` en la raíz del repo.** Lo
haya lanzado una persona o un orquestador.

**Y antes de pararte a preguntar, también** — con `status: needs_input`,
su `question` y su `owner`. **Pararse ES un final** para quien te lanzó:
si la pregunta espera en pantalla y el archivo no existe, un orquestador
no distingue *"está pensando"* de *"necesita algo"*, y `needs_input` se
queda sin productor aunque tres piezas lo consuman. Se midió el
2026-09-12 corriendo `/spec-implement` dentro de herdr: paró en una
decisión real de `stack/`, dejó la pregunta en pantalla y **no escribió
nada**. Si al contestarte puedes seguir, lo sobrescribes al terminar.

```json
{"status":"done","escalate":false,
 "question":null,"owner":null,"session":"<id de esta sesión>"}
```

| `status` | Cuándo |
|---|---|
| `done` | Terminaste lo que el comando pide |
| `needs_input` | Falta algo para seguir. Va con `question` y `owner` |
| `blocked` | No se pudo trabajar. El motivo, en `question` |

**`escalate` dice a quién le toca la pregunta**: `false` se queda en el
repo y lo contesta su tech lead —el caso normal—; `true` sube al hub,
sólo si la respuesta puede mover el reparto. Escalar por reflejo es el
error caro.

**Por qué es un archivo y no la consola.** El formato de stdout cambia
entre runtimes; un archivo no. Y se midió el 2026-09-10: `/spec-design`
paró pidiendo una definición y **no escribió nada**, así que quien lo
lanzó no tenía forma de saber por qué — `dispatch` reporta
`fallo-sin-veredicto` y el motivo queda dentro de un archivo de sesión
que nadie abre. Un comando que puede pararse y no lo declara es un
cuelgue silencioso en cuanto no hay una persona mirando.

**No lo commitees, y no hace falta que lo borres**: está en el
`.gitignore` del repo. Es el estado transitorio de esta corrida.
