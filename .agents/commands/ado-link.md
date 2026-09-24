---
name: ado-link
description: Vincular un PR a uno o más work items de Azure DevOps (sólo si tracker=azure-devops)
argument-hint: <pr> <wi> [--tracker <name>]
model-class: mecanico    # mapea spec <-> work item; no decide nada
---

# `/ado-link <pr-id> <wi-id> [--tracker <name>]` — Vincular PR a work items de Azure DevOps

> **Argumentos:** `$ARGUMENTS` — si el token aparece sin sustituir, los
> argumentos son el texto con el que se invocó el comando.

**Aplicabilidad**: este comando aplica **sólo si**
`repo-config.yaml > tracker: azure-devops` (§6 *Configuración del
repo*). Si el tracker es otro o `none`, **parar** y proponer el
equivalente (`/gh-link`, `/jira-link`, etc.) o reportar que no aplica.

Para PR `<pr-id>` con work items `<wi-ids>` (separados por coma):

> **PARADA — el veredicto va primero.** Si en cualquier paso de abajo te
> paras a preguntar, escribe antes `result.json` con
> `status: needs_input`, la pregunta y su `owner`. Quien te lanzó no ve
> tu pantalla.

0. **Leer `repo-config.yaml`** y verificar `tracker: azure-devops`. Si
   no lo es, parar con el mensaje arriba.
1. Verificar que el PR existe y que el repo pertenece al project
   declarado en `tracker_config.org` / `tracker_config.project`.
2. Verificar que los work items existen; si están en otro project,
   usar relación **Related** (no Parent), §6 del methodology.
3. Linkear vía `az repos pr update --id <pr-id> --work-items <wi-ids>`.
4. Si el PR description no menciona `AB#<id>`, proponer agregarlo
   (mejora la auto-trazabilidad de ADO).
5. Reportar resultado y URLs.

Requiere MCP `azure-devops` configurado (ver AGENTS.md § Servidores MCP)
o `az` CLI autenticado.

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
