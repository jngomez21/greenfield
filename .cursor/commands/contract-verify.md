---
name: contract-verify
description: Auditar un contrato de disciplina — implementability check si es nuevo, verificación de fidelidad si es derivado
argument-hint: <id>
model-class: mecanico    # comprueba criterios ya escritos
---

# `/contract-verify <id>` — Auditoría e implementability check

> **Argumentos:** `$ARGUMENTS` — si el token aparece sin sustituir, los
> argumentos son el texto con el que se invocó el comando.

Sigue el protocolo §7 (AGENTS.md). **Read-only sobre el código**: audita
un contrato de disciplina y produce un veredicto. Es el paso que
convierte *"esto es lo que quiero"* en *"esto es construible y lo
acordamos"* — sin él, un contrato de otra disciplina llega a G2 como
imposición unilateral y el retrabajo aparece en implementación.

Ver §6 *Dependencias de otras disciplinas* y §9 del methodology.

> **PARADA — el veredicto va primero.** Si en cualquier paso de abajo te
> paras a preguntar, escribe antes `result.json` con
> `status: needs_input`, la pregunta y su `owner`. Quien te lanzó no ve
> tu pantalla.

1. **CONTEXT** — resolver `<id>` buscando de lo específico a lo general
   (§9): `specs/<feature>/` → `.ai-dlc/design/` → `.org/contracts/`.
   Si hay más de un match, reportar **todos** y parar: dos contratos
   con el mismo `id` en niveles distintos es un problema en sí mismo.
   Cargar el par humano + máquina y el tipo desde el registro.

2. **CONSISTENCIA INTERNA** — severidad `CRITICAL` bloquea el paso a
   `AGREED`:

   | Check | Severidad |
   |---|---|
   | Frontmatter completo: `id`, `version`, `estado`, `owner`, `consumers` | CRITICAL |
   | `version` es SemVer válido | CRITICAL |
   | Sección de criterios de aceptación presente y no vacía | CRITICAL |
   | Cada criterio declara **cómo se verifica** y su nivel (automático/manual) | CRITICAL |
   | Todo elemento normativo tiene identificador propio y **único** (anatomía, variantes, estados, accesibilidad) | CRITICAL |
   | Los estados cubren vacío, carga, error, sin permisos y sin resultados — o se justifica por qué no aplican | WARNING |
   | Cada variante declara **cuándo NO usarla** | WARNING |
   | El artefacto máquina existe y es parseable | CRITICAL |
   | Humano y máquina coinciden en `id`, `version`, `estado` y en los IDs de los elementos | CRITICAL |
   | Contratos citados en dependencias existen y no están en `deprecated/` pasado su `sunset_date` | CRITICAL |
   | Extensión del artefacto humano ≤200 líneas | WARNING |

3. **PRUEBA ÁCIDA, LÍNEA POR LÍNEA** — recorrer el cuerpo normativo y
   marcar toda afirmación que **no** declare cómo se comprueba:

   > **Si no se puede escribir cómo se comprueba, no es contrato.**

   Reportarlas agrupadas, con la propuesta concreta para cada una:
   (a) reescribirla como criterio verificable, o (b) sacarla a
   documentación. Los adjetivos sin métrica —"moderno", "limpio",
   "intuitivo", "consistente"— son el caso típico.

4. **MODO SEGÚN EL ORIGEN.** Un contrato `derived: true` **no pasa por
   el implementability check**: ya está implementado — lo está desde
   antes de que existiera el contrato. Lo que hay que verificar es otra
   cosa:

   | `derived` | Qué se verifica | Veredictos |
   |---|---|---|
   | `false` | Que sea **construible**: el paso 5 de abajo | APTO · APTO CON SALVEDADES · NO APTO |
   | `true` | Que **describa la realidad**: cada afirmación se contrasta contra el código o contra producción, y se anota su fuente. No se juzga si es buena, se juzga si es cierta | FIEL · FIEL CON HUECOS *(lo que no se pudo verificar, listado)* · NO FIEL |

   Un contrato `derived: true` **nunca** llega a `AGREED` por esta vía:
   se queda `LIVE` con su marca, y el camino a acordado es la **v2** que
   propone la disciplina (§16). Reportarlo así en vez de decir que "no
   es APTO", que no es ninguno de sus veredictos.

5. **IMPLEMENTABILITY CHECK** *(sólo si `derived: false`)* — el corazón
   del comando para un contrato nuevo. Cruzar el
   contrato contra `stack/` (`tech-stack.md`, `constraints.md`,
   `patterns.md`) y contra lo que ya existe en el repo. Responder por
   escrito las cuatro preguntas:

   1. **¿Es construible** con el stack declarado? Si algo exige una
      capacidad que el stack no tiene, nombrarla explícitamente.
   2. **¿El costo es proporcional** al valor? Si no, proponer negociar
      alcance en vez de rechazar.
   3. **¿Hay algo existente que ya lo cubre?** Buscar componentes,
      utilidades o contratos que hagan esto redundante.
   4. **¿Los criterios son verificables** tal como están escritos, con
      las herramientas que el repo tiene hoy? Un criterio que exige
      una herramienta inexistente no es verificable todavía.

6. **VEREDICTO** — uno de tres, sin ambigüedad. *(Para `derived: true`
   son los tres del paso 4: FIEL / FIEL CON HUECOS / NO FIEL.)*

   | Veredicto | Cuándo | Qué se escribe |
   |---|---|---|
   | **APTO** | Sin CRITICALs y las 4 preguntas resueltas | Llenar `implementability` (quién, fecha, salvedades) y **proponer** el paso a `AGREED` |
   | **APTO CON SALVEDADES** | Construible pero con partes diferidas o condicionadas | Igual que arriba, con cada salvedad registrada y su slice destino (p. ej. "virtualización difiere a P3") |
   | **NO APTO** | Hay CRITICALs o una pregunta se responde que no | Volver a `NEGOTIATING` con la **objeción concreta**. Nunca un "no" genérico |

7. **CERRAR** — reportar (§7): veredicto, hallazgos por severidad,
   salvedades registradas y siguiente paso.

   **Restricciones**:
   - Mover el contrato a `AGREED` es **irreversible** (§3.16): se
     propone, se pide OK explícito, y sólo entonces se escribe.
     Compromete a las dos partes.
   - Este comando **no edita el cuerpo del contrato**. Propone
     correcciones; quien las aplica es el dueño de la disciplina, vía
     `/contract-new` o a mano.
   - Un contrato `derived: true` se queda en `LIVE` con su marca: no
     pasa a `AGREED` por esta vía (paso 4). Documenta lo que hay, no
     lo que se acordó, así que **no es norma para elementos nuevos**.
     El camino a acordado es la v2 que propone la disciplina (§16).

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
