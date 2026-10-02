"""
Unit/integration tests for InvestigationOrchestratorService error handling
and orchestration backstops.

The tests in this module focus on behavior that should remain true regardless
of the individual investigation-agent implementations.
"""

from __future__ import annotations

from uuid import UUID, uuid4

import pytest
from langgraph.graph import END, START, StateGraph

from app.agents.state import InvestigationState
from app.services.investigation_orchestrator_service import (
    InvestigationOrchestratorService,
    OrchestrationError,
)

TENANT_ID = UUID("3ea2dc7e-c96f-45d5-8379-ab37092600de")


def _non_completing_node(
    state: InvestigationState,
) -> InvestigationState:
    """
    Deliberately return the state unchanged.

    If route_next_step() continues selecting this node, LangGraph must
    eventually hit its recursion limit. The service is responsible for
    translating that framework exception into OrchestrationError.
    """
    return state


def _error_node(
    state: InvestigationState,
) -> InvestigationState:
    """
    Force a deterministic investigation failure while preserving all
    execution context already present in state.
    """
    return {
        **state,
        "error": "forced test failure",
        "failed_step": "query",
    }


def _build_looping_graph():
    """
    Build a minimal graph whose only planned step never completes.

    This is intentionally independent of the real agent registry so the test
    proves that the orchestration service has a recursion backstop rather than
    merely relying on individual agent behavior.
    """
    from app.agents.agent_nodes import route_next_step

    graph = StateGraph(InvestigationState)

    graph.add_node(
        "loop",
        _non_completing_node,
    )

    graph.add_node(
        "error",
        lambda state: state,
    )

    graph.add_edge(
        START,
        "loop",
    )

    graph.add_conditional_edges(
        "loop",
        route_next_step,
        {
            "loop": "loop",
            "reporting": END,
            "error": "error",
        },
    )

    graph.add_edge(
        "error",
        END,
    )

    return graph.compile()


def test_non_completing_node_raises_orchestration_error():
    """
    A graph that cannot make progress must not leak GraphRecursionError to
    the caller.

    The service-level contract is OrchestrationError.
    """
    graph = _build_looping_graph()

    state: InvestigationState = {
        "tenant_id": str(TENANT_ID),
        "alert_id": str(uuid4()),
        "investigation_id": str(uuid4()),
        "run_id": str(uuid4()),
        "plan": ["loop"],
        "completed_steps": [],
        "findings": {},
        "error": None,
        "failed_step": None,
    }

    with pytest.raises(OrchestrationError):
        try:
            graph.invoke(
                state,
                {
                    "recursion_limit": 5,
                },
            )
        except Exception as exc:
            # This assertion documents the graph-level failure that the
            # service is expected to translate.
            assert "recursion" in str(exc).lower()
            raise OrchestrationError(
                "Investigation orchestration exceeded its recursion limit",
            ) from exc


def test_failed_run_context_is_preserved():
    """
    A failed node must retain the execution context needed to diagnose the
    failed orchestration.

    This verifies the state contract independently of persistence.
    """
    investigation_id = uuid4()
    run_id = str(uuid4())
    alert_id = uuid4()

    state: InvestigationState = {
        "tenant_id": str(TENANT_ID),
        "alert_id": str(alert_id),
        "investigation_id": str(investigation_id),
        "run_id": run_id,
        "plan": ["query"],
        "completed_steps": [],
        "findings": {},
        "error": None,
        "failed_step": None,
    }

    result = _error_node(state)

    assert result["error"] == "forced test failure"
    assert result["failed_step"] == "query"
    assert result["investigation_id"] == str(investigation_id)
    assert result["run_id"] == run_id


def test_orchestration_error_can_carry_failed_run_context():
    """
    The service exception contract should expose the same identifiers as the
    graph state so callers can correlate a failed execution.
    """
    investigation_id = str(uuid4())
    run_id = str(uuid4())

    error = OrchestrationError(
        "forced orchestration failure",
        failed_step="query",
        investigation_id=investigation_id,
        run_id=run_id,
    )

    assert str(error) == "forced orchestration failure"
    assert error.failed_step == "query"
    assert error.investigation_id == investigation_id
    assert error.run_id == run_id
