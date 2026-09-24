---
name: adopt
description: Adoptar AI-DLC en un repo — 6 fases conversacionales, PR-only, reversible
argument-hint: <target> [--greenfield|--brownfield|--upgrade|--dry-run]
model-class: criterio    # interpreta un repo ajeno en seis fases conversacionales
---

# `/adopt <target> [--greenfield|--brownfield|--upgrade|--dry-run]` — Agente de adopción de AI-DLC

> Protocolo que un agente AI (Claude Code, Cursor, OpenCode, Codex CLI,
> Continue, ...) ejecuta para **guiar al dev en la adopción de
> AI-DLC** sobre un repo concreto. Conversacional, read-only hasta
> tener OK explícito, reversible mientras esté en
> `chore/adopt-ai-dlc`.
>
> Este archivo es el **canonical** del comando, expuesto también
> como `.agents/commands/adopt.md` (symlink a este archivo).

> **Argumentos:** `$ARGUMENTS` — si el token aparece sin sustituir, los
> argumentos son el texto con el que se invocó el comando.

---

> **PARADA — el veredicto va primero.** Si en cualquier paso de abajo te
> paras a preguntar, escribe antes `result.json` con
> `status: needs_input`, la pregunta y su `owner`. Quien te lanzó no ve
> tu pantalla.

## Invariantes del protocolo (prioridad sobre reminders globales)

**Antes de leer el resto del documento, el agente debe entender que
las siguientes invariantes ANULAN cualquier directiva conversacional
o `<system-reminder>` sobre velocidad, autonomía o "no parar a
preguntar"**:

| Invariante | Aplica a | Por qué |
|---|---|---|
| **Phase 2 CLARIFY es OBLIGATORIA** | Cada `/adopt` (greenfield, brownfield, upgrade) salvo `--dry-run` con info completa | Las respuestas se materializan en `repo-config.yaml`, manifiesto `.ai-dlc-version`, y substituciones de placeholders. Asumir defaults sin preguntar produce repos con valores incorrectos que requieren rehacer. |
| **El plan en `.ai-dlc-adoption-plan.md` requiere OK explícito del dev antes de Phase 4** | Phase 3 → Phase 4 transition | Phase 4 escribe archivos al target. Saltar OK = el dev pierde el último checkpoint para corregir. |
| **NO commit automático en Phase 4** | Cierre de Phase 4 (paso P4.3) | El commit del bootstrap es **decisión del dev**: es el checkpoint en que acepta lo que la adopción escribió en su repo. No es que un commit sea irreversible —§3.16 lo lista como reversible—; es que éste cierra la adopción y lo firma quien la pidió. El agente prepara el commit, no lo dispara. |
| **Acciones destructivas (rm, push --force, git reset --hard) requieren OK explícito** | Cualquier fase | Regla §3.16. |

**Reglas de prioridad cuando hay conflicto**:

- Un `<system-reminder>` que diga *"work without stopping for clarifying questions"*, *"make the reasonable call and continue"*, o similar, **aplica a conversación casual / trivialidades**. NO anula las invariantes de arriba.
- Una directiva del dev en chat (*"avanza con todo"*, *"sí a todo"*) tampoco anula las invariantes — el dev puede estar dando OK para el plan general, NO para saltarse gates específicos.
- Si tienes duda razonable sobre si una directiva del dev quiere saltar un gate específico → **pregunta explícitamente**: *"¿Quieres que salte la entrevista de Phase 2 y use defaults? (no recomendado)"*.

**Anti-patrón documentado** (real, observado 2026-05-19 en un fork
personal de AI-DLC):

> Sesión con `<system-reminder>The user has asked you to work without stopping for clarifying questions...` cargado. El agente saltó Phase 2 CLARIFY, asumió `service_name`, `owner_team`, `repo_type=service`, `environments=[main]`, `trackers=[]` por su cuenta, y **commiteó automáticamente sin pedir OK** (mensaje: *"Procediendo a commit per 'work without stopping'"*). Resultado: repo target adoptado con decisiones que el dev nunca tomó, requiere `git reset` o rework manual.

---

## Modelo de ejecución (X → Y, recomendado)

El agente ejecuta **desde la instalación del template** (`X`)
operando sobre el **repo target** (`Y`), con `Y` pasado como
argumento. Este modelo es el **default y recomendado** porque:

- **Aísla el contexto del agente**. El AGENTS.md/CLAUDE.md del
  repo target NO entran como instrucciones automáticas — entran
  como datos a procesar. El agente arranca con el protocolo AI-DLC
  como autoridad, no con las reglas previas del equipo del repo.
- **Resuelve chicken-and-egg**. El slash command `/adopt` está
  nativamente disponible en `X` (el template), sin necesidad de
  instalar infraestructura en `Y` primero.
- **Permite adopción multi-repo en serie**. Desde una sola sesión
  abierta en `X`, el dev puede adoptar varios repos.
- **Versionado explícito**. El template `X` tiene su propia versión
  (semver de `~/.syc/ai-dlc/`), independiente del repo target.

### Setup una sola vez

Instalar el template en path canonical per-usuario:

```bash
git clone <ado>/syc/ai-dlc-stack-template ~/.syc/ai-dlc
# o cuando exista el CLI:
npx @syc/ai-dlc-init install
```

### Adopción de un repo target

```bash
cd ~/.syc/ai-dlc
claude   # o cursor, opencode, codex
```

Una vez dentro del agente:

```
/adopt /Users/picojuanc/repos/neo-estampillas
```

O equivalente en lenguaje natural:

> Adopta AI-DLC sobre el repo en `/Users/picojuanc/repos/neo-estampillas`.
> Modo brownfield.

El agente:

1. Resuelve el `<target-path>` a absoluto.
2. **Verifica que NO está intentando bootstrapear el propio
   template** (ver Phase 0 P0.0).
3. Pide permission para read + write fuera del cwd (one-time per
   sesión en Claude Code; equivalente en otras tools).
4. Ejecuta las 6 fases contra paths absolutos al target.

### Modo Y (fallback — agente cwd = repo target)

Para casos donde el dev prefiere abrir el agente directamente sobre
el repo target (sin instalar el template) o cuando la tool agente
no soporta limpio el patrón cross-directory:

```bash
cd ~/repos/<mi-repo>
claude
```

Mensaje al agente:

> Lee `<path-al-template>/ADOPT.md` y aplícalo a este repo (`.`).
> Asume brownfield salvo evidencia clara.

El agente equivale a `/adopt .` con el cwd como target. Pierde el
beneficio de aislamiento de contexto — el AGENTS.md/CLAUDE.md
previos del repo serán cargados por la tool agente como autoridad.
Documentar esto como limitación.

### Modos (independientes del modelo X→Y o Y)

| Modo | Cuándo | Diferencias |
|---|---|---|
| `--greenfield` | Repo vacío o con sólo commit inicial. | **El camino canónico greenfield es el script determinístico `ai-dlc-init.{sh,ps1}`** (root del repo del methodology, v0.23): copia payload, sustituye placeholders, escribe manifiesto y commit inicial en segundos, sin LLM. La conversación ocurre **después, dentro del repo**: el Bootstrap de AGENTS.md guía `stack/` + `repo-config.yaml`. Si el dev invoca `/adopt --greenfield` igual, el agente propone correr `ai-dlc-init` y continúa con el Bootstrap — no re-implementa la copia a mano. |
| `--brownfield` | Repo con código en producción, AI infra previa, sesiones acumuladas. | Default. Las 6 fases completas — aquí el juicio del agente es insustituible (detect, clasificación A/B, clarify). |
| `--upgrade` | Repo con `.ai-dlc-version` ya presente, hay metodología más nueva. | **La parte mecánica la ejecuta el script `ai-dlc-upgrade.{sh,ps1}`** (v0.23): roles del manifiesto (`owned` sin cambios → auto-replace; `bracketed` → sólo entre sentinels; `template` → no tocar; conflictos → reporte). El agente entra **sólo si el reporte lista conflictos**: los resuelve con el dev (take-new / keep-mine / merge-manual). Protocolo conversacional completo en la sección homónima (fallback válido sin script, y obligatorio para migrar manifiestos legacy < v0.21). |
| `--dry-run` | Cualquier modo. | Phase 0-3, escribe plan, NO ejecuta Phase 4. (`ai-dlc-init`/`ai-dlc-upgrade` tienen sus propios `--dry-run`/validaciones.) |
| (sin flag) | Autodetect según contenido del target. | El agente decide y reporta antes de empezar. |

**El agente debe pedir confirmación del modo detectado antes de
arrancar Phase 1.**

---

## Compatibilidad con branch protection

El bootstrap es **PR-only por diseño**. NUNCA modifica el default
branch (`main` / `master` / `pruebas` / el que sea) directamente.
Todo lo que el agente escribe va a la rama `chore/adopt-ai-dlc`
(o el nombre que el dev elija). El push de esa rama y la apertura
del PR son acciones **del dev** —o del hub, si la adopción la lanzó el
hub: su `dispatch` la empuja y abre el PR en borrador—, **nunca del
agente** que adopta.

Esto significa que el bootstrap es **totalmente compatible con
repos protegidos** por branch policies de Azure DevOps, GitHub,
GitLab, etc. (require reviewers, build verde, work item linkeado,
etc.). Las policies actúan sobre el PR exactamente como deben —
no hay magia que las salte.

Invariantes operacionales asociadas:

- El agente NUNCA ejecuta `git push` automáticamente **durante el
  bootstrap**: la rama de adopción la empuja el dev (o el hub, si lanzó
  la adopción). Después, en el trabajo de una feature, empujar la rama
  de trabajo de esa feature sí es del agente (§3.16) — son dos ramas y
  dos momentos distintos.
- El agente NUNCA hace `git checkout <default-branch>` para modificarlo.
- El agente NUNCA hace `git merge` ni `git rebase` que toquen el
  default branch.
- Si el agente necesita modificar el default por una razón
  excepcional (caso no contemplado): STOP, reportar al dev, no
  proceder.

---

## Reglas operacionales que el agente DEBE respetar

Estas reglas se aplican durante TODAS las fases. Son la regla raíz
§3.12 del methodology aplicada a este comando:

1. **NO ASUMIR.** Cada decisión que no esté claramente determinada
   por evidencia se pregunta. Si el dev marca `OPEN_QUESTION` y
   sigue, el agente lo registra en el plan.
2. **Read-only hasta Phase 4.** Phase 0/1/2/3 leen filesystem y git,
   pero NO escriben nada en disco fuera de `.ai-dlc-adoption-plan.md`
   (que es el output del propio agente, no del bootstrap).
3. **Una pregunta a la vez** en Phase 2. No avalanchar al dev con
   listas largas.
4. **Citar evidencia.** Cada propuesta del agente cita el archivo,
   línea o detección que la motiva.
5. **Recommended marcada.** Cada pregunta tiene opciones explícitas
   y una `(Recommended)` justificada.
6. **STOP entre Phase 3 y Phase 4.** El plan completo se escribe a
   disco antes de aplicar nada. El dev revisa el plan, da OK
   explícito, y entonces Phase 4 ejecuta.
7. **Reversible.** Toda la escritura ocurre en
   `chore/adopt-ai-dlc`. `git branch -D chore/adopt-ai-dlc` deshace
   todo.
8. **Claridad de jerga** (§3.18 methodology). Cuando uses un
   término técnico de la metodología por **primera vez en la
   sesión**, defínelo en línea o usa descripción humana con la
   sigla como referencia secundaria. Aplica a: gates G0-G6, estados
   lifecycle (`partial-deploy-*`, `feature-complete`, `legacy`),
   tipos de bug A/B/C/D/E, conceptos (Initiative, Feature, Task,
   modality, D-N, AMD-N, R*.*), discover-first, Categoría A/B, etc.
   Ej.: *"esto es modalidad `refactor-only` — la spec NO crea
   requirements nuevos, sólo refactoriza preservando tests"* en
   lugar de *"declárate como `refactor-only`"*. Glosario rápido:
   §3 *Glosario rápido* del methodology.
9. **NUNCA**:
   - Sobreescribir `CLAUDE.md` sustantivo, `.cursorrules`,
     `.cursor/plans/*`, `.copilot-instructions.md`, `.windsurfrules`,
     `.github/chatmodes/`, `.agents/skills/<skill>/` poblada, sin OK
     explícito **adicional al de Phase 4**.
   - Renombrar branches existentes (rompe links).
   - Backfillear specs retroactivas para todo el código legacy
     (anti-patrón §16 *strangler*).
   - Instalar dependencias (npm/pip/nuget). Fuera de alcance.
   - Borrar archivos del proyecto. NUNCA. Mover sí, con `git mv` y
     OK.

---

## Phase 0 — Pre-flight (read-only, ~30 seg)

### P0.0 Resolver el target

El agente determina qué repo es el **target Y** (el repo que va a
ser bootstrappeado) y qué directorio es el **template X** (la
fuente del protocolo y el contenido a copiar).

Resolución del target:

1. IF el comando se invocó como `/adopt <path>` → `target = path
   absoluto del argumento`.
2. IF se invocó como `/adopt .` o sin argumento → `target = cwd`.
3. IF se invocó en lenguaje natural ("adopta el repo en X") →
   extraer path del mensaje, expandir a absoluto.

Resolución del template:

1. IF existe variable de entorno `SYC_AI_DLC_HOME` → `template =
   $SYC_AI_DLC_HOME`.
2. ELSE IF existe `~/.syc/ai-dlc/` → `template = ~/.syc/ai-dlc/`
   (path canonical default).
3. ELSE IF el cwd contiene `ADOPT.md` Y `.agents/commands/` →
   `template = cwd`.
4. ELSE → preguntar al dev por el path del template.

**Validación crítica — NO bootstrap del propio template**:

- IF `target == template` → ⛔ STOP. El dev se confundió e
  intentó bootstrapear el propio template. Reportar: *"El target
  apunta a la propia instalación del template AI-DLC. Eso no
  tiene sentido — el template ya ES AI-DLC. Cambia el target a
  un repo de tu equipo o aborta."*
- IF `target` está **dentro** del `template` (subdirectorio) →
  ⛔ STOP por misma razón.

**Validación de paths absolutos**:

- IF `target == cwd` → modo Y (fallback). Anotar para el reporte
  final: "el agente operó sobre su propio cwd; el contexto
  previo del repo puede haber influido en el comportamiento".
- IF `target != cwd` → modo X→Y (recomendado). Anotar paths
  absolutos.

**Permission preflight** (Claude Code / Cursor / OpenCode):

- El agente declara explícitamente los permisos que necesita:
  - Read recursivo bajo `target`.
  - Bash con `git -C <target>`, `ls <target>`, `cat`, `grep` en
    `target`.
  - Write bajo `target` (sólo Phase 4).
- IF la tool agente pide confirmación de permisos por path →
  esperar OK del dev antes de continuar.

### P0.1 Verificar que el target sea un repo git

```bash
git -C <target> status
```

- IF no es repo git → preguntar al dev si quiere `git -C <target>
  init`. Si no, abortar.
- IF working tree sucio → listar archivos modificados + ofrecer 4
  opciones:
  - **(a)** stash con label `pre-ai-dlc-bootstrap`
  - **(b)** commit con mensaje del dev
  - **(c)** abortar y pedir al dev cerrar el trabajo en vuelo
    primero. *(Recommended si N > 50 archivos modificados — a
    esa escala stash/commit son inseguros.)*
  - **(d)** abortar.

  No asumir cuál. Pedir.

  ⚠️ Si el working tree tiene **cientos** de archivos modificados
  (caso real observado: 511 en `Neo_estampillas`), las opciones
  (a) y (b) son inseguras — un stash gigante o un commit que mezcla
  bootstrap con un feature en vuelo. Default fuerte: opción (c).

### P0.2 Verificar rama segura

```bash
git -C <target> branch --show-current
```

- IF la rama actual matchea `feat/*`, `feature/*`, `feature_*`,
  `bug/*`, `hotfix/*` → STOP. Proponer crear `chore/adopt-ai-dlc`
  desde el default branch.
- IF ya estamos en `chore/adopt-ai-dlc` → continuar.
- IF la rama es la default (`main`/`master`/`pruebas`/etc.) →
  proponer crear `chore/adopt-ai-dlc` antes de cualquier escritura.

### P0.3 Detectar modo

Reglas (en orden):

1. `.ai-dlc-version` existe al root → modo `--upgrade`.
2. `git log --oneline | wc -l` > 5 Y existe al menos un manifiesto
   de proyecto al root (`package.json`, `*.csproj`, `pyproject.toml`,
   `pom.xml`, `go.mod`, `Cargo.toml`) → modo `--brownfield`.
3. Repo vacío o sólo commit inicial sin manifiestos → modo
   `--greenfield`.
4. Ambiguo → preguntar al dev.

**Reportar al dev**: "Detecté modo `<X>`. ¿Continuamos así o forzamos
otro modo?". Esperar OK antes de Phase 1.

### P0.4 Detectar el default branch

Crítico: el agente NO debe asumir que el default branch es `main`.
Detección dinámica:

```bash
# Canonical via HEAD remoto:
git -C <target> symbolic-ref refs/remotes/origin/HEAD --short 2>/dev/null
# → "origin/main" o "origin/master" o "origin/pruebas" o lo que sea

# Fallback si HEAD remoto no está configurado:
git -C <target> remote show origin 2>/dev/null | grep 'HEAD branch:' | awk '{print $NF}'
```

Casos a manejar:

- IF la detección retorna un valor → reportar al dev y pedir
  confirmación: *"Detecté el default branch como `<X>`. ¿Es esa la
  base correcta para el bootstrap?"*
- IF la detección **falla** (no hay `origin`, HEAD remoto sin
  configurar) → preguntar al dev cuál es el default branch.
  Sospechosos comunes: `main`, `master`, `pruebas`, `desarrollo`,
  `develop`, `production`.
- IF el HEAD remoto apunta a una rama **no estándar** (caso real
  observado en edesk: `chore/remove-layouts`) → reportar como
  anomalía y pedir confirmación enfática (probablemente
  misconfiguration del repo, no decisión deliberada).

Guardar el valor confirmado como `<default-branch>` para usar en
P4.1 al crear `chore/adopt-ai-dlc`.

---

## Phase 1 — Detect (read-only, ~3 min)

Sólo aplica en modos `--brownfield` y `--upgrade`. En greenfield se
saltea esta fase.

El agente construye un mapa mental del repo **antes** de proponer
nada. Todo lo que detecta lo usa para pre-llenar las preguntas de
Phase 2 — distinguiendo siempre **detectado** (con evidencia) vs
**asumido** (sin evidencia, pendiente de confirmar).

### P1.1 Stack técnico

Detectar lenguajes mediante marcadores:

| Marcador | Lenguaje/runtime |
|---|---|
| `*.sln`, `*.csproj`, `nuget.config` | .NET |
| `package.json`, `.nvmrc`, `pnpm-lock.yaml`, `yarn.lock`, `bun.lockb` | Node |
| `pyproject.toml`, `setup.py`, `requirements.txt`, `Pipfile`, `uv.lock` | Python |
| `pom.xml`, `build.gradle`, `*.gradle.kts` | Java/Kotlin |
| `go.mod`, `go.sum` | Go |
| `Cargo.toml`, `Cargo.lock` | Rust |
| `composer.json` | PHP |
| `Gemfile`, `*.gemspec` | Ruby |

Detectar también: build/test tools (scripts en `package.json`,
targets en `Makefile`, `dotnet test`, `pytest.ini`), frameworks
(React/Vue/Angular/Express/NestJS/ASP.NET/Spring/FastAPI/Django),
deploy artifacts (`Dockerfile`, `Chart.yaml`, `kustomization.yaml`,
`azure-pipelines*.yml`, `.github/workflows/`), feeds privados
(scopes `@<org>/*` en `package.json`, `<packageSources>` en
`nuget.config`).

**NO inferir**: NFRs, deploy target final, política de versionado.
Eso queda como TODO en `stack/tech-stack.md`.

### P1.2 AI infra previa — clasificación CRÍTICA

Esta es la sección donde el agente más fácilmente se equivoca.
Hay **dos categorías** distintas de AI infra previa, y se tratan
diferente:

#### Categoría A: AI infra de **tool externo**

Es de la herramienta, no del equipo. El equipo la respeta porque la
herramienta la lee. No se toca, sólo se **espejan reglas codificables**
a `stack/constraints.md`.

| Path | Tool dueño | Acción default |
|---|---|---|
| `.cursorrules`, `.cursor/rules/` | Cursor | NO tocar. Espejar reglas a `stack/constraints.md`. |
| `.cursor/plans/` | Cursor | NO tocar. Coexisten con `specs/`. |
| `.copilot-instructions.md`, `.github/copilot-instructions.md` | GitHub Copilot | NO sobreescribir. Si existe: añadir la línea que apunta a `AGENTS.md`. Si no existe: crearlo como puntero puro. |
| `.github/chatmodes/` | Copilot chatmodes | NO tocar. |
| `.github/prompts/` | Copilot slash menu | **De AI-DLC**, como `.claude/commands/`. Se genera desde `.agents/commands/` con sufijo `.prompt.md`. NO es Categoría A. |
| `.windsurfrules` | Windsurf | NO tocar. Espejar. |
| `.continuerules`, `.continue/` | Continue | NO tocar. |
| `.aider/`, `.aider.conf.yml` | Aider | NO tocar. |
| `.gemini/` | Gemini CLI | NO tocar. |
| `CLAUDE.md` (boilerplate del template) | Claude Code | Sobreescribible si es boilerplate. |
| `CLAUDE.md` (sustantivo, >1 KB con reglas del proyecto) | Claude Code | NO tocar. Crear `AGENTS.md` aparte (sub-protocolo abajo). |
| `AGENTS.md` previo | Estándar abierto multi-tool | **Sub-protocolo de 4 categorías** (ver abajo). |

**Lista de exclusión** — dirs/archivos estándar NO-AI que la
heurística Categoría B podría falsamente clasificar:

- `.vscode/`, `.idea/`, `.devcontainer/`, `.editorconfig`,
  `.run/`, `.fleet/` — config de IDE.
- `node_modules/`, `__pycache__/`, `bin/`, `obj/`, `target/`,
  `dist/`, `build/`, `.next/`, `.nuxt/` — outputs de build.
- `.git/`, `.gitattributes`, `.gitmodules`, `.husky/` — git infra.
- `.github/` (excepto `chatmodes/`, `copilot-instructions.md` y
  `prompts/`) — CI/CD config genérica. **`prompts/` no se excluye**: es
  el menú de slash commands de Copilot y lo escribe AI-DLC. Excluir
  `.github/` entero es lo que dejó a Copilot sin un solo comando hasta
  v0.49, sin ningún error visible.

#### Sub-protocolo `AGENTS.md` previo (4 categorías)

`AGENTS.md` es asimétrico con `CLAUDE.md`: lo leen TODAS las tools
agente al arrancar (Claude Code, Cursor, OpenCode, Codex, Continue,
Aider). Si AI-DLC sobreescribe un AGENTS.md previo, el dev pierde
toda la orientación que sus tools tenían. Estrategia per categoría:

| Cat | Heurística | Acción default |
|---|---|---|
| **A.1 Boilerplate** | < 500 B, sólo TODOs, headers vacíos. | Reemplazar con el de AI-DLC sin preguntar — es nada que preservar. |
| **A.2 Partial AI-DLC** | Referencia `.agents/commands/`, `stack/`, `repo-config.yaml`, sección `Bootstrap`, etc. Adopción AI-DLC previa incompleta. | Modo `--upgrade`: diff + apply cambios incrementales. NO reemplazar — preservar configuración del equipo. |
| **A.3 Otro standard** | Estructurado con otro framework (openai-agents, agents.md openai spec, etc.). No referencia AI-DLC. | **Appended-section** (ver abajo). |
| **A.4 Custom sustantivo** | Prosa libre o estructurado pero no de un framework conocido — el equipo lo escribió a mano. | **Appended-section** (ver abajo). |

**Estrategia "appended-section"** (para A.3 y A.4):

El agente NO toca lo que está arriba en AGENTS.md. **Agrega un
único bloque al final** con bordes explícitos y sentinels:

```markdown
[... contenido del equipo intacto ...]

---

<!-- ai-dlc:section-start v=0.170 -->
## AI-DLC Protocol

Este repo adopta AI-DLC (v0.170). **Las secciones
de arriba son del equipo y tienen precedencia** para conflictos.

- Slash commands en `.agents/commands/` (ver tabla abajo).
- Stack y convenciones en `stack/`.
- Config operacional en `repo-config.yaml`.
- Protocolo del agente: ver `ai-dlc-methodology.md` §§ 6, 11.

[tabla de slash commands disponibles]

<!-- ai-dlc:section-end -->
```

> **Importante para el agente que ejecuta Phase 4**: reemplazar
> `0.170` por la versión real leída del frontmatter
> de `ai-dlc-methodology.md` (ej. `0.19`). NUNCA escribir
> `0.170` literal en el AGENTS.md del target — eso
> rompe el matching del `--upgrade` futuro que busca el sentinel
> por valor de versión.

Justificación:

- **Cero merge semántico**. El agente NO parsea ni reorganiza el
  contenido del equipo. Sólo append.
- **Border explícito** con comentarios sentinel
  (`ai-dlc:section-start v=<version>` / `end`). Un `--upgrade`
  futuro puede reemplazar SOLO ese bloque sin tocar el resto.
- **Precedencia declarada**: si el equipo tiene "auto-commit" y
  AI-DLC tiene "PR-only", la regla del equipo gana — el bloque
  AI-DLC lo declara explícitamente.
- **Una sola fuente de verdad para las tools** (siguen leyendo
  AGENTS.md). NO hay archivos paralelos.
- **Reversible quirúrgicamente**: borrar el bloque entre los
  sentinels deja AGENTS.md exactamente como estaba.

**Pedir OK explícito** antes de hacer el append. Si el dev rechaza:
NO modificar AGENTS.md. Reportar al dev que tendrá que documentar
la coexistencia manualmente (ej. agregar pointer a
`.agents/commands/` cuando le convenga).

#### Higiene del AGENTS.md producido por AI-DLC

Cuando el agente bootstrap **produce** un AGENTS.md (Cat A.1
reemplazo) o un appended-section (Cat A.3/A.4), aplica un target de
tamaño: **≤ ~100 líneas substantivas** (excluye blank lines,
separators, sentinels y tablas-catálogo de slash commands).

**Por qué**:

- AGENTS.md lo lee el modelo en **toda** invocación de cualquier tool
  (Claude Code, Cursor, OpenCode, Codex). Cada regla compite por
  atención. Un AGENTS.md largo se vuelve ruido — los devs lo ignoran,
  las tools lo cargan igual y el modelo lo prioriza peor.
- AI-DLC ya tiene archivos canonical donde viven los detalles:
  `.agents/commands/<name>.md` (bodies de slash commands), `stack/*`
  (lenguaje, convenciones, constraints), `repo-config.yaml`
  (trackers, ambientes, runtime), `ai-dlc-methodology.md` por sección.
  AGENTS.md es **índice + reglas raíz**, no manual.

**Auto-check al cerrar Phase 4 (EXECUTE)**:

1. Contar líneas substantivas del AGENTS.md (o del bloque entre
   sentinels en el caso appended-section).
2. Si > ~100: reportar al dev con candidatos a mover:

   | Contenido | Dónde debería vivir |
   |---|---|
   | Body detallado de un slash command | `.agents/commands/<name>.md` |
   | Convenciones de stack (lenguaje, framework, naming, deps) | `stack/patterns.md`, `stack/constraints.md` |
   | Detalle de tracker / ambientes / runtime | `repo-config.yaml` |
   | Justificación / "why" / referencias al methodology | Linkear al `§` correspondiente, no inlinear |
   | Plantillas de spec/PR | Apéndices A–I de `ai-dlc-methodology.md`, o `.agents/templates/` |

3. Si la decisión del dev es "déjame el extra inlineado": OK,
   registrar la excepción en Phase 5 con la razón. El target es
   **default disciplinado, no bloqueo**.

> **Estado actual del template**: el `AGENTS.md` de
> `<AI_DLC_REPO>/template/` mismo está por encima del target (~460
> líneas, bracketeado con sentinels desde v0.21). Deuda conocida —
> el agente bootstrap NO replica esa verbosidad cuando produce
> AGENTS.md en repos target. Trimming del template propio es ítem
> separado del backlog.

**Conflictos de protocolo** (caso ortogonal):

Independiente del merge de archivos, puede haber **conflictos
semánticos** entre el protocolo previo del equipo y el de AI-DLC
(auto-commit vs PR-only, branch naming, commit format, etc.). El
agente:

1. Detecta conflictos comparando keywords/patterns conocidos
   (`auto-commit`, `PR-only`, `feat/` vs `feature/`,
   `Co-authored-by:`, etc.).
2. Los lista en el plan como **OPEN_QUESTION** explícito.
3. NO los resuelve automáticamente.

#### Wrappers Categoría A que apuntan a Categoría B

Caso real observado (Neo Estampillas): un dir Categoría A
(`.cursor/commands/`, `.claude/commands/`) contiene un archivo
que es un **wrapper de texto** apuntando a un canonical en un dir
Categoría B (`.ai-integration/commands/`). Ejemplos del wrapper:

```markdown
# figma-make-integration (wrapper Cursor)

Lee y ejecuta el procedimiento definido en:
.ai-integration/commands/figma-make-integration.md
```

El protocolo trata directorios enteros como A o B, pero aquí el
archivo individual ES Categoría B disfrazada (un puente al
canonical custom interno).

**Sub-protocolo archivo-por-archivo**: para cada `.md` en dirs
Categoría A `commands/`, leer las primeras 20 líneas y detectar
si es un wrapper a Cat B:

- Heurística: contiene path relativo a un dir Categoría B
  detectado, y/o contiene la palabra "wrapper" en el header.
- IF wrapper a Cat B confirmado:
  - El canonical de Cat B se migra a `.agents/commands/<X>.md`
    (consolidación normal Cat B).
  - El wrapper de Cat A se REEMPLAZA por symlink al canonical
    AI-DLC: `.cursor/commands/<X>.md →
    ../../.agents/commands/<X>.md`.
  - Esto **elimina el drift por construcción** (un solo archivo
    canonical, dos vistas linkeadas).
  - Es la única excepción documentada a "NO tocar Categoría A".
    Pedir OK explícito.

#### Categoría B: AI infra **custom interna del equipo**

Esto es lo que el equipo construyó internamente intentando
estandarizar — directorios y archivos que **no son de ninguna
herramienta de tercero**. Son intentos previos de hacer
spec-driven / agent-instructions / standards. **AI-DLC reemplaza
esto: el equipo quería esa estandarización, AI-DLC la trae más
completa.**

Heurística para detectarlo:

1. Directorio AI-like al repo que **no aparece en el catálogo de la
   Categoría A**. Ejemplos reales observados: `.ai-integration/`,
   `.team-prompts/`, `ai-docs/`, `prompts/`, `agent-instructions/`.
2. Contiene `commands/`, `prompts/`, `rules/`, `agents/`, o `.md`
   que son claramente prompts/instrucciones (no docs del producto).
3. NO está documentado como dependencia de una herramienta externa
   (no aparece en `package.json`, `.gitignore` muestra que se
   commitea, etc.).

**Acción default para Categoría B**: **proponer consolidación en
AI-DLC** con clasificación **archivo por archivo** (no migración
genérica del dir entero). Sub-protocolo:

Para cada archivo dentro del dir Cat B, leer las primeras ~50 líneas
y clasificar:

| Indicio en el archivo | Tipo inferido | Destino propuesto |
|---|---|---|
| Frontmatter `---\ndescription: ...\n---` + cuerpo de instrucciones para un agente | **Slash command custom** | `<target>/.agents/commands/<X>.md` (canonical AI-DLC). |
| Tamaño >5 KB, narrativa larga, formato libre, dirigido a humanos (diseñadores, devs, etc.) | **Prompt humano canonical** | `<target>/examples/<topic>/<X>.md` (referencia humana). |
| Marcadores tipo `DATO_PENDIENTE`, `OPEN_QUESTION`, `TODO:`, listas de requirements informales, mermaid diagrams técnicos | **Proto-spec informal** | `<target>/archive/proto-specs/<X>.md` por default. Opcional: migración a `specs/<slug>/` con futuro `/spec-import-plan`. |
| Texto que apunta a otro archivo ("see `path/to/X`") | **Wrapper de texto** | Eliminar; reemplazar con symlink al canonical AI-DLC ya migrado. |
| Reglas codificables (estilo, naming, anti-patterns) | **Reglas** | Append a `<target>/stack/constraints.md`. |
| Meta-doc del propio dir (README.md de `.team-prompts/`, etc.) | **Meta-doc** | Descartar (la consolidación lo hace obsoleto) o mover a `<target>/examples/<topic>/README.md` si tiene contenido útil. |

**Acción siempre pregunta primero**. La heurística da una
**recomendación**, no una decisión. Algunos directorios custom son
load-bearing por otra razón (ej: el equipo tiene un script CI que
los lee). Si el dev dice "este es custom interno y quiero
migrarlo" → proceder con la clasificación archivo-por-archivo. Si
dice "no, déjalo, lo usa otra cosa" → Categoría A.

**Post-consolidación**: el dir Cat B original queda vacío. Default:
`git -C <target> rm -r <dir-cat-B>`. Alternativa: dejar un
`<dir>/MIGRATED.md` apuntando a las nuevas ubicaciones (compat para
refs viejas). Pedir OK al dev.

### P1.3 Memoria de sesión ad-hoc

Listar archivos al root que NO matchean
`README|CHANGELOG|LICENSE|CLAUDE|AGENTS|BOOTSTRAP|BROWNFIELD-CHECKLIST|ADOPT|CONTRIBUTING|CODE_OF_CONDUCT|SECURITY|repo-config`.

Buscar patrones (extensible — agregar al catálogo cuando aparezcan
casos nuevos):

| Patrón de nombre | Tipo probable |
|---|---|
| `SESSION_*`, `NEXT_SESSION_*` | Handoffs |
| `*_HANDOFF.md` | Handoffs |
| `TRACE_*`, `analisis-*`, `analysis-*` | Análisis bug |
| `*_PROGRESS.md`, `*_STATUS.md` | Progreso parcial |
| `TEST_*`, `DEBUG_*`, `*_NOTES.md` | Notas ad-hoc |
| `PLAN_*.md` | Plan informal (refactor, mejora) |
| `YYYY-MM-DD-HHMMSS-*.txt` | **Transcript bruto** de sesión AI |
| `YYYY-MM-DD-*.md` | Notas datadas |

> Nota crítica: el catálogo incluye **`.txt`**, no sólo `.md`.
> Algunos clientes AI (Claude Code, OpenCode, Codex) exportan
> conversaciones completas a `.txt` con timestamp-prefix. Esos
> archivos son frecuentemente 50–200 KB cada uno y viven al root.

### P1.3.b Escaneo de leaks (secretos trackeados + artefactos publicables)

**Obligatorio**, no opcional. Patrón recurrente observado en repos
reales: secretos commiteados (`.env` trackeado con tokens, JWT en
transcripts) y estructura interna que se publica sin querer.

**(a) Secretos trackeados.** Detectar archivos sensibles que git
está versionando:

```bash
git -C <target> ls-files | grep -iE '(^|/)\.env($|\.)|secrets?\.|\.pem$|\.pfx$|credential'
# Si .env aparece como TRACKED → leer su contenido y buscar valores reales
git -C <target> ls-files --error-unmatch .env 2>/dev/null && \
  grep -iE 'TOKEN|SECRET|PASSWORD|KEY|PAT' <target>/.env
```

IF se encuentra un secreto trackeado → emitirlo como **OPEN_QUESTION
de ALTA PRIORIDAD** con remediación estándar (el bootstrap NO
reescribe historia ni untrackea sin OK explícito):

1. **Rotar/invalidar el secreto** (asumirlo comprometido — está en la
   historia git). *(Si el dev confirma que ya expiró/es inválido,
   este paso se omite.)*
2. `git rm --cached <archivo>` (deja de trackearlo; el archivo local queda).
3. Agregar el patrón al `.gitignore` (este bootstrap ya lo hace para `.env`).
4. Crear `<archivo>.example` con las claves y valores vacíos.
5. Opcional: purgar de la historia (`git filter-repo`) — coordinado, reescribe historia.

**(b) Leak de publicación (sólo `repo_type: library`).** Si el repo
publica a un registry, el `files: [...]` de `package.json` (o
`.npmignore`, o el equivalente nuget/pip) define qué se empaqueta.
Verificar que **ningún artefacto AI-DLC ni doc interno caiga en un
directorio publicado**:

```bash
# ¿Qué directorios publica el paquete?
grep -A8 '"files"' <target>/package.json
```

Caso real: `files: ["dist", "docs"]` publica todo `docs/`. Un
`docs/ado-map.md` (mapa de la jerarquía ADO del discover-first) o
cualquier doc interno ahí adentro **se publicaría al registry**,
filtrando estructura interna. → Colocar artefactos internos AI-DLC
(mapas ADO, output de discover-first, notas) **fuera** de los
directorios publicados (raíz, `.org/`, o `archive/`), o agregarlos a
`.npmignore`. Anotarlo en el plan (Phase 3) y respetarlo en Phase 4.

### P1.4 Branches y flujo

```
git branch -a
git remote show <origin>  # opcional, para HEAD remoto
```

- Listar branches locales + remotas.
- Identificar **candidatas a ambiente** (matchean catálogo:
  `main`, `master`, `prod`, `production`, `pruebas`, `qa`,
  `staging`, `preprod`, `uat`, `develop`, `desarrollo`, `dev`,
  `test`).
- Identificar **convención de feature branches** contando cuántas
  ramas matchean cada patrón (`feat/`, `feature/`, `feature_`,
  `feature-`, etc.). Reportar drift.
- HEAD remoto: si NO es `main`/`master`, reportar (info, no
  bloqueo).

**Nunca asumir que una rama candidata ES un ambiente.** El dev
confirma cuál es cuál en Phase 2.

#### Branch policies del default branch

Detectar (best-effort) policies que afectarán el PR del bootstrap:

- **Azure DevOps**: si está disponible `az repos policy list
  --branch <default-branch>` (requiere `az login` previo) — listar
  las policies activas (require reviewers, build verde, work item
  linkeado, comment resolution).
- **GitHub**: si está disponible `gh api repos/<owner>/<repo>/branches/<default-branch>/protection`
  — extraer required reviewers, status checks, etc.
- **CODEOWNERS**: leer `.github/CODEOWNERS`, `CODEOWNERS` al root,
  `docs/CODEOWNERS` — listar dueños del path donde el bootstrap
  escribe.
- **Pipelines requeridos**: leer `azure-pipelines*.yml` y
  `.github/workflows/*.yml` para anticipar qué builds se van a
  disparar al abrir el PR.

IF la detección falla (no CLI, no permisos, no estructura
estándar): NO bloquea. Anotar como "policies no detectables —
revisar al abrir el PR".

Estas detecciones NO modifican el comportamiento del bootstrap —
sólo enriquecen el reporte final (P5.1) para que el dev sepa qué
requisitos va a enfrentar al mergear.

### P1.5 Estructura del repo (single / monorepo)

Listar sub-directorios con manifiesto propio.

- 1 manifiesto al root → **single-project**.
- N manifiestos del mismo tipo → **monorepo homogéneo**.
- N manifiestos de tipos distintos → **monorepo heterogéneo**.
  Inferir `type` por sub-proyecto (service / library /
  frontend-app / infra) o marcar `TBD`.
- Buscar regla de **feature parity** en `CLAUDE.md` /
  `.cursorrules` (string match "parity"/"feature parity"/
  "espejado"/"100%"). Si aparece, proponer
  `cross_cutting_specs: true` en Phase 2.

### P1.6 Pipelines y multi-tenant fan-out

Leer pipelines en `azure-pipelines*.yml`, `.github/workflows/`,
`.gitlab-ci.yml`, `Jenkinsfile`, etc.

- Detectar **nombres de ambientes** en el pipeline (`-test.yml`,
  `-qa.yml`, `-prod.yml`). Comparar con branches detectadas en
  P1.4. Si los nombres difieren (branch `pruebas` → pipeline `test`),
  reportar.
- Detectar **fan-out multi-tenant**: variables groups o
  parámetros con patrón `<repo>-<tenant>-<env>` (ej.
  `neo-estampillas-putumayo-test`, `neo-estampillas-guajira-test`).
  Si aparece, anotar para preguntar en Phase 2.
- Detectar **proxy corporativo** (`httpProxy`, `httpsProxy` en el
  pipeline). Anotar para `stack/security.md`.

### P1.6.b Tracker existente (best-effort, v0.17)

Si se detectó uso de Azure DevOps (vía pipelines `azure-pipelines*.yml`,
referencias a `dev.azure.com`, presencia de `az` CLI, etc.) o si el
dev confirma que hay ADO en uso, el agente puede ofrecer
listar la jerarquía existente para tener contexto. Read-only:

```bash
# Si hay az CLI disponible y dev autorizó:
az boards query --org <org> --project <project> \
  --wiql "SELECT [Id], [Title], [Work Item Type], [State]
          FROM workitems
          WHERE [System.WorkItemType] IN ('Epic', 'Feature')
          AND [System.State] <> 'Closed'"
```

Reportar al dev:

> "Detecté tracker `azure-devops` y quieres que liste la jerarquía
> activa del project para dar contexto antes de la primera spec?
>
> (a) Sí, lístame Epics + Features activas. *(Recommended si vas a
>   crear specs nuevas pronto.)*
> (b) No, sólo configurar `repo-config.yaml > trackers[]` y seguir."

Si (a): listar y guardar como contexto para Phase 2. NO crear nada,
NO modificar nada. Sólo enriquece la entrevista (el dev ya sabe qué
Features existen cuando llegue a `/spec-new` el primer feature).

Si no hay `az` CLI ni MCP disponible: documentar como
`OPEN_QUESTION: 'verificar acceso a ADO antes de primera spec'` y
seguir. El bootstrap no depende de esto.

### P1.7 Reporte de Phase 1

Antes de pasar a Phase 2, el agente emite un resumen estructurado:

```markdown
# Detect — resumen

**Stack**: <lenguajes + frameworks + deploy artifacts>

**AI infra previa**:
- Categoría A (externas, no tocar): <lista>
- Categoría B (custom interna del equipo, propondré consolidar):
  <lista con evidencia>

**Memoria de sesión ad-hoc**: <conteo y patrones>

**Branches**: <ambientes candidatos> | drift de convención: <sí/no>

**Estructura**: single | monorepo homogéneo | monorepo heterogéneo

**Pipelines**: <ambientes detectados> | multi-tenant: <sí/no>

**Modo**: <greenfield | brownfield | upgrade> (confirmado en P0.3)
```

> "¿El resumen refleja correctamente el repo? Si hay errores aquí,
> el resto sale mal. ¿Algún ajuste antes de Phase 2?"

Esperar OK explícito. Si el dev corrige algo, ajustar el modelo
mental antes de seguir.

---

## Phase 2 — Clarify (entrevista, ~10 min)

Una pregunta a la vez. Para cada decisión:

1. Citar evidencia detectada (de Phase 1).
2. 2–4 opciones explícitas.
3. Una marcada `(Recommended)` con la razón.
4. Una opción de salida `OPEN_QUESTION` para diferir.

### Catálogo de preguntas

**Comunes (greenfield + brownfield)**:

- **Q1**: `repo_type` — service / library / frontend-app / infra /
  custom.
- **Q2**: `trackers[]` — uno o más trackers con role (v0.17). Tres
  sub-preguntas si aplica:

  - **Q2.a Tracker `owner`** (UN solo): el project del equipo que
    desarrolla. Tipo: azure-devops / github-issues / jira / linear
    / none. Para azure-devops: org, project, default_area_path.
  - **Q2.b Stakeholders** (N, opcional): ¿hay otro equipo cliente o
    receiving team cuyos work items vas a citar? Si sí, declarar
    cada uno (type + org + project) con `role: stakeholder`. Caso
    típico SYC: equipo X desarrolla para equipo Y → declarar Y como
    stakeholder.
  - **Q2.c `creation_mode`** del tracker owner: discover-first
    (default brownfield si ya hay jerarquía ADO) / assisted (default
    greenfield) / auto (con MCP) / manual.
  - **Q2.d `work_item_mapping`** (opcional): si el equipo no usa
    Features y trabaja con User Stories, declarar `feature_to:
    "User Story"` en lugar del default `Feature`.
- **Q3**: `environments` — confirmar candidatos de P1.4. NO inventar
  ambientes que el repo no usa.
- **Q4**: `promotion_path` — orden de los ambientes confirmados.
- **Q4.bis — Rama base del bootstrap**. El default detectado en
  P0.4 es `<default-branch>` (típicamente `main`). Pero la rama
  base del **bootstrap chore** puede no ser el default si el equipo
  trabaja con flujo de promoción estricto. Opciones:

  > "El bootstrap va a crear `chore/adopt-ai-dlc` y todo lo
  > escrito vivirá ahí. ¿Desde qué rama la corto?
  >
  > **(a)** `<default-branch>` directo (típicamente `main`). El PR
  > será `chore/adopt-ai-dlc → <default>`. Las branch policies
  > actúan normal. *(Recommended para chores — son cambios de
  > configuración, no de código, no necesitan validación en
  > ambientes.)*
  >
  > **(b)** La primera rama del `promotion_path` (típicamente
  > `pruebas`). El bootstrap viaja por el flujo normal: `chore →
  > pruebas → qa → main`. Más conservador, más PRs. Recomendado
  > si el equipo es estricto con cualquier cambio que toque main.
  >
  > **(c)** Otra rama específica que me indiques.
  >
  > ¿Cuál?"

  Default fuerte: **(a)**. Excepción: si el repo declara una policy
  de "todo cambio pasa por promotion_path" en `repo-config.yaml`
  o el dev lo confirma, usar **(b)**.

- **Q5**: `runtime` — openshift / k8s / npm-registry / static-host
  / none / TBD.
- **Q6**: `branch_pattern` — `feat/` (default) o el patrón histórico
  del repo (`feature/`, `feature_`, etc.).
- **Q7**: **disciplina de diseño** — ¿hay interlocutor de diseño?
  (sí/no). Si sí: escribir el bloque `disciplines.design` con su
  `owner` (§12). Preguntar por la **persona**, no por la herramienta:
  ningún gate ni comando puede depender de cuál se use, y
  `tooling` es opcional y de forma libre. `design_service` se sigue
  aceptando como alias legacy en repos ya adoptados, pero **no se
  escribe en adopciones nuevas**.
- **Q8**: Owner team + lead email + service name slug.

**Sólo brownfield**:

- **Q9 — Categoría B AI infra** (la pregunta importante NUEVA).
  Para cada directorio detectado en P1.2 como Categoría B:

  > "Detecté `<dir>` con `<conteo>` archivos (`<lista corta>`).
  > No matchea ningún tool conocido (Cursor, Copilot, Windsurf,
  > Aider, ...). Heurística sugiere que es un **intento interno
  > del equipo** de estandarizar prompts/instrucciones.
  >
  > **(a)** Es custom interno y quiero consolidarlo en AI-DLC. Voy
  >   a proponer migración: prompts → `.agents/commands/` o
  >   `examples/`, reglas → `stack/constraints.md`. *(Recommended si
  >   el directorio contiene `commands/`, `prompts/`, `rules/` con
  >   `.md`s que son claramente instrucciones para agentes.)*
  > **(b)** Es de un tool externo / lo usa otra cosa que no detecté.
  >   No tocar. Lo trato como Categoría A.
  > **(c)** OPEN_QUESTION — decidimos después.
  >
  > ¿Cuál aplica para `<dir>`?"

- **Q10**: Specs location en monorepo — `<sub>/specs/` per
  sub-proyecto vs `specs/` al root con `cross_cutting_specs: true`.
- **Q11**: Memoria de sesión ad-hoc — archive / migrate-to-specs /
  leave. Default recomendado: **archive**.
- **Q12**: `CLAUDE.md` existente sustantivo — dejar intacto (default)
  / extraer reglas a `stack/` (costoso) / reemplazar (sólo si
  boilerplate).
- **Q13**: `.cursorrules` y similares — espejar a
  `stack/constraints.md` (default) / no espejar.
- **Q14**: Pipelines con nombres distintos a branches — declarar
  ambos (`branch: pruebas` / `env_name: test`) o normalizar.
- **Q15**: Multi-tenant fan-out — si se detectó, declarar
  `tenants:` en `repo-config.yaml > environments[].fan_out`.
- **Q16**: Skills ya instaladas — respetar todas (default) /
  auditar.
- **Q17**: Planes informales / refactor (`PLAN_*.md`, etc.) —
  archive / migrar a `specs/<slug>/` modality `refactor-only` /
  leave.

> El agente NO hace las 17 preguntas siempre. Si en P1 no se detectó
> evidencia para una pregunta, la saltea. Ej.: si no hay AI infra
> Categoría B detectada, Q9 no aplica.

### Reglas de Phase 2

- Tras cada respuesta, el agente confirma:
  > "Anotado: `<campo> = <valor>`. ¿Siguiente?"
- Si el dev marca `OPEN_QUESTION`, el agente anota el campo con
  `# OPEN_QUESTION: <razón>` para que aparezca en el plan.
- Si una respuesta implica acciones reversibles (mover archivos,
  espejar reglas), el agente las anota como pendientes — NO las
  ejecuta hasta Phase 4.

---

## Phase 3 — Propose (escribir plan en disco)

El agente escribe **un solo archivo**: `.ai-dlc-adoption-plan.md`
al root del repo destino. Este archivo es el contrato — todo lo
que Phase 4 va a hacer está aquí.

### Formato del plan

```markdown
---
generated_at: <ISO8601>
generated_by: <agent name>
target_repo: <repo name>
target_branch: chore/adopt-ai-dlc
methodology_version: <v>
template_source: <path>
mode: brownfield | greenfield | upgrade
---

# Plan de adopción AI-DLC

## Decisiones tomadas (Phase 2)

<tabla>

## OPEN_QUESTIONS pendientes

<lista — sin esto el bootstrap igual aplica, pero el dev debe
resolver antes del primer merge>

## Archivos a CREAR

<lista exacta de paths + breve descripción>

## Archivos a MODIFICAR

<lista — sólo modificaciones quirúrgicas, ej. agregar líneas a
.gitignore, espejar reglas a stack/constraints.md>

## Archivos a MOVER

<lista con `git mv` source → dest>

## Archivos a CONSOLIDAR (Categoría B AI infra)

<si aplica — qué viene de `.ai-integration/`/etc., a dónde va>

## Archivos NO TOCADOS (respetar lo existente)

<lista — confirma explícitamente qué queda intacto>

## Commit propuesto

```
chore: adopt AI-DLC v<version> [bootstrap]

<bullets>

Methodology: see ai-dlc-methodology.md v<version>
```

## Reversión

```bash
git checkout <branch-original>
git branch -D chore/adopt-ai-dlc
```

## Siguientes pasos post-merge

<lista — PR, primer /spec-new, llenar TODOs de stack/, etc.>
```

### STOP — esperar OK explícito

Al terminar de escribir el plan, el agente para y dice:

> "Plan escrito en `.ai-dlc-adoption-plan.md`. Revísalo. Si está OK,
> dime '**aplica el plan**' y procedo a Phase 4. Si quieres
> cambios, indícalos y reescribo el plan antes de aplicar."

**NO ejecutar Phase 4 sin esa confirmación explícita.** Aunque el
dev haya dicho "sí" implícitamente en Phase 2, debe haber un sí
explícito sobre el plan escrito.

---

## Phase 4 — Execute (escribir, ~2 min)

Sólo se ejecuta tras OK explícito de Phase 3.

### P4.1 Crear/cambiar a branch dedicada

Usar `<base-branch>` confirmado en Q4.bis (default a `<default-branch>`
resuelto en P0.4):

```bash
# Asegurar que la base está actualizada del remoto
git -C <target> fetch origin <base-branch>

# Crear la rama del bootstrap desde la base
git -C <target> checkout -b chore/adopt-ai-dlc origin/<base-branch>
```

Si la branch `chore/adopt-ai-dlc` ya existe localmente (re-run):
preguntar antes — puede tener bootstrap previo en progreso. Opciones:

- Continuar sobre la branch existente (re-aplicar plan).
- Borrarla y empezar de cero (`git branch -D chore/adopt-ai-dlc`).
- Renombrar con sufijo numérico (`chore/adopt-ai-dlc-2`).

**NUNCA hacer**: `git push origin <base-branch>`, `git checkout
<base-branch>` para modificarlo, `git merge` que toque la base.
El default branch del repo es **sagrado** durante todo Phase 4.

### P4.2 Aplicar writes en orden

Todas las rutas son **absolutas al target**. En modo X→Y el agente
opera sobre `<target>` (path absoluto resuelto en P0.0); en modo Y
fallback el agente opera sobre el cwd. Orden estricto:

1. **Crear estructura base** copiando de `<template>/AGENTS.md`,
   `<template>/.agents/commands/`, `<template>/.agents/templates/`,
   `<template>/scripts/spec-lint.{sh,ps1}`, etc. a `<target>/`. NO
   copiar archivos que ya existen en el target salvo que el plan lo
   diga explícitamente.
2. **AGENTS.md previo**: aplicar el sub-protocolo de 4 categorías
   (P1.2):
   - A.1 Boilerplate → reemplazar.
   - A.2 Partial AI-DLC → modo `--upgrade` (diff incremental).
   - A.3 Otro standard / A.4 Custom sustantivo → **appended-section
     con sentinels**:
     ```bash
     # Append al final del AGENTS.md previo:
     cat >> <target>/AGENTS.md <<'EOF'

     ---

     <!-- ai-dlc:section-start v=<version> -->
     ## AI-DLC Protocol
     <contenido AI-DLC con tabla de slash commands>
     <!-- ai-dlc:section-end -->
     EOF
     ```
   - Cualquier categoría con OK pendiente del dev: ⛔ no escribir
     todavía.
3. **Reemplazar placeholders** en los archivos copiados:
   - `greenfield`, `TBD`, `TBD` →
     valores capturados en Phase 2.
   - `0.170` → valor del campo `version:` del
     frontmatter de `ai-dlc-methodology.md`. **Crítico**: el AGENTS.md
     del template trae sentinels `<!-- ai-dlc:section-start
     v=0.170 -->`; si no se substituye, el sentinel
     queda con el placeholder literal y `--upgrade` futuro NO matchea.
     Aplicar a todos los archivos copiados, no sólo a AGENTS.md.
4. **Escribir `<target>/repo-config.yaml`** con los valores
   negociados, marcando `# OPEN_QUESTION:` cualquier campo no
   resuelto.
5. **Pre-llenar `<target>/stack/`** con lo detectado en Phase 1.
   Dejar el resto en TODO.
6. **Espejar reglas** de `<target>/.cursorrules` /
   `<target>/.copilot-instructions.md` / etc. a
   `<target>/stack/constraints.md` si el dev lo aceptó en Q13.
7. **Consolidar Categoría B** (si aplica): mover/copiar contenido
   de `<target>/.ai-integration/` / `<target>/.team-prompts/` /
   etc. a las ubicaciones AI-DLC. Usar `git -C <target> mv` para
   preservar historia.
8. **Reemplazar wrappers Cat A → Cat B** (si aplica, sub-protocolo
   P1.2): los wrappers de texto en `.cursor/commands/X.md` que
   apuntan a `.ai-integration/commands/X.md` se reemplazan por
   symlinks al nuevo canonical `.agents/commands/X.md`.
9. **Mover memoria de sesión** (si Q11=archive) a
   `<target>/archive/session-history/` con `git -C <target> mv`.
10. **Crear symlinks/wrappers**. Son **dos** conjuntos, no uno:

    - `<target>/.claude/commands/*.md` → `../../.agents/commands/*.md`
      (12 slash commands).
    - `<target>/.agents/commands/adopt.md` → `../../ADOPT.md` (el
      canonical del propio `/adopt`).

    La fuente de verdad de qué es symlink es el **modo del índice del
    template** (`git -C <template> ls-files -s template/ | awk '$1=="120000"'`),
    no una lista hardcodeada — así los symlinks nuevos se replican solos.

    ⚠️ **Nunca copiar un symlink con `cp`**: en POSIX `cp` sigue el link y
    duplicaría el contenido del destino (ej. `adopt.md` pasaría de 14 B a
    los ~75 KB de ADOPT.md), lo que además rompería cada `--upgrade`
    posterior por hash divergente. Los symlinks se materializan aparte del
    copiado del payload.

    **Detección de plataforma** (POSIX vs Windows sin developer mode):

    ```bash
    if [[ "$(uname)" == "Darwin" || "$(uname)" == "Linux" ]]; then
      ln -s "$link_target" "$TARGET/$rel"
      git -C "$TARGET" add "$rel"
    else
      # Windows con core.symlinks=false: wrapper de texto en el working
      # tree + modo 120000 en el índice vía plumbing. El repo queda
      # correcto para quien clone en POSIX.
      printf '%s' "$link_target" > "$TARGET/$rel"
      blob=$(printf '%s' "$link_target" | git -C "$TARGET" hash-object -w --stdin)
      git -C "$TARGET" update-index --add --cacheinfo "120000,$blob,$rel"
    fi
    ```

11. **Escribir `<target>/.ai-dlc-version`** — manifiesto que habilita
    `--upgrade` futuros con safety per-archivo.

    **Crítico — orden de operaciones**: este paso corre **al final** de
    P4.2, **después** de copiar archivos, substituir placeholders y
    consolidar Cat B. Los `sha256_at_install` reflejan el contenido
    **final en disco** (post-substitución, post-merge). Si se calculan
    antes, el primer `--upgrade` detectará "el usuario modificó esto"
    falsamente (lo que cambió fue la substitución, no el usuario).

    **Para `bracketed`**: `sha256_at_install` se calcula sobre el
    **bloque entre sentinels**, no sobre el archivo completo. Pseudo:

    ```
    open  = índice de "<!-- ai-dlc:section-start v=<X> -->" en archivo
    close = índice de "<!-- ai-dlc:section-end -->" en archivo
    bracketed_content = file[open+len(open_marker) : close]
    sha256_at_install = sha256(bracketed_content)
    ```

    Schema:

   ```yaml
   # Versión y trazabilidad
   methodology_version: <v>           # del frontmatter de ai-dlc-methodology.md
   template_version: <v>              # tag/sha del syc-stack-template usado
   applied_at: <ISO8601>
   applied_by: <git user.email>
   mode: brownfield                   # greenfield | brownfield | upgrade
   installer: adopt                   # adopt (agente) | ai-dlc-init | ai-dlc-upgrade

   # Placeholders sustituidos al instalar (v0.23) — los reusa
   # ai-dlc-upgrade para re-sustituir en los archivos nuevos.
   # Sin este bloque (instalaciones < v0.23), el upgrade avisa y
   # reporta los archivos que queden con {{...}} sin resolver.
   placeholders:
     SERVICE_NAME: <valor>
     OWNER_TEAM: <valor>
     LEAD_EMAIL: <valor>

   # Decisiones de adopción
   plan_path: .ai-dlc-adoption-plan.md
   decisions_summary: { ... }
   open_questions: [ ... ]

   # ─── files: manifiesto per-archivo (habilita --upgrade safe) ──
   # role:
   #   owned       — AI-DLC manda. Si el usuario lo modifica, --upgrade
   #                 muestra diff y pide decisión (take-new / keep-mine
   #                 / merge-manual).
   #   bracketed   — AI-DLC sólo toca dentro de sentinels
   #                 <!-- ai-dlc:section-start v=<X> -->...<:section-end -->.
   #                 Afuera = territorio del usuario, intocable.
   #   template    — Usuario llena el contenido. --upgrade lo copia
   #                 SÓLO SI FALTA; si ya existe no lo toca, sea cual
   #                 sea su contenido. NO hay additive merge: un bloque
   #                 o clave nueva de una versión posterior NO llega
   #                 por --upgrade, se agrega a mano. Ver §16
   #                 *Limitación conocida del role `template`*.
   #   user        — Nunca tocado por --upgrade.
   #
   # sha256_at_install: hash del archivo (o del bloque entre sentinels
   #   en el caso bracketed) en el momento del install/último upgrade.
   #   Sirve para detectar cambios del usuario.
   files:
     AGENTS.md:
       role: bracketed
       sentinel_version: <v>          # versión declarada en el sentinel
       sha256_at_install: <hash-del-bloque-bracketeado>
     CLAUDE.md:
       role: owned
       sha256_at_install: <hash>
     repo-config.yaml:
       role: template
       sha256_at_install: <hash>
     ADOPT.md:
       role: owned
       sha256_at_install: <hash>
     BOOTSTRAP.md:
       role: owned
       sha256_at_install: <hash>
     BROWNFIELD-CHECKLIST.md:
       role: owned
       sha256_at_install: <hash>
     .agents/commands/spec-new.md:
       role: owned
       sha256_at_install: <hash>
     # ... un entry por cada .agents/commands/*.md
     .agents/templates/spec/requirements.md:
       role: owned
       sha256_at_install: <hash>
     # ... un entry por cada .agents/templates/**/*.md
     .agents/templates/contract/CONTRACT-000.md:
       role: owned
       sha256_at_install: <hash>
     # ... un entry por cada .agents/templates/contract/*.md
     #
     # NOTA: el payload de los instaladores NO se condiciona por
     # `repo_type` ni por capacidad declarada — se arma con
     # `git ls-files template/`. Todo repo recibe todas las plantillas
     # y todos los comandos, igual que ya recibía los `/ado-*` sin
     # tener tracker. Lo que SÍ es condicional es lo que se le exige a
     # una feature (§17 *métrica de control*): cero artefactos, cero
     # ítems de checklist y cero firmantes para quien no declara la
     # capacidad.
     .vscode/settings.json:
       role: template          # `SIM-180` — ver nota abajo
       sha256_at_install: <hash>
     .github/copilot-instructions.md:
       role: owned
       sha256_at_install: <hash>
     #
     # NOTA sobre `.vscode/settings.json` (v0.49). Es el único archivo
     # del payload que NO es de AI-DLC: es del equipo —formateador,
     # debug, exclusiones— y AI-DLC sólo necesita UNA clave dentro,
     # `chat.useAgentsMdFile`. Con `owned` el instalador pisaría las
     # settings del equipo; con `template` no se copia si ya existe, y
     # entonces la clave no llega y **el repo opera sin contrato de
     # agente sin ningún error visible**.
     #
     # Se elige `template` y el fallo se hace RUIDOSO: `ai-dlc-init`
     # avisa en el resumen y `ai-dlc-upgrade` lo lista bajo *Claves
     # pendientes de añadir a mano*. El brownfield lo cubre `D6ter`.
     # La solución de fondo es un `role` que declare propiedad de
     # CLAVES y no de archivos —arreglaría también `.mcp.json`— y toca
     # el schema del manifiesto, así que va aparte.
     .org/contract-types.yaml:
       role: template
       sha256_at_install: <hash>
     scripts/spec-lint.sh:
       role: owned
       sha256_at_install: <hash>
     scripts/spec-lint.ps1:
       role: owned
       sha256_at_install: <hash>
     # Los dos gemelos de `restore-symlinks`, explícitos desde v0.85
     # por el mismo motivo que `spec-lint`: se leen de ejemplo. **La
     # entrega no depende de estar aquí** — el payload se arma con
     # `git ls-files template/` (ver la NOTA de abajo), así que un
     # archivo trackeado llega aunque este manifiesto no lo nombre.
     # Se comprobó al añadir el `.ps1`, contra la sospecha contraria.
     scripts/restore-symlinks.sh:
       role: owned
       sha256_at_install: <hash>
     scripts/restore-symlinks.ps1:
       role: owned
       sha256_at_install: <hash>
     stack/tech-stack.md:
       role: template
       sha256_at_install: <hash>
     stack/README.md:
       role: template
       sha256_at_install: <hash>
     stack/architecture.md:
       role: template
       sha256_at_install: <hash>
     stack/patterns.md:
       role: template
       sha256_at_install: <hash>
     stack/security.md:
       role: template
       sha256_at_install: <hash>
     stack/constraints.md:
       role: template
       sha256_at_install: <hash>
     stack/testing.md:
       role: template
       sha256_at_install: <hash>

   # Archivos que el usuario crea y AI-DLC nunca toca (specs/, .org/
   # contracts publicados, etc.) NO van al manifiesto. La ausencia
   # implica role: user. Esto evita inflar el manifiesto.
   ```

12. **Mover el plan**: `<target>/.ai-dlc-adoption-plan.md` se mueve
    a `<target>/archive/ai-dlc-adoption-plan.md` (queda commiteado
    para auditoría posterior).

### P4.3 NO hacer commit todavía

El agente prepara el commit **propuesto** pero NO lo ejecuta. Reporta
al dev con `git status` + `git diff --stat` y pregunta:

> "Cambios aplicados en `chore/adopt-ai-dlc`. ¿Haces el commit
> ahora? Mensaje propuesto:
>
> ```
> chore: adopt AI-DLC v<v> [bootstrap]
> <bullets>
> ```

> ¿OK o quieres ajustar el mensaje?"

### Invariantes que el agente DEBE respetar durante P4

- IF `<target>/CLAUDE.md` es sustantivo → NO sobreescribir.
- IF `<target>/AGENTS.md` previo es A.3 o A.4 (categorías en P1.2)
  → SÓLO append del bloque entre sentinels `ai-dlc:section-start/end`.
  NUNCA modificar contenido fuera de ese bloque.
- IF `<target>/.cursorrules` etc. existe → NO modificar. Sólo
  espejar si Q13.
- IF `<target>/.agents/skills/<skill>/` poblada → NO remover.
- IF `<target>/stack/<file>.md` ya existe → ofrecer merge (preservar
  contenido del equipo + agregar TODOs faltantes) en lugar de
  sobreescritura.
- IF un write falla → abortar Phase 4 limpio e indicar al dev cómo
  deshacer (`git -C <target> checkout -- .`,
  `git -C <target> clean -fd archive/`, etc.).

---

## Phase 5 — Close (reporte, ~1 min)

### P5.1 Resumen final

Emitir un reporte humano con:

- Branch donde quedó el bootstrap (`chore/adopt-ai-dlc`) y rama
  base usada (`<base-branch>` confirmado en Q4.bis).
- Conteo de archivos: nuevos / modificados / movidos / consolidados
  / respetados intactos.
- Lista de `OPEN_QUESTIONS` con quién/cuándo resolver.
- Lista de archivos NO tocados por respeto.
- **Branch policies detectadas** (de P1.4 sub-fase): qué necesita
  el PR para mergear. Ej.:

  ```
  Para mergear el PR de chore/adopt-ai-dlc → <base-branch>:
  - 1+ reviewer requerido (policy ADO)
  - Build CI verde: azure-pipelines-test.yml
  - Work item linkeado (formato AB#<id>)
  - CODEOWNERS: @team-platform (paths .agents/, stack/)
  ```

  IF las policies no se pudieron detectar: anotar
  *"policies no detectables — revisar al abrir el PR"*.

- Siguientes pasos:
  1. `git -C <target> diff <base-branch>..chore/adopt-ai-dlc`
     para revisar.
  2. Si OK, hacer `git -C <target> push -u origin chore/adopt-ai-dlc`
     **(esta acción la hace el dev, NO el agente)**.
  3. Abrir PR `chore/adopt-ai-dlc → <base-branch>` cumpliendo las
     policies listadas arriba.
  4. **Propagar a las otras ramas de ambiente permanentes** (ver abajo).
  5. Tras merge: primer feature con `/spec-new <slug>`.
  6. Llenar TODOs pendientes en `stack/architecture.md`,
     `stack/security.md`.
- Comando de reversión: `git -C <target> branch -D chore/adopt-ai-dlc`.

#### P5.1.b Propagación multi-ambiente del bootstrap

El bootstrap se escribió sobre **una** rama base (Q4.bis, típicamente
el default). Pero si el repo tiene **varias ramas de ambiente
permanentes** (caso real: `main` + `pruebas`, ambas viven para
siempre), la metodología debe vivir en **todas** — si no, las feature
branches cortadas de `pruebas` no tendrían `AGENTS.md`/`.agents/` y el
agente arrancaría sin protocolo.

Para cada rama de ambiente permanente **distinta de la base** (de
`environments[]` confirmados en Q3):

```bash
# El bootstrap es un commit autocontenido; cherry-pick limpio si los
# árboles no divergen (típico en repos donde pruebas == main):
git -C <target> fetch origin <env-branch>
git -C <target> switch -c chore/adopt-ai-dlc-<env-branch> origin/<env-branch>
git -C <target> cherry-pick <bootstrap-sha>   # + cualquier commit de wiring (ej. .mcp.json)
```

Resultado: **un PR por rama de ambiente** (`chore/adopt-ai-dlc → main`,
`chore/adopt-ai-dlc-pruebas → pruebas`). Cada PR respeta sus branch
policies y queda autocontenido. **NO** mergear `main → pruebas` para
propagar (va al revés del `promotion_path` y arrastra commits ajenos).
El push y los PRs los hace el dev (o el hub, si lanzó la adopción), no
el agente. Si los árboles divergen y el
cherry-pick conflictúa, reportar y pedir decisión — no resolver a ciegas.

### P5.2 Archivar el plan

El `<target>/.ai-dlc-adoption-plan.md` ya fue movido en P4.2 paso 12
a `<target>/archive/ai-dlc-adoption-plan.md`. Mencionarlo en el
reporte para que el dev lo encuentre.

### P5.3 Caso especial: dry-run (`--dry-run`)

Si el dev arrancó con `--dry-run`, **no ejecutar Phase 4** en
absoluto. Phase 5 reporta lo que **habría** hecho. El plan en
`.ai-dlc-adoption-plan.md` queda al root sin commiteo.

---

## Modo `--upgrade` — protocolo detallado

Cuando el repo ya tiene `.ai-dlc-version` y hay una versión más nueva
del methodology / template disponible, el flujo es distinto al
bootstrap: no se escriben archivos nuevos, se **reconcilian** los
existentes contra la versión nueva preservando customizaciones del
equipo.

> **División mecánico / juicio (v0.23)**: el ejecutor preferido de
> P3.U/P4.U es el script determinístico `ai-dlc-upgrade.{sh,ps1}` del
> repo del methodology — comparar hashes y reemplazar bloques entre
> sentinels no requiere (ni conviene a) un LLM. El script aplica lo
> auto-aplicable, deja intactos los conflictos y escribe
> `archive/upgrade-reports/upgrade-v<X>-<fecha>.md`. El protocolo
> conversacional de abajo aplica: (a) como fallback sin script, (b)
> para **migrar manifiestos legacy** (< v0.21, sin `files:`), y (c)
> para **resolver los conflictos del reporte** — el dev abre su agente
> y pide `/adopt --upgrade` citando el reporte; el agente salta
> directo a los items en conflicto con las opciones take-new /
> keep-mine / merge-manual.
>
> Tres salvaguardas del script para manifiestos pre-v0.23: (1) un
> archivo que existe en el target sin entry en el manifiesto pero
> **byte-idéntico** a la versión nueva se registra y sigue, sin
> conflicto (típico: `.claude/commands/*` que el `/adopt` agéntico no
> registraba); (2) si el manifiesto no tiene bloque `placeholders:`,
> el script se detiene **antes de tocar nada** (error de validación)
> con la instrucción exacta — agregar el bloque al manifiesto con los
> valores reales del repo y volver a correr; (3) si el bloque
> bracketed nuevo trae una clave `{{...}}` sin valor en
> `placeholders:` (clave nueva del template), el archivo va a
> **conflicto** en vez de escribir el placeholder crudo.

### Cuándo se entra a este modo

- Auto-detectado en P0.3: `<target>/.ai-dlc-version` existe.
- O forzado: `/adopt <target> --upgrade`.
- O el agente lo propone al detectar que `.ai-dlc-version` tiene
  `methodology_version` < versión actual del methodology.

**Pre-requisito**: el manifiesto en `.ai-dlc-version` tiene el bloque
`files:` (formato v0.21+). Si NO lo tiene (instalación previa a
v0.21), el agente lo reconstruye en una **fase de migración** (ver
"Migración de manifiestos legacy" abajo) antes de ejecutar el upgrade.

### Variante de las 6 fases para upgrade

| Fase | Comportamiento en `--upgrade` |
|---|---|
| **P0 Pre-flight** | Igual. Validar `cwd`, target absoluto, no es el template, working tree limpio. |
| **P1 Detect** | **Reducido**. NO re-clasificar AI infra previa (ya está clasificada en el manifiesto). Solo verificar: ¿el `.ai-dlc-version` está bien formado y la versión registrada existe en el repo del template? |
| **P2 Clarify** | **Reducido**. Pregunta única clave: *"versión actual `vX`, versión disponible `vY`. ¿Upgrade directo X→Y, o paso a paso X→X+1→...→Y?"* (default: directo si Y-X ≤ 2; step-by-step si Y-X > 2 — ver "Multi-version upgrade" abajo). |
| **P3 Propose** | Reemplazado por el **algoritmo de plan de upgrade** (ver `P3.U` abajo). Output: `<target>/.ai-dlc-upgrade-plan.md`. |
| **P4 Execute** | Reemplazado por la **aplicación del plan de upgrade** (ver `P4.U` abajo). |
| **P5 Close** | Igual. Reportar lo hecho, dejar plan en `archive/`, actualizar `.ai-dlc-version` con nuevos hashes. |

### P3.U — Generar plan de upgrade

Para cada archivo del manifiesto, calcular:

- `current_hash` = `sha256(<target>/<file>)` (o del bloque entre
  sentinels en el caso `bracketed`).
- `installed_hash` = `files[<file>].sha256_at_install` del manifiesto.
- `new_template_content` = contenido del archivo en la nueva versión
  del template (leído desde `<template>/<file>` en el modelo X→Y).
- `installed_template_content` = contenido del archivo en la versión
  registrada en el manifiesto (leído de `git show
  <installed-version>:<file>` sobre el repo del template, o del
  archive de releases si está disponible).

**Tabla de decisión por `role`**:

| Role | `current == installed` (sin cambios del usuario) | `current != installed` (usuario modificó) |
|---|---|---|
| `owned` | Auto-replace: copiar `new_template_content` sobre el archivo. Reportar como "actualizado". | **Diff prompt**: mostrar 3 versiones (installed / current / new), opciones: `take-new` (perder cambios del user) / `keep-mine` (perder cambios del template) / `merge-manual` (abrir editor o marcar `<<<<<<<` conflict markers) / `skip` (dejar como está, marcar en plan). Default sugerido: `merge-manual` si los hunks de cambio del template y del usuario NO se solapan; `keep-mine` si se solapan profundamente. |
| `bracketed` | Reemplazar SOLO el bloque entre sentinels con la versión nueva del bloque. **Al reemplazar, el sentinel-start también se actualiza**: `v=<X>` → `v=<Y>`. Contenido afuera de sentinels: intocable, sea cual sea el `current_hash` del archivo completo. | Idem fila anterior — el `sha256_at_install` del bracketed compara **sólo el bloque entre sentinels**, no el archivo entero. Si el bloque cambió (el usuario editó adentro de los sentinels), aplicar el mismo diff prompt que `owned`. |
| `template` | **Ruta mecánica** (`ai-dlc-upgrade`): se copia sólo si falta; si existe, **no se toca** y aparece en el reporte como *No tocados*. **Ruta conversacional** (este protocolo, cuando el dev lo pide explícitamente): YAML/JSON additive merge — agregar keys/sub-keys nuevas del template, NUNCA pisar valores del usuario; markdown, marcar en plan para revisión manual. | Idem (el usuario llenando lo suyo NO cuenta como "cambio del archivo en sentido bracketed/owned"). |
| `user` | Skip. | Skip. |

**Archivos nuevos en la versión nueva, ausentes del manifiesto**:
agregar al plan como "nuevo" → en P4.U se copian + se registran en el
manifiesto con `role` inferido del path (`.agents/commands/*` →
`owned`, `stack/*` → `template`, etc.) o preguntando al dev si no
hay heurística clara.

**Archivos del manifiesto ausentes en la versión nueva** (template
dropped a file): agregar al plan como "deprecated" → preguntar al
dev si remover del target o conservar (default: conservar +
marcar `# DEPRECATED upstream` en el archivo).

**Y qué pasa con su entry del manifiesto, que es la mitad que faltaba**
(`SIM-187`):

| Rama | El archivo | La entry del manifiesto |
|---|---|---|
| **Remover** | Se borra | Se borra con él |
| **Conservar** (default) | Se queda, marcado `# DEPRECATED upstream` | **Se queda, con `role: user`** |

`role: user` significa *AI-DLC no lo toca* (§16 *Tabla de roles*), que
es exactamente en lo que el archivo se convirtió. Dejarlo con su `role`
anterior hace que el upgrade lo reporte como retirado **en todas las
versiones futuras**, y un aviso que sale siempre se aprende a ignorar;
borrar la entry lo vuelve invisible para AI-DLC, que es peor. Los dos
instaladores saltan el aviso cuando la entry es `user`.

**Renames** (mismo contenido conceptual, otro path): la versión
nueva del template puede declarar renames en su changelog
(`<template>/RENAMES.yaml`). Si está presente, el agente aplica
`git mv` para preservar historia y actualizar el manifiesto.

### P3.U output: `.ai-dlc-upgrade-plan.md`

```markdown
# Plan de upgrade AI-DLC: v<X> → v<Y>

**Generado**: <ISO8601>
**Agente**: <tool>
**Target**: <abs-path>
**Estrategia**: <directo | step-by-step>

## Acciones automáticas (auto-replace, sin cambios del usuario)

- `AGENTS.md` (bracketed, sentinel `v=<X>` → `v=<Y>`): reemplazar bloque AI-DLC.
- `.agents/commands/spec-new.md` (owned, hash unchanged): reemplazar.
- ...

## Acciones que requieren decisión

### `.agents/commands/bug-triage.md` (owned, hash divergente)

- Cambios del template `v<X>` → `v<Y>`: paso 5 ratchet harness agregado.
- Cambios del usuario sobre `v<X>`: comentario `# tweak local` en paso 3.
- **Solape**: ninguno.
- **Sugerencia**: `merge-manual` — los hunks no chocan.
- **Acción del dev**: [ ] take-new   [ ] keep-mine   [ ] merge-manual   [ ] skip

### `AGENTS.md` (bracketed, bloque AI-DLC modificado por el usuario)

- ...

## Archivos nuevos en v<Y>

- `.agents/commands/<new-command>.md` (role inferido: owned). [ ] OK agregar.

## Archivos deprecated en v<Y>

- (ninguno)

## Renames

- `BOOTSTRAP.md` → `RUNBOOK-greenfield.md` (de RENAMES.yaml). [ ] OK aplicar.

---

**El agente NO ejecuta ninguna acción hasta que el dev marque las
casillas y confirme.**
```

### P4.U — Aplicar plan de upgrade

1. **Re-leer el plan** después de que el dev lo edite — el archivo
   en disco es el contrato.
2. **Aplicar acciones automáticas** primero (auto-replace, archivos
   nuevos sin ambigüedad). El additive-merge de archivos `template`
   **no** es automático: sólo ocurre si el dev lo pidió y quedó como
   acción marcada en el plan (ver tabla de decisión por `role`).
3. **Aplicar acciones decididas** según las casillas marcadas. Para
   `merge-manual`: insertar conflict markers `<<<<<<< current /
   ======= / >>>>>>> incoming` y dejar el archivo para que el dev
   resuelva.

   **Default cuando una acción NO tiene casilla marcada**: `skip` +
   reportar en P5. NUNCA inferir `take-new` o `keep-mine` del silencio
   del dev. Si > 50% de las acciones quedaron sin marcar, el agente
   sospecha que el dev no llegó a revisar el plan y **pregunta**
   antes de continuar.

   **Si el archivo es YAML/JSON `template` y el dev pidió additive
   merge**: preservar comentarios del usuario. Usar un parser que mantenga
   trivia (ej. `ruamel.yaml` en Python). Anti-patrón: regenerar el
   archivo desde cero perdiendo comentarios load-bearing.

   **Si el archivo `bracketed` tiene más de un par de sentinels**
   (corruption, copy-paste error): NO inferir cuál es el correcto.
   Reportar al dev y pedir que limpie antes de seguir.
4. **Actualizar `.ai-dlc-version`**:
   - `methodology_version` y `template_version` → versión nueva.
   - `applied_at` → ISO8601 ahora.
   - `mode: upgrade`.
   - Recomputar `sha256_at_install` de cada archivo tras los cambios
     (refleja el nuevo baseline).
   - Agregar entry `files:` para archivos nuevos.
   - Remover entries de archivos dropped (si el dev autorizó remover)
     o marcarlos `deprecated_upstream: true`.
5. **Mover `.ai-dlc-upgrade-plan.md`** a `archive/ai-dlc-upgrade-plan-<ISO>.md`.
6. **NO hacer commit** (igual que P4.3 del bootstrap normal — el
   commit lo dispara el dev tras revisar).

### Migración de manifiestos legacy (instalación previa a v0.21)

Si `.ai-dlc-version` existe pero NO tiene bloque `files:`:

1. El agente reporta: *"Detecté `.ai-dlc-version` formato legacy (sin
   manifiesto per-archivo). Necesito reconstruirlo antes del upgrade."*
2. Reconstrucción:
   - Listar todos los archivos AI-DLC del target (con la lista
     canónica de la versión registrada en `methodology_version`).
   - Asignar `role` por path según las heurísticas (AGENTS.md →
     `bracketed`; `.agents/commands/*` → `owned`; `stack/*` →
     `template`; `repo-config.yaml` → `template`).
   - Calcular `sha256_at_install` = `sha256(current)`. **Limitación
     conocida**: el baseline asume "el estado actual del archivo es
     el baseline" — los cambios pre-existentes del usuario quedan
     incorporados al baseline. El upgrade futuro detectará SÓLO
     cambios posteriores a la migración, no los anteriores.
3. Escribir el manifiesto reconstruido. Reportar la limitación al
   dev. Continuar con P3.U normal.

### Multi-version upgrade (X→Y donde Y-X > 2)

- Si `Y-X ≤ 2`: upgrade directo. El plan compara baseline `v<X>` con
  target `v<Y>` y resuelve en una sola pasada.
- Si `Y-X > 2`: el agente **sugiere** step-by-step (`v<X> → v<X+1>`,
  luego `v<X+1> → v<X+2>`, etc.) para que renames/deprecations
  intermedios se apliquen correctamente. El dev puede forzar directo.

### Invariantes que el agente DEBE respetar durante `--upgrade`

- IF `current_hash` de un `owned` divergió y NO hay decisión explícita
  del dev en el plan → NO aplicar `take-new`. Skip + flag en reporte.
- IF un archivo `bracketed` no tiene sentinels en el target
  (corruption / dev los borró) → NO inferir; reportar y preguntar.
- IF `installed_template_content` no se puede recuperar (tag perdido
  en el repo del template) → degradar a 2-way diff (installed vs new,
  sin baseline). Avisar la pérdida de precisión.
- IF `merge-manual` deja conflict markers → reportar al dev al cerrar
  P5 con lista explícita de archivos a resolver.

---

## Anti-patrones que el agente DEBE rechazar

| Anti-patrón | Por qué |
|---|---|
| Auto-aplicar sin entrevista (modo `--yes`) | Cada decisión saltada termina mal en algún repo. |
| Migrar `.cursor/plans/` / `SESSION_*` sin pedir | §16 — anti-patrón documentado. |
| Sobreescribir `CLAUDE.md` "porque es el del template" | F3 P1.2 protege. |
| Renombrar branches históricas para normalizar | P5 invariante. Rompe links. |
| Backfillear specs retroactivas para todo el código | Anti-patrón §16 *strangler*. |
| Inventar ambientes que no existen (agregar `qa` por default) | P1.4 — sólo confirmar candidatos. |
| Instalar dependencias | Fuera de alcance. |
| Borrar `.cursor/`/`.copilot/`/`.aider/` para "consolidar" | Categoría A se respeta. |
| Tratar Categoría B (custom interna) como Categoría A | El equipo quería esta consolidación — pierdes el valor de la migración. |
| Pre-llenar `stack/architecture.md` con asunciones genéricas | TODO honesto > asunción genérica. |
| Ejecutar Phase 4 sin OK explícito sobre el plan escrito | El plan en disco es el contrato. |
| **Merge semántico de `AGENTS.md` previo sustantivo** (parsear, reordenar, redistribuir secciones) | Riesgo alto, valor bajo. La estrategia correcta es appended-section con sentinels (P1.2 sub-protocolo). El agente NO interpreta el contenido del equipo. |
| **Inlinear el methodology en AGENTS.md** producido (copiar reglas, ejemplos EARS, decision trees) | AGENTS.md es índice + reglas-raíz. El detalle vive en `ai-dlc-methodology.md`, `.agents/commands/`, `stack/*`. Inlinear infla el contexto que todas las tools cargan en cada invocación — anti-patrón explícito de harness engineering (cada regla compite por atención). Ver P1.2 *Higiene del AGENTS.md producido*. |
| **`--upgrade` con `take-new` automático en archivos `owned` modificados** | Pisas trabajo del equipo silenciosamente. La decisión es del dev — siempre prompt con diff. |
| **Aplicar `--upgrade` sin reconstruir manifiesto legacy** (`.ai-dlc-version` previo a v0.21 sin bloque `files:`) | Sin manifiesto, el upgrade es a-ciegas. Reconstruir primero (con la limitación documentada en P4.U *Migración*). |
| **Modificar contenido fuera de los sentinels `ai-dlc:section-start/end`** durante `--upgrade` | Sentinels son el contrato. Afuera = territorio del usuario, incluso en archivos AI-DLC produjo originalmente (Cat A.1). |
| **Recomputar `sha256_at_install` antes de aplicar el plan** | El hash debe recomputarse **después** de aplicar, no antes — sino la próxima detección de divergencia falla. |
| **Saltar la regeneración del manifiesto tras `--upgrade`** | El manifiesto debe reflejar el estado post-upgrade. Si se olvida, el siguiente upgrade no tiene baseline correcto. |
| **Modificar contenido fuera del bloque `ai-dlc:section-start/end`** en AGENTS.md previo | El bloque es el único territorio AI-DLC. Fuera = del equipo, sagrado. |
| **Resolver conflictos de protocolo automáticamente** (auto-commit vs PR-only, branch naming, commit format) | El agente DETECTA y reporta como OPEN_QUESTION. El dev decide. |
| **Ejecutar `/adopt` con `cwd = target`** sin advertir al dev del costo | Es modo Y fallback válido pero contamina el contexto inicial del agente con el AGENTS.md/CLAUDE.md previo. Reportar explícitamente. |
| **Tratar `<target>` como subdirectorio del template** | P0.0 validation crítica. No tiene sentido bootstrapear el template a sí mismo. |
| **Asumir POSIX para symlinks** sin chequear plataforma | P4.2 paso 10 — Windows sin developer mode requiere wrappers de texto (degradado). |
| **Asumir que el default branch es `main`** sin detección dinámica | P0.4 detección via `git symbolic-ref refs/remotes/origin/HEAD`. Puede ser `master`, `pruebas`, `desarrollo`, `develop` según el repo. |
| **Ejecutar `git push`, `git merge` o `git checkout <base>` que modifique el default branch** | El default branch es **sagrado** durante todo Phase 4. El push y la apertura del PR son acciones del dev (o del hub, si lanzó la adopción), no del agente. Bootstrap = PR-only. |
| **Saltarse Q4.bis** y asumir que la base del bootstrap = default branch | Algunos equipos exigen que TODO cambio (incluido chores) pase por el `promotion_path`. Preguntar. |

---

## Notas para el agente que lee esto

1. **Si te falta acceso a alguna ruta**: pedila explícitamente. No
   adivines paths.
2. **Si el dev se frustra con el ritmo**: ofrece saltar a un modo más
   directo, pero sigue respetando las invariantes (no escribir sin OK
   sobre el plan).
3. **Si encuentras algo que no encaja con este protocolo**: páralo,
   repórtalo al dev como "**gap del protocolo: <descripción>**", y
   ofrece seguir con la heurística más cercana o abortar. No
   inventes flujo nuevo.
4. **Si el repo está en un estado raro** (merge en curso, rebase
   interrumpido, detached HEAD): para en P0, reporta, NO intentes
   resolverlo automáticamente.
5. **Si vienen sorpresas en Phase 1** que no encajan con ninguna
   categoría (ej. un directorio AI nuevo que no es ni A ni B
   claramente): **preguntar**. Heurística primero, decisión del dev
   siempre.

---

## Trazabilidad

Este protocolo deriva de:

- `ai-dlc-methodology.md` §§ 3.12, 6, 10, 11, 16
- `BROWNFIELD-CHECKLIST.md` (runbook manual brownfield)
- `BOOTSTRAP.md` (runbook manual greenfield)
- `ai-dlc-init-spec.md` (spec del CLI scripted)
- `BROWNFIELD-DRYRUN-edesk.md` (dry-run sobre repo SYC real,
  origen de las categorías A vs B)

Si el methodology cambia, revisar:

- Las 17 preguntas de Phase 2 vs schema `repo-config.yaml` (§6).
- El catálogo de tools de la Categoría A vs §16 *coexistir con AI
  infra previa*.
- Anti-patrones vs §18.

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
