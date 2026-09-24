# Testing

> **Servicio**: `<TODO: nombre del servicio>`
> **Estado**: TODO — completar durante bootstrap

## Niveles obligatorios

<!-- TODO: ¿cuáles de unit / integration / e2e / contract / load /
accessibility / security se exigen para cada feature? Cada `R*.*`
en `requirements.md` declara qué niveles lo cubren. -->

## Cobertura mínima

<!-- TODO: ¿% por nivel? Ej. unit ≥ 80%, integration ≥ 60%, e2e ≥
"flujos críticos cubiertos" (no porcentaje sino lista). NO usar
exclusions del coverage para inflar el % — declarar qué se excluye
y por qué. -->

## Frameworks

<!-- TODO: unit (vitest/jest/pytest/junit/go test), integration (lo
mismo o testcontainers), e2e (playwright/cypress/selenium), contract
(pact/spring cloud contract), load (k6/locust/gatling), accessibility
(axe-core). Cruzar con `stack/tech-stack.md`. -->

## Convención `// Derived from R*.*`

Cada test debe declarar el `R*.*` que cubre como comment al inicio:

```
// Derived from R1.2 (token entropy)
test('reset token has 256 bits of entropy', () => { ... });
```

Esto permite a `/spec-verify` cruzar tests ↔ requirements y detectar
tests huérfanos (sin `R*.*` válido tras Amendment) o `R*.*` sin
cobertura.

## Política de mocks

<!-- TODO: cuándo usar mocks (D-N no LIVE, 3rd party como Stripe),
cuándo NO (propia DB → testcontainer, propia lib → import directo).
Cruzar con §6 *Mocks como ciudadanos de primera clase* del methodology
y la regla *Ready to unmock*. -->

## Estructura de archivos

<!-- TODO: co-located (`src/foo.ts` + `src/foo.test.ts`) vs separate
dir (`tests/`). Naming exacto de archivos. -->

## TDD vs test-after

<!-- TODO: política. La metodología (§4 Fase 4) recomienda **tests
primero** (TDD) cuando hay lógica de negocio compleja; test-after es
aceptable para boilerplate. `/spec-implement` aplica tests primero
por default — declarar excepciones explícitas. -->

## CI gates de tests

<!-- TODO: qué pipelines corren qué niveles, en qué momento del
flujo (PR / pre-merge / pre-deploy). Cruzar con
`repo-config.yaml > environments[].gate`. -->
