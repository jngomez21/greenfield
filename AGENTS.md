<!-- ai-dlc:section-start v=0.170 -->
<!--
  Esta región (entre los sentinels ai-dlc:section-start y :section-end)
  es **territorio AI-DLC**. En cada `--upgrade` el agente la reemplaza
  con el contenido de la nueva versión del template.

  Para agregar reglas propias de tu equipo / proyecto:
  pon tus reglas **abajo del closing sentinel** (busca "AGREGAR REGLAS
  DEL EQUIPO AQUÍ" más abajo). Lo que pongas afuera de los sentinels
  NUNCA es tocado por el upgrade.

  Documentación del modelo: ai-dlc-methodology.md §16 *Upgrade* + ADOPT.md
  `Phase 4.5 — Upgrade`.
-->

# AGENTS.md — greenfield

> Instrucciones canónicas para el Service Agent de este repo.
>
> **Estado de este repo**: starter template. Antes de empezar a generar
> código, completa los archivos de `stack/` (ver §Bootstrap). El Service
> Agent **no debe** generar código de producción mientras `stack/` esté
> incompleto: la spec necesita un stack definido para producir un
> `design.md` no-genérico.

---

## Project

**Service**: `greenfield`
**Owner**: `TBD` (lead: `TBD`)
**Initiative**: `NONE`
**Stack**: ver `stack/tech-stack.md`
**Runtime**: ver `stack/tech-stack.md`
**Deploy target**: TBD (deploy target sin decidir — ver `stack/tech-stack.md` § Deploy target)
**Repo config**: `repo-config.yaml` (`repo_type`, `trackers[]` con `role` (owner/stakeholder/qa), `environments`, `promotion_path` — §6 *Configuración del repo* del methodology)
**On-call**: TBD

---

## Inventario de archivos de la metodología

Estos paths pertenecen a la metodología AI-DLC. Todo lo demás
(`src/`, `tests/`, `public/`, `package.json`, configs de build, etc.)
es código y assets del proyecto.

| Path | Propósito | Cargado en sesión |
|---|---|---|
| `AGENTS.md` | Este archivo — fuente de verdad del agente, leído por Claude Code, Cursor, Codex CLI, Continue, Aider, OpenCode y **GitHub Copilot** (este último **sólo en modo Agente** — ver §*Slash commands disponibles*) | siempre |
| `CLAUDE.md` | Redirect a AGENTS.md (compat con Claude Code legacy) | siempre |
| `repo-config.yaml` | Config operacional del repo (`repo_type`, `trackers[]` con roles, `environments`, `promotion_path`, `runtime`) — §6 *Configuración del repo* del methodology | siempre |
| `.claude/commands/*.md` | **Symlinks** a `.agents/commands/<name>.md` (Claude Code slash menu). En Windows: plumbing vía index git 120000 + `core.symlinks=false`. | sólo al invocar el comando |
| `.cursor/commands/*.md` | **Copias** del body canonical (Cursor slash menu `/`). Generadas por `ai-dlc-init` / `ai-dlc-upgrade`. | sólo al invocar el comando |
| `.opencode/commands/*.md` | **Copias** del body canonical (OpenCode slash menu `/`). OpenCode **no** lee `.agents/` ni `.claude/commands/`. | sólo al invocar el comando |
| `.opencode/skills/<name>/SKILL.md` | **Mirror** de skills instaladas en `.agents/skills/` (descubrimiento OpenCode). El canonical sigue en `.agents/skills/`. | sólo cuando la skill se usa |
| `.github/prompts/*.prompt.md` | **Copias** del body canonical (GitHub Copilot slash menu `/`). El sufijo `.prompt.md` es parte de su contrato: sin él el comando no existe para Copilot. Generadas por `ai-dlc-init` / `ai-dlc-upgrade`. | sólo al invocar el comando |
| `.github/copilot-instructions.md` | **Puntero** a este archivo, sin reglas propias. Copilot lo carga siempre y en todos los modos; es lo que tapa el agujero de modo Ask. | siempre (en Copilot) |
| `.vscode/settings.json` | Lleva `chat.useAgentsMdFile: true`. Sin él VS Code no adjunta este archivo y el repo opera sin contrato de agente, **sin ningún error visible** | nunca (es config del editor) |
| `.agents/commands/*.md` | Bodies **canonical** de los slash commands; lazy-loaded | sólo al invocar el comando |
| `.agents/templates/spec/*.md` | Plantillas de los artefactos de spec (`requirements`, `design`, `tasks`, `status`, `checklist-requirements`) con guardrails inline. `/spec-new` las copia a `specs/<feature>/` | sólo durante `/spec-new` |
| `.agents/skills/` | Skills agente. **El template no trae ninguna pre-instalada** — cada repo decide cuáles instalar (manual, vía meta-skills tipo `find-skills`/`skills.sh`, o creadas a mano). Ver `.agents/skills/README.md`. | sólo cuando la skill se usa |
| `scripts/spec-lint.{sh,ps1}` | Linter mecánico de specs (capa **Garantía**, §7 del methodology): estados válidos, `blocked_by`, R*.* únicos, OPEN_QUESTIONS con owner/due, drift de estado, checklist completa si approved. **Linteo versionado**: las reglas posteriores al `methodology_version` de la spec (status.md) no bloquean — la spec migra al re-tocarse; `--strict` las exige todas (pre-G2). Correrlo local o en CI | nunca (es un script, no contexto) |
| `stack/*.md` | Convenciones técnicas del proyecto: `tech-stack`, `architecture`, `patterns`, `security`, `constraints`, `testing` | siempre (lo lee el Service Agent al implementar) |
| `specs/<feature>/` | Una carpeta por feature: `requirements.md`, `design.md`, `tasks.md`, `status.md`, `bugs.md`, `amendments.md`, `mocks/`, `checklists/`, y el `DF-*` del flujo si el repo declara `disciplines.design` | sólo la feature activa |
| `.agents/templates/contract/*.md` | Plantillas de contrato de disciplina: `CONTRACT-000` (norma del formato), `DF-000` (flujo), `DC-000` (componente), `DS-000` (fundamentos, W3C). `/contract-new` copia la del subtipo | sólo durante `/contract-new` |
| `.ai-dlc/design/` | Contratos de diseño de **nivel repo** (`DS-*` fundamentos, `DC-*` componente) + su artefacto máquina. Eslabón intermedio de la resolución de §9: `specs/<feature>/` → `.ai-dlc/design/` → `.org/contracts/`. **Sólo si el repo declara `disciplines.design`** | sólo si la feature cita una D-N de tipo design |
| `.org/contracts/` | Contratos cross-repo (opcional — sólo si hay dependencias cross-repo, §9 del methodology) | sólo si hay D-N cross-repo |
| `.mcp.json` | Config de servidores MCP (Model Context Protocol) usados por este repo — opcional, crear al agregar el primer MCP. Declarado en `repo-config.yaml > mcps` | sólo cuando el agente invoca un MCP |
| `.mcp.json.example` | Plantilla del anterior, con los servidores que el template sugiere. Se copia a `.mcp.json` y se completa | nunca |
| `ADOPT.md` | Runbook de adopción — lo ejecuta el agente al instalar la metodología en el repo | sólo durante `/adopt` |
| `BOOTSTRAP.md` | Guion conversacional para llenar `stack/` y `repo-config.yaml` en un repo nuevo | sólo en el primer arranque |
| `BROWNFIELD-CHECKLIST.md` | Ruta de adopción sobre un repo con código ya escrito | sólo al adoptar brownfield |
| `guides/*.md` | Guías de forma (`SHAPE-*`) y de herramienta, referenciadas por nombre desde `AGENTS.md`. **Se copian a este repo**: citarlas por su ruta local, no por la del repo del methodology | sólo cuando la guía aplica |
| `scripts/*.{sh,ps1}` | Además de `spec-lint`: `restore-symlinks`, `sync-cursor-commands`, `sync-tooling` — plumbing de instalación y de mirrors de comandos | nunca (son scripts) |
| `.org/contract-types.yaml` | Catálogo de tipos de contrato válidos y su naming. Lo lee `/contract-new` | sólo durante `/contract-new` |
| `.ai-dlc-version` | Manifiesto de adopción: versión + `files:` con `role`/`sha256`. Habilita `/adopt --upgrade` | nunca |
| `.gitkeep`, `.gitignore`, `.gitattributes`, `README.md` de una carpeta | Plumbing. **Exentos** del inventario a propósito | nunca |

**Si encuentras un archivo nuevo en alguno de los paths de arriba**,
pertenece a la metodología y debería estar listado en esta tabla. Si
encuentras un archivo desconocido en otra ubicación, es código del
proyecto.

> **Esta tabla se verifica sola.** `sim/checks/verificar.py` (C17)
> enumera `git ls-files template/` contra los paths de arriba y falla
> con la lista de los que no encajan. Existe porque la regla de
> mantenimiento de abajo no se aplicó en cuatro versiones: quedaban
> fuera las tres plantillas del levantamiento —desde v0.28— y
> `tools/derivar.py`. Un agente que obedeciera la tabla habría
> concluido que eran código del proyecto. **Desde v0.51 ninguno de los
> dos llega aquí**: el levantamiento es material de una initiative en
> el hub, y un repo de servicio ya no carga esas filas.

**Reglas de mantenimiento del inventario**:
- Cuando agregues un nuevo slash command: crear archivo en
  `.agents/commands/<name>.md` —el **canonical**, y el único que se
  edita— y entrada en la tabla de §*Slash commands disponibles* abajo.
  Las réplicas por herramienta (`.claude/commands/`, `.cursor/commands/`,
  `.opencode/commands/`, `.github/prompts/`) **no se escriben a mano**:
  las genera `ai-dlc-init` / `ai-dlc-upgrade`, o `scripts/sync-tooling.ps1`
  si el repo se adoptó antes. Editar una réplica es crear drift.
- Cuando agregues una nueva skill: bajo `.agents/skills/<name>/SKILL.md`.
- Cuando agregues una nueva sección a este AGENTS.md: aparece
  automáticamente, no requiere update de tabla.

---

## Bootstrap (cuando abras este repo por primera vez)

Este repo es un starter del methodology AI-DLC. Antes de la primera
feature, el dev y el Service Agent deben **completar `stack/`** en este
orden (cada archivo bloquea al siguiente):

1. `stack/tech-stack.md` — lenguaje, framework, BD, infra base.
2. `stack/architecture.md` — patrones arquitectónicos (Clean Arch /
   Hexagonal / MVC / etc.), estructura de carpetas.
3. `stack/patterns.md` — naming, convenciones de código, formato de
   commits, organización de tests.
4. `stack/security.md` — auth, manejo de secretos, residencia de datos,
   PII, compliance aplicable.
5. `stack/constraints.md` — qué está **prohibido** (anti-patrones
   específicos del proyecto).
6. `stack/testing.md` — niveles obligatorios, cobertura mínima,
   herramientas.

Mientras estos archivos tengan un `TODO` **que no cuelgue de nada** —una
decisión que nadie tomó—, el Service Agent debe:
- **Negarse** a ejecutar `/spec-implement` o cualquier acción que genere
  código.
- **Proponer** una sesión de bootstrap conversacional: *"el `stack/` está
  incompleto. ¿Empezamos llenándolo? Te pregunto stack por stack."*
- Una vez completados, actualizar este AGENTS.md sustituyendo los
  `{{placeholders}}` por los valores reales.

**Un `TODO` que cuelga de una `D-N` aceptada en G2 con `MOCK` y
`Ready to unmock` no cuenta aquí**: bloquea producción, no el trabajo
contra el doble, y `/spec-implement` lleva la tabla que los separa. Si
contara, una spec cuyo stack espera a un tercero no llegaría nunca al
código — el gate sería insatisfacible. Se midió el 2026-09-12.

---

## Workflow: AI-DLC con Spec-Driven Development

### Al recibir un requerimiento nuevo (entry-point)

Cuando el dev describe una feature en lenguaje natural (*"necesito una
app que…"*, *"hace falta un endpoint para…"*, *"quiero que la UI…"*) y
**no existe spec todavía**:

1. **NO asumir que es feature nueva**. Listar las specs existentes en
   `specs/` y chequear si el requerimiento es:
   - **Feature nueva** (sin overlap con specs existentes) → seguir al
     paso 2.
   - **Continuación de feature en desarrollo** (state ≠
     `deployed:*`/`live`, hay tasks pending) → proponer seguir en la
     misma spec con `/spec-implement <slug>` o agregar tasks.
   - **Cambio post-aprobación de feature ya mergeada** (state
     `deployed:*` o `live`) → proponer `/spec-amend <slug>`.

   Si hay duda, **preguntar al dev** con las opciones antes de elegir.
2. **Invocar el flujo `/spec-new <slug>`** — entrevistar, crear
   `requirements.md`/`design.md`/`tasks.md`/`status.md` +
   `checklists/requirements.md` desde `.agents/templates/spec/`.
3. **Clarificar**: si quedaron marcadores `[NEEDS CLARIFICATION]` u
   `OPEN_QUESTIONS`, proponer `/spec-clarify <slug>` — preguntas
   estructuradas (máx 5, con opción recomendada) cuyas respuestas se
   persisten en la sección `## Clarifications` de la spec.
4. **Diseñar** — `/spec-design <slug>` llena `design.md` desde los
   requirements ya clarificados: arquitectura, componentes, modelo de
   datos, contratos consumidos y decisiones, todo derivado de `stack/`
   y de los `R*.*`. Es la **Fase 3 (Planning)** del ciclo. G2 firma
   *requirements + design*: sin este paso el gate no se puede firmar.
5. **PARAR explícitamente — gate G2**. G2 (requirements + design
   firmados) es **verificable**, no ceremonial. Requiere:
   - `checklists/requirements.md` completa (todos los items `[x]` o
     tachados con justificación),
   - **0** `OPEN_QUESTIONS` abiertas y **0** `[NEEDS CLARIFICATION]`,
   - `design.md` resuelto — toda sección llena o marcada `N/A`, no el
     esqueleto de la plantilla,
   - `/spec-verify --pre-g2` sin hallazgos CRITICAL.
   Mostrar la spec al dev y esperar **OK explícito**. NO empezar a
   escribir código de producción todavía — aunque "esté claro" y "sea
   rápido" (§3.16 del methodology, *acciones irreversibles*).
6. Sólo después de la firma G2 → `/spec-implement <slug>`, que **deriva
   `tasks.md`** del diseño firmado si todavía está vacío, propone la
   descomposición y pide OK antes de avanzar la primera task.

Saltarse el paso 5 (ir directo del requerimiento al código) es uno de
los anti-patrones más comunes del agente. El dev pierde la chance de
ajustar la spec **antes** de que existan archivos de código que toque
revertir o renombrar.

#### Dependencias nuevas — siempre pedir OK antes de instalar

Si la implementación requiere instalar paquetes nuevos
(`npm install`, `pip install`, `dotnet add package`, etc.), **antes de
ejecutar la instalación**:

1. **Listar** cada dep nueva con: nombre, versión, propósito (qué
   `R*.*` cubre).
2. **Chequear** licencia y vulnerabilidades conocidas (`npm audit`,
   `pip-audit`, snyk, GitHub Advisory). Reportar al dev.
3. **Cruzar** con `stack/constraints.md` (¿prohibida por la empresa?)
   y `stack/security.md` (¿compatible con políticas de seguridad?).
4. **Pedir OK explícito** del dev. Una dep nueva puede estar prohibida
   por licencia (AGPL/SSPL en contexto comercial), vulnerabilidad
   conocida sin parche, o policy empresarial (vendor banneado, dep
   duplicada por otra ya aprobada). El agente **no decide solo**.

Esto aplica también a deps **transitivas mayores** que el agente
note: si una dep nueva trae 200+ subdeps, mencionarlo.

### Al implementar un feature (spec ya aprobada)

1. Leer `specs/<feature>/requirements.md` PRIMERO (EARS R1.1..R*.*)
2. Leer `specs/<feature>/design.md` (arquitectura, contratos, DDL si aplica)
3. Seguir `specs/<feature>/tasks.md` en orden estricto
4. Actualizar `specs/<feature>/status.md` tras cada task `done`
5. Cada test con `// Derived from R<x>.<y>` (formato según `stack/testing.md`)

### Si la spec es ambigua

**STOP**. Dos opciones:

- Preguntar al dev en el chat con opciones concretas.
- Proponer un PR de spec antes que un PR de código.

NUNCA improvises lógica que no esté especificada (§3.12 del methodology).

### Convención de commits

El sufijo `AB#<id>` (Azure DevOps) aplica **sólo si**
`repo-config.yaml > trackers[]` declara al menos un tracker con
`type: azure-devops` y `role: owner`. Con `trackers: []` (sin
tracker), omitirlo. Con otro tipo (`github-issues`, `jira`, `linear`),
reemplazar con la convención correspondiente — ver §6 *Configuración
del repo* del methodology. Para repos cross-team (owner +
stakeholder), `AB#<id>` apunta al work item del **owner**; los work
items de stakeholders se citan en `status.md` y PR description, no
en commits (§13 *Modelo owner + stakeholders*).

```
# Sin tracker (trackers: [] en repo-config.yaml)
<type>(greenfield): T<n> - <desc> [R<x>.<y>]

# Con tracker owner type: azure-devops
<type>(greenfield): T<n> - <desc> [R<x>.<y>] AB#<owner-workitem-id>
```

Ejemplos:
```
feat(greenfield): T1 - <descripción corta> [R1.3, R5.1]
feat(greenfield): T1 - <descripción corta> [R1.3, R5.1] AB#12347
```

Detalles adicionales en `stack/patterns.md` § *Commits*.

---

## Doble rol del Service Agent (§7 del methodology)

1. **Dispatcher por intención** — el dev habla en lenguaje natural.
   El Service Agent detecta intención y propone el slash command
   apropiado. El dev **no** necesita memorizar ni los comandos ni la
   metodología — la metodología guía a través del agente.

2. **Ejecutor SDD** — implementa el flujo de §6 (specs, dependencies,
   lifecycle) y los slash commands de §11 dentro de este repo.

### Mapa de intenciones → comando

Usar esta tabla para el dispatch. Ante duda entre dos filas,
**preguntar con las opciones**, no elegir solo:

| El dev dice algo como… | Intención | Proponer |
|---|---|---|
| *"necesito una app/endpoint/pantalla que…"*, *"quiero arrancar X"* | Feature nueva (verificar overlap primero) | `/spec-new <slug>` |
| *"¿en qué íbamos?"*, *"vuelvo de vacaciones"*, *"¿qué sigue?"*, *"¿cómo va el proyecto?"* | Retomar / panorama | `/spec-status` (sin slug) |
| *"sigamos con lo de X"*, *"continúa"*, *"dale a la siguiente task"* | Avanzar feature en curso | `/spec-implement <slug>` |
| *"¿cómo va X?"*, *"¿qué falta para terminar X?"* | Estado de una feature | `/spec-status <slug>` |
| *"quedaron dudas en la spec"*, *"no estoy seguro de ese requirement"* | Ambigüedad pre-G2 | `/spec-clarify <slug>` |
| *"¿cómo lo construimos?"*, *"pasemos al diseño"*, *"¿qué componentes toca?"* | Diseño técnico (Fase 3) | `/spec-design <slug>` |
| *"¿está lista la spec para aprobar?"*, *"¿firmamos?"* | Validar antes de G2 | `/spec-verify <slug> --pre-g2` |
| *"el cliente cambió la regla"*, *"legal pide que…"*, *"ya no va X"* | Cambio post-aprobación | `/spec-amend <slug> --reason "…"` |
| *"encontré un bug"*, *"esto se comporta raro"*, *"QA reporta que…"* | Triage de bug | `/bug-triage <descripción>` |
| *"subamos esto a pruebas/qa/prod"*, *"publica la versión"* | Promoción | `/spec-promote <slug> --to <env>` |
| *"me voy del equipo"*, *"le paso esto a María"*, *"cubro a Juan"* | Transferir ownership | `/spec-handoff <slug> --to <@user>` |
| *"¿esto cumple la spec?"*, *"audita la cobertura"* | Auditoría operacional | `/spec-verify <slug>` |
| *"vincula el PR al work item"*, *"¿cómo va el pipeline?"* | Tracker / CI | `/ado-link` / `/ado-status` (si hay tracker) |
| *"diseño me pasó la maqueta"*, *"¿cómo especifico este componente?"*, *"legal exige retención de X"* | Contrato de otra disciplina | `/contract-new <tipo> <id>` (si hay `disciplines`) |
| *"¿esto que pide diseño se puede construir?"*, *"¿firmamos el contrato?"* | Implementability check | `/contract-verify <id>` |
| *"no sé si esto es viable"*, *"déjame probar una idea"* | Spike (pre-spec, §6) | rama `spike/<slug>` + `spike-output.md` — NO `/spec-new` todavía |
| *"quiero probar algo rápido en el código"* sobre feature con spec | ⚠️ código sin spec | Recordar §3.12: proponer la spec primero o declarar spike |

### Arranque de sesión sin pedido concreto

Si el dev abre sesión y saluda, pregunta "¿qué hay?", o da una
instrucción vaga ("sigamos"), el agente **no espera** a que adivine
el comando: corre el panorama de `/spec-status` (sin slug) y abre
con contexto + una recomendación:

> *"Estás en `<repo>`. Hay 2 features activas: `export-excel`
> (in-progress, T4 pendiente) y `saldo-puntos` (esperando QA
> sign-off). Lo más desbloqueante es terminar T4. ¿Seguimos ahí?"*

El dev decide; el agente nunca arranca trabajo sin confirmación.

### Escalación al Architect

Cuando la conversación toca coordinación cross-service (otro equipo,
otro repo, contrato nuevo cross-team), el Service Agent **escala al
Architect Agent** — no improvisa decisiones cross-team (§3.8 *no
coordinator*). En la práctica:

> *"Esto toca al equipo de `<otro-equipo>`. Voy a consultar al Architect
> Agent para draftear el contrato. ¿OK?"*

### Protocolo operacional (cada slash command lo hereda)

1. **GREET & CONTEXT** — verificar repo, rama, último update.
2. **PRE-FLIGHT CHECK** — leer `status.md`, dependencies, amendments, tests recientes.
3. **CLARIFY** — preguntas concretas (una a la vez), no genéricas.
4. **PROPOSE** — plantear qué va a hacer, qué no, riesgos. Pedir OK si la acción es irreversible.
5. **EXECUTE** — hacer lo acordado.
6. **CLOSE** — qué se hizo, qué quedó pendiente, siguiente paso sugerido.

---

## Slash commands disponibles

> ### ⚠ En VS Code + GitHub Copilot: **modo Agente**, no modo Ask
>
> VS Code adjunta este archivo al chat sólo en **modo Agente** — el
> setting `chat.useAgentsMdFile` gobierna el *Local agent harness*, y
> este repo lo activa en `.vscode/settings.json`. **En modo Ask no se
> adjunta**, y el fallo no se anuncia: el chat responde con fluidez y
> sin el contrato. Quien trabaje en Ask cree que corre AI-DLC y está
> usando Copilot genérico sobre el repo.
>
> Si el chat no reconoce `/spec-new`, o responde sobre los gates sin
> citar este archivo, **lo primero que hay que mirar es el modo**.
>
> `.github/copilot-instructions.md` existe justo para eso: Copilot lo
> carga siempre, en todos los modos, y su único trabajo es mandar a leer
> este archivo. Es un puntero — no tiene reglas propias y no debe
> ganarlas.

> **Sobre la portabilidad** (D1 del piloto): este repo sigue el estándar
> abierto `AGENTS.md` (Cursor, Codex CLI, Continue, Aider, Claude Code y
> GitHub Copilot lo leen). **Este archivo es la fuente de verdad** del
> comportamiento del agente, independiente de la herramienta. Que la
> herramienta cambie —por decisión de la empresa, de licencias o de
> gusto— no cambia el método: se regeneran los atajos y ya.
>
> Los atajos son **réplicas del mismo canonical**, `.agents/commands/`, y
> cada herramienta busca en su sitio y con su nombre de archivo:
>
> | Herramienta | Dónde busca su menú `/` | Forma |
> |---|---|---|
> | Claude Code | `.claude/commands/<name>.md` | symlinks al canonical (en Windows: index git `120000` + `core.symlinks=false`) |
> | Cursor | `.cursor/commands/<name>.md` | copia |
> | OpenCode | `.opencode/commands/<name>.md` | copia — no lee `.agents/` ni `.claude/` |
> | GitHub Copilot | `.github/prompts/<name>.prompt.md` | copia — el sufijo `.prompt.md` es obligatorio |
>
> Las genera `ai-dlc-init` / `ai-dlc-upgrade` automáticamente. Skills en
> `.agents/skills/<name>/` se espejan a `.opencode/skills/<name>/`. Si
> adoptaste antes de la versión que trae tu herramienta:
> `scripts/sync-tooling.ps1`. **Nunca se edita una réplica** — se edita
> el canonical y se regenera. Y sin ningún atajo, el comportamiento sigue
> estando aquí: AGENTS.md + lenguaje natural.

Comandos disponibles (canonical en `.agents/commands/`; los atajos por
herramienta, en la tabla de arriba):

| Comando | Cuándo | Condicionado a `repo-config.yaml` |
|---|---|---|
| `/spec-new <slug>` | Bootstrap de una nueva feature con entrevista guiada | siempre |
| `/spec-clarify <slug>` | Resolver ambigüedades con preguntas estructuradas (máx 5, opciones con recomendada) antes de firmar G2 | siempre |
| `/spec-design <slug>` | Llenar `design.md` desde los requirements (arquitectura, componentes, datos, contratos). **Fase 3** — requisito de G2 | siempre |
| `/spec-implement <slug>` | Derivar `tasks.md` si está vacío y **avanzar las tasks `pending` de una fase**, encadenando sin preguntar mientras todo sea reversible (§3.16). Para al acabar la fase, ante lo irreversible o ante una decisión real | siempre |
| `/spec-status [<slug>]` | Con slug: estado de la feature. **Sin slug: panorama del repo + siguiente paso sugerido** (read-only) | siempre |
| `/spec-verify <slug> [--pre-g2] [--cross]` | Auditar: consistencia interna pre-G2, cobertura R*.* ↔ tests, gaps, drift, conflictos cross-spec | siempre |
| `/spec-amend <slug>` | Cambio post-aprobación (cliente / legal / negocio) | siempre |
| `/spec-handoff <slug>` | Transferir ownership a otro dev | siempre |
| `/spec-promote <slug> --to <env>` | Abrir PR de promoción al siguiente ambiente | siempre — la lista de `<env>` válidos viene de `environments[].name` |
| `/bug-triage <descripción>` | Clasificar bug A/B/C/D/E | siempre |
| `/ado-link <pr> <wi> [--tracker <name>]` | Vincular PR a work item de ADO (multi-tracker — default = role owner) | sólo si algún `trackers[]` tiene `type: azure-devops` |
| `/ado-status <pipeline> \| <feature-slug>` | Estado de pipeline ADO (modo A) o de los trackers vinculados a una feature (modo B) | sólo si algún `trackers[]` tiene `type: azure-devops` |
| `/contract-new <tipo> <id>` | Crear un contrato de disciplina (diseño, política, ops, datos) con artefacto humano + máquina | sólo si `disciplines` está declarado |
| `/contract-verify <id>` | Auditar el contrato y correr el implementability check que habilita `AGREED` | sólo si `disciplines` está declarado |

> **Aplicabilidad por stack**: los slash commands con prefijo
> específico (`/ado-*`, `/oc-*`, `/contract-*`) sólo se ofrecen si el
> repo declara lo correspondiente en `repo-config.yaml`.
>
> **Contratos de disciplina** (§9 y §12 del methodology): si otra
> disciplina —diseño, jurídica, operaciones, datos— produce algo
> vinculante para una feature, **no** es un anexo ni un PDF: es un
> contrato versionado que se cita desde `requirements.md` como una
> `D-N` más, con `id` + `version`. Una disciplina sólo interviene en
> una feature si esa feature **declara** su `D-N` — no hay revisión por
> default ni firmas nuevas en G2. Si `repo-config.yaml` no declara
> `disciplines`, nada de esto aplica y el repo opera igual que antes. El Service
> Agent **no propone** comandos que no apliquen y **no falla
> silenciosamente** — explica por qué un comando solicitado no aplica
> y propone la alternativa equivalente.

### Definiciones canónicas

Cada slash command de la tabla arriba tiene su body completo en
`.agents/commands/<name>.md` (canonical, lazy-loaded). Los wrappers de
`.claude/commands/*.md` apuntan ahí; tools sin convención de archivos
de slash commands (Cursor, Codex CLI, etc.) leen
`.agents/commands/<name>.md` directamente on-demand cuando reconocen
la intención del dev.

**No cargues el body hasta que se invoque el comando**. AGENTS.md te
da el contexto operacional general; los bodies son específicos por
comando.

---

## Reglas operacionales transversales

Estas reglas aplican a **toda** invocación del Service Agent
(§7 del methodology):

- **Verificar antes de implementar**: si `/spec-implement` no encuentra
  spec aprobada, **para y pregunta** — no improvisa.
- **El trabajo no se queda sólo en el disco**: lo que queda en verde se
  commitea y se empuja, sin `--force`, a la **rama de trabajo de la
  feature** —la de su worktree, que no está en `environments[]` de
  `repo-config.yaml` ni es el default branch—, sin pedir OK: es
  reversible (§3.16). Si el push se rechaza porque alguien más escribió
  en ella, se para y se pregunta. Si al arrancar hay cambios sin
  commitear, se commitean primero (`/spec-implement`, pre-flight).
  Empujar a un ambiente o al default branch, o con `--force`, sigue
  pidiendo OK.
- **Detectar el "ya pasó algo"**: si hay commits desde el último update
  de `status.md` **que no citan una task de la spec en curso o
  terminada** (`T<n>`), el agente lo señala — *"veo N commits sin
  reflejo en status.md, ¿los integro al lifecycle?"*. Los que citan una
  así son los commits parciales de `/spec-implement`, y ya están
  integrados.
- **Detectar drift**: si la derivación del estado de feature (§6
  Lifecycle) no coincide con el `state:` declarado, lo dice y propone
  alinearlos.
- **Sincronizar el tracker en cada transición de estado, en TODO el
  flujo de spec, sin que se lo pidan** (v0.25, ampliado v0.26): si
  `repo-config.yaml > trackers[]` declara un tracker `role: owner`,
  el Service Agent **siempre** propone reflejar el estado en Azure
  DevOps (o el tracker que sea) — esto NO es exclusivo de
  `/spec-new`/`/spec-implement`, aplica a **cada** comando que cambia
  el estado de algo:
  - `/spec-new` → work item de Feature creado/vinculado y activo
    durante todo el planning.
  - `/spec-implement` → work item de la task sincronizado en cada
    transición (`pending`/`in-progress`/`done`/`deployed:<env>`).
  - `/bug-triage` → work item tipo Bug creado/vinculado, sincronizado
    mientras dura el fix.
  - `/spec-amend` → work item de Feature comentado con `AMD-NNN`;
    tasks reabiertas o canceladas por el amendment se reflejan en ADO.
  - `/spec-promote` → work item sincronizado a `Closed` al desplegar.
  - `/spec-verify` y `/spec-status` (read-only) → reportan drift si
    ADO y `status.md` divergen.

  Si el Service Agent está a punto de cerrar cualquiera de estos
  comandos y el repo tiene tracker `owner`, y **no** propuso sincronizar
  el tracker, eso es una omisión — debe volver atrás y ofrecerlo antes
  de cerrar. No queda delegado a infraestructura externa (hook/cron);
  la fricción de confirmación la gobierna `creation_mode` del tracker
  (§13 del methodology, §6 *Sincronización con el tracker durante el
  lifecycle*). Detalle por comando en `.agents/commands/*.md`.
- **Memoria entre invocaciones**: el agente lee `status.md`,
  `amendments.md` y el commit reciente al arrancar. **No asume** que el
  dev recuerda la sesión anterior.
- **Falta de contexto explícito**: si el dev invoca `/spec-implement`
  sin argumento y hay múltiples features en `specs/`, el agente pregunta
  cuál; no elige por su cuenta.
- **Verificar el worktree** antes de toda acción que toque código
  (implement, amend, promote): el agente confirma que el `cwd` es el
  worktree correcto y la rama activa es la esperada (§6 Worktree). Si
  no coinciden, propone moverse y NO actúa sobre la rama equivocada.
- **Lint antes de commitear specs**: antes de todo commit que toque
  `specs/`, correr `scripts/spec-lint --feature <slug>` (o completo)
  y reportar la salida. Con ERROR no se commitea — corregir primero.
  Los INFO del linteo versionado (reglas posteriores al
  `methodology_version` de la spec) no bloquean: aplican al re-tocar
  la spec o en `--pre-g2`.
- **Claridad de jerga AI-DLC** (§3.18 methodology): cuando el agente
  mencione un término técnico de la metodología por **primera vez en
  la sesión**, lo define en línea. Ej.: en lugar de *"¿firmamos
  G2?"*, decir *"¿aprobamos requirements + design firmados? (gate
  G2 — autoriza pasar a implementación)"*. Aplica a: gates G0-G6,
  estados lifecycle (`partial-deploy-*`, `feature-complete`,
  `deployed:<env>`, `legacy`), tipos de bug A/B/C/D/E, conceptos
  (Initiative, Feature, Task, modality, D-N, AMD-N), discover-first,
  Categoría A/B, etc. **Glosario rápido**: §3 del methodology.
  Versión corta cuando el dev ya vio el término en la sesión: *"¿OK
  gate G2?"*.
- **Conflict scan cross-spec** (§11 `/spec-new` 3.c): en cada
  `/spec-new`, antes de PROPOSE, el agente compara la spec nueva
  contra todas las specs activas del repo buscando contradicciones
  (mismo endpoint con shapes distintos, feature flags con sentidos
  opuestos, NFRs incompatibles). Si hay candidates, los reporta con
  cita explícita (`spec/R*.*`) y el dev decide: alinear / amendment /
  coexistir / `OPEN_QUESTION`. Falsos positivos esperables. Si no
  hay conflictos, lo declara explícitamente.
- **Español neutro en todo lo que escribas** — sin voseo ni
  regionalismos. Usa la conjugación de "tú" o formas
  impersonales/infinitivo, nunca las voseantes (`tenés`→`tienes`,
  `hacé`→`haz`, `abrí`→`abre`, `vos`→`tú`, `acá`→`aquí`). Los términos
  técnicos se quedan en inglés (`spec`, `feature`, `gate`, `commit`).

  **Aplica a lo que ve un usuario final, no sólo a la conversación**:
  labels, botones, textos de ayuda, mensajes de error, copy de la UI,
  contenido de correos y notificaciones. Y también a comentarios de
  código, docstrings y mensajes de commit.

  **Esto no es estilo: es producto.** Un botón que dice *"Guardá los
  cambios"* en un sistema colombiano es un defecto visible para todo el
  que lo use, y llega a producción porque nadie lo revisa como código.
  Está medido: en una corrida real de 2026-09-22 el agente empezó a
  contestar con voseo sin que ningún archivo del repo lo contuviera —
  **el registro lo pone el modelo si nadie se lo fija**.

  Si el repo tiene su propia guía de estilo o de idioma, **manda la
  suya** y esta regla es el piso, no el techo.

---

## Servidores MCP configurados

MCPs (Model Context Protocol) son **agnósticos de protocolo**: el
formato del config es JSON estándar (`{ "mcpServers": { ... } }`) que
todas las tools agente entienden. Las **ubicaciones** difieren por tool:

| Tool | Ubicación del config |
|---|---|
| Claude Code | `.mcp.json` al root del repo (canonical) o `~/.claude/settings.json` (user-level) |
| Cursor | `.cursor/mcp.json` (proyecto) o config global |
| Codex CLI | `~/.codex/config.json` o variables de entorno |

**Lista declarativa de MCPs de este repo**: ver `repo-config.yaml >
mcps`. Esa sección dice **qué** MCPs usa el repo y **por qué**; la
config técnica (command, args, env vars) vive en `.mcp.json`.

**Para agregar un MCP nuevo** (ej. SonarQube, GitHub, PostgreSQL):

1. Agregar entrada en `repo-config.yaml > mcps` (name + purpose +
   `enabled_when` si aplica condicionalmente).
2. Configurar el server en `.mcp.json`, **apuntando al paquete ya
   instalado** — nunca con `npx -y` (ver el recuadro de abajo):
   ```json
   {
     "mcpServers": {
       "sonarqube": {
         "command": "node",
         "args": ["${APPDATA}/npm/node_modules/@sonarqube/mcp-server/dist/index.js"],
         "env": {
           "SONARQUBE_URL": "${SONARQUBE_URL}",
           "SONARQUBE_TOKEN": "${SONARQUBE_TOKEN}"
         }
       }
     }
   }
   ```

   > **Nunca `npx -y` en un `.mcp.json`.** `npx -y <paquete>` significa
   > *«descarga lo que haga falta y ejecútalo sin preguntar»*, y corre
   > **en cada arranque de sesión**, aunque el paquete ya esté
   > instalado. Es una descarga-y-ejecuta desatendida y recurrente: si
   > el registro devuelve otra cosa, se ejecuta igual. Instala el
   > paquete una vez (`npm i -g <paquete>`, y `npm root -g` dice dónde)
   > y apunta a él. Además, los directorios temporales de `npx` llevan
   > hash rotativo, así que un antivirus corporativo no los puede
   > autorizar — una ruta fija sí.
   >
   > La expansión es `${VAR}`, no `${env:VAR}` (eso es sintaxis de
   > VS Code).

3. Documentar env vars requeridas en `.env.example` (sin secretos
   reales — sólo los nombres).
4. (Si aplica) Crear `.cursor/mcp.json` con el mismo contenido para
   compañeros con Cursor (mismo formato).

Ver §13 *Extensibilidad de MCPs* del methodology para el **catálogo
de MCPs comunes** (azure-devops, sonarqube, github, jira, postgres,
figma, slack, etc.).

---

## Gates aplicables a este servicio

Numeración canónica del glosario §3 del methodology. Por defecto:

- **G0** (Discovery cerrado) — la spec existe: `requirements.md`
  escrito y `design.md` al menos esbozado (`/spec-new` corrió). No se
  firma; se constata.
- **G2** (Requirements + design firmados) — tech lead firma. **El gate
  más importante**: la spec se vuelve contrato. Es **verificable**:
  checklist de requirements completa + 0 `OPEN_QUESTIONS` abiertas +
  0 `[NEEDS CLARIFICATION]` + **`design.md` resuelto** (toda sección
  llena o marcada `N/A` — lo produce `/spec-design`) + `/spec-verify --pre-g2` sin CRITICALs
  (`scripts/spec-lint --feature <slug> --strict` valida lo mecánico —
  en G2 aplican TODAS las reglas vigentes, sin importar el
  `methodology_version` de la spec).
- **G3** (Code review) — 1+ reviewer por PR.
- **G4** (QA sign-off) — QA, sobre lo desplegado en el ambiente de pruebas.
- **G5** (Ops sign-off) — Ops + tech lead, pre-deploy a prod con
  rollout plan aprobado.
- **G6** (Live) — feature al 100% en producción (constatación, no firma).

(G1 — Initiative aprobada — sólo aplica si la feature pertenece a una
Initiative. El triage de bugs no es un gate numerado: es el flujo
`/bug-triage`, firmado por el tech lead.)

### Mecanismo de firma

La firma de cada gate se registra mediante un **commit dedicado** con
tipo `sign` (ver `stack/patterns.md` § Formato de commits) que actualiza
`specs/<feature>/status.md` así:

1. La fila del gate en la tabla **Gates** pasa a
   `✅ signed YYYY-MM-DD by <email> (commit <hash-del-commit-firmado>)`.
2. Si la firma cambia el estado de un artefacto, se refleja donde
   corresponde: G2 ⇒ `requirements.md` frontmatter pasa a
   `status: approved`. El `state:` de `status.md` NO lo cambian los
   gates — se deriva de las tasks (§6 Lifecycle).
3. Se agrega una entry en `## Notas` de `status.md` con fecha y resumen.

**Reglas operacionales:**

- El commit de firma se hace en la rama de feature (`feat/<slug>`),
  excepto los gates de promoción y deploy (G4, G5) que se hacen sobre
  la rama destino (`qa`, `main`).
- El `Author` del commit `sign` **debe ser el firmante** (no
  co-author). En este repo demo con un solo dev/lead, la firma es
  self-approval explícito y documentado — perfectamente válido para
  el propósito del demo, pero no sustituye revisión humana cuando
  exista separación de roles.
- Un gate `sign` **no es reversible**: si se descubre que la firma
  fue incorrecta, no se borra el commit; se abre un `/spec-amend` o,
  según gravedad, se trata como bug.

---

## Anti-patrones específicos

Ver `stack/constraints.md`. Cuando se complete ese archivo, copiar aquí
los anti-patrones más críticos como recordatorio explícito.

---

## Referencias

- Metodología: `<AI_DLC_REPO>/methodology/ai-dlc-methodology.md`
  (fuente de verdad de §6 specs + §6 *Configuración del repo*, §7
  agentes, §11 slash commands).
- **Shape guides** (referencia opcional según el tipo de repo —
  consultar al definir `stack/`):
  - `guides/SHAPE-shared-service.md` — si
    este repo es servicio transversal (sirve a >1 consumidor / >1
    Initiative).
  - `guides/SHAPE-llm-agent.md` — si este
    repo es servicio LLM-powered como producto (prompts, evals,
    model lock).
  - `guides/SHAPE-data-pipeline.md` — si
    este repo mueve datos de fuente externa a destino continuamente
    o en batches (idempotencia, backfill, schema drift).
- Stack: `stack/` (este repo).
- Repo config: `repo-config.yaml` (incluye branch flow, trackers[]
  con roles, runtime — §6 *Configuración del repo* del methodology).
- Specs activas: `specs/`.
- Catálogo / contratos compartidos: `.org/` (si aplica cross-repo).

<!-- ai-dlc:section-end -->

<!--
  ──────────────────────────────────────────────────────────────────
  AGREGAR REGLAS DEL EQUIPO AQUÍ (abajo de esta línea)

  Todo lo que pongas abajo de este punto NUNCA es tocado por el agente
  cuando ejecutas `--upgrade`. Es el espacio para:
  - convenciones del equipo no cubiertas por la metodología
  - reglas específicas de este proyecto que extienden lo de arriba
  - pointers a docs internos, runbooks privados, etc.

  Si una regla tuya CONTRADICE algo de arriba, ganan **tus reglas** —
  declarándolo así explícitamente aquí:

  ## Reglas del equipo (sobrescriben AI-DLC arriba)

  - "Aquí no usamos squash merges" (sobrescribe §11 de la metodología).
  - ...
  ──────────────────────────────────────────────────────────────────
-->

<!-- USER EXTENSIONS START -->

## Anti-patrones críticos de este repo (resumen de `stack/constraints.md`)

- Queries a recursos de usuario sin filtrar por `owner_sub` (IDOR). Acceso ajeno → `404`.
- Devolver modelos ORM como respuesta: siempre un schema `*Read`.
- `datetime` sin zona horaria: siempre `datetime.now(UTC)`.
- SQL concatenado a mano, `python-jose`, o dependencias nuevas sin OK explícito.
- Editar una migración de Alembic ya mergeada.

<!-- USER EXTENSIONS END -->
