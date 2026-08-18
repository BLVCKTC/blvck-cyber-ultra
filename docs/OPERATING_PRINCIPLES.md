# Operating Principles

> How we build and what "honest" means here. These principles govern both the
> code and the documentation.

## 1. Documentation is the source of truth

- Design decisions live in `docs/` **before** they are built.
- Code that diverges from the docs is a bug in one of them; reconcile immediately.
- Every doc marks unbuilt design as **[PLANNED]** so intent is never mistaken for reality.

## 2. The UI must not overstate capability

- A page that renders mock data must be tracked as **Mock** in [`STATUS.md`](./STATUS.md).
- UI surface area must not imply backend capability that does not exist.
- When a surface is wired to a real endpoint, `STATUS.md` moves it to **Backed**
  in the same change.

## 3. Security is server-side and non-negotiable

- Isolation, authorization, and validation happen in the backend, always.
- The frontend reflects decisions; it never makes them.
- See [`SECURITY_MODEL.md`](./SECURITY_MODEL.md) for the enforced controls.

## 4. AI is advisory

- AI may enrich and recommend; it may never execute a privileged action.
- All AI output is schema-validated and treated as a proposal (`ActionRequest`).

## 5. Human-in-the-loop for privileged actions

- Every response action requires an explicit human approval by a principal with
  the right permission.
- Approvals and executions are audited immutably.

## 6. Build depth before breadth

- Prove one vertical slice of the golden path end-to-end before widening.
- New SOC pages stay mock until their backend exists and tests pass.

## 7. Tenant-scoping is universal

- Every domain row carries `tenant_id`; every query is scoped by resolved membership.
- No cross-tenant reads, writes, or evidence edges — enforced and tested.

## 8. Honesty in status

- [`STATUS.md`](./STATUS.md) is updated in the same PR as the behavior it describes.
- "Done" means backed + tested, not "renders in the UI".
