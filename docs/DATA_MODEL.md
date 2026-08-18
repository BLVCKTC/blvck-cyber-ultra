# Data Model

> Source of truth for persisted entities. **Implemented** entities exist as
> SQLAlchemy models + Alembic migrations. **[PLANNED]** entities are the target
> for the SOC domain and do not exist yet.

## 1. Conventions

- Every domain row carries `tenant_id` (FK → `tenants`), `created_at`, and
  (where relevant) `updated_at`.
- Provenance-bearing rows (evidence, findings, actions) also carry a `source`
  and, where applicable, a `confidence` score.
- All timestamps are UTC.

## 2. Implemented entities (identity, tenancy, RBAC)

Location: `backend/app/db/models/`.

| Entity | Purpose | Key fields |
| --- | --- | --- |
| `User` | Authenticated principal (Keycloak-backed) | id, external subject, email |
| `Tenant` | Isolation boundary | id, name, slug, timestamps |
| `Membership` | User ↔ Tenant link (with role) | user_id, tenant_id, role |
| `Permission` | Atomic capability | key |
| `TenantRole` | Role within a tenant | tenant_id, name |
| `RolePermission` / `TenantRolePermission` | Role ↔ Permission mapping | role_id, permission_id |
| `PkceAttempt` | PKCE flow state | verifier/challenge, expiry |

Relevant migrations: `25a51b968a05` (auth tables), `651a14c9928f` (RBAC),
`4ebd48c80180` (membership↔RBAC), `740583192cd2` (PKCE),
`b04c5da2d9e9`/`47dc2cb41846` (tenant slug/timestamps).

### Isolation invariant

`Membership` is the enforcement point: no `(user_id, tenant_id)` row ⇒ `403`.
All planned SOC entities inherit isolation by requiring a resolved membership
before any query.

## 3. SOC domain entities **[PLANNED]**

These back the golden path. None exist yet — they are the schema to build in
recommendation #2.

| Entity | Purpose | Notable fields |
| --- | --- | --- |
| `TelemetryEvent` | Normalized raw signal | tenant_id, source, kind, raw, occurred_at |
| `Detection` | Rule with lifecycle | tenant_id, status (`draft`→`production`), logic, version |
| `Alert` | Detection firing | tenant_id, detection_id, severity, status, entities |
| `Incident` | Correlated alerts | tenant_id, severity, status, summary, assignee |
| `IncidentAlert` | Incident ↔ Alert link | incident_id, alert_id |
| `EvidenceNode` | Graph node | tenant_id, type, ref, source, confidence, observed_at |
| `EvidenceEdge` | Graph relationship | tenant_id, src_id, dst_id, relation, observed_at |
| `Finding` | AI/analyst conclusion | tenant_id, incident_id, confidence, rationale |
| `ActionRequest` | Proposed privileged action | tenant_id, requested_by, params, status (`pending`→`approved`/`rejected`/`executed`) |
| `Approval` | Human decision on a request | action_request_id, approver_id, decision, decided_at |
| `AuditEvent` | Immutable record | tenant_id, actor, action, target, before/after, created_at |

### Detection lifecycle (state machine) **[PLANNED]**

```
draft ─▶ test ─▶ backtest ─▶ canary ─▶ approved ─▶ production
                                   └─(reject)─▶ draft
```

### ActionRequest lifecycle **[PLANNED]**

```
pending ─(approve)─▶ approved ─(execute)─▶ executed
   └─────(reject)──▶ rejected
```

## 4. Referential rules **[PLANNED]**

- `Alert.detection_id → Detection.id` (same tenant).
- `IncidentAlert` correlates alerts into a single incident (same tenant).
- `EvidenceEdge.src_id/dst_id → EvidenceNode.id` (same tenant, no cross-tenant edges).
- `Approval.action_request_id → ActionRequest.id`; execution is blocked unless a
  matching approved `Approval` exists.
- `AuditEvent` rows are append-only (no update/delete).
