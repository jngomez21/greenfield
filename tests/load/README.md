# Prueba de carga — NFR1 (`gestion-tareas`)

`tasks.js` verifica NFR1 con [k6](https://grafana.com/docs/k6/) (DEC-11 de `design.md`):

| Umbral | Operaciones |
|---|---|
| p95 < 300 ms | crear, consultar una, actualizar, eliminar (`kind:single`) |
| p95 < 500 ms | listado, listado filtrado, pendientes, vencidas (`kind:list`) |

Carga: **10 usuarios concurrentes** (un VU por usuario) con **1.000 tareas cada uno** sembradas en
`setup()`. La siembra y la limpieza llevan `kind:seed` y no cuentan para los umbrales. k6 termina
con código distinto de 0 si algún umbral no se cumple.

Se corre **contra `pruebas`** (T13): requiere el runtime desplegado y tokens reales del IdP (D1).

## Variables

| Variable | Obligatoria | Default | Qué es |
|---|---|---|---|
| `BASE_URL` | sí | — | URL del servicio, sin `/v1` |
| `TOKENS` | sí | — | 10 Bearer tokens de **10 usuarios de prueba distintos**, separados por comas |
| `TASKS_PER_USER` | no | `1000` | Tareas sembradas por usuario |
| `DURATION` | no | `2m` | Duración de la medición |
| `CLEANUP` | no | `true` | Borra al final las tareas sembradas |

Los tokens no se commitean ni se pegan en el chat: se exportan en la terminal de quien corre la
prueba.

## Ejecución

```powershell
$env:BASE_URL = "https://<host-de-pruebas>"
$env:TOKENS   = "<t1>,<t2>,...,<t10>"
k6 run tests/load/tasks.js
```

k6 es una herramienta externa (AGPL-3.0, binario aparte; no se enlaza ni se distribuye con el
servicio). Instalarla requiere permisos de administrador o la versión portable (`.zip`).
