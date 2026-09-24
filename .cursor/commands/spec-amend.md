---
name: spec-amend
description: Cambio de spec post-aprobación (cliente, regulación, negocio)
argument-hint: <slug> --reason "<motivo>"
model-class: criterio    # cambia una spec FIRMADA
---

# `/spec-amend <feature-slug> --reason "<motivo>"` — Cambio de spec post-aprobación

> **Argumentos:** `$ARGUMENTS` — si el token aparece sin sustituir, los
> argumentos son el texto con el que se invocó el comando.

Para feature `<feature-slug>` con motivo `<motivo>`:

> **PARADA — el veredicto va primero.** Si en cualquier paso de abajo te
> paras a preguntar, escribe antes `result.json` con
> `status: needs_input`, la pregunta y su `owner`. Quien te lanzó no ve
> tu pantalla.

1. **CONTEXT** — leer `requirements.md`, `tasks.md`, `status.md` y
   `amendments.md` (si existe) de la feature.
2. **ALCANCE** — identificar qué `R*.*` y tasks están potencialmente
   afectadas (proponer, NO decidir en solitario). Confirmar con el
   usuario el alcance final del cambio.
3. **WORKTREE/RAMA** — preparar el espacio aislado **antes de tocar
   ningún archivo** (§6 *Worktree, ramas y flujo de promoción*,
   convención `amend/...`):
   - **Numerar el amendment**: elegir el siguiente `AMD-NNN` leyendo
     `amendments.md` (si no existe, `AMD-001`). Reservar el número
     para la rama y los commits.
   - **Determinar rama base** según `status.md`:
     - Feature aún en desarrollo (state ≠ `deployed:*`/`live`,
       worktree `feat/<slug>` vivo): trabajar **sobre la misma**
       `feat/<slug>` — sólo verificar `cwd` y continuar.
     - Feature ya mergeada (state `deployed:<env>` o `live`,
       worktree borrado): crear rama nueva desde el ambiente vivo.
   - **Proponer** y pedir OK antes de ejecutar (acción reversible
     pero observable, §3.16):
     ```bash
     git worktree add -b amend/<feature-slug>/AMD-NNN \
       ../<repo>--amend-<feature-slug>-<NNN> \
       origin/<base-branch>
     ```
   - **Verificar** que el `cwd` quedó en el worktree/rama correcta
     **antes** de editar nada. Editar directo sobre `main` (o
     cualquier rama de ambiente) es un anti-patrón (§8 *Amendments*).
4. **EDITAR `requirements.md`**:
   - `R*.*` que dejan de aplicar se marcan ~~tachadas~~ (no se borran).
   - `R*.*` que cambian se reescriben in-place.
   - `R*.*` nuevas se añaden con la siguiente numeración disponible.
   - **Migración de versión**: subir `methodology_version:` de
     `status.md` a la versión actual (`.ai-dlc-version` del root) y
     correr `scripts/spec-lint --feature <feature-slug> --strict`:
     re-tocar la spec la compromete con las reglas vigentes (linteo
     versionado). Resolver los hallazgos como parte del amendment.
5. **EDITAR `tasks.md`**: tasks que dejan de aplicar → `cancelled`;
   tasks que cambian → modificadas; tasks nuevas → al final, ordenadas
   por dependencia.

   **Sincronizar el tracker (v0.26, no opcional)**: si hay tracker
   `owner` declarado y alguna task cambió de estado por este amendment
   (ej. `done`→reabierta porque el requirement cambió, o
   →`cancelled`), **siempre** proponer reflejarlo en el work item de
   ADO mapeado — mismo mapeo de estados de §6 *Sincronización con el
   tracker durante el lifecycle* (`cancelled`→`Removed`, task
   reabierta→`Active` de nuevo aunque antes estuviera `Resolved`).
6. **REGISTRAR** el evento en `amendments.md` (crear si no existe) con
   el `AMD-NNN` reservado en el paso 3:

   ```
   ## AMD-NNN — <título corto> (<fecha>)
   - Motivo: <descripción + fuente: cliente / legal / negocio>
   - Autor: <quién lo dictó> vía <quién lo registró>
   - R*.* afectadas: <lista>
   - Tasks afectadas: <lista>
   - PR de spec: !<id>
   - PR de implementación: !<id>
   ```

7. **Sincronizar el work item de Feature (v0.26, no opcional)**: si
   hay tracker `owner`, **siempre** proponer comentar el work item de
   Feature en ADO con `AMD-NNN` + el motivo (fricción según
   `creation_mode`, mismo modelo que el resto de la sincronización).
   No requiere crear un work item nuevo — un Amendment no es un tipo
   propio en el mapeo de §13, es un evento sobre la Feature/User
   Stories existentes.

8. Los commits posteriores citan `AMD-NNN` además de `R*.*`.

Un Amendment **NO** es un bug Tipo B. Tipo B son cosas que estaban mal
desde el inicio; un Amendment es un evento nuevo posterior a la
aprobación. Mantener la distinción mejora la métrica de calidad de
spec authoring.

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
