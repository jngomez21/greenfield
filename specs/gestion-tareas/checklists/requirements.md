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
# Checklist de requirements: gestion-tareas

**Propósito**: validar que `requirements.md` está listo para firmar G2.
**Creada**: 2026-09-25 · **Spec**: [requirements.md](../requirements.md)

## Completitud

- [x] CHK-001 ¿Cada slice (P1/P2/P3) declara su prueba independiente? [Estructura]
- [x] CHK-002 ¿Todos los flujos de error/excepción tienen un R*.* (IF/THEN)? [Gap]
- [x] CHK-003 ¿Los casos límite (vacío, máximo, concurrencia, duplicados) están contemplados? [Gap]
- [x] CHK-004 ¿"Fuera de scope" lista lo que un lector podría asumir incluido? [Estructura]

## Claridad

- [x] CHK-005 ¿Cero adjetivos sin métrica ("rápido", "intuitivo", "robusto", "escalable")? [Claridad]
- [x] CHK-006 ¿Cero marcadores [NEEDS CLARIFICATION] pendientes? [Claridad]
- [x] CHK-007 ¿Cada R*.* admite UNA sola interpretación razonable? [Claridad]
- [x] CHK-008 ¿Los términos de dominio se usan consistentemente (sin sinónimos intercambiados)? [Claridad]

## Testeabilidad

- [x] CHK-009 ¿Cada R*.* tiene `Tests:` declarado con niveles concretos (o `none` justificado)? [Cobertura]
- [x] CHK-010 ¿Cada R*.* es verificable por un test automatizable? [Cobertura]
- [x] CHK-011 ¿Las métricas de éxito son medibles sin leer el código? [Cobertura]

## Consistencia

- [x] CHK-012 ¿Ningún R*.* contradice a otro R*.* o a un NFR? [Conflicto]
- [x] CHK-013 ¿El conflict scan cross-spec (3.c) corrió y sus hallazgos están resueltos o documentados? [Conflicto]

## Dependencias y supuestos

- [x] CHK-014 ¿Toda dependencia externa está declarada como D-N con estado y estrategia? [Gap]
- [x] CHK-015 ¿Las OPEN_QUESTIONS abiertas tienen owner y due? (0 abiertas para firmar G2) [Estructura]
- [x] CHK-016 ¿Los supuestos tomados como default están escritos (no implícitos en la cabeza del autor)? [Gap]

## Items específicos de esta feature

- [x] CHK-017 ¿Está definido que el acceso a una tarea ajena es indistinguible de una inexistente, en consultar, actualizar y eliminar? [R1.3]
- [x] CHK-018 ¿Los límites de longitud del título y la descripción están cuantificados y su violación tiene un R*.*? [R2.4, R2.5]
- [x] CHK-019 ¿Está definido el "día actual" (zona horaria) que determina si una tarea está vencida? [R6.3]
- [x] CHK-020 ¿Se distingue en la actualización parcial un campo ausente (no cambia) de un campo enviado nulo (se quita)? [R4.1, R4.4]
- [x] CHK-021 ¿Está definido el comportamiento ante actualizaciones concurrentes de la misma tarea? [Gap]
- [x] CHK-022 ¿Está definido si los listados se paginan y con qué límites? [R3.3]
- [x] CHK-023 ¿El orden de los listados es total y determinista, con desempate definido? [R3.3, R6.2]
- [x] CHK-024 ¿Está explícito qué datos del usuario no se registran en logs? [NFR2]
