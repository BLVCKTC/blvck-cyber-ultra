# BLVCK CYBER — Documentation

These documents are the **source of truth** for the platform. Code that diverges
from them is a bug in one of the two; reconcile immediately. Design that is not
yet built is marked **[PLANNED]**.

## Index

| Doc | Purpose |
| --- | --- |
| [`OPERATING_PRINCIPLES.md`](./OPERATING_PRINCIPLES.md) | How we build; what "honest" and "done" mean. |
| [`ARCHITECTURE.md`](./ARCHITECTURE.md) | System design, trust flow, module map. |
| [`SECURITY_MODEL.md`](./SECURITY_MODEL.md) | Auth, isolation, RBAC, approval, AI safety, required tests. |
| [`DATA_MODEL.md`](./DATA_MODEL.md) | Persisted entities (implemented + planned) and lifecycles. |
| [`GOLDEN_INCIDENT.md`](./GOLDEN_INCIDENT.md) | The canonical end-to-end acceptance scenario. |
| [`MVP.md`](./MVP.md) | Scope, acceptance criteria, build order. |
| [`STATUS.md`](./STATUS.md) | Honest, surface-by-surface mock-vs-backed matrix. |

## Reading order

1. `OPERATING_PRINCIPLES.md` — the rules of the road.
2. `GOLDEN_INCIDENT.md` — what the product must ultimately do.
3. `ARCHITECTURE.md` + `SECURITY_MODEL.md` + `DATA_MODEL.md` — how it is built.
4. `MVP.md` — what we build first.
5. `STATUS.md` — where we actually are today.

## One-line truth

Identity, multi-tenancy, and RBAC are real and enforced server-side. The entire
SOC domain (alerts, incidents, evidence, AI, approvals, response, audit) is
currently frontend mock. See `STATUS.md`.
