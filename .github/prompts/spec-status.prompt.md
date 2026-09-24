---
name: spec-status
description: Estado legible — de una feature (con slug) o panorama del repo (sin slug) (read-only)
argument-hint: [<slug>]
model-class: mecanico    # reporta lo que los archivos ya dicen
---

# `/spec-status [<feature-slug>]` — Estado legible (read-only)

> **Argumentos:** `$ARGUMENTS` — si el token aparece sin sustituir, los
> argumentos son el texto con el que se invocó el comando.

Dos modos según el argumento. Ninguno escribe nada.

> **PARADA — el veredicto va primero.** Si en cualquier paso de abajo te
> paras a preguntar, escribe antes `result.json` con
> `status: needs_input`, la pregunta y su `owner`. Quien te lanzó no ve
> tu pantalla.

## Sin argumento — panorama del repo ("¿y ahora qué?")

Es la respuesta a *"¿en qué íbamos?"*, *"retomo después de
vacaciones"*, *"no sé qué sigue"*. También es lo que el agente ofrece
al **abrir sesión sin pedido concreto** (ver AGENTS.md § Protocolo).

1. Listar `specs/*/status.md` y leer frontmatter de cada una
   (ignorar `legacy` salvo conteo).
2. Si existe `scripts/spec-lint`, correrlo y partir de su salida.
3. Producir el panorama:

   | Feature | State | Próxima acción concreta |
   |---|---|---|
   | `<slug>` | `in-progress` | T4 pending — `/spec-implement <slug>` |
   | `<slug>` | `partial-deploy-pruebas` | QA sign-off pendiente — `/spec-promote --to qa` cuando firme |
   | `<slug>` | draft sin G2 | 2 OPEN_QUESTIONS — `/spec-clarify <slug>` (o `/contract-new` si esperan el `id` de un contrato) |

   Más: tasks `blocked` con su causa (`blocked_by`), `D-N` que
   exceden SLAs (§6), gates pendientes de firma, drift declarado vs
   derivado, drift de tracker (ADO vs `status.md`, ver abajo), y
   conteo de `legacy`.
4. Cerrar con **una recomendación concreta**: *"lo más
   desbloqueante ahora es X porque Y. ¿Arranco con eso?"* — no una
   lista neutra de 10 opciones. Si no hay nada activo, proponer
   `/spec-new` o revisar el backlog del tracker (si hay).

## Con `<feature-slug>` — detalle de una feature

Leer (sin modificar nada):

- `requirements.md` → contar `R*.*` totales, agrupar por estado;
  `[NEEDS CLARIFICATION]` y `OPEN_QUESTIONS` abiertas (bloquean G2).
- `checklists/requirements.md` → items pendientes (G2).
- `tasks.md` + `status.md` → done / in-progress / pending / blocked
  (con causa), fase/slice actual, tabla Gates.
- `bugs.md` → bugs abiertos por tipo (A/B/C/D/E).
- (si existe) `amendments.md` → últimos `AMD-NNN` y `HANDOFF-NNN`.
- Sección `Dependencies` de `requirements.md` → `D-N` y su estado (§6).
- Última ejecución de tests por nivel con cuántos `R*.*` cubre cada
  nivel.
- **Si `status.md > work_items` declara tracker**: comparar (read-only,
  vía MCP) el estado real del work item en ADO contra el estado
  declarado en `status.md` y reportar drift — ej. *"task T4 `done` en
  status.md pero el work item AB#6791 sigue en `New`; ¿lo
  actualizo?"* (§6 *Sincronización con el tracker* del methodology).

Producir un resumen humano con: progreso global de `R*.*`, tasks por
estado y causa, cobertura de tests **por nivel** (no sólo global),
bugs abiertos con tipo, amendments recientes, gates firmados vs
pendientes, y **siguiente paso sugerido** (una acción concreta con su
comando, no un menú).

Pensado para retomar trabajo tras una pausa (límite de tokens, fin de
jornada, handoff). **NO escribe nada**.

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
