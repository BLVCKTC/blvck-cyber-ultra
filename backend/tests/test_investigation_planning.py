from __future__ import annotations

import pytest

from app.agents import planning
from app.agents.planning import decide_plan, validate_plan
from app.agents.state import _DEFAULT_PLAN


def test_validate_plan_rejects_unknown_step():
    with pytest.raises(ValueError, match="unknown"):
        validate_plan(
            [
                "query",
                "evidence",
                "not_a_real_agent",
            ]
        )


def test_validate_plan_requires_query_or_evidence():
    with pytest.raises(
        ValueError,
        match="query.*evidence|evidence.*query",
    ):
        validate_plan(
            [
                "mitre",
                "threat_intel",
            ]
        )


@pytest.mark.parametrize("missing", ["query", "evidence"])
def test_validate_plan_rejects_each_core_step_missing_individually(
    missing: str,
):
    # Each core step is required on its own: a plan that has one core step
    # but not the other must still be rejected.
    plan = [
        step
        for step in ("query", "evidence", "mitre", "threat_intel")
        if step != missing
    ]

    with pytest.raises(ValueError, match=missing):
        validate_plan(plan)


def test_validate_plan_accepts_default_plan_round_trip():
    # The shared default plan must itself pass the validator unchanged,
    # otherwise the orchestrator's build-time registry check and the
    # planner's validation would disagree about what a legal plan is.
    assert validate_plan(list(_DEFAULT_PLAN)) == list(_DEFAULT_PLAN)


def test_validate_plan_dedupes_steps():
    result = validate_plan(
        [
            "query",
            "evidence",
            "query",
            "mitre",
            "evidence",
            "mitre",
        ]
    )

    assert result == [
        "query",
        "evidence",
        "mitre",
    ]


def test_validate_plan_reorders_to_canonical_order():
    result = validate_plan(
        [
            "threat_intel",
            "mitre",
            "evidence",
            "query",
        ]
    )

    expected = [
        step
        for step in _DEFAULT_PLAN
        if step in {
            "query",
            "evidence",
            "mitre",
            "threat_intel",
        }
    ]

    assert result == expected


@pytest.mark.parametrize(
    (
        "has_rule",
        "has_event",
        "expected_plan",
        "expected_skipped",
    ),
    [
        (
            True,
            True,
            [
                "query",
                "evidence",
                "mitre",
                "threat_intel",
            ],
            {
                "ot_context": "site/zone model not implemented",
            },
        ),
        (
            True,
            False,
            [
                "query",
                "evidence",
                "mitre",
            ],
            {
                "threat_intel": "no triggering event to extract values from",
                "ot_context": "site/zone model not implemented",
            },
        ),
        (
            False,
            True,
            [
                "query",
                "evidence",
                "threat_intel",
            ],
            {
                "mitre": "no rule linked and event asserts no technique",
                "ot_context": "site/zone model not implemented",
            },
        ),
        (
            False,
            False,
            [
                "query",
                "evidence",
            ],
            {
                "mitre": "no rule linked and event asserts no technique",
                "threat_intel": "no triggering event to extract values from",
                "ot_context": "site/zone model not implemented",
            },
        ),
    ],
)
def test_decide_plan_rule_event_combinations(
    has_rule: bool,
    has_event: bool,
    expected_plan: list[str],
    expected_skipped: dict[str, str],
):
    plan, skipped = decide_plan(
        has_rule=has_rule,
        has_event=has_event,
        event_asserts_technique=False,
    )

    assert plan == expected_plan
    assert skipped == expected_skipped


def test_decide_plan_event_asserting_technique_selects_mitre():
    plan, skipped = decide_plan(
        has_rule=False,
        has_event=True,
        event_asserts_technique=True,
    )

    assert "mitre" in plan
    assert "mitre" not in skipped


def test_decide_plan_without_technique_still_uses_rule_for_mitre():
    plan, skipped = decide_plan(
        has_rule=True,
        has_event=True,
        event_asserts_technique=False,
    )

    assert "mitre" in plan
    assert "mitre" not in skipped


def test_decide_plan_includes_ot_context_when_available(monkeypatch):
    # The day site/zone modeling lands and the flag flips, the planner must
    # select ot_context, stop reporting it as skipped, and still produce a
    # plan in canonical order that passes the validator.
    monkeypatch.setattr(planning, "OT_CONTEXT_AVAILABLE", True)

    plan, skipped = decide_plan(
        has_rule=True,
        has_event=True,
        event_asserts_technique=False,
    )

    assert "ot_context" in plan
    assert "ot_context" not in skipped
    assert plan == validate_plan(plan)
    assert plan == [step for step in _DEFAULT_PLAN if step in set(plan)]