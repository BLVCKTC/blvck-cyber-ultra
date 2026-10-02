from __future__ import annotations

from sqlalchemy.orm import Session
from langgraph.graph import END, START, StateGraph

from app.agents.agent_nodes import (
    make_error_node,
    make_evidence_node,
    make_load_context_node,
    make_mitre_node,
    make_ot_context_node,
    make_planner_node,
    make_query_node,
    make_reporting_node,
    make_threat_intel_node,
    route_after_load_context,
    route_next_step,
)
from app.agents.state import InvestigationState, _DEFAULT_PLAN


_AGENT_FACTORIES = {
    "query": make_query_node,
    "evidence": make_evidence_node,
    "mitre": make_mitre_node,
    "threat_intel": make_threat_intel_node,
    "ot_context": make_ot_context_node,
}


def build_investigation_graph(db: Session):
    """
    Build and compile the investigation orchestration graph.

    The graph shape is:

        START
          |
        load_context
          |
          +--> planner
                  |
                  +--> selected agent
                  |        |
                  |        +--> next selected agent
                  |        |
                  |        +--> reporting
                  |
                  +--> reporting
                  |
                  +--> error
                           |
                           +--> END

    load_context initializes the investigation execution state and provides
    the default plan as a fallback.

    The deterministic planner then narrows that plan based on the alert's
    linked records. Subsequent routing uses the planner-selected state["plan"].

    Agent node registration is sourced from _AGENT_FACTORIES so the registry
    remains the single wiring point for investigation agents.
    """

    graph = StateGraph(InvestigationState)

    graph.add_node(
        "load_context",
        make_load_context_node(db),
    )

    for name, factory in _AGENT_FACTORIES.items():
        graph.add_node(
            name,
            factory(db),
        )

    graph.add_node(
        "planner",
        make_planner_node(db),
    )

    graph.add_node(
        "reporting",
        make_reporting_node(db),
    )

    graph.add_node(
        "error",
        make_error_node(),
    )

    route_targets = {
        **{name: name for name in _AGENT_FACTORIES},
        "reporting": "reporting",
        "error": "error",
    }

    graph.add_edge(
        START,
        "load_context",
    )

    graph.add_conditional_edges(
        "load_context",
        route_after_load_context,
        {
            "planner": "planner",
            "error": "error",
        },
    )

    graph.add_conditional_edges(
        "planner",
        route_next_step,
        route_targets,
    )

    for name in _AGENT_FACTORIES:
        graph.add_conditional_edges(
            name,
            route_next_step,
            route_targets,
        )

    graph.add_edge(
        "reporting",
        END,
    )

    graph.add_edge(
        "error",
        END,
    )

    return graph.compile()
