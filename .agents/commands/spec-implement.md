---
name: spec-implement
description: Avanzar la siguiente task con pre-flight check
argument-hint: <slug>
model-class: codigo      # escribe y modifica codigo con las convenciones del repo
---

# `/spec-implement <feature-slug>` — Avanzar la siguiente task

> **Argumentos:** `$ARGUMENTS` — si el token aparece sin sustituir, los
> argumentos son el texto con el que se invocó el comando.

Sigue el protocolo §7 (AGENTS.md). Para feature `<feature-slug>`:

**Sin argumento**: si hay UNA sola feature activa (state ∈
{in-progress, partial-deploy-*} o aprobada sin arrancar), proponerla
explícitamente (*"la única activa es `<slug>`, ¿sigo con esa?"*). Si
hay varias, mostrar el panorama corto de `/spec-status` (sin slug) y
preguntar cuál — nunca elegir solo.

> **PARADA — el veredicto va primero.** Si en cualquier paso de abajo te
> paras a preguntar, escribe antes `result.json` con
> `status: needs_input`, la pregunta y su `owner`. Quien te lanzó no ve
> tu pantalla.

1. **CONTEXT** — leer `status.md`, `tasks.md`, `requirements.md`,
   `design.md`, y `dependencies`/`amendments` si existen.

2. **PRE-FLIGHT CHECK** — reportar al dev:
   - **Lint mecánico primero**: correr
     `scripts/spec-lint --feature <feature-slug>` (sh o ps1) si existe
     y partir de su salida. Con ERROR: **parar** y proponer corregir
     antes de avanzar. WARN/INFO: reportar y seguir.
   - **`stack/` completo**: si algún archivo aún tiene `TODO`, mirar
     **de qué cuelga cada uno** antes de parar. No es qué archivo es:
     es qué lo dejó sin llenar.

     | El `TODO` cuelga de… | |
     |---|---|
     | Nada declarado — lenguaje, framework, persistencia, testing o target sin decidir | **Parar** y proponer completar `stack/` (AGENTS.md § Bootstrap). Sin eso el código sale genérico y los tests no trazan a convenciones reales |
     | Una `D-N` que G2 aceptó con `MOCK` y `Ready to unmock` observable | **Seguir.** Bloquea producción, no implementación contra el doble — §12 *Los dos sentidos de `MOCK`*, la misma regla del paso 3 |

     Parar por un `TODO` que cuelga de una `D-N` en `NEGOTIATING` deja
     el gate **insatisfacible**: esas dependencias esperan a un tercero,
     así que el código no se escribiría nunca. Se midió el 2026-09-12
     con `D3`-`D8` esperando a un cliente: `/spec-implement` se paraba
     sobre una spec con **G2 firmado y `tasks.md` ya derivado**, y su
     propio `status.md` decía que esos `TODO` bloquean producción y no
     la firma. Preguntarlo es fricción sobre algo que el gate resolvió.
   - **Worktree correcto**: `cwd` es `<repo>--<feature-slug>/` y la
     rama activa es `feat/<feature-slug>` (§6 Worktree). Si no
     coinciden, **parar** y proponer moverse al worktree correcto.
   - **Árbol limpio**: si `git status` trae cambios sin commitear de
     antes —otra sesión, otra herramienta, una corrida cortada—, **no se
     construye encima**. Se commitean primero, tal cual, en **un** commit
     con el tipo de la convención (`feat` si hay código) y un mensaje
     que diga lo que es —`feat(<scope>): trabajo previo sin verificar,
     de otra sesión`—, **sin refs `[R*.*]` ni `T<n>`**: nadie ha
     comprobado todavía que cubra algo, y una ref es una afirmación. Se
     empuja (paso 5), y queda como commit sin reflejo en `status.md`:
     integrarlo a sus tasks —verificarlo contra ellas— es el trabajo que
     sigue, y **es una decisión**, así que se reporta. Se midió qué pasa
     si no: 13 tasks `in-progress` y cero commits, todo en el disco de
     una máquina.
   - Spec aprobada (`status.md` lo confirma; si no, **parar**).
   - Última task `done` y commit hash.
   - **Si `tasks.md` está vacío** (spec recién firmada): **derivarlo
     aquí**, antes de seguir. Del `design.md` firmado + los slices
     P1/P2/P3 de `requirements.md`: cada task cita los `R*.*` que
     cubre, se agrupa por fase de slice, y P1 debe quedar desplegable
     solo con su prueba independiente. **Proponer la descomposición
     completa y pedir OK** antes de escribirla — es la Fase 3 (§4) y la
     aprueba un humano. Después continuar el pre-flight normal.
   - Cuál es la siguiente task `pending` (no `blocked`).
   - ¿Hay tasks `blocked` que el dev quizá quiera revisar antes
     (`blocked_by`: dependencia, decisión humana, etc.)?
   - ¿Tests del último deploy verdes? Si no, **parar** y reportar.
   - ¿Commits desde el último update de `status.md` **que no citan una
     task de esta spec en curso o terminada** (`T<n>` en `in-progress` o
     `done`)? Si sí, preguntar si integrarlos al lifecycle (§7 reglas
     operacionales). Los que citan una así son los commits parciales del
     propio paso 5 y ya están integrados: su task los lleva. Uno que cita
     una task `pending` no lo es —alguien trabajó por fuera siguiendo la
     convención— y se pregunta igual. Preguntar por ellos cada vez que se
     retoma una task a medias sería una pregunta que no es una decisión.
   - ¿`state` declarado coincide con la derivación del Lifecycle (§6)?
     Si no, decirlo.

3. **CLARIFY** — si la siguiente task tiene ambigüedad, depende de una
   `D-N` **sin estrategia declarada**, o requiere decisión humana
   (naming, migration risk, breaking change), **preguntar antes de
   tocar código** (§3.12).

   **No** es motivo de consulta una `D-N` en `NEGOTIATING` **con**
   estrategia `MOCK` y `Ready to unmock` observable: es el camino
   normal del paralelismo por slice (§12 *Los dos sentidos de `MOCK`*)
   y G2 ya lo aceptó — vía `CHK-D1` **si la feature declara una `D-N` de
   diseño**, que es una sección condicional de la checklist; en un repo
   sin esa disciplina la regla vale igual y ese ítem no existe. Citarlo
   como si siempre estuviera es fuga de alcance: lo destapó E0 en
   v0.85. Se implementa contra el mock y se
   reporta en el CLOSE; `/spec-status` lo cuenta como progreso real,
   no como feature a medias. Preguntarlo task por task es fricción
   sobre algo que el gate acaba de resolver.

4. **PROPOSE** — explicar archivos a crear/modificar (respetando
   `stack/architecture.md` y `stack/patterns.md`), tests a escribir
   (con `// Derived from R*.*` según `stack/testing.md`), nivel de
   riesgo. **Pedir OK explícito si la task es M/L o toca código
   compartido**.

   **Si la task implica instalar dependencias nuevas** (modificar
   `package.json`, `pyproject.toml`, `*.csproj`, etc.), antes de
   ejecutar `npm install` / `pip install` / etc.:
   - Listar cada dep nueva: nombre, versión, propósito (qué `R*.*`
     cubre).
   - Reportar licencia y resultado de `npm audit` / `pip-audit` /
     equivalente.
   - Cruzar con `stack/constraints.md` (¿prohibida?) y
     `stack/security.md` (¿compatible con políticas?).
   - **Pedir OK explícito** del dev. NO instalar sin OK — una dep
     puede estar prohibida por licencia (AGPL/SSPL), vuln conocida
     sin parche, o policy empresarial. Ver AGENTS.md *Dependencias
     nuevas*.

5. **EXECUTE**: tests primero, código que pase tests (respetando
   `stack/constraints.md`), linter, typecheck, iterar hasta verde.

   **Y en cuanto está en verde, COMMIT y PUSH**, sin pedir OK:
   - **Commit** de la task, o de la parte de ella que ya se sostiene
     sola —sus tests pasan—, con la convención de commits de
     `AGENTS.md`: citando su `T<n>` y sus `R*.*`, que es además lo que
     el pre-flight usa para reconocerlo como propio. Una task que sigue `in-progress` también commitea lo
     que tiene en verde: esperar a `done` para commitear es lo que
     dejó una feature entera sin un solo commit.
   - **Push de la rama de trabajo** (`git push -u origin HEAD`), tras
     comprobar que no es compartida: no está en `environments[]` de
     `repo-config.yaml` y no es el default branch (§3.16). Si lo es,
     **no se empuja** y se para: es un error de worktree. Nunca
     `--force`.
   - **Si el push se rechaza por *no fast-forward***, alguien más
     escribió en la rama —el commit `sign` de un gate, un compañero—:
     **se para y se pregunta** cómo integrarlo. No se fuerza ni se
     reescribe nada por cuenta propia.
   - **Si falla por otra causa** —sin remoto, sin credencial, una
     política del repo—, se sigue: el commit local ya existe. Pero se
     dice en el CLOSE, con el motivo, porque ese trabajo todavía vive
     sólo en esta máquina.

6. **UPDATE STATUS**:
   - `status.md`: task → `done` o `deployed:<env>` con commit hash y
     fecha (§6 Lifecycle). Actualizar `state` si cambia.
   - **Sincronizar el tracker (v0.25, no opcional)**: si
     `status.md > work_items` declara tracker `owner`, **siempre**
     proponer reflejar el nuevo estado de la task en el work item de
     ADO mapeado — mapeo `pending`→`New`, `in-progress`→`Active`,
     `done`→`Resolved`/`Closed`, `deployed:<env>`→`Closed` + comentario
     de ambiente (§6 Lifecycle del methodology). Fricción según
     `creation_mode` del tracker: `auto` ejecuta vía MCP con 1 OK;
     `assisted` entrega el comando `az boards work-item update`
     listo; `discover-first`/`manual` deja el recordatorio explícito
     en CLOSE. El agente lo ofrece en cada transición, aunque la
     respuesta del dev sea "más tarde". Si no hay tracker, se omite
     sin repetir el disclaimer.

7. **CLOSE** — reportar qué se hizo (task ID, R*.* cubiertos, commit
   hash, y si la rama quedó empujada o por qué no), si el tracker quedó
   sincronizado o pendiente, qué quedó
   pendiente, siguiente paso sugerido.

   **Y seguir con la siguiente task de la MISMA fase**, sin preguntar,
   mientras se cumplan las cuatro:

   | Sigue si… | |
   |---|---|
   | Todo lo que toca está en la lista **reversible** de §3.16 | editar archivos, mover el estado de una task en `status.md`, commits y push sin `--force` de la **rama de trabajo** de la feature |
   | La siguiente task es `pending`, no `blocked` | una `blocked` para y se reporta con su `blocked_by` |
   | Los gates de la task que cierras quedaron verdes | tests, linter, typecheck |
   | No aparece nada del paso 3 — ambigüedad, `D-N` sin estrategia, decisión humana | si aparece, para y pregunta ahí |

   **Para al terminar la fase**, y también ante lo primero de la lista
   **irreversible** de §3.16 —push a rama compartida (la de trabajo de
   la feature no lo es), PR, `AGREED`,
   deploy—, que es donde el OK explícito sí lo manda el método.

   **Por qué cambió (v0.86).** Esta línea decía *"preguntar antes de
   continuar — NO auto-avanzar (§3.16)"* y **§3.16 dice lo contrario**:
   su lista de acciones reversibles nombraba *"mover tasks de estado
   dentro de `status.md`"* y *"hacer commits locales (sin push)"* como
   cosas que el agente hace **sin OK explícito** (desde v0.170 también
   el push de la rama de trabajo: ver el paso 5). Citaba como fundamento
   la sección que la desmentía — un F2 en el sentido estricto del banco.
   El coste estaba medido: la feature del laboratorio tiene **49 tasks**,
   así que la regla imponía **49 intervenciones humanas por feature**,
   por diseño y sin que ninguna fuera una decisión.

   **Y por qué el tope es la fase y no "hasta acabar".** No es
   prudencia: es que la calidad de un agente cae cuando su contexto
   crece, y una fase es un corte que ya existe en `tasks.md` y agrupa
   trabajo que comparte convenciones. El tope protege el resultado, no
   pide permiso. *(La evidencia de degradación por contexto largo la
   trajo el replanteo y **no está verificada por nosotros**: si se
   verifica y el corte correcto es otro, se mueve el tope — lo que no
   vuelve es pedir un OK para algo que §3.16 declara reversible.)*

   **Esto NO cambia el ciclo del hub.** `agent-tick` sigue lanzando
   **una acción por pasada**: es el lazo de reconciliación, donde cada
   acción cambia el estado desde el que se deriva la siguiente. Son dos
   reglas distintas y unificarlas rompería la derivación.

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
