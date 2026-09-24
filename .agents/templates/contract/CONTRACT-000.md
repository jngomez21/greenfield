---
id: CONTRACT-000
titulo: Estándar del contrato de disciplina
version: 1.0.0
estado: DRAFT
owner: plataforma
---
<!--
  PLANTILLA AI-DLC — estándar de contrato de disciplina (canonical:
  .agents/templates/contract/). `/contract-new` la usa como base para
  cualquier tipo declarado en `.org/contract-types.yaml`.

  Ver §9 *Tipos de contrato: cómo entra una disciplina* del methodology.
  Este archivo es la NORMA del formato, no un contrato concreto: no se
  edita por feature y no se copia tal cual.

  Para un contrato real, copiar la plantilla de su subtipo —DF-000.md
  (flujo), DC-000.md (componente), DS-000.md (fundamentos)— y
  renombrarla con su `id`. Para un tipo que todavía no tiene plantilla
  propia (POL-*, SLO-*, DAT-*…), crear el archivo siguiendo las
  secciones obligatorias de §3 de este documento.
-->

# CONTRACT-000 — Estándar del contrato de disciplina

Estándar **genérico**: aplica a cualquier tipo declarado en `.org/contract-types.yaml`
(diseño, cumplimiento, operaciones, datos, contenido…). Cada tipo añade sus
secciones específicas; **ninguno puede quitar** las obligatorias de aquí.

Este documento es corto a propósito. Si crece más allá de lo que un dueño de
disciplina puede leer de una vez, deja de cumplir su función.

---

## 1. Qué es y qué no es

| Es | No es |
|---|---|
| El acuerdo **verificable** entre quien produce una restricción y quien la implementa | Documentación, contexto, justificación o material de comunicación |
| Corto, versionado, con `id` estable | Un documento vivo que crece por acumulación |
| Vinculante desde `AGREED` | Vinculante por existir |
| Semántico (qué debe cumplirse) | Prescriptivo de implementación (cómo hacerlo) |

### Prueba ácida

> **Si no se puede escribir cómo se comprueba, no es contrato.**

Aplicar línea por línea. Lo que no la pasa se va a la documentación (que puede
vivir donde el equipo quiera y **no** se versiona como norma).

**Pero no todo lo descartado es ceremonia.** La *guía de decisión* —cuándo usar
esto y no aquello— no se verifica, así que no es contrato; y sí se echa de
menos, así que tampoco es relleno. De ella, la **forma decisoria** sube al
contrato como columna (*"cuándo usarla / cuándo no"*) y la **elaborada** se
queda en la documentación de la disciplina, referenciada como insumo. No se
crea un artefacto nuevo para alojarla: eso es costo desproporcionado (§9).

### Insumo ≠ contrato

Prototipos, maquetas, demos, MVPs, wireframes, bocetos y código generado son
**insumo**: se referencian por ruta/URL y fecha, no se versionan como norma, no
se citan como `D-N` y no bloquean gates. El contrato es lo que se **extrae** de
ellos. El insumo puede no existir; el contrato sigue siendo posible.

---

## 2. Frontmatter obligatorio (artefacto humano) y su espejo en el máquina

El bloque de abajo vive en el **`.md`**. El artefacto máquina lleva su
**espejo**: `id`, `version`, `estado`, `tipo` y `derived` como mínimo
—en JSON, en la raíz; en un archivo W3C de tokens, bajo `$extensions`
del grupo raíz (ver `DS-000.md`)—. `owner`, `consumers` y
`implementability` pueden vivir sólo en el humano.

`/contract-verify` corre el check de frontmatter completo sobre el
**humano**, y el de coincidencia `id`/`version`/`estado` **entre los
dos**.

```yaml
---
id: <PREFIJO>-<SLUG>              # estable para siempre; es lo que se cita
tipo: <id del tipo en contract-types.yaml>
version: <MAJOR.MINOR.PATCH>
estado: DRAFT | NEGOTIATING | AGREED | IMPLEMENTED | LIVE | DEPRECATED
derived: false                    # true = derivado del código existente (brownfield)
scope: feature | repo | organizacion

owner:
  disciplina: <diseno | juridica | operaciones | datos | ingenieria | …>
  persona: "@<usuario>"
consumers:
  - <repo, equipo o producto>

human_artifact: <ruta de este archivo>
machine_artifact: <ruta del .json / .yaml / .schema>

implementability:                 # requerido para pasar a AGREED
  confirmado_por: "@<usuario>"
  fecha: <YYYY-MM-DD>
  salvedades: []                  # lista; vacía si no hay

supersedes: <id@version>          # opcional
deprecated_at: <YYYY-MM-DD>       # sólo en estado DEPRECATED
sunset_date: <YYYY-MM-DD>         # mínimo 90 días después de deprecated_at
replaced_by: <id@version>
---
```

**Regla `derived`.** En brownfield la v1 documenta **lo que hay**, no lo que
debería ser. Un contrato `derived: true` no puede citarse como norma para
elementos nuevos; el estado ideal llega por amendment.

---

## 3. Secciones obligatorias (artefacto humano)

### 3.1 Propósito — 3 líneas máximo
Qué restringe y por qué existe. Si necesita más de tres líneas, es documentación.

### 3.2 Alcance
Qué cubre y —explícitamente— **qué no cubre**. Lo segundo evita más discusiones
que lo primero.

### 3.3 Especificación
El cuerpo normativo. Cada afirmación debe pasar la prueba ácida. Formato libre
según el tipo, pero **cada elemento con identificador propio** para poder
citarlo desde una `R*.*`, un test o un bug.

### 3.4 Criterios de aceptación
Tabla obligatoria. Sin ella el contrato no puede pasar de `NEGOTIATING`.

| ID | Criterio | Cómo se verifica | Nivel |
|---|---|---|---|
| AC-1 | *(observable, no opinable)* | test / lint / auditoría / revisión humana | automático \| manual |

### 3.5 Dependencias del contrato
Otros contratos que éste asume vigentes, por `id` + `version`.
Si especializa a uno de nivel superior, declararlo aquí; si lo **contradice**,
registrar la excepción con motivo (§9 del methodology).

### 3.6 Bindings *(opcional, N secciones)*
Traducción a una plataforma o stack concreto (web, escritorio, móvil, CLI).
**Informativo, no normativo.** Un binding que contradice la semántica es un bug
del binding. Un contrato sin bindings es perfectamente válido.

### 3.7 Insumos de referencia *(opcional)*
De dónde salió: maqueta, prototipo, demo, captura, conversación.
Ruta o URL + fecha. **No versionado.**

### 3.8 Historial
| Versión | Fecha | Cambio | Breaking |
|---|---|---|---|

---

## 4. Ciclo de vida

```
DRAFT ──► NEGOTIATING ──► AGREED ──► IMPLEMENTED ──► LIVE ──► DEPRECATED
```

| Estado | Significado | Condición para entrar |
|---|---|---|
| `DRAFT` | Borrador del dueño | — |
| `NEGOTIATING` | Propuesto al consumidor | Criterios de aceptación completos |
| `AGREED` | Acordado y vinculante | **Implementability check** del consumidor |
| `IMPLEMENTED` | Implementado, no disponible donde se necesita | — |
| `LIVE` | Disponible en el ambiente que lo consume | — |
| `DEPRECATED` | Reemplazado | `sunset_date` ≥ 90 días |

**SLAs y escalación**: idénticos a los de `D-N` en §6 del methodology
(`NEGOTIATING` > 10 días hábiles ⇒ escalación; `AGREED` > 6 semanas sin
`IMPLEMENTED` ⇒ conversación entre leads).

**Versionado SemVer**: `MAJOR` = cambio incompatible para el consumidor;
`MINOR` = añade sin romper; `PATCH` = corrección o aclaración.

**Deprecación**: no se borra, se mueve a `deprecated/` con `sunset_date`.
Es acción **irreversible**: requiere OK explícito y notificación a `consumers`.

---

## 5. Implementability check

Antes de `AGREED`, el consumidor responde por escrito:

1. ¿Es construible con lo declarado en `stack/`?
2. ¿El costo es proporcional al valor? *(si no, negociar alcance)*
3. ¿Hay algo existente que ya lo cubre? *(evita duplicar contratos)*
4. ¿Los criterios de aceptación son verificables como están escritos?

Resultado: `AGREED` (con salvedades registradas si las hay) **o** vuelta a
`NEGOTIATING` con la objeción concreta.

> Desde `AGREED` el contrato **no se renegocia caso por caso**. Una discrepancia
> posterior es un bug (Tipo A/B/C/E) o un amendment (`AMD-NNN`) — con registro,
> no una discusión.

---

## 6. Cómo se cita desde una spec

```markdown
### D<n> — <ID>@<version> (<tipo>: <descripción corta>)
- **Tipo**: contrato / disciplina: <disciplina>
- **Estado**: AGREED
- **Contrato**: <ruta del artefacto humano> (+ artefacto máquina)
- **Owner**: <disciplina> / @<usuario>
- **Implementability**: confirmado <fecha> por @<usuario> — salvedades: <…>
- **Estrategia**: MOCK | BLOCK | PIN | WORKAROUND | NONE
- **Ready to unmock**: <condición observable>
```

Es la sección `Dependencies` que ya existe. Sin mecanismo nuevo.

---

## 7. Anti-patrones

| Anti-patrón | Síntoma | Mitigación |
|---|---|---|
| **Contrato-enciclopedia** | Introducción, contexto, beneficios, audiencia, resultado esperado… y 3 líneas normativas | Prueba ácida. Lo demás es documentación |
| **Criterios opinables** | "El componente debe verse moderno y limpio" | Todo criterio necesita columna *cómo se verifica* |
| **`AGREED` unilateral** | El dueño marca `AGREED` sin que el consumidor mire | `implementability` es campo obligatorio para ese estado |
| **Contrato ideal en brownfield** | La v1 describe lo que se quisiera; la realidad no lo cumple | `derived: true` en la v1 |
| **Re-especificar un producto de terceros** | 5.000 líneas describiendo un componente de la librería del proveedor | Perfil de adopción: qué se permite, qué se prohíbe, qué se enlaza |
| **Contrato sin consumidores** | Nadie lo cita; nadie sabe si se cumple | Si tras 90 días no hay `D-N` que lo cite, se archiva |
| **Insumo tratado como contrato** | El prototipo se cita como `D-N` y bloquea un gate | Insumo se referencia, contrato se cita |
| **Tipo declarado sin caso real** | El registro tiene 8 tipos y se usa 1 | Un tipo entra cuando hay caso que lo ejerce |
