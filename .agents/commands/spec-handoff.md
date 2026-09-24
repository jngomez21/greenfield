---
name: spec-handoff
description: Transferir ownership de una feature a otro dev (rotación, baja)
argument-hint: <slug> --to <@user>
model-class: redaccion   # empaqueta lo que ya esta decidido
---

# `/spec-handoff <feature-slug> --to <@user>` — Transferir ownership

> **Argumentos:** `$ARGUMENTS` — si el token aparece sin sustituir, los
> argumentos son el texto con el que se invocó el comando.

Sigue el protocolo §7 (AGENTS.md). Para feature `<feature-slug>` con destino
`<@new-owner>`:

> **PARADA — el veredicto va primero.** Si en cualquier paso de abajo te
> paras a preguntar, escribe antes `result.json` con
> `status: needs_input`, la pregunta y su `owner`. Quien te lanzó no ve
> tu pantalla.

1. **CONTEXT** — leer `requirements.md`, `status.md`, `amendments.md`,
   `bugs.md`, commits recientes del worktree y `OPEN_QUESTIONS`.

2. **CLARIFY** — preguntar: handoff total o parcial; dev saliente
   sigue accesible; conversaciones abiertas con equipos proveedores
   de `D-N` que sólo el dev saliente conocía.

3. **GENERATE RESUMEN** — producir resumen ejecutable para el new
   owner (mostrar primero, NO escribir aún): problema y motivación;
   estado actual de tasks; `D-N` activas con último contacto conocido;
   bugs abiertos; amendments aplicados; pre-flight check obvio;
   `OPEN_QUESTIONS` con owner/due; riesgos.

4. **EXECUTE** — tras OK del dev saliente y, si está accesible, del
   new owner:
   - Actualizar `owner:` en frontmatter de `requirements.md`.
   - Re-asignar work items en el tracker declarado en
     `repo-config.yaml` (si `tracker: azure-devops`, vía
     `az boards work-item update --assigned-to`; si `github-issues`,
     vía `gh`; si `none`, omitir este paso).
   - Anotar el evento en `amendments.md` como entrada especial con
     prefijo `HANDOFF-NNN`:

     ```
     ## HANDOFF-001 — <fecha>
     - **Tipo**: total | parcial
     - **De**: @<saliente>
     - **A**: @<entrante>
     - **Motivo**: <rotación | baja | vacaciones | ayuda>
     - **Conversaciones a re-abrir**: D1 (canal X), D3 (email a Y)
     - **Resumen handoff**: <link al doc del paso 3>
     ```

   - `D-N` cuyo `Tracking:` apuntaba a una conversación personal del
     saliente: marcar como `NEGOTIATING-stale` (§6 SLAs) y proponer
     reabrir el contacto desde el nuevo owner.

5. **CLOSE** — entregar al new owner: path del worktree, link al
   resumen, acciones inmediatas sugeridas, confirmación de que el dev
   saliente puede ejecutar `git worktree remove` tras OK explícito.

Un handoff **NO** es un Amendment ni un bug — es un evento de
ownership. El prefijo `HANDOFF-` lo distingue de `AMD-` y no contamina
métricas.

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
