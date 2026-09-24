# Patterns

> **Servicio**: `<TODO: nombre del servicio>`
> **Estado**: TODO — completar durante bootstrap

## Naming

### Archivos

<!-- TODO: kebab-case / PascalCase / snake_case según convención del
ecosistema (TS suele kebab-case, .NET PascalCase, Python snake_case,
Go snake_case en archivos pero camelCase en código). -->

### Funciones / métodos

<!-- TODO: camelCase / snake_case / PascalCase según lenguaje. -->

### Clases / tipos / interfaces

<!-- TODO: PascalCase usualmente. Convenciones específicas (ej.
prefijo `I` para interfaces en C#? sin prefijo en TS?). -->

### Variables / constantes

<!-- TODO: camelCase / snake_case / UPPER_SNAKE_CASE para constantes. -->

## Imports

<!-- TODO: ¿alias de path (@/ → src/)? ¿imports relativos vs
absolutos? ¿orden (built-in, external, internal, parent, sibling)?
¿auto-organizado por linter? -->

## Convención de commits

<!-- TODO: convención del repo. La metodología recomienda:

  <type>(<scope>): T<n> - <desc> [R<x>.<y>] AB#<workitem-id>

con `AB#` opcional según `repo-config.yaml > tracker`. Ver
AGENTS.md § Convención de commits. -->

## Branching

<!-- TODO: viene de `repo-config.yaml > environments` +
`promotion_path`. Worktree por feature (`feat/<slug>`) según §6
*Worktree, ramas y flujo de promoción* del methodology. -->

## Organización de tests

<!-- TODO: estructura (co-located `foo.ts` + `foo.test.ts`, vs
separate dir `tests/`), naming (`*.test.ts` / `*_test.go` /
`test_*.py`), convención `// Derived from R*.*`. Ver stack/testing.md
para detalle de política. -->

## Logging

<!-- TODO: framework, niveles (debug/info/warn/error), formato
(estructurado JSON vs texto), qué NO loguear (PII, secrets). Cruzar
con stack/security.md. -->

## Error reporting

<!-- TODO: ¿Sentry / Datadog / Application Insights / propio? Cómo
se reportan errores no manejados, política de breadcrumbs. -->
