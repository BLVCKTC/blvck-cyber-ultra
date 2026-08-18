# MVP Definition

> Source of truth for scope. The MVP is defined by the
> [Golden Incident](./GOLDEN_INCIDENT.md): an analyst completing stages 0→11
> against backed, tenant-scoped data.

## 1. In scope (MVP)

- Keycloak authentication (PKCE) — **done**.
- Multi-tenant selection with server-side isolation — **done**.
- Per-tenant RBAC — **done**.
- One **vertical slice** of the golden path, end-to-end, backed by Postgres:
  telemetry → detection → alert → incident → evidence → AI recommendation →
  human approval → response → verification → audit.
- The SOC console pages wired to those endpoints (replacing `lib/soc/mock.ts`).
- Automated security-boundary tests (cross-tenant, permission denial, AI-cannot-execute).

## 2. Explicitly out of scope (post-MVP)

- Breadth of SOC pages not on the golden path (academy, insurance, mobile,
  compliance, billing, growth/admin analytics) — remain mock until the vertical
  slice is proven.
- Multiple detection sources / integrations beyond the single golden-path source.
- Advanced AI (multi-agent, autonomous playbooks). MVP AI is single-shot,
  advisory, schema-constrained.

## 3. MVP acceptance criteria

1. All 12 golden-incident stages pass against backed data.
2. All four golden-incident invariants hold.
3. Security tests in [`SECURITY_MODEL.md`](./SECURITY_MODEL.md) §7 pass.
4. No golden-path page reads from a mock module.
5. [`STATUS.md`](./STATUS.md) marks every golden-path surface as **Backed**.

## 4. Build order (recommended)

1. **Docs** (this set) — _current step_.
2. Data model: `Incident`, `Alert`, `Evidence`, `ActionRequest`, `AuditEvent`
   (models + migrations), each tenant-scoped.
3. One vertical slice end-to-end against Postgres; wire the UI via a typed client.
4. Response path: `require_permission` + mandatory approval + immutable audit.
5. AI behind a boundary: tool allowlist + structured output; add injection tests.
6. Security-boundary test suite.

## 5. Current MVP readiness

**Not ready.** Only stages 0–1 are backed. The remaining stages are UI mock with
no backend. See [`STATUS.md`](./STATUS.md) for the surface-by-surface matrix.
