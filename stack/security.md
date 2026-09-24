# Security

> **Servicio**: `<TODO: nombre del servicio>`
> **Estado**: TODO — completar durante bootstrap

## Autenticación

<!-- TODO: ¿JWT / session / OAuth 2.0 / OIDC / mTLS / API key /
basic auth? Proveedor (Auth0, Okta, Azure AD, Keycloak, propio). -->

## Autorización

<!-- TODO: ¿RBAC / ABAC / policies / scopes / claims? Cómo se
expresan los permisos (decoradores, middleware, policy engine como
OPA). -->

## Manejo de secretos

<!-- TODO: ¿Azure Key Vault / AWS Secrets Manager / HashiCorp Vault /
Doppler / 1Password CLI / .env (sólo dev local)? Cómo se inyectan en
runtime (env vars, CSI driver, init container). NUNCA hardcodear en
código ni en specs. -->

## PII / datos sensibles

<!-- TODO: qué se considera PII en este servicio (email, teléfono,
documento, dirección, datos médicos, financieros). Política de
masking en logs. Encryption at rest e in transit. -->

## Compliance

<!-- TODO: ¿GDPR / HIPAA / PCI-DSS / SOX / ISO 27001 / local? Si
aplica alguna, cada R*.* relevante debe trazar a la regulación. -->

## Residencia de datos

<!-- TODO: si la regulación exige residencia (EU, US, LATAM),
declararlo aquí. Cruzar con runtime declarado en `repo-config.yaml`
para que los namespaces / regiones coincidan. -->

## Vulnerabilidades

<!-- TODO: política de patches: ¿Dependabot, Snyk, Renovate?
SLA por severidad (ej. CVE crítico → 24h, alto → 1 semana, medio →
1 mes). Responsable del triage. -->

## Auditoría

<!-- TODO: si se exige (compliance, SOX), qué eventos se loguean
(login, cambios de permisos, accesos a PII), retención, dónde se
guardan, quién los revisa. -->
