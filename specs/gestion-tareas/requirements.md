---
feature: gestion-tareas
modality: code                  # code | config-only | data-migration | catalog-only | docs-only | refactor-only (§6)
initiative: NONE                # opcional — slug/URL sólo si pertenece a una Initiative
owner: "@jngomez21"
status: draft                   # draft | in-review | approved | in-implementation | done
                                # Quién produce cada transición:
                                #   draft            /spec-new
                                #   in-review        el owner, al pedir revisión de la spec
                                #   approved         firma de G2 (commit `sign`)
                                #   in-implementation  /spec-implement, en su primera task
                                #   done             firma de G5 (§6 Lifecycle)
---
<!--
  PLANTILLA AI-DLC — requirements.md (canonical: .agents/templates/spec/)
  El Service Agent la copia a specs/<feature>/requirements.md durante
  /spec-new y la llena con la entrevista. Las notas en comentarios HTML
  son guardrails para el agente: se CONSERVAN en la spec generada (no
  renderizan y guían amendments futuros). El frontmatter YAML va
  SIEMPRE primero en el archivo (los parsers lo exigen).

  GUARDRAILS (obligatorios al llenar):
  - ✅ QUÉ necesita el usuario y POR QUÉ. ❌ CÓMO se implementa
    (nada de stack, librerías, endpoints internos, estructura de
    código — eso va en design.md).
  - Una acción por requirement. Si tiene "y", dividirlo.
  - NFRs medibles: "rápido" ❌ → "p99 < 500ms" ✅.
  - Casos negativos explícitos (qué hacer ante error/abuso/límite).
  - Cada R*.* debe ser TESTEABLE y NO AMBIGUO: si no puedes escribir
    un test que lo verifique, o admite dos interpretaciones razonables,
    reescribirlo o marcarlo.
  - Ambigüedad: marcar inline con [NEEDS CLARIFICATION: <pregunta
    concreta + opciones>]. MÁXIMO 3 en toda la spec — si necesitas
    más, la captura de intención fue insuficiente: volver a conversar
    con el dev antes de seguir. /spec-clarify los resuelve.
  - NO inventar: lo que no se sabe se marca, no se asume (§3.12).
-->

# Feature: Gestión de tareas personales

## Contexto

Las personas necesitan registrar sus tareas personales y darles seguimiento:
qué tienen que hacer, en qué punto está cada cosa y para cuándo. Este servicio
permite a cada usuario autenticado crear, consultar, actualizar y eliminar sus
propias tareas, asignarles un estado y una fecha límite y, sobre todo, consultar
qué tiene pendiente, empezando por lo más urgente.

**Usuario primario**: una persona autenticada que gestiona **sólo sus propias**
tareas. No hay tareas compartidas ni asignadas a terceros.

**Glosario** (términos usados de forma consistente en toda la spec):

- **Tarea**: unidad de trabajo con título, descripción opcional, estado y fecha
  límite opcional.
- **Dueño**: el usuario autenticado que creó la tarea. Es el único que puede
  verla o modificarla.
- **Estado**: uno de `pendiente`, `en_progreso` o `completada`.
- **Tarea pendiente**: una tarea cuyo estado es `pendiente` o `en_progreso`, es
  decir, no `completada`.
- **Fecha límite**: una fecha de calendario (día, sin hora), opcional.
- **Tarea vencida**: una tarea pendiente cuya fecha límite es anterior al día
  actual.

## Stakeholders

- @jngomez21 — dev y tech lead del repo (firma G2)

## Métricas de éxito

- Un usuario puede ejecutar el ciclo completo (crear → consultar → actualizar
  estado → ver en pendientes → eliminar) usando sólo la API documentada, sin
  intervención manual en la base de datos.
- 0 respuestas que incluyan tareas de un usuario distinto del que hace la
  petición (verificado por la suite de integración y en `pruebas`).
- Tasa de respuestas de error de servidor < 0,5 % de las peticiones en `pruebas`
  durante la semana posterior al despliegue.

## Slices priorizados

### P1 — CRUD de tareas propias con estado y fecha límite (MVP)
- **Por qué esta prioridad**: sin crear, ver, modificar y borrar tareas no hay
  producto. Por sí solo ya permite llevar una lista personal de tareas con
  estado y fecha límite, filtrable por estado.
- **Prueba independiente**: con dos usuarios A y B, A crea una tarea con fecha
  límite, la consulta, cambia su estado a `en_progreso`, la ve en su listado
  filtrado por estado y la elimina; B no puede verla ni modificarla en ningún
  momento.
- **Cubre**: R1.*, R2.*, R3.*, R4.*, R5.*

### P2 — Consulta de tareas pendientes
- **Por qué esta prioridad**: es la consulta principal del día a día ("¿qué me
  falta y qué es lo más urgente?"). Es aditiva: se apoya en las tareas que ya
  crea P1 y no cambia ningún comportamiento de P1.
- **Prueba independiente**: con tareas precargadas en los tres estados, con y
  sin fecha límite, algunas vencidas, la consulta de pendientes devuelve sólo
  las no completadas, en el orden de R6.2, con la marca de vencida correcta, y
  el filtro de sólo vencidas devuelve el subconjunto esperado.
- **Cubre**: R6.*

## Requisitos funcionales

<!-- EARS (§5): WHEN / WHILE / WHERE / IF-THEN / THE SYSTEM SHALL.
     Numeración estable R<grupo>.<n> — nunca renumerar; las R*.* se
     citan en commits, tests y PRs. Cada R*.* declara `Tests:` con
     niveles: unit | integration | e2e | contract | load |
     accessibility | security | none (este último con justificación). -->

### R1 — Autenticación y propiedad [P1]

**R1.1** IF una petición no trae una credencial válida (ausente, mal formada,
         expirada o emitida para otro servicio), THEN THE SYSTEM SHALL
         rechazarla como no autenticada sin devolver ni modificar ninguna tarea.
         Tests: integration

**R1.2** WHEN un usuario autenticado crea una tarea, THE SYSTEM SHALL registrar
         a ese usuario como su dueño.
         Tests: integration

**R1.3** IF un usuario consulta, actualiza o elimina una tarea de la que no es
         dueño, THEN THE SYSTEM SHALL responder exactamente igual que si la
         tarea no existiera, sin modificarla.
         Tests: integration

**R1.4** THE SYSTEM SHALL incluir en cualquier listado únicamente tareas cuyo
         dueño es el usuario que hace la petición.
         Tests: integration

### R2 — Crear tareas [P1]

**R2.1** WHEN un usuario envía una tarea con título válido, THE SYSTEM SHALL
         crearla y devolverla completa, incluido su identificador único,
         su fecha de creación y su fecha de última actualización.
         Tests: integration

**R2.2** WHEN una tarea se crea sin estado, THE SYSTEM SHALL asignarle el
         estado `pendiente`.
         Tests: unit, integration

**R2.3** WHERE la petición de creación incluye descripción, estado o fecha
         límite válidos, THE SYSTEM SHALL guardarlos en la tarea creada.
         Tests: integration

**R2.4** IF el título falta, está vacío, contiene sólo espacios o supera 200
         caracteres, THEN THE SYSTEM SHALL rechazar la petición con un error
         de validación que identifique el campo `título`.
         Tests: unit, integration

**R2.5** IF la descripción supera 2000 caracteres, THEN THE SYSTEM SHALL
         rechazar la petición con un error de validación que identifique el
         campo `descripción`.
         Tests: unit, integration

**R2.6** IF el estado no es `pendiente`, `en_progreso` ni `completada`, THEN THE
         SYSTEM SHALL rechazar la petición con un error de validación que
         identifique el campo `estado`.
         Tests: unit, integration

**R2.7** IF la fecha límite no es una fecha de calendario válida en formato
         `AAAA-MM-DD`, THEN THE SYSTEM SHALL rechazar la petición con un error
         de validación que identifique el campo `fecha límite`.
         Tests: unit, integration

**R2.8** WHEN la fecha límite indicada es anterior al día actual, THE SYSTEM
         SHALL aceptarla (se permite registrar tareas ya atrasadas).
         Tests: integration

### R3 — Consultar tareas [P1]

**R3.1** WHEN un usuario solicita una tarea propia por su identificador, THE
         SYSTEM SHALL devolver su identificador, título, descripción, estado,
         fecha límite, fecha de creación y fecha de última actualización.
         Tests: integration

**R3.2** IF el identificador solicitado no corresponde a ninguna tarea o no
         tiene un formato válido, THEN THE SYSTEM SHALL responder que la tarea
         no existe.
         Tests: integration

**R3.3** WHEN un usuario solicita el listado de sus tareas, THE SYSTEM SHALL
         devolverlas paginadas según R3.7, por fecha de creación descendente
         (más recientes primero) y, en caso de empate, por identificador.
         Tests: integration

**R3.4** WHERE el usuario indica un estado como filtro del listado, THE SYSTEM
         SHALL devolver sólo sus tareas con ese estado.
         Tests: integration

**R3.5** IF el filtro de estado no es un estado válido, THEN THE SYSTEM SHALL
         rechazar la petición con un error de validación.
         Tests: integration

**R3.6** WHEN el usuario no tiene tareas que cumplan la consulta, THE SYSTEM
         SHALL devolver un listado vacío, no un error.
         Tests: integration

**R3.7** THE SYSTEM SHALL paginar los listados por posición, con 50 tareas por
         página por defecto o el tamaño elegido por el usuario entre 1 y 100,
         e incluir en cada respuesta el total de tareas que cumplen la consulta.
         Tests: integration

**R3.8** IF el tamaño de página está fuera del rango 1–100 o la posición
         inicial es negativa, THEN THE SYSTEM SHALL rechazar la petición con
         un error de validación que identifique el parámetro.
         Tests: integration

### R4 — Actualizar tareas [P1]

**R4.1** WHEN un usuario envía cambios a una tarea propia, THE SYSTEM SHALL
         modificar sólo los campos incluidos en la petición y dejar los demás
         intactos.
         Tests: integration

**R4.2** WHEN una tarea se modifica, THE SYSTEM SHALL actualizar su fecha de
         última actualización y devolver la tarea resultante.
         Tests: integration

**R4.3** THE SYSTEM SHALL permitir cambiar el estado de una tarea de cualquier
         estado a cualquier otro, incluido reabrir una tarea `completada`.
         Tests: unit, integration

**R4.4** WHERE la petición envía la descripción o la fecha límite explícitamente
         vacías (nulas), THE SYSTEM SHALL quitar ese valor de la tarea.
         Tests: integration

**R4.5** IF los cambios enviados incumplen alguna validación de R2.4–R2.7 o
         intentan dejar el título vacío, THEN THE SYSTEM SHALL rechazar la
         petición completa sin modificar ningún campo de la tarea.
         Tests: integration

**R4.6** IF el identificador de la tarea a actualizar no corresponde a ninguna
         tarea o no tiene un formato válido, THEN THE SYSTEM SHALL responder
         que la tarea no existe.
         Tests: integration

**R4.7** WHEN llegan dos actualizaciones concurrentes de la misma tarea, THE
         SYSTEM SHALL aplicarlas en el orden en que se procesan, prevaleciendo
         la última, sin control de versión ni error de conflicto.
         Tests: integration

### R5 — Eliminar tareas [P1]

**R5.1** WHEN un usuario elimina una tarea propia, THE SYSTEM SHALL borrarla de
         forma permanente.
         Tests: integration

**R5.2** IF el identificador de la tarea a eliminar no corresponde a ninguna
         tarea (nunca existió o ya fue eliminada) o no tiene un formato
         válido, THEN THE SYSTEM SHALL responder que la tarea no existe.
         Tests: integration

### R6 — Consultar tareas pendientes [P2]

**R6.1** WHEN un usuario consulta sus tareas pendientes, THE SYSTEM SHALL
         devolver sus tareas en estado `pendiente` o `en_progreso`.
         Tests: integration

**R6.2** THE SYSTEM SHALL ordenar las tareas pendientes por fecha límite
         ascendente con las que no tienen fecha al final, luego por fecha de
         creación ascendente y, si persiste el empate, por identificador.
         Tests: unit, integration

**R6.3** THE SYSTEM SHALL indicar en cada tarea pendiente si está vencida, es
         decir, si su fecha límite es anterior al día actual en UTC.
         Tests: unit, integration

**R6.4** WHERE el usuario pide sólo las tareas vencidas, THE SYSTEM SHALL
         devolver únicamente las tareas pendientes vencidas.
         Tests: integration

**R6.5** WHEN el usuario no tiene tareas pendientes, THE SYSTEM SHALL devolver un
         listado vacío, no un error.
         Tests: integration

**R6.6** THE SYSTEM SHALL paginar la consulta de tareas pendientes con las mismas
         reglas de R3.7 y R3.8.
         Tests: integration

## Requisitos no funcionales

**NFR1** THE SYSTEM SHALL responder cada operación individual (crear, consultar
         una, actualizar, eliminar) con latencia p95 < 300 ms y cada consulta
         de listado o de pendientes con p95 < 500 ms, medido en `pruebas` con
         10 usuarios concurrentes y 1.000 tareas por usuario.
         Tests: load

**NFR2** THE SYSTEM SHALL no registrar en logs el título ni la descripción de
         las tareas ni las credenciales de acceso.
         Tests: integration

## Dependencies

<!-- Omitir si no hay dependencias externas. Formato D-N (§6):
     todo lo que la feature necesita y aún no existe. -->

### D1 — Proveedor de identidad OIDC
- **Tipo**: externa
- **Estado**: NEGOTIATING
- **Contrato**: OpenID Connect Core 1.0 (tokens JWT firmados) + JSON Web Key Set, RFC 7517 — id `oidc-core`, version `1.0`
- **Owner**: @jngomez21 (elige y configura el proveedor)
- **Tracking**: —
- **ETA**: antes de la primera promoción a `pruebas`
- **Estrategia**: MOCK
  <!-- NONE = la dependencia ya está LIVE al declararse (contrato
       `derived: true` de brownfield). Sin mock y sin Ready to unmock. -->
- **Mock**: par de llaves y emisor de tokens generados por las pruebas; sin archivo en `mocks/`
- **Ready to unmock**: existe un IdP accesible desde `pruebas` con issuer, audience y URL de JWKS publicados, y un token real emitido por él es aceptado por el servicio.

## Fuera de scope

- Interfaz de usuario (web o móvil): sólo API.
- Registro, login, recuperación de contraseña y gestión de usuarios: son del IdP (D1).
- Compartir tareas, asignarlas a otros usuarios o ver tareas ajenas (incluido un rol administrador).
- Subtareas, etiquetas, prioridades, proyectos o listas.
- Recordatorios y notificaciones por vencimiento.
- Tareas recurrentes.
- Búsqueda por texto libre.
- Papelera, borrado lógico o restauración de tareas eliminadas.
- Historial de cambios de una tarea.
- Fecha límite con hora (sólo fecha de calendario).
- Operaciones masivas (crear, actualizar o borrar varias tareas en una petición).

## Dependencias internas

- Ninguna: es la primera feature del repo.

## Clarifications

### Session 2026-09-25
- Q: ¿Qué estados puede tener una tarea? → A: `pendiente`, `en_progreso`, `completada`; transición libre entre cualquiera de ellos, incluido reabrir.
- Q: ¿Qué devuelve "consultar mis tareas pendientes"? → A: las no completadas, ordenadas por fecha límite ascendente, sin fecha al final, con filtro opcional de sólo vencidas.
- Q: ¿Cómo es la fecha límite? → A: opcional, sólo fecha (AAAA-MM-DD); vencida si es anterior a hoy.
- Q: ¿Cómo se identifica al dueño? → A: por el usuario autenticado del token de un IdP externo (ver D1); el servicio no gestiona usuarios.
- Q (/spec-clarify): ¿En qué zona horaria se calcula el "día actual" que define una tarea vencida? → A: UTC, igual para todos los usuarios (R6.3).
- Q (/spec-clarify): ¿Los listados se paginan? → A: sí, por posición; 50 por defecto, máximo 100, con total de resultados; aplica al listado general y a pendientes (R3.3, R3.7, R3.8, R6.6).
- Q (/spec-clarify): ¿Qué pasa ante actualizaciones concurrentes de la misma tarea? → A: gana la última escritura, sin control de versión (R4.7).
- Q (/spec-clarify): ¿Se confirman los supuestos por defecto? → A: sí: título ≤ 200 y descripción ≤ 2000 caracteres (R2.4, R2.5); fecha límite pasada permitida al crear (R2.8); eliminación permanente (R5.1); acceso a tarea ajena indistinguible de inexistente (R1.3); umbrales de NFR1.
- Nota (/spec-clarify): para que los listados tengan un orden determinista (CHK-023), los empates se resuelven por identificador (R3.3, R6.2). Se permiten varias tareas con el mismo título: la spec no exige unicidad.
- Nota (/spec-verify --pre-g2, aceptada por el dev): V2 — `Tests: security` pasa a `integration` en R1.1, R1.3 y R1.4 (son casos adversos de integración; `stack/testing.md` no define un nivel `security`). V3 — R4.6 y R5.2 cubren también identificadores inexistentes o con formato inválido, igual que R3.2.

## OPEN_QUESTIONS

<!-- Preguntas que NO se pudieron resolver en la sesión. Toda entrada
     abierta BLOQUEA el gate G2 (status no puede pasar a approved), y
     también PARA `/spec-design`.

     Por eso, antes de dejar una aquí: ¿es una pregunta o es una `D-N`?
     Si ya sabes QUÉ construir y lo que falta es CON QUÉ, va a
     `Dependencies` con su estrategia, no aquí — y si está en las dos
     listas, ciérrala aquí citando su `D-N`. Ver §6 *Una `D-N` y una
     `OPEN_QUESTION` no son lo mismo*.
     owner y due son obligatorios — spec-lint lo verifica.

     Formato, UNA sola línea por pregunta:

         - [ ] <pregunta> — owner: @<persona>, due: <YYYY-MM-DD>

     El ejemplo vive dentro de este comentario a propósito. Fuera de él
     sería una pregunta abierta de verdad: `spec-lint` la contaría y
     [E8] bloquearía la spec al llegar a `approved`, sin que nadie la
     haya escrito. Una spec recién creada tiene CERO preguntas
     abiertas, y esta sección arranca vacía. -->
