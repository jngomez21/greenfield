# .org/ — catálogo organizacional

> Esta carpeta es **opcional** (§9 del methodology). Sólo tiene sentido
> si este repo coordina con otros repos del mismo equipo o team project
> y necesita publicar contratos / políticas / ADRs compartidos.
>
> Si tu repo es self-contained (no expone contratos hacia afuera),
> puedes **borrar esta carpeta** sin perder funcionalidad.

## Contenido típico

```
.org/
├── contract-types.yaml ← opcional: registro de tipos de contrato (§9, v0.27)
├── contracts/          ← OBLIGATORIO cuando hay dependencias cross-repo (§9)
│   ├── apis/           ←   OpenAPI
│   ├── events/         ←   AsyncAPI
│   ├── design/         ←   opcional: DS-* / DC-* (v0.27)
│   └── deprecated/     ←   política de sunset (aplica a todo tipo)
├── catalog.yaml        ← opcional: inventario de servicios
├── policies/           ← opcional: políticas org (PII, auth standards)
├── decisions/          ← opcional: ADRs cross-repo
└── templates/          ← opcional: templates compartidos de specs / agents
```

## Contratos de otras disciplinas (v0.27)

Desde v0.27 este mecanismo **no es sólo para APIs**. Diseño,
cumplimiento, operaciones o datos publican aquí su contrato con la
misma gobernanza: `id` + `version` + `owner` + estados + criterios
verificables, citado desde la spec como `D-N` (§3.19 del methodology).

Las carpetas por tipo son **hermanas** de `apis/` y `events/` — no una
reorganización. Una carpeta aparece cuando hay un contrato real de ese
tipo, nunca antes.

`contract-types.yaml` declara qué tipos existen. **Agregar una
disciplina = agregar una entrada ahí.**

## Cuándo publicar un contrato aquí

Cualquier `D-N` cross-team que llegue a estado `AGREED` (§6 del
methodology) debe tener su contrato versionado en `.org/contracts/`. Es
el único requisito **obligatorio** del catálogo.

## Si trabajas en una org real

Lo normal es que `.org/` sea un repo separado (`<org>-platform/`) y este
repo lo consuma como submódulo, paquete o vía registry. La carpeta
local sirve para arrancar — luego se migra al repo central cuando haya
más de un servicio que la consuma.
