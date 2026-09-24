<!--
  PLANTILLA AI-DLC — checklist de requirements (canonical:
  .agents/templates/spec/). /spec-new la copia a
  specs/<feature>/checklists/requirements.md y la ADAPTA: conserva
  los items base y agrega items específicos de la feature.

  CONCEPTO — "unit tests del requirements": esta checklist valida la
  CALIDAD DE LA REDACCIÓN de la spec, NO la implementación.

  ✅ BIEN (interroga la spec):
    "¿Está cuantificado 'rápido' con un umbral medible?"
    "¿Se define qué pasa cuando el archivo supera el límite?"
  ❌ MAL (testea la implementación — va en tests, no aquí):
    "Verificar que el endpoint retorna 200"
    "Probar que el botón funciona"

  REGLAS:
  - Numeración global CHK-NNN incremental; al agregar items nuevos,
    continuar la numeración (nunca renumerar).
  - ÍTEM NO APLICABLE: se marca `- [~]` con la razón al final —
    `- [~] CHK-NNN <texto> — N/A: <razón>`. NO dejarlo en `- [ ]`
    (spec-lint lo cuenta como pendiente y erra en G2) ni marcarlo
    `- [x]` (queda indistinguible de uno cumplido y la checklist
    miente). Los dos linters aceptan `[~]`: sólo reaccionan a `[ ]`.
  - ≥80% de los items con referencia de trazabilidad: [R<x>.<y>]
    para items sobre un requirement concreto, [Gap] para algo que la
    spec NO cubre y debería, [Conflicto] para inconsistencias.
  - Máximo ~25 items: si hay más, priorizar por riesgo.
  - GATE G2: el tech lead firma G2 sólo con TODOS los items `[x]`
    o `[~]` con razón. spec-lint lo verifica cuando requirements.md
    pasa a status: approved: cualquier `- [ ]` restante es `[E9]`.
-->
# Checklist de requirements: <feature>

**Propósito**: validar que `requirements.md` está listo para firmar G2.
**Creada**: <YYYY-MM-DD> · **Spec**: [requirements.md](../requirements.md)

## Completitud

- [ ] CHK-001 ¿Cada slice (P1/P2/P3) declara su prueba independiente? [Estructura]
- [ ] CHK-002 ¿Todos los flujos de error/excepción tienen un R*.* (IF/THEN)? [Gap]
- [ ] CHK-003 ¿Los casos límite (vacío, máximo, concurrencia, duplicados) están contemplados? [Gap]
- [ ] CHK-004 ¿"Fuera de scope" lista lo que un lector podría asumir incluido? [Estructura]

## Claridad

- [ ] CHK-005 ¿Cero adjetivos sin métrica ("rápido", "intuitivo", "robusto", "escalable")? [Claridad]
- [ ] CHK-006 ¿Cero marcadores [NEEDS CLARIFICATION] pendientes? [Claridad]
- [ ] CHK-007 ¿Cada R*.* admite UNA sola interpretación razonable? [Claridad]
- [ ] CHK-008 ¿Los términos de dominio se usan consistentemente (sin sinónimos intercambiados)? [Claridad]

## Testeabilidad

- [ ] CHK-009 ¿Cada R*.* tiene `Tests:` declarado con niveles concretos (o `none` justificado)? [Cobertura]
- [ ] CHK-010 ¿Cada R*.* es verificable por un test automatizable? [Cobertura]
- [ ] CHK-011 ¿Las métricas de éxito son medibles sin leer el código? [Cobertura]

## Consistencia

- [ ] CHK-012 ¿Ningún R*.* contradice a otro R*.* o a un NFR? [Conflicto]
- [ ] CHK-013 ¿El conflict scan cross-spec (3.c) corrió y sus hallazgos están resueltos o documentados? [Conflicto]

## Dependencias y supuestos

- [ ] CHK-014 ¿Toda dependencia externa está declarada como D-N con estado y estrategia? [Gap]
- [ ] CHK-015 ¿Las OPEN_QUESTIONS abiertas tienen owner y due? (0 abiertas para firmar G2) [Estructura]
- [ ] CHK-016 ¿Los supuestos tomados como default están escritos (no implícitos en la cabeza del autor)? [Gap]

## Diseño

<!-- SECCIÓN CONDICIONAL — /spec-new la incluye SÓLO si la feature
     declara una D-N de tipo `design` (§12 del methodology). Una feature
     sin UI, o con UI pero sin contrato de diseño declarado, NO lleva
     estos items: se borra la sección entera. Cero costo para quien no
     usa la disciplina. -->

- [ ] CHK-D1 ¿Cada D-N de diseño cita `id` **y** `version`? Si está en `NEGOTIATING`, ¿declara estrategia `MOCK` y un `Ready to unmock` observable? Si está `LIVE` con `derived: true`, estrategia `NONE` y sin `Ready to unmock` — no hay nada que desmockear (§16) [Gap]
- [ ] CHK-D2 **Si el contrato está `AGREED` o `IMPLEMENTED`**: ¿el implementability check está registrado (quién, cuándo, salvedades)? No aplica —`- [~] N/A: <razón>`— si está en `NEGOTIATING` (ver CHK-D1) ni si es `derived: true` (nunca pasa por el check: ya está implementado, §16) [Estructura]
- [ ] CHK-D3 ¿Los estados UX del flujo (vacío, carga, error, sin permisos, sin resultados) están cubiertos por al menos un R*.*? [Gap]
- [ ] CHK-D4 ¿Los criterios de accesibilidad del contrato son verificables y tienen nivel de prueba declarado en el R*.* correspondiente? [Cobertura]
- [ ] CHK-D5 ¿Las desviaciones respecto del contrato están registradas en `design.md` con justificación? [Conflicto]
- [ ] CHK-D6 Si algún contrato citado lleva `derived: true`, ¿se usa **sólo como descripción de lo que hay** y NO como norma para elementos nuevos? Un elemento nuevo que cite un contrato derivado necesita antes su v2 acordada (§16) [Estructura]

## Items específicos de esta feature

<!-- /spec-new agrega aquí items derivados de la entrevista: NFRs del
     dominio (accesibilidad si hay UI, retención si hay PII, límites
     si hay archivos/colas, idempotencia si hay pagos/webhooks...). -->

- [ ] CHK-017 <item específico> [R<x>.<y>]
