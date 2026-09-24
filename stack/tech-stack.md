# Tech stack

> **Servicio**: `<TODO: nombre del servicio>`
> **Estado**: TODO — completar durante bootstrap (ver AGENTS.md § Bootstrap)

> El Service Agent se **negará a generar código** mientras este archivo
> tenga un `TODO` **que no cuelgue de nada** — lenguaje, framework,
> persistencia o testing sin decidir. Razón: sin eso, los `design.md`
> salen genéricos y los tests no pueden trazar a las convenciones
> reales.
>
> **Un `TODO` que cuelga de una `D-N` aceptada en G2 con `MOCK` y
> `Ready to unmock` no bloquea**: bloquea producción, no el trabajo
> contra el doble. Si bloqueara, una spec cuyo stack espera a un
> tercero no llegaría nunca al código. La tabla está en
> `/spec-implement`.

## Lenguaje y framework

<!-- TODO: ¿Qué lenguaje (TS, Python, Go, Rust, Kotlin, .NET, etc.)?
¿Qué framework principal (Next.js, FastAPI, Spring, Actix, etc.)?
Versiones específicas. -->

## Persistencia

<!-- TODO: ¿Base de datos (Postgres, MySQL, MongoDB, DynamoDB, etc.)?
¿ORM o query builder (Prisma, SQLAlchemy, Entity Framework, GORM)?
¿Cache (Redis, Memcached)? Versiones. -->

## Build y package manager

<!-- TODO: package manager (pnpm/npm/yarn, pip/poetry, cargo, maven,
gradle, etc.), bundler/build tool si aplica, lockfile a commitear. -->

## Tests

<!-- TODO: framework de tests (vitest, jest, pytest, junit, go test,
etc.). Detalle de política en stack/testing.md. -->

## Lint y formato

<!-- TODO: linter (eslint/ruff/golangci-lint/clippy), formatter
(prettier/black/gofmt/rustfmt), pre-commit hooks si aplica. -->

## Deploy target

<!-- TODO: OpenShift / Kubernetes / Vercel / AWS Lambda / static host
(S3+CloudFront, Cloudflare Pages) / npm registry (para library) / etc.
Cruzar con `repo-config.yaml > runtime.type`. -->

## Versiones pineadas

<!-- TODO: versiones de runtime y librerías críticas para evitar drift.
Ej. Node 22.x, .NET 9.0, Python 3.13, etc. -->
