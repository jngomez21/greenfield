---
name: spec-new
description: Iniciar una feature spec con entrevista guiada
argument-hint: <feature-slug> [--from <brief>]
model-class: redaccion   # requirements EARS desde un brief ya aterrizado
---

# `/spec-new <feature-slug> [--from <brief>]` — Iniciar una feature spec

> **Argumentos:** `$ARGUMENTS` — si el token aparece sin sustituir, los
> argumentos son el texto con el que se invocó el comando.

Sigue el protocolo §7 (AGENTS.md). Para la feature `<feature-slug>`:

> **PARADA — el veredicto va primero.** Si en cualquier paso de abajo te
> paras a preguntar, escribe antes `result.json` con
> `status: needs_input`, la pregunta y su `owner`. Quien te lanzó no ve
> tu pantalla.

1. **CONTEXT** — verificar:
   - Repo actual y rama de trabajo.
   - **`stack/` completo**: si algún archivo de `stack/` aún tiene
     `TODO`, **no se para la spec entera** — se para donde el stack
     empieza a hacer falta.

     | Con `TODO` en `stack/` | |
     |---|---|
     | `requirements.md` | **Se escribe.** Son EARS: comportamiento. Qué valida el formulario y cuándo se emite el radicado no cambia porque falte elegir el ORM |
     | `design.md`, `tasks.md`, código | **Se paran.** Sin stack declarado el diseño sale genérico y los tests no trazan a convenciones reales — que es la razón que da `stack/tech-stack.md` |

     **Y un `TODO` no es como otro**: el que cuelga de una `D-N` que G2
     aceptó con `MOCK` y `Ready to unmock` **no para nada** —bloquea
     producción, no el trabajo contra el doble—. El que cuelga de una
     decisión que nadie tomó sí para. `/spec-implement` lleva la misma
     tabla: si no fuera así, una spec cuyo stack espera a un tercero
     nunca llegaría al código.

     Al parar en ese punto, en `status.md`: **`state` se queda en un
     valor del lifecycle** —`not-started`— y el aviso va en una clave
     aparte, `bootstrap: pendiente`. `state` tiene un enum cerrado que
     `spec-lint` valida (`not-started|in-progress|feature-complete|live|
     cancelled|legacy|partial-deploy-*|deployed:*`); meter ahí un valor
     nuevo rompe el lint. Además, **nombrar los archivos de `stack/` que
     faltan** y proponer `Bootstrap` (ver AGENTS.md § *Bootstrap*).

     **Por qué no se para antes**: la regla de fondo dice
     *"se negará a generar **código**… los `design.md` salen genéricos"*,
     y este paso la estiraba hasta bloquear los requirements, que no
     dependen del stack en nada. El efecto medido: un repo recién
     adoptado **no se podía despachar sin consola**, porque el Bootstrap
     es conversacional y no había nadie al otro lado. Un gate que
     detiene trabajo que no depende de él es trámite, no orden.
   - ¿La feature pertenece a una Initiative? Si sí, pedir URL o slug
     (recordar: Initiative es opcional, §6 del methodology).
   - ¿Hay un PR de requerimiento del cliente, work item de origen,
     conversación previa relevante?
   - **¿Toca un módulo legacy?** (§16 *brownfield*): si la feature toca
     código en producción **sin spec**, la regla del estrangulador es
     que *"la primera feature nueva sobre un módulo legacy abre la spec
     inicial del módulo"*. Proponerlo y **pedir OK**: crear
     `specs/<modulo>/` con un `requirements.md` mínimo —qué hace el
     módulo hoy, sin reverse-engineering— y `status.md` con
     `state: legacy`; los `R*.*` de la feature nueva lo citan. Si el
     dev prefiere no abrirlo, registrar la decisión y seguir: es una
     regla del estrangulador, no un bloqueo.

2. **WORKTREE** — preparar el espacio de trabajo aislado (§6 del
   methodology *Configuración del repo* + *Worktree, ramas y flujo de
   promoción*):
   - **Leer** `repo-config.yaml` y obtener las ramas declaradas en
     `environments[].branch`. Si el archivo no existe, **parar** y
     proponer crearlo antes de seguir (no asumir `pruebas/qa/main`
     por reflejo).
   - **Preguntar** la rama base ofreciendo **sólo** las ramas
     declaradas (default = la primera de `promotion_path`).
   - **Proponer** crear:
     `git worktree add -b feat/<feature-slug> ../<repo>--<feature-slug> origin/<base>`
     y pedir OK antes de ejecutar (acción reversible pero observable).
   - Tras crear, **verificar** que el `cwd` quedó en el worktree nuevo
     antes de continuar.
   - **`--from <brief>`: saltarse este paso entero.** Cuando la spec
     arranca desde un brief de reparto, quien invoca ya preparó el
     aislamiento —un clon fresco del repo, en su propia rama— y crear
     un worktree dentro de él anida un aislamiento dentro de otro.
     Leer el brief, tomar de él la initiative, los `D-N` citados por
     `id` y `version`, el work item y las clarificaciones ya resueltas,
     y **no volver a preguntar lo que el brief ya contesta**.

3. **CLARIFY** — entrevista guiada, **una pregunta a la vez**:

   **3.a Overlap con specs existentes** — antes de cualquier otra
   pregunta, listar las features actuales en `specs/` y confirmar con
   el dev que ésta es realmente nueva (no continuación, extensión o
   amendment de algo ya existente). Si hay overlap, proponer
   `/spec-implement` o `/spec-amend` y cerrar este flujo.

   **3.b Discover work item existente** — sólo si
   `repo-config.yaml > trackers[]` declara al menos un tracker:

   > "¿Esta spec corresponde a un work item existente?
   > (a) Sí — pásame el ID o el título que busque. *(Recomendado
   >     en brownfield con `creation_mode: discover-first`.)*
   > (b) Parcial — el padre existe, faltan children por crear.
   > (c) No — es nueva; propondré crear la jerarquía en EXECUTE."

   IF (a) o (b): consultar vía MCP o `az boards work-item show` /
   `az boards query`. Reportar lo encontrado (Feature, children,
   Acceptance Criteria — son **input** para los R*.*, no se
   descartan). Si el repo declara trackers `stakeholder`, preguntar
   también si implementa una Feature/Story del project stakeholder y
   citarla en `status.md > work_items.stakeholders[]`.
   **Anti-patrón duplicación catastrófica**: antes de proponer crear
   work items, buscar por título similar y reportar matches (§13).

   IF (c): además de proponer la jerarquía, **preguntar dónde
   crearla** si `default_area_path` del tracker no está declarado o el
   dev quiere uno distinto — no asumir un default en silencio. Si hay
   MCP configurado, ofrecer consultar los area paths válidos del
   project en vez de que el dev los recuerde de memoria.

   **Defaults al crear (v0.26, no preguntar salvo excepción)**:
   iteración = sprint actual del team (`System.IterationPath` vía MCP
   o `az boards iteration team list --timeframe current`) — sólo
   preguntar si la consulta falla o hay ambigüedad entre teams;
   estado inicial = `Active` (nunca `New`), porque abrir la spec ya
   es empezar a trabajarla.

   **Sincronización no opcional (v0.25)**: sea cual sea la respuesta
   (a/b/c), una vez identificado o creado el work item de Feature, el
   agente **siempre** propone dejarlo en estado activo en ADO — no
   sólo al crearlo, sino sostenido durante todo el planning
   (requirements → design → tasks, hasta firmar G2). Ver methodology
   §6 *Sincronización con el tracker durante el lifecycle* para la
   tabla de mapeo de estados y el modelo de fricción por
   `creation_mode`.

   **3.c Entrevista funcional**:
   - ¿Cuál es el problema que resuelve? ¿Quién es el usuario primario?
   - ¿Cuáles son los criterios de éxito **observables**? (forzar NFRs
     medibles — "rápido" no vale; "p99 < 500ms" sí)
   - **¿Cómo se parte en slices priorizados?** Identificar P1 (el MVP:
     lo mínimo que entrega valor y es desplegable solo) y qué queda
     para P2/P3. Cada slice declara su **prueba independiente**
     (plantilla § Slices priorizados). Si la feature no admite partición,
     declararlo (una feature de un solo slice es válida).
   - ¿Restricciones legales / compliance / residencia de datos? (cruzar
     con `stack/security.md`)
   - ¿Toca otros servicios? ¿De qué equipos? Si sí, **escalar al
     Architect Agent** (§7 del methodology).
   - ¿Depende de algo que aún no existe (SP, endpoint, librería,
     componente de diseño)? — futuras `D-N` (§6).
   - **¿Requiere nuevas dependencias** (npm/pip/nuget/etc.)? Si sí,
     listar las anticipadas y marcar `OPEN_QUESTION` sobre
     licencia/vulnerabilidades/policy. El OK de cada dep es parte de
     G2 (ver AGENTS.md *Dependencias nuevas*).
   - ¿Cómo se prueba cada R*.* (unit / integration / e2e / contract /
     load / accessibility)? Cruzar con `stack/testing.md`.
   - Lo que no tenga respuesta clara: marcar inline
     `[NEEDS CLARIFICATION: <pregunta + opciones>]` (**máximo 3** en
     toda la spec — si necesitas más, la conversación de intent no
     alcanzó: seguir entrevistando antes de escribir) o registrarlo
     en `OPEN_QUESTIONS` con `owner:` y `due:` si la respuesta depende
     de un tercero. **NO inventar** (§3.12).

   **3.d Conflict scan cross-spec** — antes de PROPOSE, comparar la
   spec nueva contra las specs activas del repo (state ≠ `legacy`,
   `archived`, `cancelled`) buscando contradicciones: mismo endpoint
   con shapes distintos, feature flags con sentidos opuestos, NFRs
   incompatibles (timeouts, límites, formatos), módulos compartidos
   con reglas opuestas. Reportar candidates con cita explícita
   (`specs/<otra>/R*.*` vs lo nuevo) y resolver cada uno con el dev:
   (a) alinear mi spec, (b) amendment de la otra, (c) coexisten
   intencionalmente → documentar en `design.md > Conflicts resolved`,
   (d) `OPEN_QUESTION`. Falsos positivos esperables — mejor
   sobre-detectar. Si no hay conflictos, **declararlo explícitamente**
   (el silencio es ambiguo).

4. **PROPOSE** la estructura inicial; pedir OK antes de escribir.
   Si 3.b fue (a): los `R*.*` se extraen de los Acceptance Criteria
   existentes y `tasks.md` mapea a los work items con
   `discovered: true` — **cero work items nuevos**. Si (b)/(c):
   proponer los faltantes con comandos `az` listos, OK por cada uno.

5. **EXECUTE** — crear `specs/<feature-slug>/` **copiando las
   plantillas de `.agents/templates/spec/`** (no generar de memoria —
   las plantillas traen los guardrails):
   - `requirements.md` ← plantilla, llena con la entrevista (slices,
     EARS + Tests strategy, Dependencies, Clarifications vacía,
     OPEN_QUESTIONS).
   - `design.md` ← plantilla, **esqueleto**. Lo llena `/spec-design`
     antes de G2 — el gate firma *requirements + design*, y
     `/spec-verify --pre-g2` da CRITICAL si sigue siendo el esqueleto.

   > **Bloques condicionales — aplican a las TRES plantillas de
   > arriba** (`requirements.md`, `design.md`, `checklists/`). Cada una
   > marca en sus comentarios de qué capacidad de `repo-config.yaml`
   > depende cada bloque. **Al generar la spec**, si el repo no declara
   > esa capacidad, esas líneas **no se escriben** — no se escriben y
   > se borran después, ni se dejan para que otro comando las quite.
   > `/spec-design` corre más tarde y en cuatro modalidades no corre
   > nunca (`config-only`, `docs-only`, `catalog-only`,
   > `refactor-only`), así que esperar a él deja el artefacto generado
   > cobrando una capacidad que el repo no tiene (§17 *métrica de
   > control*).
   - `tasks.md` ← plantilla, **vacío**. Lo deriva `/spec-implement` del
     diseño ya firmado (§4 Fase 3). Descomponer en tareas un diseño que
     todavía puede cambiar en G2 es trabajo que se tira.
   - `status.md` ← plantilla (state: not-started, tabla Gates en
     pending, `methodology_version:` = el `methodology_version` de
     `.ai-dlc-version` al root del repo; si el archivo no existe,
     preguntar al dev qué versión usa el repo. NO omitir el stamp:
     sin él, spec-lint trata la spec como pre-v0.22).
   - `checklists/requirements.md` ← plantilla checklist, **adaptada**:
     conservar los items base CHK-001..016 y agregar items específicos
     de la feature detectados en la entrevista (retención si hay PII,
     idempotencia si hay pagos/webhooks, límites si hay
     archivos/colas...).
     **Secciones condicionales por disciplina** (`CHK-D*` y las que
     vengan): se **conservan** si la feature declara —o va a
     declarar— una `D-N` de ese tipo; si no, se **borra la sección
     entera** (la plantilla lo dice en su comentario).
     Ojo con el orden: el contrato normalmente **todavía no existe**
     cuando corre `/spec-new` (lo crea `/contract-new` después). Si la
     entrevista detectó que la feature tiene UI y el repo declara
     `disciplines.design`, **conservar la sección** y abrir el
     pendiente del `id` del contrato **con esta forma exacta**, para
     que sea cerrable y el linter lo vea:

     ```
     ## OPEN_QUESTIONS
     - [ ] Id y version del contrato de <tipo> de esta feature — owner: @<owner de disciplines.<tipo> en repo-config.yaml>, due: <fecha del gate G2 previsto>
     ```

     **Una sola línea**: `spec-lint` parsea `owner:` y `due:` en la
     misma línea del `- [ ]`; partirla en dos dispara `[E6]`.

     **Antes de abrir una `OPEN_QUESTION`, preguntarse si es una
     `D-N`.** Si ya se sabe qué construir y lo que falta es el dato —un
     endpoint, un catálogo, un proveedor—, va a `Dependencies` con su
     estrategia, **no a las dos listas**. Duplicarla deja la spec
     bloqueada por algo que ya tenía sustituto (§6 *Una `D-N` y una
     `OPEN_QUESTION` no son lo mismo*).

     El `owner` **no se inventa**: sale de `repo-config.yaml`. Si la
     disciplina no lo declara, preguntarlo al dev — es dato del repo,
     no de la feature. Lo cierra `/contract-new`.
     Borrarla porque el contrato aún no existe firma G2 sin un solo
     ítem de diseño en un repo que declaró la disciplina. Cuando se conserva `CHK-D*`, **no** agregar un
     ítem propio de accesibilidad: `CHK-D4` ya la cubre y duplicarlo
     infla la checklist sin agregar señal.
   - **Si hay tracker `owner`**: sincronizar el/los work item(s) recién
     mapeados a estado activo vía MCP. Fricción según `creation_mode`
     (`auto` = ejecuta con 1 OK; `assisted` = entrega el comando `az
     boards work-item update --id <id> --state Active` listo;
     `discover-first`/`manual` sin MCP = deja el recordatorio en
     CLOSE). Reflejar el resultado en `status.md > work_items`.

6. **CLOSE** — **escribir `result.json` en la raíz del repo** y luego
   reportar en consola.

   **Y antes de pararte a preguntar, también** — con `status:
   needs_input`, su `question` y su `owner`. **Pararse ES un final**
   para quien te lanzó: si la pregunta espera en pantalla y el archivo
   no existe, un orquestador no distingue *"está pensando"* de
   *"necesita algo"*, y `needs_input` se queda sin productor aunque
   tres piezas lo consuman. Si al contestarte puedes seguir, lo
   sobrescribes al terminar.

   ```json
   {"status":"spec_drafted","escalate":false,
    "question":null,"owner":null,"session":"<id de esta sesión>"}
   ```

   | `status` | Cuándo |
   |---|---|
   | `spec_drafted` | La spec quedó escrita, aunque falten `design.md` o respuestas |
   | `needs_input` | Hace falta algo para seguir. Va con `question` y `owner` |
   | `blocked` | No se pudo trabajar. El motivo, en `question` |

   **`escalate` dice a quién le toca la pregunta, y la regla es una:**
   *¿la respuesta cambia algo fuera de este repo?*

   - **`false`** — se queda aquí. Qué ORM, qué convención, qué pasa con
     un caso borde de este servicio: lo contesta el tech lead del repo,
     que es quien sabe. **Es el caso normal.**
   - **`true`** — sube al hub. Sólo si la respuesta puede mover el
     reparto: contradice el requerimiento, toca a otro repo, o cambia un
     contrato compartido.

   **Escalar por reflejo es el error caro**: el hub no lo va a contestar
   mejor que quien tiene el repo delante, y cada rebote añade días a
   algo que se resolvía en dos minutos.

   **Este archivo se escribe siempre**, lo haya lanzado una persona o un
   orquestador. Es el contrato de salida, y es **un archivo** porque el
   formato de stdout cambia entre runtimes y un archivo no. A quien
   trabaja con consola no le estorba: dice en una línea cómo terminó.

   **No lo commitees, y no hace falta que lo borres**: está en el
   `.gitignore` del repo. Es el estado transitorio de esta corrida y
   caduca en cuanto termina — dejarlo en la rama de la feature deja ahí
   algo que ya no es cierto.

   En consola: qué se creó, marcadores
   `[NEEDS CLARIFICATION]` y `OPEN_QUESTIONS` abiertas (bloquean G2),
   y siguiente paso sugerido: **`/spec-clarify <feature-slug>`** para
   resolver ambigüedades de forma estructurada. **Si se conservó una
   sección condicional de disciplina** (`CHK-D*`), el paso siguiente es
   **`/contract-new <tipo> <id>`**: es lo que cierra el
   `OPEN_QUESTION` del `id` del contrato, y sin él `/spec-design` va a
   parar. Después,
   **`/spec-design <feature-slug>`** para llenar `design.md` — que es
   requisito de G2. Luego completar la checklist y pedir la firma.

**STOP — gate G2**. La firma de G2 requiere: checklist de requirements **completa**, **0** `OPEN_QUESTIONS`
abiertas, **0** marcadores `[NEEDS CLARIFICATION]` y **`design.md`
resuelto** (`/spec-design`)
(verificable con `scripts/spec-lint` y `/spec-verify --pre-g2`). Mostrar la spec al dev y **esperar OK
explícito** antes de invocar `/spec-implement`. NO escribir código de
producción todavía, aunque el requerimiento "esté claro" o "sea
rápido" — el dev pierde la chance de ajustar la spec **antes** de que
existan archivos de código que toque revertir (§3.16 del methodology).
