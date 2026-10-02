from __future__ import annotations

from collections.abc import Iterable

from app.agents.state import _DEFAULT_PLAN

# Steps every plan must contain. Planning may skip context, never the core
# retrieval and evidence capture.
REQUIRED_STEPS: tuple[str, ...] = ("query", "evidence")

# Flip to True when site/zone modeling exists and ot_context is real.
OT_CONTEXT_AVAILABLE = False


def validate_plan(proposed: Iterable[str]) -> list[str]:
    """
    Validate a proposed plan against the shared step list.

    Rejects unknown steps and plans missing required steps; drops
    duplicates; always returns steps in canonical _DEFAULT_PLAN order.
    This is the gate any future LLM planner's output must pass through:
    the model proposes, this function decides what can run.
    """
    proposed = list(proposed)

    unknown = sorted(set(proposed) - set(_DEFAULT_PLAN))
    if unknown:
        raise ValueError(f"Plan contains unknown step(s): {unknown}")

    wanted = set(proposed)
    missing = [s for s in REQUIRED_STEPS if s not in wanted]
    if missing:
        raise ValueError(f"Plan is missing required step(s): {missing}")

    return [s for s in _DEFAULT_PLAN if s in wanted]


def decide_plan(
    *,
    has_rule: bool,
    has_event: bool,
    event_asserts_technique: bool,
) -> tuple[list[str], dict[str, str]]:
    """
    Pick steps from what the alert actually links to.
    Returns (validated_plan, {skipped_step: reason}).
    """
    skipped: dict[str, str] = {}
    steps: list[str] = ["query", "evidence"]

    if has_rule or event_asserts_technique:
        steps.append("mitre")
    else:
        skipped["mitre"] = "no rule linked and event asserts no technique"

    if has_event:
        steps.append("threat_intel")
    else:
        skipped["threat_intel"] = "no triggering event to extract values from"

    if OT_CONTEXT_AVAILABLE:
        steps.append("ot_context")
    else:
        skipped["ot_context"] = "site/zone model not implemented"

    return validate_plan(steps), skipped