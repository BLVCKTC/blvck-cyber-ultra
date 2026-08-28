# Status

> The honest, surface-by-surface state of the system. Updated in the same change
> as the behavior it describes. **Backed** = real tenant-scoped endpoint.
> **Mock** = renders from a frontend mock module. **Partial** = some real, some mock.

_Last reconciled against code: identity/tenancy/RBAC and the Structural MVP operation workflows are backed; most SOC enrichment surfaces remain mock._

## 1. Backend routers

| Router | State | Notes |
| --- | --- | --- |
| `health` | ✅ Backed | Liveness. |
| `auth` | ✅ Backed | Keycloak OIDC + PKCE, JWT via JWKS. |
| `tenants` | ✅ Backed | Tenant list/selection. |
| `memberships` | ✅ Backed | User↔tenant membership + RBAC. |
| `dashboard` | ⚠️ Stub | `GET /dashboard/summary` returns a hardcoded literal, not real data. |
| _SOC domain_ (alerts, incidents, evidence, detections, ingestion, actions, approvals, audit, AI) | ❌ Missing | No routes exist. |

## 2. Frontend surfaces (`app/`)

### Golden-path surfaces

| Route | State | Backing |
| --- | --- | --- |
| `/login`, `/signup` | ✅ Backed | Keycloak/session. |
| `/dashboard/[tenantId]` (home) | ⚠️ Partial | Tenant/membership real; KPIs/widgets mock. |
| `/dashboard/[tenantId]/alerts` + `/[alertId]` | ❌ Mock | `lib/soc/mock.ts`. |
| `/dashboard/[tenantId]/incidents` + `/[incidentId]` | ❌ Mock | `lib/soc/mock.ts`; approval is a client toggle. |
| `/dashboard/[tenantId]/ai-assistant` | ❌ Mock | No AI code exists anywhere in the repo. |
| `/dashboard/[tenantId]/ai-config` | ❌ Mock | No AI subsystem to configure. |
| `/dashboard/[tenantId]/forensics` | ❌ Mock | Static data. |
| `/dashboard/[tenantId]/hunting` | ❌ Mock | Static data. |
| `/dashboard/[tenantId]/threat-intel` | ❌ Mock | `lib/threat-data.ts`. |
| `/dashboard/[tenantId]/vulnerabilities` | ❌ Mock | `lib/soc/mock.ts`. |
| `/dashboard/[tenantId]/audit` | ❌ Mock | No `AuditEvent` backend. |

### Non-golden-path surfaces (post-MVP, all mock)

| Route | State |
| --- | --- |
| `/dashboard/[tenantId]/assets` | ❌ Mock |
| `/dashboard/[tenantId]/compliance` | ❌ Mock |
| `/dashboard/[tenantId]/reports` | ❌ Mock |
| `/dashboard/[tenantId]/academy` | ❌ Mock |
| `/dashboard/[tenantId]/insurance` | ❌ Mock |
| `/dashboard/[tenantId]/mobile` | ❌ Mock |
| `/dashboard/[tenantId]/integrations` | ❌ Mock |
| `/dashboard/[tenantId]/api-keys` | ❌ Mock |
| `/dashboard/[tenantId]/billing` | ❌ Mock |
| `/dashboard/[tenantId]/{users,roles,teams,organization,tenants,sessions,mfa,settings}` | ⚠️ Partial — identity/RBAC backend exists; management UIs mostly mock |
| `/dashboard/[tenantId]/soc-demo` | ❌ Mock (demo) |
| `/admin/*` (growth, leads, partners, revenue, subscribers, subscription-health) | ❌ Mock |
| `/`, `/app`, `/demo`, `/test`, `/bug-bounty` | ❌ Mock/marketing |

## 3. Cross-cutting capabilities

| Capability | State |
| --- | --- |
| Authentication (Keycloak, PKCE) | ✅ Backed |
| Tenant isolation (server-side `403 not_a_member`) | ✅ Backed |
| Per-tenant RBAC | ✅ Backed |
| Telemetry ingestion | ❌ Missing |
| Detection lifecycle | ❌ Missing |
| Evidence graph | ❌ Missing |
| AI investigation / recommendation | ❌ Missing (zero AI code) |
| ActionRequest + human approval | ❌ Missing (UI toggle only) |
| Controlled response executor | ❌ Missing |
| Verification | ❌ Missing |
| Immutable audit log | ❌ Missing |
| Security-boundary tests | ❌ Missing |

## 4. Golden-incident readiness

Stages 0–1 backed; stages 2–11 not. See [`GOLDEN_INCIDENT.md`](./GOLDEN_INCIDENT.md).

**MVP readiness: not ready.**
