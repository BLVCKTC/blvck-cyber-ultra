from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from app.agents.state import InvestigationState
from app.db.models.alert import Alert
from app.schemas.investigation import (
    EvidenceCreate,
    InvestigationCreate,
    InvestigationUpdate,
)
from app.services.investigation_service import InvestigationService

logger = logging.getLogger(__name__)


# Fixed order for the skeleton.
# These are still stub agents, but the graph will now actually use this plan
# to determine which node runs next.
_DEFAULT_PLAN: tuple[str, ...] = (
    "query",
    "evidence",
    "mitre",
    "threat_intel",
    "ot_context",
)


def _error_state(
    state: InvestigationState,
    message: str,
    *,
    failed_step: str | None = None,
) -> InvestigationState:
    """
    Return a consistent error update without destroying existing state.
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
        }

    load_context.__name__ = "load_context"
    return load_context


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
    Placeholder query node.

    The db argument is accepted intentionally so the future implementation can
    query alert and investigation-related records without changing graph
    construction code.
    """
    del db
    return _make_stub_agent_node("query")


def make_evidence_node(db: Session):
    """
    Placeholder evidence node.
    """
    del db
    return _make_stub_agent_node("evidence")


def make_mitre_node(db: Session):
    """
    Placeholder MITRE node.
    """
    del db
    return _make_stub_agent_node("mitre")


def make_threat_intel_node(db: Session):
    """
    Placeholder threat-intelligence node.
    """
    del db
    return _make_stub_agent_node("threat_intel")


def make_ot_context_node(db: Session):
    """
    Placeholder OT-context node.
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
    It does not by itself enforce idempotency. That requires a database-level
    run record or unique constraint.
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

        metadata: dict[str, Any] = {
            "run_id": run_id,
            "findings": findings,
            "completed_steps": completed_steps,
            "plan": list(state.get("plan", [])),
        }

        investigations = InvestigationService(db)

        try:
            investigations.add_evidence(
                tenant_id,
                investigation_id,
                EvidenceCreate(
                    evidence_type="agent_summary",
                    title="Orchestrator run summary",
                    notes=summary,
                    metadata_json=metadata,
                ),
            )

            investigations.update(
                tenant_id,
                investigation_id,
                InvestigationUpdate(summary=summary),
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
    """
    Route after the context-loading node.
    """
    if state.get("error"):
        return "error"

    return route_next_step(state)


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
