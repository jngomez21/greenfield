---
name: spec-promote
description: Abrir PR de promoción al siguiente ambiente declarado en repo-config.yaml
argument-hint: <slug> --to <env>
model-class: criterio    # gate de ambiente; el error se ve en produccion
---

# `/spec-promote <feature-slug> --to <env>` — Abrir PR de promoción

> **Argumentos:** `$ARGUMENTS` — si el token aparece sin sustituir, los
> argumentos son el texto con el que se invocó el comando.

Sigue el protocolo §7 (AGENTS.md). Para feature `<feature-slug>` con destino
`<env>`:

> **PARADA — el veredicto va primero.** Si en cualquier paso de abajo te
> paras a preguntar, escribe antes `result.json` con
> `status: needs_input`, la pregunta y su `owner`. Quien te lanzó no ve
> tu pantalla.

1. **CONTEXT** — verificar:
   - Worktree correcto (`cwd` = `<repo>--<feature-slug>/`) y rama
     actual (§6 Worktree).
   - Estado actual de la feature (`status.md`).
   - **Leer `repo-config.yaml`** (§6 *Configuración del repo*) y
     extraer: `repo_type`, `tracker`, `environments`, `promotion_path`.
     Si el archivo no existe, **parar** y proponer crearlo.
   - **Ambiente destino válido**: `<env>` debe estar presente en
     `environments[].name`. Si no, **parar** y listar los válidos.

2. **PRE-FLIGHT CHECK** — verificar el gate del ambiente destino. Las
   reglas exactas vienen de `environments[<destino>].gate` en
   `repo-config.yaml`. Patrón general:

   **`repo_type: service`** (default SYC: pruebas → qa → main):
   - PR a `pruebas`: tests verdes + spec aprobada + state ≥
     `partial-deploy-pruebas`.
   - PR a `qa`: tests verdes + QA sign-off + state ≥
     `partial-deploy-qa` o `feature-complete`.
   - PR a `main`: state `feature-complete` + `rollout-plan.md` +
     Ops sign-off.

   **`repo_type: library`** (paquete npm/pip/maven, p.ej. pruebas →
   main):
   - PR a `pruebas` (`deploy_trigger: publish-prerelease`): tests
     verdes, version bump prerelease y changelog. NO hay "ambiente"
     — el publish al registry **es** el deploy.
   - PR a `main` (`deploy_trigger: publish-release`): state
     `feature-complete`, QA del consumidor firmó sobre el prerelease,
     release notes y tag firmado.

   **`repo_type: infra`** (sandbox → prod):
   - PR a `sandbox`: `terraform plan` dry-run y revisión.
   - PR a `prod`: state `feature-complete`, `terraform plan` revisado,
     Ops sign-off y ventana de cambio si aplica.

   **`repo_type: frontend-app`**: igual a `service` salvo que también
   considera previews por PR si están declarados.

   Si falta algo, **parar** y reportar qué falta y a quién pedirlo.

3. **CLARIFY** — si la rama destino del PR es ambigua, preguntar cuál.
   Si el feature flag de prod debe ir `OFF` al merge (lo normal),
   confirmar.

4. **PROPOSE** — mostrar branch source/target, resumen del PR (`R*.*`
   cubiertos, `AMD-NNN` aplicados, tasks done, commit count), reviewers
   sugeridos. Si `repo_type: library`: tipo de publish y version bump
   propuesto. **Pedir OK explícito** antes de abrir el PR (§3.16).

5. **EXECUTE** — comando según `tracker` declarado:
   - `tracker: azure-devops` → `az repos pr create ...` (vía MCP de
     ADO o `az` CLI). Linkear work items (`--work-items`).
   - `tracker: github-issues` → `gh pr create --base <target> --head <current> ...`. Linkear issues (`closes #<n>`).
   - `tracker: jira` / `linear` / etc. → análogo.
   - `tracker: none` → `gh pr create` (o equivalente), sin work items.

   Para `repo_type: library`: en lugar de PR a `main` para "release",
   el comando puede ser un workflow de publish (`npm publish`,
   `pnpm publish`, etc.). Confirmar el modo con el dev antes de actuar.

6. **UPDATE STATUS** — cuando el dev confirme merge (o publish para
   library): tasks afectadas → `deployed:<target-env>` (o
   `published:<target>`). Recalcular `state:` (§6 Lifecycle).

   **Sincronizar el tracker (v0.26, no opcional)**: si hay tracker
   `owner`, **siempre** proponer reflejar `deployed:<target-env>` en
   el work item de ADO mapeado (`Closed` + comentario de ambiente —
   §6 *Sincronización con el tracker durante el lifecycle*). Fricción
   según `creation_mode`.

7. **CLOSE** — URL del PR/release, qué gates faltan, siguiente paso
   sugerido (usar el siguiente nombre de `promotion_path`, no asumir
   `qa`).

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
