from __future__ import annotations

from typing import Any, TypedDict


class InvestigationState(TypedDict, total=False):
    """
    Serializable state passed between LangGraph nodes.

    The SQLAlchemy session is deliberately not stored here. It is injected
    into node closures when the graph is built and must not become part of
    checkpointed graph state.
    """

    tenant_id: str
    alert_id: str
    investigation_id: str

    # Unique identifier for this orchestration execution.
    # This distinguishes repeated executions, although true idempotency still
    # requires persistence-level enforcement.
    run_id: str

    # The ordered steps selected for this run.
    plan: list[str]

    # Nodes append their names here after successful completion.
    completed_steps: list[str]

    # Node name -> node result.
    findings: dict[str, Any]

    # Set when the graph encounters a recoverable failure.
    error: str | None

    # Name of the node that failed, when applicable.
    failed_step: str | None
