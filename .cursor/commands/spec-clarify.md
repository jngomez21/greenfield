---
name: spec-clarify
description: Resolver ambigüedades de una spec con preguntas estructuradas antes de firmar G2
argument-hint: <slug> [--respuesta-del-hub <Q-NNN> --hub <ruta>]
model-class: criterio    # resuelve ambiguedad; si se equivoca, la spec queda mal
---

# `/spec-clarify <feature-slug> [--respuesta-del-hub <Q-NNN> --hub <ruta>]` — Clarificación estructurada

> **Argumentos:** `$ARGUMENTS` — si el token aparece sin sustituir, los
> argumentos son el texto con el que se invocó el comando.

Sigue el protocolo §7 (AGENTS.md). Reduce la ambigüedad residual de
`specs/<feature-slug>/requirements.md` **antes** de firmar G2. Se
invoca después de `/spec-new` (o en cualquier momento mientras
`status: draft | in-review`). Read-mostly: sólo escribe en
`requirements.md` y `checklists/requirements.md`.


> **PARADA — el veredicto va primero.** Si en cualquier paso de abajo te
> paras a preguntar, escribe antes `result.json` con
> `status: needs_input`, la pregunta y su `owner`. Quien te lanzó no ve
> tu pantalla.

## 0. UNA RESPUESTA QUE BAJA DEL HUB — sólo con `--respuesta-del-hub`

Con esos dos flags **no vienes a buscar ambigüedad**: vienes a
**incorporar un dato que ya llegó**. Haz esto y para; el resto del
comando no aplica.

1. **Lee `<ruta>/initiatives/<slug>/questions/<Q-NNN>.yaml`.** La
   respuesta viene en el archivo y **no** en los argumentos, a propósito:
   el texto lleva `¿`, comillas y saltos de línea, y cada runtime los
   escapa distinto. Un dato copiado a un argumento es un dato que se
   puede mutilar sin que nadie lo note.
2. **Localiza qué cerraba esa pregunta aquí.** Es una `OPEN_QUESTION` de
   `requirements.md`, una `D-N` de `design.md` en `MOCK`, o las dos. El
   campo `question` del archivo es **literalmente el texto que este repo
   escribió** cuando escaló, así que es la forma fiable de encontrarlo —
   no busques por parecido.
3. **Incorpora la respuesta** donde corresponda: cierra la
   `OPEN_QUESTION`, y si había una `D-N` en `MOCK` cuyo dato era éste,
   actualiza su estrategia y su `Ready to unmock`.
4. **Si la respuesta NO responde** —un *"no sé"*, un dato parcial, algo
   que contradice lo que ya está escrito— **no la incorpores**. Deja todo
   como está y repórtalo con `status: needs_input` y `escalate: true`:
   volvió mal ruteada, y forzarla aquí mete un dato falso en una spec.
5. **Si la pregunta ya estaba cerrada** —alguien la resolvió por otra
   vía— dilo y no toques nada. Que baje dos veces es normal.

**No toques `status.md`.** Incorporar un dato no firma un gate.


1. **CONTEXT** — leer `requirements.md` completo (incluida la
   checklist si existe). Si `status: approved` o posterior, **parar**:
   los cambios a una spec aprobada van por `/spec-amend`, no por
   clarify.

2. **SCAN de ambigüedad** — evaluar la spec contra esta taxonomía y
   marcar cada categoría `Clara` / `Parcial` / `Faltante`:

   | Categoría | Qué busca |
   |---|---|
   | Alcance | Límites difusos, "fuera de scope" vacío, slices sin prueba independiente |
   | Dominio y datos | Entidades sin definir, cardinalidades ambiguas, ciclo de vida de los datos (retención, borrado) |
   | Flujo de interacción | Pasos del usuario sin orden claro, estados de UI/proceso sin transiciones |
   | Atributos no funcionales | "rápido/seguro/escalable" sin umbral; NFRs faltantes para el tipo de feature |
   | Integraciones y D-N | Dependencias mencionadas en prosa pero no declaradas como D-N; contratos sin versión |
   | Edge cases | Vacío, máximo, concurrencia, duplicados, errores de terceros sin R*.* |
   | Restricciones | Legal/compliance/residencia de datos no cruzadas con `stack/security.md`; límites del stack |
   | Terminología | Mismo concepto con dos nombres; jerga del cliente sin definir |
   | Señal de completitud | ¿Cómo se sabe que la feature está "lista"? Métricas de éxito no observables |
   | Otro | Lo que no encaje arriba |

   **Insumos adicionales del scan** (entran a la misma cola):
   - Marcadores `[NEEDS CLARIFICATION: ...]` inline (prioridad alta —
     el autor ya sabía que faltaba).
   - `OPEN_QUESTIONS` abiertas cuyo dueño es el propio dev presente
     (las de owner externo NO se inventan aquí — siguen abiertas con
     su due).

> **Promover a `D-N` es cerrar, no aplazar.** Si al mirar una ambigüedad
> resulta que ya se sabe **qué** construir y lo que falta es el **dato**
> —un endpoint, un catálogo, un proveedor—, muévela a `Dependencies` con
> su estrategia (`MOCK`/`PIN`/`WORKAROUND`) y **ciérrala en
> `OPEN_QUESTIONS` citando su `D-N`**.
>
> No es despacharla: el dato sigue pendiente, con su `owner`, su `ETA` y
> su `Ready to unmock`. Lo que se cierra es **la ambigüedad para
> diseñar**. Dejarla abierta bloquea `/spec-design` y con él G2, por algo
> que ya tiene sustituto (§6 *Una `D-N` y una `OPEN_QUESTION` no son lo
> mismo*).
>
> **No promuevas** si la respuesta cambiaría *qué* se construye en vez de
> *con qué*: un mock no sustituye una decisión de comportamiento.

3. **PRIORIZAR** — máximo **5 preguntas** por sesión, ordenadas por
   `impacto × incertidumbre` (impacto = cuánto cambia
   arquitectura/datos/UX/tests si la respuesta sorprende). Si hay más
   de 5 candidatas, las restantes se listan al final como *diferidas*
   (el dev decide si correr otra sesión o registrarlas como
   `OPEN_QUESTIONS` con owner/due).

4. **PREGUNTAR — una a la vez**, formato obligatorio:
   - **Multiple choice** (default): tabla de 2-5 opciones, con la
     recomendada marcada y justificada en 1 línea:

     > **P1 (Atributos no funcionales)** — R2.1 dice "la búsqueda
     > responde rápido". ¿Qué umbral fijamos?
     >
     > | Opción | Umbral | Notas |
     > |---|---|---|
     > | A (Recomendada) | p95 < 1s | consistente con el resto del módulo |
     > | B | p99 < 500ms | exige cache; ¿lo justifica el caso? |
     > | C | Otro | dime el valor |
   - **Respuesta corta** cuando no hay opciones enumerables: pedir
     valor concreto (≤5 palabras) y ofrecer un default sugerido.
   - Si el dev contesta "la recomendada" / "ok", usar la propuesta.
   - Esperar la respuesta antes de la siguiente pregunta (§3.12).

5. **INTEGRAR cada respuesta inmediatamente** (no acumular al final):
   - Registrar en la sección `## Clarifications` de `requirements.md`
     bajo `### Session <YYYY-MM-DD>`:
     `- Q: <pregunta> → A: <respuesta final>`
   - **Aplicar** la decisión donde corresponda: reescribir el `R*.*`
     afectado, agregar uno nuevo, actualizar NFR/edge case/D-N, y
     borrar el marcador `[NEEDS CLARIFICATION]` resuelto.
   - Si la respuesta resuelve una `OPEN_QUESTION`, marcarla
     `- [x] ... resuelto: <fecha> con <decisión corta>`.
   - No reordenar secciones ni renumerar R*.* existentes.

6. **RE-VALIDAR checklist** — si existe
   `checklists/requirements.md`, re-evaluar los items afectados y
   actualizar `[ ]`→`[x]` sólo donde el estado realmente cambió.
   Reportar conteo antes/después.

7. **CLOSE** — reportar:
   - Tabla de cobertura: categoría → Clara / Parcial / Faltante /
     Diferida.
   - Q&A integradas y R*.* tocados.
   - Marcadores `[NEEDS CLARIFICATION]` y `OPEN_QUESTIONS` restantes
     (recordar: bloquean G2).
   - Siguiente paso sugerido: otra sesión de clarify si quedaron
     marcadores de ambigüedad; si queda una `OPEN_QUESTION` esperando
     el `id` de un contrato de disciplina, **`/contract-new`** (esta
     sesión no la puede cerrar: su dueño es la disciplina, no el dev
     presente); si no queda ninguna, **`/spec-design <slug>`** para
     llenar `design.md`, que es requisito de G2. Después completar la
     checklist y pedir la firma (`/spec-verify --pre-g2` primero).

**Anti-patrones**: preguntar las 5 de una vez (abruma y el dev contesta
mal); preguntar lo que la spec ya responde (leer antes de preguntar);
hacer preguntas genéricas de catálogo en vez de citar el texto
ambiguo concreto; "resolver" en el chat sin persistir en
`## Clarifications` (la decisión se pierde — es el anti-patrón que
esta sesión existe para evitar).

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
