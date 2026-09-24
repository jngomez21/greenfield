---
name: bug-triage
description: Clasificar un bug en la taxonomía A/B/C/D/E (§8) con entrevista
argument-hint: <descripcion del bug>
model-class: criterio    # la taxonomia decide si el defecto vuelve a la spec
---

# `/bug-triage <descripción>` — Clasificar bug en taxonomía A/B/C/D/E

> **Argumentos:** `$ARGUMENTS` — si el token aparece sin sustituir, los
> argumentos son el texto con el que se invocó el comando.

Sigue el protocolo §7 (AGENTS.md). Para el bug descrito en `<descripción>`:

> **PARADA — el veredicto va primero.** Si en cualquier paso de abajo te
> paras a preguntar, escribe antes `result.json` con
> `status: needs_input`, la pregunta y su `owner`. Quien te lanzó no ve
> tu pantalla.

1. **CONTEXT** — verificar: en qué feature/spec aparece; repro estable
   o intermitente; ¿ya hay `BUG-NNN` abierto con síntomas similares?

2. **CLARIFY** — entrevistar al reportero: qué se esperaba vs qué
   pasó; si la spec cubre el caso explícitamente (cita `R*.*`); si es
   cambio externo o defecto técnico; si la dependencia es 3rd party.

3. **PROPOSE** clasificación:
   - **A** — spec cubre el caso y el código está mal. Regression test
     + fix. **No tocar spec.**
   - **B** — spec NO cubre el caso (gap). Nuevo `R*.*` en
     `requirements.md` antes del fix.
   - **C** — spec lo cubre pero es ambigua. Refinar `requirements.md`
     + posible fix.
   - **D** — incidente en prod con SLA roto. Hotfix directo + spec
     retroactiva en post-mortem.
   - **E** — causa raíz es paquete / SaaS 3rd party. Reportar al
     vendor. Estrategia: `WORKAROUND` / `PIN` / `WAIT`. La `R*.*`
     afectada queda `blocked_by: ext:<id>` en `status.md`.
   - **Amendment** — no es bug; es cambio externo. Redirigir a
     `/spec-amend` (no contaminar la métrica de Tipo B).
   - Pedir confirmación al reportero.

4. **EXECUTE** — registrar en `bugs.md` (formato §8 Tracking):
   `BUG-NNN`, tipo, requirement afectado, fecha, reportero. Para Tipo
   B/C: abrir PR de spec antes del fix. Para Tipo E: marcar
   `blocked_by: ext:<id>` en `status.md`.

   **Sincronizar el tracker (v0.26, no opcional)**: si hay tracker
   `owner` declarado, **siempre** proponer crear o vincular un work
   item tipo **Bug** en ADO (parent = la Feature afectada), citando
   `BUG-NNN` en la descripción. **Defaults al crear** (no preguntar,
   aplicar directo salvo que el dev diga lo contrario): iteración =
   sprint actual del team, estado inicial = `Active` (nunca `New` —
   triagear el bug ya es empezar a trabajarlo). Mientras dura el fix,
   sincronizar su estado: se mantiene `Active` → `Resolved`/`Closed`
   cuando el fix mergea (Tipo E: se queda abierto/`Blocked` mientras
   el vendor no resuelva). Fricción según `creation_mode` del tracker
   — mismo modelo que §6 *Sincronización con el tracker durante el
   lifecycle* del methodology. No es algo que el reportero deba pedir.

5. **CLOSE** — siguiente paso sugerido (PR de spec, fix directo,
   workaround, escalación a vendor, etc.), y si el work item de ADO
   quedó sincronizado o pendiente.

   Para Tipo B / C, además: aplicar **ratchet harness** si el gap es
   una **clase** detectable por regla (no caso aislado). Preguntar:
   ¿qué entrada del harness — AGENTS.md, slash-command, plantilla
   EARS, `spec-lint`, hook — habría evitado este gap a priori? Si la
   respuesta existe, abrir PR sobre el harness y referenciarlo como
   `Harness PR:` en `BUG-NNN`. Si no es una clase, cerrar con el
   `R*.*` y seguir. Ver `ai-dlc-methodology.md` §8 *Ratchet harness*
   para la tabla de capas (consejo → garantía).

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
