// Prueba de carga de NFR1 (specs/gestion-tareas): p95 < 300 ms en operaciones individuales
// y p95 < 500 ms en listados, con 10 usuarios concurrentes y 1.000 tareas por usuario.
// Uso y variables de entorno: tests/load/README.md.
import http from 'k6/http';
import { check, fail } from 'k6';

const BASE_URL = (__ENV.BASE_URL || '').replace(/\/+$/, '');
const TOKENS = (__ENV.TOKENS || '').split(',').map((t) => t.trim()).filter(Boolean);
const USERS = 10;
const TASKS_PER_USER = Number(__ENV.TASKS_PER_USER || 1000);
const CLEANUP = (__ENV.CLEANUP || 'true') === 'true';
const SEED_BATCH = 100;

export const options = {
  setupTimeout: '15m',
  teardownTimeout: '15m',
  scenarios: {
    nfr1: {
      executor: 'constant-vus',
      vus: USERS,
      duration: __ENV.DURATION || '2m',
    },
  },
  thresholds: {
    // NFR1 — la siembra y la limpieza llevan kind:seed y no cuentan.
    'http_req_duration{kind:single}': ['p(95)<300'],
    'http_req_duration{kind:list}': ['p(95)<500'],
    'http_req_failed{kind:single}': ['rate<0.01'],
    'http_req_failed{kind:list}': ['rate<0.01'],
    checks: ['rate>0.99'],
  },
};

function headers(token) {
  return { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' };
}

function isoDate(offsetDays) {
  const d = new Date();
  d.setUTCDate(d.getUTCDate() + offsetDays);
  return d.toISOString().slice(0, 10);
}

const STATUSES = ['pending', 'in_progress', 'completed'];

function seedTask(i) {
  // Mezcla realista: tres estados, fechas pasadas y futuras, algunas sin fecha límite.
  return {
    title: `Tarea de carga ${i}`,
    status: STATUSES[i % STATUSES.length],
    due_date: i % 5 === 0 ? null : isoDate((i % 121) - 60),
  };
}

export function setup() {
  if (!BASE_URL) fail('Falta BASE_URL');
  if (TOKENS.length !== USERS) fail(`TOKENS debe traer ${USERS} tokens de usuarios distintos`);

  const seeded = [];
  for (const token of TOKENS) {
    const ids = [];
    for (let start = 0; start < TASKS_PER_USER; start += SEED_BATCH) {
      const batch = [];
      for (let i = start; i < Math.min(start + SEED_BATCH, TASKS_PER_USER); i++) {
        batch.push({
          method: 'POST',
          url: `${BASE_URL}/v1/tasks`,
          body: JSON.stringify(seedTask(i)),
          params: { headers: headers(token), tags: { kind: 'seed' } },
        });
      }
      for (const res of http.batch(batch)) {
        if (res.status !== 201) fail(`La siembra falló: HTTP ${res.status}`);
        ids.push(res.json('id'));
      }
    }
    seeded.push(ids);
  }
  return { seeded };
}

export default function () {
  const token = TOKENS[(__VU - 1) % USERS];
  const h = headers(token);
  const single = { headers: h, tags: { kind: 'single' } };
  const list = { headers: h, tags: { kind: 'list' } };

  const created = http.post(
    `${BASE_URL}/v1/tasks`,
    JSON.stringify({ title: `Iteración ${__ITER}`, due_date: isoDate(3) }),
    single,
  );
  check(created, { 'crear 201': (r) => r.status === 201 });
  const url = `${BASE_URL}/v1/tasks/${created.json('id')}`;

  check(http.get(url, single), { 'consultar 200': (r) => r.status === 200 });
  check(http.patch(url, JSON.stringify({ status: 'in_progress' }), single), {
    'actualizar 200': (r) => r.status === 200,
  });
  check(http.get(`${BASE_URL}/v1/tasks?limit=50`, list), { 'listar 200': (r) => r.status === 200 });
  check(http.get(`${BASE_URL}/v1/tasks?status=in_progress&limit=50`, list), {
    'listar filtrado 200': (r) => r.status === 200,
  });
  check(http.get(`${BASE_URL}/v1/tasks/pending?limit=50`, list), {
    'pendientes 200': (r) => r.status === 200,
  });
  check(http.get(`${BASE_URL}/v1/tasks/pending?overdue=true&limit=50`, list), {
    'vencidas 200': (r) => r.status === 200,
  });
  check(http.del(url, null, single), { 'eliminar 204': (r) => r.status === 204 });
}

export function teardown(data) {
  if (!CLEANUP) return;
  // Borra sólo las tareas que sembró esta corrida.
  data.seeded.forEach((ids, u) => {
    const params = { headers: headers(TOKENS[u]), tags: { kind: 'seed' } };
    for (let start = 0; start < ids.length; start += SEED_BATCH) {
      http.batch(
        ids.slice(start, start + SEED_BATCH).map((id) => ['DELETE', `${BASE_URL}/v1/tasks/${id}`, null, params]),
      );
    }
  });
}
