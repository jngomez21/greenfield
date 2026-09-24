# Brownfield Adoption Checklist — AI-DLC

> Runbook secuencial para adoptar AI-DLC **manualmente** en un repo
> que ya existe (con código, historia, posiblemente AI infra previa).
> Pensado para que un dev pueda completarlo solo en ~2 horas sin
> herramientas adicionales — sólo este template y un agente AI a mano
> (Claude/Cursor/OpenCode).
>
> Para greenfield (repo nuevo desde cero), ver `BOOTSTRAP.md`.

**Versión metodología que aplica**: leer el frontmatter de
`ai-dlc-methodology.md` (campo `version:`) y usar ese valor cuando
este runbook diga `0.170`. Secciones de referencia:
§ 6, § 10, § 15.

**Tiempo estimado**: 2 horas (10 min audit + 30 min entrevista + 1.5 h
copiar/configurar archivos).

**Principio raíz**: NO ASUMIR. Cada decisión se documenta — si no
está clara, **preguntar al equipo**, no decidir solo (§3.12).

---

## Antes de empezar (5 min — safety)

- [ ] **Working tree limpio**. Si hay cambios sin commitear,
      decide y ejecuta UNO:
      - `git stash push -u -m "pre-ai-dlc-bootstrap"` (recuperable)
      - `git commit -am "wip"` (si los cambios son tuyos)
      - posponer el bootstrap si los cambios son de otra persona
- [ ] **No estás en una rama de feature en vuelo**. Crear rama
      dedicada para todo el bootstrap:
      ```bash
      git checkout -b chore/adopt-ai-dlc
      ```
      Reversible: `git branch -D chore/adopt-ai-dlc` deshace todo
      en un segundo si algo sale mal.
- [ ] **Tienes una copia local del repo AI-DLC** (clonado del git
      corporativo). Este runbook usa `$AI_DLC_REPO/template` como
      fuente.
- [ ] **Tienes acceso a un agente AI** abierto sobre este repo
      (Claude Code / Cursor / OpenCode / Codex CLI). El bootstrap
      es manual pero algunos pasos pegan mejor con un agente que
      lea archivos y proponga ediciones.

---

## Phase 1 — Audit (10 min, sólo lectura)

Hacer inventario **antes** de tocar nada. Documentar resultados en
una nota temporal — los necesitas en Phase 2.

### 1.1 Stack detectado

- [ ] Lenguajes presentes:
      - `*.sln`, `*.csproj` → .NET
      - `package.json`, `.nvmrc` → Node (anotar versión Node)
      - `pyproject.toml`, `requirements.txt`, `setup.py` → Python
      - `pom.xml`, `build.gradle` → Java
      - `go.mod` → Go
      - `Cargo.toml` → Rust
- [ ] Build/test tools (desde scripts en `package.json` o targets):
      jest? vitest? mocha? pytest? xunit? dotnet test? gradle test?
- [ ] Frameworks (desde deps): React, Vue, Angular, Express,
      NestJS, ASP.NET Core, Spring, FastAPI, etc.
- [ ] Dependencias de scopes privados (`@org/*`, registry interno):
      indica feed npm/nuget privado de la empresa.
- [ ] Container / deploy files: `Dockerfile`, `docker-compose.yml`,
      `.dockerignore`, `Chart.yaml`, `kustomization.yaml`, ADO
      pipelines `azure-pipelines.yml`, GH Actions `.github/workflows/`.

**Decisión derivada**: qué pre-llenar en `stack/tech-stack.md` (lo
detectado) vs qué dejar como TODO (NFRs, deploy target, política de
versionado de libs internas).

### 1.2 AI infra previa

- [ ] `CLAUDE.md` existe? Tamaño? Es boilerplate o tiene contenido
      sustantivo del proyecto (reglas, procedimientos, deuda
      técnica)?
- [ ] `AGENTS.md` existe? (raro en brownfield, pero posible)
- [ ] `.cursorrules` existe? Cuántas reglas?
- [ ] `.cursor/plans/` con archivos? (son "specs" de Cursor)
- [ ] `.copilot-instructions.md` o `.github/copilot-instructions.md`?
- [ ] `.github/chatmodes/` con archivos?
- [ ] `.vscode/settings.json` existe? (si sí, hay que añadirle a mano
      `chat.useAgentsMdFile` — ver D6ter)
- [ ] `.github/prompts/*.prompt.md` con archivos? (menú `/` de Copilot —
      **no es Categoría A**: AI-DLC escribe ahí. Anotar los nombres
      previos para detectar colisión con los comandos del template)
- [ ] `.windsurfrules`, `.continuerules`, otros tool-rules?
- [ ] `.agents/skills/` con skills instaladas?
- [ ] `skills-lock.json`?
- [ ] `.aider/`, `.gemini/`, otros directorios de herramientas AI?

**Decisión derivada**: ninguno de estos se sobreescribe. Se respetan
o se espejan reglas (Phase 2 D5, D6). **Excepción: `.github/prompts/`**
— es el menú de comandos de Copilot, no una regla del equipo, y lo
puebla AI-DLC igual que `.claude/commands/`. Ver D6.

### 1.3 Memoria de sesión ad-hoc

- [ ] Lista archivos `.md` al root que NO son `README.md`,
      `CHANGELOG.md`, `LICENSE.md`. Patrones típicos:
      - `SESSION_*.md`, `*_HANDOFF.md`, `NEXT_SESSION_*.md`
      - `TRACE_*.md`, `analisis-*.md`, `*_PROGRESS.md`
      - `TEST_STATUS.md`, `*_NOTES.md`, `DEBUG_*.md`

**Decisión derivada**: archive, migrate-to-specs, o leave (D3).

### 1.4 Branches y flujo

- [ ] `git branch -a` — listar TODAS las ramas locales y remotas.
- [ ] Identificar ramas que son **ambientes** (long-lived,
      mergeadas continuamente): `main`, `master`, `develop`,
      `desarrollo`, `pruebas`, `qa`, `staging`, `production`.
- [ ] Identificar **convención feature**: contar ramas
      `feature/X` vs `feature_X` vs `feature-X` vs `feat/X`. Hay
      drift?
- [ ] `git remote show origin` — cuál es HEAD remoto? (Suele ser
      `main` pero a veces se desconfigura.)

**Decisión derivada**: qué declarar en `repo-config.yaml`
(environments, branch_pattern). NO inventar ambientes que no
existen (D7, D8).

### 1.5 Estructura del repo

- [ ] Single-project (un único `package.json`/`*.sln` al root)?
- [ ] Monorepo homogéneo (todos los sub-proyectos son services o
      todos son libraries)?
- [ ] Monorepo **heterogéneo** (mix de services + libraries +
      frontend-apps)?
- [ ] Hay regla de "feature parity" entre sub-proyectos? (Ej.
      backend .NET y backend Node alterno que deben tener el
      mismo endpoint.)

**Decisión derivada**: `repo_type` único vs bloque `monorepo:` con
sub-proyectos (D1, D2 — ver § 10 *Monorepos heterogéneos*).

---

## Phase 2 — Decisiones (30 min con el equipo)

12 decisiones, cada una con opciones explícitas. **Documentar la
decisión** (no dejarla en la cabeza). Cada decisión se traduce
después a un campo de `repo-config.yaml` o a una acción de Phase 3.

> **Cómo usar esta tabla**: lee la pregunta, mira las opciones,
> conversa con el equipo (no decidas solo si la respuesta no es
> obvia), marca la elegida. Si la respuesta no está clara: marcar
> `OPEN_QUESTION` y seguir — se resuelve después.

### D1 — Estructura del repo

> ¿El repo es single-project o monorepo? Si monorepo, ¿homogéneo
> o heterogéneo (mix de services + libraries)?

- [ ] **(a) Single-project** — un único `repo_type` aplica a todo.
- [ ] **(b) Monorepo homogéneo** — todos los sub-proyectos del
      mismo tipo. `repo_type` único.
- [ ] **(c) Monorepo heterogéneo** — mix. Usar `repo_type: custom`
      + bloque `monorepo:` en `repo-config.yaml` (§ 6 schema).
- [ ] **(d) Sólo un sub-proyecto por ahora** — empezar conservador,
      aplicar AI-DLC a uno, expandir después.

### D2 — Ubicación de specs

> Si monorepo, ¿dónde viven las specs?

- [ ] **(a) `specs/` al root** — features transversales o single-project.
- [ ] **(b) `<sub-proyecto>/specs/`** — default §6 *Monorepos*, per servicio.
- [ ] **(c) Cross-cutting al root con `cross_cutting_specs: true`** —
      cuando hay feature parity exigida entre sub-proyectos.

### D3 — Memoria de sesión existente

> ¿Qué hacer con los archivos `SESSION_*`/`*HANDOFF*`/`TRACE_*`
> detectados en 1.3?

- [ ] **(a) Archive** — mover a `archive/session-history/`. Default
      recomendado (reversible, sin re-trabajo, libera root).
- [ ] **(b) Migrate-to-specs** — convertir cada archivo a
      `specs/<slug>/` retroactivo con state `legacy`. Costoso pero
      estructurado.
- [ ] **(c) Leave** — no tocar. Conviven con AI-DLC. Estado
      transitorio aceptable.

### D4 — Cursor `.cursor/plans/` (y similares)

> Si hay planes de Cursor, ¿qué hacer?

- [ ] **(a) Dejar** — Cursor sigue usándolos. AI-DLC convive.
      Default recomendado (§16 *coexistir AI infra previa*).
- [ ] **(b) Migrar todos a `specs/`** — costoso, pero unifica
      formato.
- [ ] **(c) Migrar selectivos** — el equipo elige cuáles son
      "vivas" y migran sólo esas.

### D5 — `CLAUDE.md` existente

> Si hay CLAUDE.md sustantivo (>5 KB con reglas del proyecto), ¿qué
> hacer?

- [ ] **(a) Crear `AGENTS.md` nuevo, dejar `CLAUDE.md` intacto** —
      Default recomendado. Claude lee ambos, AGENTS.md tiene el
      protocolo AI-DLC, CLAUDE.md sigue con reglas custom.
- [ ] **(b) Extraer reglas codificables** a `stack/constraints.md`/
      `stack/testing.md`, dejar `CLAUDE.md` apuntando a ellas.
      Costoso pero más limpio.
- [ ] **(c) Reemplazar `CLAUDE.md` por el del template** — SÓLO si
      el existente es boilerplate vacío.

### D6 — `.cursorrules` / `.copilot-instructions.md` / `.windsurfrules`

> ¿Espejar las reglas a `stack/constraints.md`?

- [ ] **(a) Espejar reglas codificables, dejar el archivo intacto** —
      Default recomendado. Cursor/Copilot siguen leyendo el original;
      Claude/OpenCode leen `stack/constraints.md`.
- [ ] **(b) Sólo dejar el archivo, no espejar** — si las reglas son
      muy tool-específicas.

> **`.github/copilot-instructions.md` es el caso mixto.** Si existe, se
> respeta como (a) y además se le **añade** la línea que apunta a
> `AGENTS.md` — sin esa línea, quien trabaje en modo Ask opera sin el
> contrato del agente y sin ningún error visible. Si no existe, AI-DLC
> lo crea como puntero puro, sin reglas propias.

### D6ter — `.vscode/settings.json` (la clave que activa `AGENTS.md`)

> **Sólo si el repo ya tenía un `.vscode/settings.json`.** El instalador
> **no lo pisa** —es del equipo: formateador, debug, exclusiones— así que
> la clave que AI-DLC necesita **no llega sola**, y su ausencia no
> produce ningún error: VS Code deja de adjuntar `AGENTS.md` y el chat
> responde igual de fluido, sin el contrato del agente.

- [ ] Abrir `.vscode/settings.json` del target y añadir:
      `"chat.useAgentsMdFile": true`
- [ ] Verificarlo: en el chat, en **modo Agente**, preguntar *"según
      AGENTS.md, ¿qué exige el gate G2?"*. Si responde en genérico, la
      clave no está surtiendo efecto.

> Es `SIM-180`. La solución de fondo —un `role` que declare que AI-DLC
> posee **claves** y no archivos, lo que también arreglaría `.mcp.json`—
> queda pendiente porque toca el schema del manifiesto.

### D6bis — `.github/prompts/` (menú `/` de Copilot)

> No es una decisión de espejado: AI-DLC **posee** este directorio,
> igual que `.claude/commands/`. La decisión es sólo qué hacer con lo
> que ya hubiera:

- [ ] **(a) Conservar los `.prompt.md` previos que no colisionen** —
      Default. AI-DLC añade los suyos (`spec-*`, `contract-*`, …) al lado.
- [ ] **(b) Hay colisión de nombres** — un `.prompt.md` previo se llama
      igual que un comando del template. **Preguntar al dev**: renombrar
      el previo, o no instalar ese comando en este repo.

### D7 — Convención de branches

> Si hay drift histórico (mezcla `feature/`, `feature_`, etc.),
> ¿qué hacer?

- [ ] **(a) Adoptar `feat/<slug>` para lo nuevo, no tocar el
      pasado** — convención AI-DLC default.
- [ ] **(b) Mantener la convención más reciente del repo** (ej.
      `feature/<slug>`) y declararla en `repo-config.yaml >
      branch_pattern: "feature/"`. Default recomendado para
      brownfield (evita introducir un tercer formato).
- [ ] **(c) Renombrar ramas históricas** — NO recomendado, rompe
      links a PRs y work items.

### D8 — Ambientes en `repo-config.yaml`

> ¿Qué ramas son ambientes reales (de 1.4)?

Listar las ramas detectadas como ambientes y el `deploy_trigger` de
cada una:

| Rama detectada | Es ambiente? | `deploy_trigger` |
|---|---|---|
| `main` | sí | `manual` |
| `pruebas` | ? | ? |
| `qa` | ? | ? |
| `desarrollo` | ? | ? |
| `staging` | ? | ? |
| `production` | ? | ? |
| _otra_ | ? | ? |

> NO inventar ambientes que no existen. Si el repo no tiene `qa`,
> no agregarlo al `promotion_path`.

### D9 — Tracker

> ¿Qué sistema de work items usa el equipo?

- [ ] **(a) Azure DevOps** (default SYC). Necesario: `org`,
      `project`, `default_area_path`.
- [ ] **(b) GitHub Issues** — `[R*.*] #<issue>` en commits.
- [ ] **(c) Jira** — `[R*.*] PROJ-<id>`.
- [ ] **(d) Linear** — `[R*.*] <TEAM>-<n>`.
- [ ] **(e) None** — sólo `[R*.*]` en commits, sin sync con boards.

### D10 — Deploy target / runtime

> ¿A dónde se despliega?

- [ ] **(a) OpenShift** (default SYC services). Necesario: cluster,
      namespace pattern.
- [ ] **(b) Kubernetes vanilla**.
- [ ] **(c) npm registry / nuget feed** (libraries).
- [ ] **(d) Static host** (Vercel, Netlify, S3+CloudFront — frontend
      apps).
- [ ] **(e) None** — repo no se despliega (`docs-only`,
      `catalog-only`, sólo build local).
- [ ] **(f) Mixto** — en monorepo heterogéneo cada sub-proyecto
      puede ir a un target distinto (anotar per sub-proyecto en
      `monorepo.services`).

### D11 — Skills ya instaladas

> Si `.agents/skills/` ya tiene skills:

- [ ] **(a) Respetar todas, agregar sólo `README.md` AI-DLC si
      falta** — Default recomendado. Zero defaults se respeta hacia
      ambos lados: no preinstalamos, pero no desinstalamos.
- [ ] **(b) Auditar y proponer al equipo cuáles seguir / cuáles
      remover** — si claramente hay skills abandonadas o
      conflictivas.

### D12 — Owner, equipo, lead

> Para reemplazar placeholders en `AGENTS.md` y `repo-config.yaml`:

- Service name (slug): `_______________`
- Owner team: `_______________`
- Lead email: `_______________` (típicamente `@syc.com.co`)

---

## Phase 3 — Apply (1.5 h, escribir archivos)

Ejecutar en orden. Cada paso es reversible mientras estés en
`chore/adopt-ai-dlc` (puedes `git checkout .` o `git reset --hard`
si algo sale mal).

### 3.1 Copiar estructura base desde el template

```bash
TEMPLATE=~/Downloads/syc-stack-template     # ajustar a tu ruta

# archivos al root (sólo si NO existen ya — respetar CLAUDE.md previo)
[ -f AGENTS.md ] || cp "$TEMPLATE/AGENTS.md" ./
cp "$TEMPLATE/repo-config.yaml" ./           # nuevo siempre
[ -f CLAUDE.md ] || cp "$TEMPLATE/CLAUDE.md" ./

# stack/ (sólo si NO existe — todos los archivos llegan con TODO)
[ -d stack ] || cp -r "$TEMPLATE/stack" ./

# .agents/commands/ (slash commands canonical)
mkdir -p .agents/commands
cp "$TEMPLATE/.agents/commands/"*.md .agents/commands/

# .claude/commands/ (symlinks a .agents/commands/)
mkdir -p .claude/commands
for f in .agents/commands/*.md; do
  ln -sf "../../$f" ".claude/commands/$(basename $f)"
done

# .agents/skills/README.md (sólo si no existe — respeta skills previas)
mkdir -p .agents/skills
[ -f .agents/skills/README.md ] || cp "$TEMPLATE/.agents/skills/README.md" .agents/skills/
```

**Verificar**: `git status` debe mostrar sólo archivos `?? new` o
`M` esperables. Nada que pise el código del proyecto.

### 3.2 Reemplazar placeholders

En `AGENTS.md` y `repo-config.yaml`, reemplazar:

| Placeholder | Reemplazar por (D12) |
|---|---|
| `greenfield` | service name slug |
| `TBD` | owner team |
| `TBD` | lead email |

Con `sed` (macOS):
```bash
SVC="mi-servicio"; OWNER="team-x"; EMAIL="x@syc.com.co"
sed -i '' "s|greenfield|$SVC|g; s|TBD|$OWNER|g; s|TBD|$EMAIL|g" AGENTS.md repo-config.yaml
```

### 3.3 Configurar `repo-config.yaml` con las decisiones D1-D11

Abrir `repo-config.yaml` y llenar según lo decidido en Phase 2:

- `repo_type`: D1 (`service` | `library` | `frontend-app` | `infra` | `custom`)
- `tracker`: D9
- `tracker_config`: campos según tracker (D9)
- `environments`: lista de D8 — sólo las que EXISTEN realmente
- `promotion_path`: orden de D8
- `runtime`: D10
- `branch_pattern`: D7 (default `feat/`, ajustar si se mantiene el
  histórico)
- `monorepo`: si D1=(c), llenar `services:` con la lista; setear
  `cross_cutting_specs` según D2

Marcar como `# OPEN_QUESTION:` cualquier campo que no quedó claro
en la entrevista (ej. credenciales de tracker que están en oficina).

### 3.4 Pre-llenar `stack/` con lo detectado en 1.1

Editar cada archivo de `stack/` y reemplazar TODOs con lo
detectado:

- `stack/tech-stack.md` — lenguajes, versiones, frameworks, deps
  internas, deploy target (de 1.1)
- `stack/architecture.md` — dejar TODO; lo llena el equipo en
  próxima sesión con un agente
- `stack/patterns.md` — si hay convenciones detectables del código
  (naming, commits), anotarlas; resto TODO
- `stack/security.md` — anotar feeds privados detectados; resto TODO
- `stack/constraints.md` — espejar reglas de `.cursorrules`/
  `.copilot-instructions.md` si D6=(a)
- `stack/testing.md` — frameworks de tests detectados (jest, vitest,
  dotnet test, pytest, etc.), comandos de run; resto TODO

### 3.5 Mover memoria de sesión a archive/ (si D3=archive)

```bash
mkdir -p archive/session-history
git mv NEXT_SESSION_HANDOFF.md SESSION_PROGRESS_*.md TEST_*.md TRACE_*.md analisis-*.md archive/session-history/ 2>/dev/null || true
```

Ajustar el glob a los archivos reales detectados en 1.3. `git mv`
preserva historia.

### 3.6 (Opcional) Crear `specs/legacy/` con stubs para features
en producción que el equipo identifique

Si quieres documentar que hay features vivas sin spec, crear:

```
specs/<feature-legacy-slug>/
└── status.md       (state: legacy, owner: @lead, 2-3 líneas)
```

Sin `requirements.md`/`design.md`/`tasks.md`. Sólo cuando alguien
re-toque esa área, se gradúa a `in-progress` con spec real (§16
strangler).

### 3.7 Commit

```bash
git add .
git status        # revisar QUE NO se cuele código del proyecto
git commit -m "chore: adopt AI-DLC v0.170 [bootstrap]

- Add AGENTS.md, repo-config.yaml, stack/, .agents/commands/
- Pre-fill stack/ from detected tooling
- Mirror .cursorrules → stack/constraints.md (if D6=a)
- Archive N session-memory files to archive/session-history/
- OPEN_QUESTIONS in repo-config.yaml: <list>

Methodology: see ai-dlc-methodology.md v0.170"
```

---

## Phase 4 — Report y siguientes pasos (5 min)

### Reporte al equipo

Mandar al canal del equipo (Slack/Teams):

```
AI-DLC adoptado en <repo> en rama chore/adopt-ai-dlc.

Resumen:
- N archivos nuevos (AGENTS.md, repo-config.yaml, stack/, .agents/commands/)
- N archivos movidos a archive/session-history/
- 0 archivos sobreescritos (todo lo existente respetado)

Decisiones documentadas: D1=..., D2=..., D7=..., etc.
OPEN_QUESTIONS pendientes: <lista>

Siguientes pasos:
1. Revisar PR de chore/adopt-ai-dlc → main
2. Para próxima feature: /spec-new <slug>
3. Llenar TODOs de stack/architecture.md, stack/security.md
   en próxima sesión con agente

Reverse: git branch -D chore/adopt-ai-dlc deshace todo.
```

### PR

- [ ] Abrir PR `chore/adopt-ai-dlc` → `main` (o destino que aplique
      en este repo).
- [ ] 1+ reviewer revisa que no hay código del proyecto en el diff,
      sólo files del bootstrap.
- [ ] Mergear.

### Primera feature post-bootstrap

- [ ] Abrir agente sobre el repo recién bootstrapeado.
- [ ] Decir: *"/spec-new <slug-de-tu-próxima-feature>"* (o
      describirlo en lenguaje natural si el agente sabe del
      protocolo entry-point AGENTS.md).
- [ ] Seguir el flujo normal AI-DLC desde ahí.

---

## Apéndice — Inventario canónico de archivos AI-DLC

Lo que debería existir en un repo con AI-DLC adoptado:

```
<repo>/
├── AGENTS.md                          ← protocolo del agente (standard abierto)
├── CLAUDE.md                          ← override Claude-específico (apunta a AGENTS.md o tiene reglas custom)
├── repo-config.yaml                   ← config operacional del repo (§6)
├── BROWNFIELD-CHECKLIST.md            ← este archivo (sólo en repos brownfield, opcional dejarlo)
├── stack/
│   ├── tech-stack.md                  ← lenguajes, frameworks, deploy target
│   ├── architecture.md                ← patrones de arquitectura
│   ├── patterns.md                    ← naming, commits, code conventions
│   ├── security.md                    ← auth, secrets, PII, compliance
│   ├── constraints.md                 ← anti-patrones específicos del repo
│   └── testing.md                     ← niveles, cobertura, herramientas
├── specs/                             ← una carpeta por feature (puede ser monorepo: <service>/specs/)
│   └── <feature-slug>/
│       ├── requirements.md            ← EARS R1.1, R1.2…
│       ├── design.md                  ← arquitectura, contratos
│       ├── tasks.md                   ← T1, T2… con R*.* citados
│       ├── status.md                  ← lifecycle, gates firmados
│       ├── bugs.md                    ← (opcional) BUG-NNN
│       ├── amendments.md              ← (opcional) AMD-NNN
│       └── dependencies.md            ← (opcional) D-N
├── .agents/
│   ├── commands/                      ← slash commands canonical (.md)
│   │   ├── spec-new.md
│   │   ├── spec-implement.md
│   │   ├── spec-amend.md
│   │   ├── spec-status.md
│   │   ├── spec-verify.md
│   │   ├── spec-handoff.md
│   │   ├── spec-promote.md
│   │   ├── bug-triage.md
│   │   ├── ado-link.md                ← sólo si tracker=azure-devops
│   │   └── ado-status.md              ← sólo si tracker=azure-devops
│   └── skills/                        ← zero defaults: cada repo decide qué instalar
│       └── README.md                  ← formato canónico SKILL.md
├── .claude/
│   └── commands/                      ← symlinks a ../.agents/commands/*.md
├── archive/
│   └── session-history/               ← (sólo brownfield) memoria ad-hoc migrada
└── .org/                              ← (opcional, §9) catálogo organizacional
    └── contracts/                     ← OpenAPI/AsyncAPI publicados
```

**Archivos que respeta el bootstrap (no sobreescribe)**:
`.cursorrules`, `.cursor/`, `.github/chatmodes/`,
`.copilot-instructions.md`, `.windsurfrules`, `.continuerules`,
`.aider/`, `.gemini/`, `.agents/skills/<skill-name>/` ya pobladas,
`CLAUDE.md` sustantivo, `skills-lock.json`, cualquier archivo de
código o config del proyecto.
