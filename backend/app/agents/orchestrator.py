from __future__ import annotations

from sqlalchemy.orm import Session
from langgraph.graph import END, START, StateGraph

from app.agents.agent_nodes import (
    make_error_node,
    make_evidence_node,
    make_load_context_node,
    make_mitre_node,
    make_ot_context_node,
    make_query_node,
    make_reporting_node,
    make_threat_intel_node,
    route_after_load_context,
    route_next_step,
)
from app.agents.state import InvestigationState


_AGENT_NODE_NAMES = (
    "query",
    "evidence",
    "mitre",
    "threat_intel",
    "ot_context",
)


def build_investigation_graph(db: Session):
    """
    Build and compile the investigation orchestration graph.

    The graph shape is:

        START
          |
        load_context
          |
          +--> error --------> END
          |
          +--> planned agent
                    |
                    +--> next planned agent
                    |
                    +--> reporting
                                  |
                                  +--> END

    The plan is currently fixed by load_context, but routing already uses the
    plan. That means replacing the hardcoded planner later does not require
    changing the graph wiring.
    """

    graph = StateGraph(InvestigationState)

    graph.add_node(
        "load_context",
        make_load_context_node(db),
    )

    graph.add_node(
        "query",
        make_query_node(db),
    )

    graph.add_node(
        "evidence",
        make_evidence_node(db),
    )

    graph.add_node(
        "mitre",
        make_mitre_node(db),
    )

    graph.add_node(
        "threat_intel",
        make_threat_intel_node(db),
    )

    graph.add_node(
        "ot_context",
        make_ot_context_node(db),
    )

    graph.add_node(
        "reporting",
        make_reporting_node(db),
    )

    graph.add_node(
        "error",
        make_error_node(),
    )

    graph.add_edge(START, "load_context")

    # Routing after context loading.
    graph.add_conditional_edges(
        "load_context",
        route_after_load_context,
        {
            "query": "query",
            "evidence": "evidence",
            "mitre": "mitre",
            "threat_intel": "threat_intel",
            "ot_context": "ot_context",
            "reporting": "reporting",
            "error": "error",
        },
    )

    # Every agent routes to the next unfinished planned step.
    route_targets = {
        "query": "query",
        "evidence": "evidence",
        "mitre": "mitre",
        "threat_intel": "threat_intel",
        "ot_context": "ot_context",
        "reporting": "reporting",
        "error": "error",
    }

    for node_name in _AGENT_NODE_NAMES:
        graph.add_conditional_edges(
            node_name,
            route_next_step,
            route_targets,
        )

    graph.add_edge("reporting", END)
    graph.add_edge("error", END)

    return graph.compile()
