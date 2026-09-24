---
name: spec-verify
description: Auditar la spec — pre-G2 (consistencia interna), cobertura R*.* ↔ tests, gaps, drift, conflicts (read-only)
argument-hint: <slug> [--pre-g2] [--cross]
model-class: criterio    # --pre-g2 emite CRITICAL que bloquean G2
---

# `/spec-verify <feature-slug> [--pre-g2] [--cross]` — Auditar (read-only)

> **Argumentos:** `$ARGUMENTS` — si el token aparece sin sustituir, los
> argumentos son el texto con el que se invocó el comando.

Sigue el protocolo §7 (AGENTS.md). Tres modos componibles; ninguno
escribe nada (única excepción: el paso Convergencia del CLOSE, que
puede appendear tasks con OK explícito). Antes de razonar, correr
`scripts/spec-lint --feature <feature-slug>` (sh o ps1) si existe y
partir de su salida — lo mecánico lo valida el script; el agente
agrega el juicio semántico. En modo `--pre-g2` correr el script con
`--strict`: una spec que se firma HOY cumple las reglas de HOY, sin
importar su `methodology_version` (linteo versionado).

> **PARADA — el veredicto va primero.** Si en cualquier paso de abajo te
> paras a preguntar, escribe antes `result.json` con
> `status: needs_input`, la pregunta y su `owner`. Quien te lanzó no ve
> tu pantalla.

## Modo default — auditoría operacional (post-aprobación)

1. **CONTEXT** — leer `requirements.md`, `tasks.md`, `status.md`,
   `mocks/`, `tests/` del repo.

2. **CHECKS** — reportar:
   - `R*.*` sin `Tests:` declarado (§5 regla 6 del methodology).
   - `R*.*` con `Tests:` declarado pero **niveles no cubiertos**
     (declara `unit, integration` y sólo hay unit con
     `// Derived from R*.*`).
   - Tests con `// Derived from R*.*` cuyo `R*.*` ya no existe
     (huérfanos por Amendment).
   - Tasks `done` sin commit hash en `status.md`.
   - `D-N` en `NEGOTIATING` > 10 días hábiles; `AGREED` > 6 semanas
     sin `IMPLEMENTED` (§6 SLAs).
   - Tasks `blocked` > 4 semanas sin decisión `BLOCK`/`WORKAROUND`/
     `cancel` (§6 SLAs).
   - Mocks sin `Ready to unmock` o sin owner declarado.
   - Drift entre `state:` declarado y derivación del Lifecycle (§6).
   - `OPEN_QUESTIONS` sin owner o sin `due`; o con `due` vencido.
   - `feature_flag.main == ON` > 90 días al 100% sin task de limpieza
     (§6 *Limpieza de feature flags*).
   - **Ajuste por modalidad** (§6): `catalog-only` omite checks de
     `design.md`/`tasks.md`; `docs-only` omite tests; `refactor-only`
     **exige** tests existentes verdes pre y post; etc.
   - **Stack drift**: violaciones a `stack/patterns.md` /
     `stack/constraints.md`.
   - **Drift de tracker (v0.26)**: si `status.md > work_items` declara
     tracker `owner`, comparar (read-only, vía MCP) el estado real del
     work item en ADO contra el estado local — mismo check que
     `/spec-status` (§6 *Sincronización con el tracker durante el
     lifecycle*).

## Modo `--pre-g2` — consistencia interna antes de firmar G2

Valida que requirements/design/tasks son coherentes **entre sí**
cuando todavía es barato corregir. Severidades: **CRITICAL** (bloquea
G2) / **HIGH** / **MEDIUM** / **LOW**.

0. **`design.md` resuelto**: **toda** sección de `design.md` está
   *resuelta* — con contenido real, o marcada `N/A — <razón>`. Queda
   **CRITICAL** cualquier sección que siga con placeholders (`<...>`,
   `TODO`, `TBD`), vacía, o sólo con los comentarios de guardrail.
   G2 firma *requirements + design*: no puede firmarse sobre la mitad
   de lo que su nombre dice. Sugerir `/spec-design`.

   El criterio es **por sección y binario** —resuelta o no— a
   propósito: "el archivo está lleno" admite dos lecturas y este es el
   gate más importante del flujo. `N/A` **con razón** es una respuesta
   válida y frecuente: deja escrito que la sección se consideró, que es
   distinto de haberla olvidado.

   Excepciones (§6 *Modalidades*): `config-only` y `docs-only` admiten
   `design.md` de un párrafo u omitido; `catalog-only` lo admite mínimo
   o ausente; `refactor-only` lo omite. En las cuatro, el check no
   aplica.
1. **Cobertura R ↔ task** (cuando `tasks.md` ya está poblado):
   - Cada `R*.*` cubierto por ≥1 task → tabla
     `R*.* | task(s) | slice`. Requirement sin task = **CRITICAL**.
   - Cada task cita `R*.*` existentes. Task sin requirement =
     **HIGH** (¿scope creep o chore disfrazado?).
2. **Vaguedad**: adjetivos sin métrica en R*.*/NFRs ("rápido",
   "intuitivo", "robusto", "escalable", "pronto") = **HIGH**.
   Placeholders (`TODO`, `???`, `TBD`) = **HIGH**.
3. **Marcadores y preguntas**: `[NEEDS CLARIFICATION]` restantes o
   `OPEN_QUESTIONS` abiertas = **CRITICAL**. Sugerir según la clase:
   la que espera el `id` de un contrato de disciplina → `/contract-new`;
   cualquier otra ambigüedad → `/spec-clarify`.
4. **Duplicación / contradicción interna**: dos `R*.*` que se
   solapan o se contradicen = **HIGH**.
5. **Drift de terminología**: mismo concepto con ≥2 nombres entre
   requirements/design/tasks = **MEDIUM**.
6. **Design ↔ requirements**: componente de `design.md` que ningún
   `R*.*`/NFR justifica y no está en `Complejidad justificada` =
   **MEDIUM** (anti-overengineering). Entidad del modelo de datos sin
   origen en la spec = **MEDIUM**.
7. **Slices**: slice sin prueba independiente declarada, o P2/P3 que
   es prerequisito de P1 = **HIGH** (rompe partial-deploy).
8. **Checklist**: `checklists/requirements.md` con items `[ ]` =
   reportar conteo (G2 exige completa).

Salida: tabla `ID | Categoría | Severidad | Ubicación | Resumen |
Recomendación` + métricas (R totales, % con task, vagos, CRITICALs).
**Con ≥1 CRITICAL, recomendar NO firmar G2.**

## Modo `--cross` — conflictos contra otras specs

El mismo scan de `/spec-new` 3.d pero a demanda contra todas las
specs activas del repo: contradicciones de endpoints, flags, NFRs,
módulos compartidos, con citas explícitas (`spec/R*.*` vs
`otra-spec/R*.*`). Útil para auditar coherencia del catálogo tras N
specs o antes de un PR grande. El dev decide: amendment / alinear /
documentar coexistencia.

## CLOSE (todos los modos)

- Gaps por categoría con sugerencia de fix concreta para cada uno.
- **Convergencia (modo default)**: si hay gaps código-vs-spec
  accionables (R*.* sin cubrir, tests faltantes, drift), ofrecer
  registrarlos como tasks nuevas **append-only** al final de
  `tasks.md` bajo `## Fase Convergence — <fecha>` (sin reescribir
  tasks existentes ni tocar requirements). Sólo con OK explícito
  del dev.
- Si todo verde en default: confirmar condiciones de promoción y
  sugerir `/spec-promote`. Si todo verde en `--pre-g2`: indicar que
  la spec está lista para firma G2.

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
