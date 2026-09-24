<!--
  PLANTILLA AI-DLC — design.md (canonical: .agents/templates/spec/)
  Se llena DESPUÉS de que requirements.md esté aprobado (o al menos
  estable). Aquí sí va el CÓMO: arquitectura, contratos, datos.

  GUARDRAILS:
  - Todo componente/abstracción nuevo debe justificarse con un R*.*
    o NFR concreto. Si ningún requirement lo exige, no va — o se
    declara en "Complejidad justificada".
  - Cruzar con stack/architecture.md y stack/constraints.md: el
    design no contradice el stack declarado del repo.
  - Decisiones con notación DEC-N (no D-N — reservado a Dependencies).
  - Registrar alternativas rechazadas: el "por qué no" vale tanto
    como el "por qué sí" (evita re-litigar en amendments).

  SECCIONES QUE NO APLICAN — dos casos distintos, y confundirlos
  le cobra la disciplina a quien no la declaró:

  a) La capacidad NO está declarada en repo-config.yaml (no hay
     `disciplines`, no hay tracker…) → la sección **SE BORRA ENTERA**.
     No se puede "considerar y descartar" una disciplina que el repo
     no tiene, y dejarla obliga a resolverla en G2 (check 0).
  b) La capacidad SÍ está declarada pero no aplica a ESTA feature →
     se marca `N/A — <razón>`.

  Regla corta: **capacidad no declarada se borra; capacidad declarada
  que no aplica se marca**. Las secciones condicionales llevan escrito
  de qué capacidad dependen.

  Para el caso (b), la marca va `N/A — <razón>`
  en una línea. Ejemplo: "## Observabilidad — N/A: no agrega
  endpoints ni jobs; la métrica existente cubre el cambio".
  Por qué marcar y no borrar: un design.md sin sección de Seguridad es
  ambiguo —¿se consideró y se descartó, o se olvidó?—. La marca deja
  escrito que se consideró, y es lo que `/spec-verify --pre-g2`
  (check 0) exige para firmar G2: toda sección resuelta, llena o N/A.
  Ojo: `N/A` no es un atajo. No se puede marcar N/A en Modelo de datos
  si algún R*.* persiste algo.
-->
# Design: <Feature>

## Arquitectura

<!-- Diagrama mermaid + prosa corta. Sólo los componentes que esta
     feature toca o crea. -->

## Componentes

| Componente | Responsabilidad | Justificado por |
|---|---|---|
| <nombre> | <una línea> | R<x>.<y> / NFR<n> |

## Modelo de datos

<!-- DDL o diagrama ER. Si modality: data-migration, incluir además:
     SQL exacto, plan de rollback por fase, plan de backfill (batch
     size, idempotencia, ETA), queries de verificación de invariantes
     (§6 expand-contract). -->

## Contratos

### API
<!-- OpenAPI snippet o link a .org/contracts/ -->

### Eventos
<!-- AsyncAPI snippet o link -->

### Contratos de disciplina
<!-- CONDICIONAL — depende de: `disciplines` en repo-config.yaml.
     Si el repo NO la declara, BORRAR esta sección entera (caso (a) del
     guardrail de cabecera).
     Si la declara: cada contrato por `id` Y `version`, con su D-N —
     DS-*/DC-*/DF-* (diseño), POL-* (política), etc. `N/A — <razón>` si
     esta feature no consume ninguno. -->

| Contrato | Versión | D-N | Estado | Qué aporta a esta feature |
|---|---|---|---|---|
| <DC-xxx> | <1.0.0> | D<n> | AGREED | |

### Desviaciones respecto del contrato
<!-- CONDICIONAL — depende de: `disciplines` en repo-config.yaml.
     Si el repo NO la declara, BORRAR esta sección entera.
     Si la declara: lo que esta feature implementa DISTINTO de lo que el
     contrato dice, con su justificación. Es lo que CHK-D5 verifica en
     G2 — "se hizo distinto porque sí" no es justificación. Si no hay
     desviaciones: `N/A — sin desviaciones`. -->

## Decisiones (DEC-N)

- **DEC-1**: <decisión> — justifica R<x>.<y>.
  - Alternativas consideradas: <opción B> (rechazada porque <razón>).
- **DEC-2**: ...

## Complejidad justificada

<!-- Guardrail anti-overengineering. Si el design introduce algo que
     un revisor podría considerar más complejo de lo que los R*.*
     exigen (capa de abstracción extra, proyecto/paquete nuevo,
     patrón no usado en el repo, generalización "para el futuro"),
     declararlo aquí. Vacío = el design usa lo más simple que cumple.
     /spec-verify --pre-g2 reporta complejidad no declarada. -->

| Qué | Por qué es necesario | Alternativa más simple rechazada porque |
|---|---|---|
| <nada — omitir tabla si no aplica> | | |

## Despliegue

<!-- Según repo_type (§6). Para service: namespace, recursos, path a
     manifiestos. Para library: registry y versionado. -->

### Configuración

| Variable | Origen | Notas |
|---|---|---|
<!-- Secrets SIEMPRE por nombre/referencia, NUNCA por valor. -->

## Seguridad

- Auth: ...
- Datos sensibles / PII: ...
- Threat model: ... <!-- cruzar con stack/security.md -->

## Observabilidad

- Métricas: ...
- Logs: ...
- Alertas: ...

## Conflicts resolved

<!-- Sólo si el conflict scan de /spec-new (3.c) detectó conflictos
     con otras specs y se decidió coexistir: documentar el por qué. -->
