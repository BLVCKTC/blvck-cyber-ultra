from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.agents.planning import decide_plan
from app.agents.state import InvestigationState, _DEFAULT_PLAN
from app.agents.tools.alert_context import collect_alert_context
from app.agents.tools.evidence_items import build_evidence_items
from app.agents.tools.mitre_context import collect_mitre_context
from app.agents.tools.threat_intel_context import collect_threat_intel_context
from app.db.models.alert import Alert
from app.db.models.security_event import SecurityEvent
from app.schemas.investigation import (
    EvidenceCreate,
    InvestigationCreate,
    InvestigationUpdate,
)
from app.services.investigation_service import InvestigationService

logger = logging.getLogger(__name__)


def _error_state(
    state: InvestigationState,
    message: str,
    *,
    failed_step: str | None = None,
    code: str | None = None,
) -> InvestigationState:
    """
    Return a consistent error update without destroying existing state.

    `code` is a machine-readable failure class for callers that must react
    differently (for example "alert_not_found" -> HTTP 404).
    """
    logger.error(
        "Investigation orchestration failed: %s; investigation_id=%s",
        message,
        state.get("investigation_id"),
    )

    return {
        **state,
        "error": message,
        "failed_step": failed_step,
        "error_code": code,
    }


def _parse_uuid(
    state: InvestigationState,
    field_name: str,
) -> tuple[UUID | None, InvestigationState | None]:
    """
    Parse a UUID from state and return either:

        (parsed_uuid, None)

    or:

        (None, error_state)
    """
    value = state.get(field_name)

    if not value:
        return None, _error_state(
            state,
            f"Missing required state field: {field_name}",
        )

    try:
        return UUID(value), None
    except (TypeError, ValueError):
        return None, _error_state(
            state,
            f"Invalid UUID for state field '{field_name}': {value}",
        )


def make_load_context_node(db: Session):
    """
    Resolve the alert, then get or create its investigation.

    This node also initializes the execution-specific state. It does not
    perform any LLM call.
    """

    def load_context(state: InvestigationState) -> InvestigationState:
        if state.get("error"):
            return state

        tenant_id, error = _parse_uuid(state, "tenant_id")
        if error is not None:
            return error

        alert_id, error = _parse_uuid(state, "alert_id")
        if error is not None:
            return error

        # The checks above guarantee these are not None.
        assert tenant_id is not None
        assert alert_id is not None

        alert = db.get(Alert, alert_id)

        if alert is None or alert.tenant_id != tenant_id:
            return _error_state(
                state,
                f"Alert {alert_id} not found for tenant",
                failed_step="load_context",
                code="alert_not_found",
            )

        investigations = InvestigationService(db)
        investigation = investigations.get_by_alert_id(
            tenant_id,
            alert_id,
        )

        if investigation is None:
            investigation = investigations.create(
                tenant_id,
                InvestigationCreate(
                    alert_id=alert_id,
                    title=f"Investigation: {alert.title}",
                    status="investigating",
                ),
            )

        # Preserve a caller-provided run_id if one exists. Otherwise create
        # one for this orchestration execution.
        run_id = state.get("run_id") or str(uuid4())

        return {
            **state,
            "investigation_id": str(investigation.id),
            "run_id": run_id,
            "plan": list(_DEFAULT_PLAN),
            "completed_steps": [],
            "findings": {},
            "error": None,
            "failed_step": None,
            "error_code": None,
        }

    load_context.__name__ = "load_context"
    return load_context


def make_planner_node(db: Session):
    """
    Deterministic planner: selects which steps run based on what the alert
    links to, and records what it skipped and why. No LLM call, no writes.
    """

    def planner_node(state: InvestigationState) -> InvestigationState:
        if state.get("error"):
            return state

        completed_steps = list(state.get("completed_steps", []))
        if "planner" in completed_steps:
            return state

        tenant_id, error = _parse_uuid(state, "tenant_id")
        if error is not None:
            return error

        alert_id, error = _parse_uuid(state, "alert_id")
        if error is not None:
            return error

        assert tenant_id is not None
        assert alert_id is not None

        try:
            alert = db.get(Alert, alert_id)

            if alert is None or alert.tenant_id != tenant_id:
                return _error_state(
                    state,
                    f"Planner: alert {alert_id} not found for tenant",
                    failed_step="planner",
                )

            event = None

            if alert.security_event_id is not None:
                event = db.get(SecurityEvent, alert.security_event_id)

                if event is not None and event.tenant_id != tenant_id:
                    event = None

            plan, skipped = decide_plan(
                has_rule=alert.detection_rule_id is not None,
                has_event=event is not None,
                event_asserts_technique=bool(
                    event is not None and event.mitre_technique_id
                ),
            )

        except Exception as exc:
            db.rollback()

            return _error_state(
                state,
                f"Planner failed for alert {alert_id}: {exc}",
                failed_step="planner",
            )

        findings = dict(state.get("findings", {}))

        findings["planner"] = {
            "status": "ok",
            "note": (
                f"plan: {', '.join(plan)}"
                + (f"; skipped: {', '.join(skipped)}" if skipped else "")
            ),
            "data": {
                "selected": plan,
                "skipped": skipped,
            },
        }

        completed_steps.append("planner")

        return {
            **state,
            "plan": plan,
            "findings": findings,
            "completed_steps": completed_steps,
            "error": None,
            "failed_step": None,
        }

    planner_node.__name__ = "planner"
    return planner_node


def _make_stub_agent_node(name: str):
    """
    Create a safe placeholder agent node.

    The node does not call an LLM. It only proves that:
    - state reaches the node,
    - the node produces a finding,
    - the completed-step list is updated,
    - the graph can continue to the next planned node.
    """

    def stub_node(state: InvestigationState) -> InvestigationState:
        if state.get("error"):
            return state

        completed_steps = list(state.get("completed_steps", []))

        # Prevent accidental duplicate execution if a graph edge is
        # misconfigured or a node is invoked more than once.
        if name in completed_steps:
            return state

        findings = dict(state.get("findings", {}))
        findings[name] = {
            "status": "stub",
            "note": f"{name} agent not yet implemented",
        }

        completed_steps.append(name)

        logger.info(
            "Stub agent '%s' completed for investigation %s",
            name,
            state.get("investigation_id"),
        )

        return {
            **state,
            "findings": findings,
            "completed_steps": completed_steps,
            "error": None,
            "failed_step": None,
        }

    stub_node.__name__ = f"{name}_agent_stub"
    return stub_node


def make_query_node(db: Session):
    """
    Read-only retrieval of alert, rule, matched-event and nearby-event
    context.

    No LLM call and no writes. Output is stored in findings["query"] and must
    be JSON-serializable because reporting persists it as Evidence metadata.
    """

    def query_node(state: InvestigationState) -> InvestigationState:
        if state.get("error"):
            return state

        completed_steps = list(state.get("completed_steps", []))

        # Prevent accidental duplicate execution.
        if "query" in completed_steps:
            return state

        tenant_id, error = _parse_uuid(state, "tenant_id")
        if error is not None:
            return error

        alert_id, error = _parse_uuid(state, "alert_id")
        if error is not None:
            return error

        # The checks above guarantee these are not None.
        assert tenant_id is not None
        assert alert_id is not None

        try:
            result = collect_alert_context(
                db,
                tenant_id=tenant_id,
                alert_id=alert_id,
            )
        except Exception as exc:
            db.rollback()

            return _error_state(
                state,
                f"Query agent failed for alert {alert_id}: {exc}",
                failed_step="query",
            )

        if result is None:
            return _error_state(
                state,
                f"Query agent: alert {alert_id} not found for tenant",
                failed_step="query",
            )

        findings = dict(state.get("findings", {}))
        findings["query"] = {
            "status": "ok",
            "note": result["note"],
            "data": result["data"],
        }

        completed_steps.append("query")

        logger.info(
            "Query agent completed: investigation_id=%s alert_id=%s",
            state.get("investigation_id"),
            alert_id,
        )

        return {
            **state,
            "findings": findings,
            "completed_steps": completed_steps,
            "error": None,
            "failed_step": None,
        }

    query_node.__name__ = "query"
    return query_node


def make_evidence_node(db: Session):
    """
    Capture point-in-time snapshots of the alert, its rule and its triggering
    event as Evidence records.

    Append-only and idempotent per (evidence_type, reference):
    re-running does not duplicate items.

    Concurrent runs are guarded by the partial unique index
    uq_evidence_tenant_investigation_type_reference. A run that loses the
    race gets an IntegrityError on insert; it rolls back, re-reads, and
    treats the item as already captured. add_evidence() commits per call, so
    the rollback only discards the single failed insert.

    No LLM call.
    """

    def evidence_node(state: InvestigationState) -> InvestigationState:
        if state.get("error"):
            return state

        completed_steps = list(state.get("completed_steps", []))

        # Prevent accidental duplicate execution.
        if "evidence" in completed_steps:
            return state

        tenant_id, error = _parse_uuid(state, "tenant_id")
        if error is not None:
            return error

        alert_id, error = _parse_uuid(state, "alert_id")
        if error is not None:
            return error

        investigation_id, error = _parse_uuid(
            state,
            "investigation_id",
        )
        if error is not None:
            return error

        # The checks above guarantee these are not None.
        assert tenant_id is not None
        assert alert_id is not None
        assert investigation_id is not None

        try:
            items = build_evidence_items(
                db,
                tenant_id=tenant_id,
                alert_id=alert_id,
            )
        except Exception as exc:
            db.rollback()

            return _error_state(
                state,
                f"Evidence agent failed to build items for alert "
                f"{alert_id}: {exc}",
                failed_step="evidence",
            )

        if items is None:
            return _error_state(
                state,
                f"Evidence agent: alert {alert_id} not found for tenant",
                failed_step="evidence",
            )

        investigations = InvestigationService(db)

        try:
            existing = investigations.evidence(
                tenant_id,
                investigation_id,
            )
        except Exception as exc:
            db.rollback()

            return _error_state(
                state,
                f"Evidence agent failed to read existing evidence: {exc}",
                failed_step="evidence",
            )

        existing_keys = {
            (e.evidence_type, e.reference)
            for e in existing
            if e.reference
        }

        created: list[str] = []
        skipped: list[str] = []
        failures: list[str] = []

        # Per-item handling: one bad item must not hide which others landed.
        for item in items:
            reference = item["reference"]

            if (item["evidence_type"], reference) in existing_keys:
                skipped.append(reference)
                continue

            try:
                record = investigations.add_evidence(
                    tenant_id,
                    investigation_id,
                    EvidenceCreate(**item),
                )
            except IntegrityError:
                # Lost a concurrent-run race on the unique index. The other
                # run's row should now be visible; confirm before treating
                # the item as already captured. If it is not there, this
                # was a different integrity failure and must fail the run.
                db.rollback()

                try:
                    refreshed = investigations.evidence(
                        tenant_id,
                        investigation_id,
                    )
                except Exception as read_exc:
                    db.rollback()
                    failures.append(
                        f"{reference}: re-read after integrity error "
                        f"failed ({type(read_exc).__name__})"
                    )
                    continue

                if any(
                    e.evidence_type == item["evidence_type"]
                    and e.reference == reference
                    for e in refreshed
                ):
                    skipped.append(reference)
                    existing_keys.add((item["evidence_type"], reference))
                else:
                    failures.append(
                        f"{reference}: integrity error but no existing row"
                    )

                continue
            except Exception as exc:
                db.rollback()
                failures.append(f"{reference}: {exc}")
                continue

            if record is None:
                db.rollback()
                failures.append(
                    f"{reference}: investigation not found",
                )
                continue

            created.append(reference)

        if failures:
            return _error_state(
                state,
                f"Evidence agent failed to write {len(failures)} item(s) "
                f"({len(created)} written before/around failure): "
                + "; ".join(failures),
                failed_step="evidence",
            )

        findings = dict(state.get("findings", {}))
        findings["evidence"] = {
            "status": "ok",
            "note": (
                f"{len(created)} evidence item(s) captured, "
                f"{len(skipped)} already present"
            ),
            "data": {
                "created": created,
                "skipped_existing": skipped,
            },
        }

        completed_steps.append("evidence")

        logger.info(
            "Evidence agent completed: investigation_id=%s "
            "created=%d skipped=%d",
            investigation_id,
            len(created),
            len(skipped),
        )

        return {
            **state,
            "findings": findings,
            "completed_steps": completed_steps,
            "error": None,
            "failed_step": None,
        }

    evidence_node.__name__ = "evidence"
    return evidence_node


def make_mitre_node(db: Session):
    """
    Read-only MITRE ATT&CK context from the rule's technique bridge.

    No LLM call and no writes are performed here. The collector is expected
    to return JSON-serializable context for the investigation finding.
    """

    def mitre_node(state: InvestigationState) -> InvestigationState:
        if state.get("error"):
            return state

        completed_steps = list(state.get("completed_steps", []))

        # Prevent accidental duplicate execution.
        if "mitre" in completed_steps:
            return state

        tenant_id, error = _parse_uuid(state, "tenant_id")
        if error is not None:
            return error

        alert_id, error = _parse_uuid(state, "alert_id")
        if error is not None:
            return error

        # The checks above guarantee these are not None.
        assert tenant_id is not None
        assert alert_id is not None

        try:
            result = collect_mitre_context(
                db,
                tenant_id=tenant_id,
                alert_id=alert_id,
            )
        except Exception as exc:
            db.rollback()

            return _error_state(
                state,
                f"MITRE agent failed for alert {alert_id}: {exc}",
                failed_step="mitre",
            )

        if result is None:
            return _error_state(
                state,
                f"MITRE agent: alert {alert_id} not found for tenant",
                failed_step="mitre",
            )

        findings = dict(state.get("findings", {}))
        findings["mitre"] = {
            "status": "ok",
            "note": result["note"],
            "data": result["data"],
        }

        completed_steps.append("mitre")

        logger.info(
            "MITRE agent completed: investigation_id=%s alert_id=%s",
            state.get("investigation_id"),
            alert_id,
        )

        return {
            **state,
            "findings": findings,
            "completed_steps": completed_steps,
            "error": None,
            "failed_step": None,
        }

    mitre_node.__name__ = "mitre"
    return mitre_node


def make_threat_intel_node(db: Session):
    """
    Read-only lookup of event values against the tenant's local Indicator
    table.

    No external feeds and no LLM call. Output must stay JSON-safe.
    """

    def threat_intel_node(state: InvestigationState) -> InvestigationState:
        if state.get("error"):
            return state

        completed_steps = list(state.get("completed_steps", []))

        # Prevent accidental duplicate execution.
        if "threat_intel" in completed_steps:
            return state

        tenant_id, error = _parse_uuid(state, "tenant_id")
        if error is not None:
            return error

        alert_id, error = _parse_uuid(state, "alert_id")
        if error is not None:
            return error

        # The checks above guarantee these are not None.
        assert tenant_id is not None
        assert alert_id is not None

        try:
            result = collect_threat_intel_context(
                db,
                tenant_id=tenant_id,
                alert_id=alert_id,
            )
        except Exception as exc:
            db.rollback()

            return _error_state(
                state,
                f"Threat intel agent failed for alert {alert_id}: {exc}",
                failed_step="threat_intel",
            )

        if result is None:
            return _error_state(
                state,
                f"Threat intel agent: alert {alert_id} not found for tenant",
                failed_step="threat_intel",
            )

        findings = dict(state.get("findings", {}))
        findings["threat_intel"] = {
            "status": "ok",
            "note": result["note"],
            "data": result["data"],
        }

        completed_steps.append("threat_intel")

        logger.info(
            "Threat intel agent completed: investigation_id=%s alert_id=%s",
            state.get("investigation_id"),
            alert_id,
        )

        return {
            **state,
            "findings": findings,
            "completed_steps": completed_steps,
            "error": None,
            "failed_step": None,
        }

    threat_intel_node.__name__ = "threat_intel"
    return threat_intel_node


def make_ot_context_node(db: Session):
    """
    Placeholder OT-context node.

    Blocked on site/zone modeling. The planner currently skips this step,
    so it only runs if OT_CONTEXT_AVAILABLE is flipped in planning.py.
    """
    del db
    return _make_stub_agent_node("ot_context")


def _finding_note(value: Any) -> str:
    """
    Convert arbitrary finding data into a safe summary string.

    Future agent implementations may return strings, dictionaries, lists, or
    other JSON-like data. Reporting must not assume every result is a dict.
    """
    if isinstance(value, Mapping):
        note = value.get("note")

        if note is not None:
            return str(note)

        return str(dict(value))

    if value is None:
        return "no finding recorded"

    return str(value)


def make_reporting_node(db: Session):
    """
    Persist one orchestration-run summary as Evidence and update the
    Investigation summary.

    This records the run_id in metadata so repeated runs can be distinguished.

    The report intentionally stores only compact status/note information from
    each finding rather than duplicating large query results or MITRE/threat
    intelligence context.

    Detailed point-in-time evidence is stored separately by the Evidence node.

    It does not by itself enforce idempotency. That requires a database-level
    run record or unique constraint.

    Both persistence operations are explicitly checked for None so a missing
    investigation cannot be reported as a successful orchestration run.
    """

    def reporting_node(state: InvestigationState) -> InvestigationState:
        if state.get("error"):
            return state

        tenant_id, error = _parse_uuid(state, "tenant_id")
        if error is not None:
            return error

        investigation_id, error = _parse_uuid(
            state,
            "investigation_id",
        )
        if error is not None:
            return error

        # The checks above guarantee these are not None.
        assert tenant_id is not None
        assert investigation_id is not None

        completed_steps = list(state.get("completed_steps", []))
        findings = dict(state.get("findings", {}))

        summary_lines = [
            f"- {step}: {_finding_note(findings.get(step))}"
            for step in completed_steps
        ]

        summary = "Automated investigation pass completed."

        if summary_lines:
            summary += "\n" + "\n".join(summary_lines)

        run_id = state.get("run_id")

        # Keep the agent_summary record compact. Detailed evidence belongs
        # in the dedicated Evidence records created by make_evidence_node().
        metadata: dict[str, Any] = {
            "run_id": run_id,
            "findings": {
                step: {
                    "status": (
                        finding.get("status")
                        if isinstance(finding, Mapping)
                        else None
                    ),
                    "note": _finding_note(finding),
                }
                for step, finding in findings.items()
            },
            "completed_steps": completed_steps,
            "plan": list(state.get("plan", [])),
        }

        investigations = InvestigationService(db)

        try:
            evidence = investigations.add_evidence(
                tenant_id,
                investigation_id,
                EvidenceCreate(
                    evidence_type="agent_summary",
                    title="Orchestrator run summary",
                    notes=summary,
                    metadata_json=metadata,
                ),
            )

            if evidence is None:
                db.rollback()

                return _error_state(
                    state,
                    f"Investigation {investigation_id} not found when "
                    f"adding evidence — reporting cannot claim success "
                    f"without a write actually landing.",
                    failed_step="reporting",
                )

            updated = investigations.update(
                tenant_id,
                investigation_id,
                InvestigationUpdate(summary=summary),
            )

            if updated is None:
                db.rollback()

                return _error_state(
                    state,
                    f"Investigation {investigation_id} not found when "
                    f"updating summary — evidence was written but the "
                    f"summary update silently did nothing.",
                    failed_step="reporting",
                )

        except Exception as exc:
            # Do not silently convert database failures into successful runs.
            # If the service does not already handle rollback, this rollback
            # protects the current session from remaining unusable.
            db.rollback()

            return _error_state(
                state,
                f"Failed to persist orchestrator report: {exc}",
                failed_step="reporting",
            )

        completed_steps.append("reporting")

        logger.info(
            "Investigation report persisted: investigation_id=%s run_id=%s",
            investigation_id,
            run_id,
        )

        return {
            **state,
            "completed_steps": completed_steps,
            "error": None,
            "failed_step": None,
        }

    reporting_node.__name__ = "reporting"
    return reporting_node


def make_error_node():
    """
    Terminal error node.

    It intentionally does not write an Evidence record because an error may
    occur before an investigation exists. The API layer should inspect the
    returned state and return an appropriate failure response.
    """

    def error_node(state: InvestigationState) -> InvestigationState:
        logger.error(
            "Investigation graph stopped with error: %s",
            state.get("error"),
        )
        return state

    error_node.__name__ = "orchestration_error"
    return error_node


def route_after_load_context(state: InvestigationState) -> str:
    """Route after context loading: to the planner, or to error."""
    if state.get("error"):
        return "error"

    return "planner"


def route_next_step(state: InvestigationState) -> str:
    """
    Select the next node from the plan.

    Returns:
        - "error" when the state contains an error
        - the next planned agent name
        - "reporting" when every planned step is complete
    """
    if state.get("error"):
        return "error"

    completed = set(state.get("completed_steps", []))

    for step in state.get("plan", []):
        if step not in completed:
            return step

    return "reporting"