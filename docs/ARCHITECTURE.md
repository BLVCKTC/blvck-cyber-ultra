# Architecture

> **Status of this document:** Source of truth for system design. Describes the
> _target_ architecture. Sections that are not yet implemented are marked
> **[PLANNED]**. Implementation reality is tracked in [`STATUS.md`](./STATUS.md).

## 1. System overview

BLVCK CYBER is a **multi-tenant Security Operations Center (SOC) platform**. It
turns raw telemetry into investigable incidents, assists analysts with an
_advisory_ AI layer, and gates every privileged action behind human approval and
an immutable audit trail.

The system is split into two deployables:

| Layer | Tech | Responsibility |
| --- | --- | --- |
| **Frontend** | Next.js (App Router), React, Tailwind | SOC console UI, tenant selection, analyst workflow |
| **Backend** | FastAPI (Python), SQLAlchemy, Alembic, Postgres | Identity, tenancy, RBAC, and (planned) all SOC domain APIs |
| **Identity Provider** | Keycloak | OIDC/OAuth2, JWT issuance, PKCE |

The frontend is **not** authoritative for any security decision. It renders
state and collects intent; the backend authorizes and persists.

## 2. Request & trust flow

```
Browser ──(OIDC PKCE)──▶ Keycloak
   │                        │
   │  ◀── id/access token ──┘
   ▼
Next.js (session cookie) ──▶ FastAPI ──▶ Postgres
                                │
                                ├─ verify JWT via JWKS
                                ├─ resolve active tenant (cookie)
                                ├─ require membership (403 if none)
                                └─ require_permission(...) for RBAC
```

Trust boundaries:

1. **Browser → Next.js** — untrusted input; session cookie only.
2. **Next.js → FastAPI** — every SOC-data request must carry identity and be
   re-authorized server-side. The frontend never filters tenant data on its own.
3. **FastAPI → Postgres** — all rows are tenant-scoped; see
   [`SECURITY_MODEL.md`](./SECURITY_MODEL.md) and [`DATA_MODEL.md`](./DATA_MODEL.md).

## 3. Backend module map (current)

```
backend/app/
├── api/
│   ├── deps.py                 # get_active_membership, require_permission
│   ├── dependencies/rbac.py
│   └── routes/                 # health, auth, tenants, dashboard, memberships
├── core/
│   ├── config.py, cookies.py, db.py, keycloak.py, permissions.py
│   └── security/               # jwks, jwt_verify, keycloak_auth, permissions
├── db/
│   ├── models/                 # user, tenant, membership, permission,
│   │                           #   role_permission, tenant_role, pkce_attempt
│   ├── repositories/           # user_repo, tenant_repo, membership_repo
│   └── seeds/                  # permissions, roles, role_permissions
├── schemas/                    # auth, tenant, membership
└── services/                   # auth, membership, pkce, rbac, tenant, token
```

Everything above is **implemented**. The SOC domain (below) is **[PLANNED]**.

## 4. SOC domain services **[PLANNED]**

The golden path (see [`GOLDEN_INCIDENT.md`](./GOLDEN_INCIDENT.md)) requires these
backend services, none of which exist yet:

- **Ingestion** — accept telemetry, normalize, tenant-tag.
- **Detection** — rules with a `draft → test → backtest → canary → approved → production` lifecycle.
- **Alerting** — detections raise tenant-scoped alerts.
- **Incidents** — correlate alerts into incidents.
- **Evidence graph** — queryable nodes/edges with provenance, timestamps, and confidence.
- **AI investigation** — advisory only; produces structured recommendations, never executes.
- **Action requests & approvals** — every privileged action becomes an `ActionRequest` requiring human approval.
- **Response** — executes only approved actions through an allowlisted tool boundary.
- **Verification** — confirms the response achieved its goal.
- **Audit** — immutable, tenant-scoped record of every decision and action.

## 5. Frontend structure

```
app/dashboard/[tenantId]/       # tenant-scoped SOC console
components/soc/                 # Panel, primitives, alerts, incidents, ...
lib/soc/mock.ts                 # deterministic mock data (temporary)
lib/api/, lib/auth/             # the ONLY real backend calls today (auth/session)
```

All SOC pages currently read from `lib/soc/mock.ts` and sibling mock modules.
The migration target is a typed API client per SOC service. See
[`STATUS.md`](./STATUS.md) for the mock-vs-backed matrix.

## 6. Architectural rules (non-negotiable)

1. AI is **advisory**. It may only emit an `ActionRequest`; it may never execute a response.
2. Every privileged action passes through `require_permission(...)` **and** a human approval.
3. Every state-changing action writes an immutable `AuditEvent`.
4. Every domain row carries `tenant_id`, `created_at`, and (where applicable) provenance/confidence.
5. The frontend never enforces isolation or authorization — it only reflects backend decisions.
