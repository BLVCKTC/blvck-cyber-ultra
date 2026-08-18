# Security Model

> Source of truth for security posture. **[PLANNED]** marks controls not yet
> implemented. See [`STATUS.md`](./STATUS.md) for what is live today.

## 1. Principles

1. **Server-side authority.** The browser is untrusted. All isolation,
   authorization, and validation happen in FastAPI.
2. **Least privilege.** Access is granted per permission, per tenant, via RBAC.
3. **Human-in-the-loop.** No privileged action executes without explicit human approval.
4. **AI is advisory, never actuating.** The AI layer can recommend; it can never execute.
5. **Everything is audited.** Every decision and state change is recorded immutably.

## 2. Identity & authentication (implemented)

- **Provider:** Keycloak (OIDC/OAuth2).
- **Flow:** Authorization Code + **PKCE** (`pkce_attempt` model + migration `740583192cd2`).
- **Token verification:** JWTs verified against Keycloak **JWKS**
  (`core/security/jwks.py`, `jwt_verify.py`) — signature, issuer, and expiry.
- **Session:** Next.js holds a session cookie (`lib/auth/session.ts`); the active
  tenant is carried in a cookie and resolved server-side.

## 3. Tenant isolation (implemented for existing routes)

Enforced in `backend/app/api/deps.py::get_active_membership`:

- The active `tenant_id` is read from the request cookie.
- `MembershipRepo.get_membership(user.id, tenant_id)` **must** return a row.
- Otherwise the request is rejected with **`403 not_a_member`**.

This means a user swapping the tenant cookie to a tenant they do not belong to is
denied server-side — isolation is **not** a frontend concern.

**[PLANNED]** Every SOC domain table must include `tenant_id`, and every SOC query
must be scoped by the resolved membership tenant. See [`DATA_MODEL.md`](./DATA_MODEL.md).

## 4. Authorization / RBAC (implemented)

- `require_permission(permission_key)` → `RBACService.has_permission(user_id, tenant_id, permission_key)`.
- Backed by tables: `permissions`, `roles`/`tenant_roles`, `role_permissions`,
  `tenant_role_permission` (migrations `651a14c9928f`, `f678243ad1e5`,
  `32ce2e6cde24`, `4ebd48c80180`) and seeds in `db/seeds/`.
- Permissions are checked **per tenant** — a role in tenant A grants nothing in tenant B.

## 5. Human approval & controlled response **[PLANNED]**

Target control path for any privileged action (isolate host, disable user, block IP, etc.):

```
proposed action ─▶ ActionRequest(status=pending, tenant_id, requested_by, params)
                        │
                        ▼
              require_permission(approve:*)  +  human approves
                        │
                        ▼
   response executor (allowlisted tools only) ─▶ AuditEvent(immutable)
                        │
                        ▼
                  verification step
```

Rules:

- AI output may **create** an `ActionRequest` but its `status` starts `pending`.
- Approval requires a human principal with the correct permission.
- Execution runs only against an **allowlist** of response tools.

## 6. AI safety **[PLANNED]**

- **Instruction/data separation:** telemetry, alerts, and threat-intel are treated
  as untrusted _data_, never as instructions.
- **Structured output:** recommendations must validate against a fixed schema
  (finding, confidence, proposed `ActionRequest`), not free-form execution.
- **Tool allowlist:** the AI can call only read/enrichment tools; no response tools.
- **Prompt-injection tests:** hostile telemetry/intel must not cause the AI to
  trigger execution or leak cross-tenant data.

## 7. Required security tests **[PLANNED]**

- Cross-tenant read: user A cannot read tenant B by swapping the tenant cookie.
- Permission denial: a user without `X` gets `403` on `require_permission(X)`.
- AI-cannot-execute: no AI path reaches a response tool without a human-approved `ActionRequest`.
- Audit completeness: every state change produces exactly one `AuditEvent`.

## 8. Known gaps (today)

- All SOC data is frontend mock; no SOC-domain authorization exists yet.
- No `ActionRequest`, approval engine, response executor, or `AuditEvent`.
- No AI subsystem, therefore no AI safety controls.
- No automated security-boundary tests.
