---
name: contract-new
description: Crear un contrato de disciplina (diseño, política, ops, datos) con entrevista al dueño y artefacto dual humano+máquina
argument-hint: <tipo> <id>
model-class: redaccion   # llena una plantilla de contrato
---

# `/contract-new <tipo> <id>` — Contrato de disciplina

> **Argumentos:** `$ARGUMENTS` — si el token aparece sin sustituir, los
> argumentos son el texto con el que se invocó el comando.

Sigue el protocolo §7 (AGENTS.md). Produce un **contrato de disciplina**
verificable a partir de una entrevista con su dueño: el par artefacto
**humano** (markdown, para revisión y auditoría) + artefacto **máquina**
(JSON/YAML, para que el agente lo consuma sin interpretar prosa).

Ver §9 *Tipos de contrato* y §12 *Integración con el servicio de
diseño* del methodology.

**Dos modos.** Si el `<id>` **ya existe**, esto es una **enmienda**:
se carga la versión vigente, se sube versión y se registra el cambio.
**La regla de origen del paso 2 no aplica a una enmienda** — la v2 de
un contrato derivado es precisamente lo que deja de describir lo que
hay para declarar lo que se acuerda, así que nace `DRAFT` y sigue el
ciclo normal, aunque haya código en producción.

**Ejemplos**: `/contract-new design DC-tabla-datos` ·
`/contract-new design DS-fundamentos` · `/contract-new policy POL-retencion-pii`

> **PARADA — el veredicto va primero.** Si en cualquier paso de abajo te
> paras a preguntar, escribe antes `result.json` con
> `status: needs_input`, la pregunta y su `owner`. Quien te lanzó no ve
> tu pantalla.

1. **CONTEXT** — verificar antes de escribir nada:
   - `repo-config.yaml` declara `disciplines` y el `<tipo>` pedido —
     **o** el alias legacy `design_service`, que §12 declara
     equivalente para el tipo `design`. Si el repo trae el alias,
     seguir y **proponer** (sin ejecutar) migrarlo a `disciplines`.
     Si **no** declara ninguno: parar y preguntar si se quiere activar
     la disciplina. **No** crear el bloque por iniciativa propia —
     activar una disciplina es decisión del equipo.
   - El `<tipo>` existe en el registro (`.org/contract-types.yaml` o
     el path que declare `contract_types_registry`). Si no existe:
     parar. Agregar un tipo al registro es una decisión de plataforma,
     no un efecto colateral de crear un contrato.
   - **Overlap check**: buscar contratos existentes del mismo tipo en
     `specs/*/`, `.ai-dlc/design/` y `.org/contracts/<tipo>/`. Si ya
     hay uno que cubre esto, proponer **citarlo o extenderlo** en vez
     de crear uno nuevo. Contratos duplicados son la vía rápida a un
     catálogo que nadie cree.

1bis. **¿NUEVO O ENMIENDA?** — si el `<id>` ya existe (el overlap check
   lo encontró), **es una enmienda**. Entonces:
   - Cargar la versión vigente como punto de partida. **No** se
     reescribe desde la plantilla: se edita lo que cambia.
   - **Saltar el paso 2** (origen). Una enmienda no tiene origen: el
     contrato ya existe. En particular, la v2 de un contrato
     `derived: true` **no** vuelve a nacer derivada — es justo lo
     contrario: deja de describir lo que hay para declarar lo
     acordado, así que `derived: false` y estado `DRAFT`.
   - **Subir la versión** (§9 *SemVer*): `MINOR` si añade sin romper a
     ningún consumidor declarado, `MAJOR` si rompe. Preguntar cuál con
     la lista de `consumers` delante — es la información que decide.
   - Registrar la fila en la sección **Historial** del contrato: qué
     cambió y si es breaking.
   - Al cerrar, el estado es **`NEGOTIATING`**: una enmienda vuelve a
     necesitar el acuerdo del consumidor. `/contract-verify` la evalúa
     con el implementability check normal, no con el de fidelidad.

2. **DETECTAR EL ORIGEN** *(sólo si es contrato nuevo)* — determina el
   resto de la conversación:

   | Origen | Señal | Consecuencia |
   |---|---|---|
   | **Greenfield** | No hay implementación previa | El contrato declara lo que *debe* ser. `derived: false` |
   | **Brownfield** | Ya hay código en producción que lo implementa | La v1 documenta **lo que hay**, no lo ideal → `derived: true` (§16). Leer el código y extraer variantes, estados y valores reales |
   | **Terceros** | Es un componente de una librería externa | **No** re-especificar al proveedor: perfil de adopción (qué se permite, qué se prohíbe, qué se enlaza, qué se desvía y por qué). 10-30 líneas |

3. **INSUMO** — preguntar qué insumo existe (maqueta, prototipo, demo,
   MVP funcional, boceto, código generado, descripción escrita, o
   **ninguno**). Reglas no negociables (§12):
   - El insumo se **referencia** por ruta/URL + fecha. Nunca se copia
     al contrato ni se versiona como norma.
   - **Ningún insumo es fuente de verdad del comportamiento**: eso vive
     en `requirements.md` en EARS. Si el insumo revela comportamiento
     no especificado, se propone `/spec-amend` — no se silencia.
   - Si el insumo es un **demo o MVP funcional**, exigir la decisión
     explícita: ¿spike (código throwaway) o integración (código que se
     queda)? Confundirlas es caro en las dos direcciones.
   - **Sin insumo el comando sigue siendo válido.** Se entrevista y ya.

4. **ENTREVISTA** — cargar la plantilla **del subtipo** desde
   `.agents/templates/contract/`:

   | Subtipo | Plantilla |
   |---|---|
   | `DF-*` flujo (el primero en greenfield, §16) | `DF-000.md` |
   | `DC-*` componente | `DC-000.md` |
   | `DS-*` fundamentos | `DS-000.md` |
   | Componente de **terceros** (origen *Terceros* del paso 2) | `DC-000.md`, **modo perfil** (su §1bis reemplaza a §3-§8) |
   | Cualquier otro tipo (`POL-*`, `SLO-*`, `DAT-*`…) | `CONTRACT-000.md` §3, que declara las secciones obligatorias comunes |

   `CONTRACT-000.md` es la **norma del formato**, no un esqueleto que
   se copie tal cual: para un tipo sin plantilla propia se sigue su §3
   y se crea el archivo con esas secciones. Recorrer las secciones
   obligatorias de la plantilla que corresponda. Máximo **5 preguntas por
   tanda**, una a la vez, con opciones tabuladas y una recomendada.

   Insistir en lo que la gente olvida y luego cuesta caro:
   - **Qué NO cubre** el contrato (evita más discusiones que el alcance).
   - **Todos** los estados, incluidos vacío, carga, error, sin permisos
     y sin resultados. Un estado no declarado es un gap de contrato
     (bug Tipo B), no una decisión libre del implementador.
   - **Cuándo NO usar** cada variante, no sólo cuándo sí.
   - Accesibilidad como criterio **verificable**, no como intención.

5. **PRUEBA ÁCIDA** — antes de escribir, pasar cada afirmación por:

   > **Si no se puede escribir cómo se comprueba, no es contrato.**

   Lo que no la pasa **no entra**: se ofrece moverlo a documentación
   (que puede vivir donde el equipo quiera y no se versiona como
   norma). Meta de extensión: **≤200 líneas** el artefacto humano. Si
   se pasa, hay documentación mezclada — separarla antes de cerrar.

6. **UBICACIÓN Y RAMA** — antes de escribir, decidir dónde aterriza:

   | Subtipo | Path | Rama |
   |---|---|---|
   | `DF-*` | `specs/<feature>/` | El worktree de la feature (§6) |
   | `DC-*`, `DS-*` | `.ai-dlc/design/` | El worktree de la feature que los necesitó, si nacen de una; si no —diseño trabajando por delante del slice actual— rama propia `contract/<id>` con su PR |
   | `POL-*`, `SLO-*`, `DAT-*` y demás tipos no-diseño | **Nace en el repo que lo necesita primero** — `contracts/<tipo>/`, y en el hub es ahí también (§16). **Sube a `.org/contracts/<tipo>/` cuando aparece el segundo consumidor real**, conservando su `id`; el repo de origen pasa a referenciarlo por ID y **no se queda una copia**. Un `POL-*` del hub sube al citarlo la primera feature de migración: sin ese tránsito, el contrato vinculante vive en el único repo que no clona la gente que debe cumplirlo | Rama propia `contract/<id>` con su PR — no cuelgan de ninguna feature |

   Decirlo **explícitamente** al dev antes de escribir. Un `DS-*`
   escrito sin querer en la rama de una feature queda invisible para
   las demás hasta el merge, que es exactamente lo que un contrato
   compartido no debe hacer.

7. **RECONCILIAR CON LA SPEC** — **no aplica en el hub**:
   ahí no hay spec que reconciliar y no puede haberla (§16 *la línea que
   no se cruza*). La reconciliación ocurre después, cuando el contrato
   se cite desde la feature de migración, en el repo que la implementa.
   En cualquier otro `repo_type`, la entrevista casi siempre destapa
   comportamiento que ninguna `R*.*` cubre: es **para lo que el
   contrato existe**, no una excepción. Antes de escribir:
   - Listar toda afirmación de comportamiento del contrato —pasos,
     estados UX, criterios de accesibilidad— que no tenga `R*.*`.
   - Proponerlas como `R*.*` nuevas en `requirements.md`, con **OK
     explícito** del dev, y registrar el origen en `## Clarifications`.
   - Si la spec ya está `approved`: **parar** y proponer
     `/spec-amend` — ahí sí es amendment (§12).

   El contrato **no** guarda comportamiento que la spec no tenga: es
   §3.20 *propiedad del hecho*, y es lo que evita que un test busque en
   el sitio equivocado.

8. **ESCRIBIR** — generar el par de artefactos:
   - Humano: `<ID>.md` desde la plantilla, con frontmatter completo.
   - Máquina: `<ID>.json` (o `.yaml` según el tipo) con el esqueleto
     del final de la plantilla.
   - **Ubicación**: ya se decidió en el **paso 6**; aquí sólo se
     escribe. No se reenuncia la regla — que estuviera enunciada dos
     veces con dos criterios es lo que hacía que un `POL-*` de un repo
     de servicio tuviera dos destinos incompatibles. Lo único que este
     paso añade: **nunca publicar en `.org/` "por si acaso"** (§9). El
     segundo consumidor es real o no ha llegado.
   - **Estado inicial, según el origen del paso 2:**
     - **Greenfield** — `DRAFT` mientras se escribe y **`NEGOTIATING`**
       al cerrar: es lo que lo vuelve citable como `D-N` (§9) y lo que
       arranca la SLA de 10 días hábiles de §6. Un contrato que se
       queda en `DRAFT` no lo puede consumir nadie y no escala si se
       estanca.
     - **Brownfield o Terceros** — `derived: true` y **`LIVE`**
       directamente (§16). Su sujeto lleva años desplegado: no falta la
       implementación ni falta el acuerdo, falta la **revisión de la
       disciplina**. No lleva `MOCK`, no le corre la SLA y no pasa por
       el implementability check.
     Las dos son acciones **reversibles** (§3.16): no requieren OK — lo
     que sí lo requiere es `AGREED`, y ése no se toca aquí.

9. **CERRAR** — reportar (§7):
   - Qué se creó y dónde, y **en qué estado quedó**: `NEGOTIATING` si
     es contrato nuevo greenfield o una enmienda; `LIVE` con
     `derived: true` si es nuevo de brownfield o terceros (paso 8).
   - **Cerrar el `OPEN_QUESTION` de la `D-N`** que `/spec-new` haya
     dejado abierto. Son **dos escrituras, las dos obligatorias**:
     1. La `D-N` en `Dependencies` con el `id` y la `version` del
        contrato recién creado, su `Estado` (`NEGOTIATING`), su
        `Estrategia` y su `Ready to unmock`.
     2. La entrada de `## OPEN_QUESTIONS`, marcada
        `- [x] … — resuelto: <fecha> con <id>@<version>`. **Es la que
        el linter mira**: escribir sólo en `Dependencies` la deja
        abierta, y entonces `[E8]`, `CHK-015` y el check 3 de
        `--pre-g2` bloquean G2 con el pendiente ya resuelto.
   - Qué queda por decidir (lo que quedó como pregunta abierta).
   - Siguiente paso concreto: `/contract-verify <id>`. Para un
     contrato en `NEGOTIATING` corre el implementability check, que es
     lo que habilita pasar a `AGREED`; para uno `derived: true` corre
     la verificación de fidelidad y **no** lo mueve de `LIVE`.

   **Nunca** marcar `AGREED` desde este comando: es acción irreversible
   (§3.16) y requiere la confirmación del consumidor.

   **Quién tiene que estar.** El dueño de la disciplina responde la
   entrevista; el dev confirma lo que toca al repo (ubicación, rama,
   `R*.*` nuevas del paso 7). Si no están los dos, escribir lo que
   falte como pregunta abierta del contrato y decirlo en el cierre —
   **no** inventar la respuesta del ausente.

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
