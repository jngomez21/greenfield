# Architecture

> **Servicio**: `<TODO: nombre del servicio>`
> **Estado**: TODO — completar durante bootstrap

## Estilo arquitectónico

<!-- TODO: ¿Clean Arch / Hexagonal / Onion / Layered / Modular
Monolith / Microservices / Event-Driven / MVC / MVVM?
Justificar la elección en 1-2 oraciones. -->

## Estructura de carpetas

<!-- TODO: árbol de directorios principal y qué va en cada uno. -->

```
src/
├── <TODO>
└── <TODO>
```

## Capas y boundaries

<!-- TODO: cuáles son las capas (si aplica), qué puede importar qué.
Ej. en Clean Arch: domain no importa de application; application no
importa de infrastructure. Reglas de dependencia explícitas. -->

## Inyección de dependencias

<!-- TODO: ¿Manual / factory functions / container DI / framework
DI? Para tests, ¿cómo se inyectan los doubles? -->

## Manejo de errores

<!-- TODO: ¿Excepciones / Result type / Either / error returns?
Tipados o no. Política de bubbling vs handling en cada capa. -->

## Concurrencia / async

<!-- TODO: si aplica — async/await, threads, actors, event loop,
queues. Política de timeouts, retries, idempotencia. -->

## ADRs

<!-- TODO: link a carpeta de ADRs si se llevan. Cada decisión
arquitectónica relevante post-bootstrap se documenta como ADR aparte
(no se sobreescribe este archivo). -->
