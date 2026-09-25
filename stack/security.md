# Security

> **Servicio**: `greenfield`
> **Estado**: completo (bootstrap 2026-09-25). Proveedor de identidad concreto `TBD`: sólo cambia configuración.

## Autenticación

- **JWT Bearer emitido por un IdP externo (OIDC)**. El servicio **no** gestiona
  usuarios ni contraseñas y no emite tokens.
- Validación con **PyJWT** + `PyJWKClient` contra el JWKS del IdP:
  - firma asimétrica (`RS256`/`ES256`); se rechazan `none` y `HS*`,
  - `iss` y `aud` obligatorios y comparados con la configuración,
  - `exp` obligatorio; tolerancia de reloj ≤ 30 s.
- Identidad del usuario = claim **`sub`** (se guarda como texto opaco).
- Token ausente o inválido → `401` con `WWW-Authenticate: Bearer`.
- Configuración por entorno: `AUTH_ISSUER`, `AUTH_AUDIENCE`, `AUTH_JWKS_URL`.
- Proveedor concreto (Keycloak / Entra ID / Auth0): `TBD`, se resuelve antes de
  desplegar en `pruebas`. En tests se usa un par de llaves generado en la
  fixture y un JWKS local.

## Autorización

- Por **propiedad**: cada recurso de usuario guarda el `sub` de su dueño y toda
  query filtra por él en la capa `service`.
- Acceso a un recurso de otro usuario → **`404`** (igual que si no existiera),
  para no revelar qué IDs existen.
- Sin roles ni scopes por ahora.

## Manejo de secretos

- Variables de entorno. `.env` **sólo** en local y en `.gitignore`; se commitea
  `.env.example` sin valores reales.
- El servicio no maneja secretos de firma (sólo llaves públicas vía JWKS). El
  único secreto es la credencial de BD (`DATABASE_URL`).
- Gestor de secretos en runtime: se decide junto con el deploy target.

## PII / datos sensibles

- `sub`: identificador seudónimo del usuario.
- El contenido que escribe el usuario (título, descripción) puede traer datos
  personales: se trata como sensible y **no se loguea** (ver
  `stack/patterns.md` § Logging).
- En tránsito: TLS terminado en el ingress/gateway. En reposo: el cifrado del
  proveedor de PostgreSQL.

## Compliance

Ninguna regulación específica declarada. Si se sirve a usuarios bajo la Ley
1581 de 2012 (Colombia) o GDPR, se revisa este archivo y el borrado de datos
por usuario.

## Residencia de datos

Sin requisito declarado.

## Vulnerabilidades

- `pip-audit` sobre las dependencias en CI.
- SLA: crítica 24 h, alta 1 semana, media 1 mes. Triage: owner del repo.

## Auditoría

No exigida. Los logs de request (método, ruta, status, `sub`) bastan.
