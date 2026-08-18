# Golden Incident

> The canonical end-to-end scenario the MVP must support. This is the acceptance
> script: when an analyst can complete every stage below against **real,
> tenant-scoped, backed data**, the MVP is done. Today only stages 0–1 are backed
> (auth + tenant selection); everything else is mock. See [`STATUS.md`](./STATUS.md).

## Scenario

> A workstation in tenant **Acme Corp** beacons to a known-malicious host. A
> detection fires, an alert is raised and correlated into an incident, the
> evidence graph assembles the attack chain, the AI proposes containment, an
> analyst approves it, the host is isolated, verification confirms containment,
> and the entire sequence is written to the audit log.

## Stages (acceptance checklist)

| # | Stage | What must happen | Backed today? |
| --- | --- | --- | --- |
| 0 | **Authenticate** | Analyst signs in via Keycloak (PKCE) | ✅ Yes |
| 1 | **Select tenant** | Analyst enters Acme; membership enforced (`403` otherwise) | ✅ Yes |
| 2 | **Ingest telemetry** | Beacon event normalized and tenant-tagged | ❌ Planned |
| 3 | **Detect** | A `production` detection matches and fires | ❌ Planned |
| 4 | **Alert** | Tenant-scoped alert created with severity + entities | ❌ Planned (UI mock only) |
| 5 | **Incident** | Alert(s) correlated into an incident | ❌ Planned (UI mock only) |
| 6 | **Evidence graph** | Nodes/edges assemble host↔C2↔user↔process with provenance | ❌ Planned (static diagram) |
| 7 | **AI investigation** | AI emits a structured recommendation + a `pending` ActionRequest | ❌ Planned (no AI exists) |
| 8 | **Human approval** | Analyst with `approve` permission approves the ActionRequest | ❌ Planned (client toggle only) |
| 9 | **Controlled response** | Allowlisted "isolate host" tool executes the approved action | ❌ Planned |
| 10 | **Verification** | System confirms the host is isolated / beaconing stopped | ❌ Planned |
| 11 | **Audit** | Every step above is written immutably with actor + tenant | ❌ Planned |

## Invariants that must hold during the golden incident

1. Every record created (alert, incident, evidence, finding, action, audit) is
   tagged with Acme's `tenant_id` and invisible to other tenants.
2. The AI at stage 7 **cannot** skip stages 8–9; it only produces a `pending`
   ActionRequest.
3. Stage 9 executes **only** because a human approved at stage 8, and only via an
   allowlisted response tool.
4. Stage 11 produces exactly one `AuditEvent` per state change, append-only.

## Definition of done for the MVP

The MVP is complete when a single analyst account can walk stages 0→11 in the UI
against backed endpoints, with all four invariants verified by automated tests
(see [`SECURITY_MODEL.md`](./SECURITY_MODEL.md) §7).
