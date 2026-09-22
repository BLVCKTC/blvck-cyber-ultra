"""
Tests for detection-rule content validation: RuleValidator's per-type
structure/syntax checks (threshold, sigma, query, correlation,
behavioral), as enforced by DetectionRuleService.transition().

Follows the same fake/monkeypatch convention as
test_detection_rule_governance.py — no live DB, DetectionRuleRepository
replaced with an in-memory fake.

Every rule here is created with created_by_id=None so the
separation-of-duties checks in transition() never fire — these tests
are isolated to content/structure validation, not governance. Every
transition targets "testing" (draft -> testing), which is the first
transition where _validate_syntax runs, so it exercises the full
validate_for_transition() pipeline: transition-allowed, structure,
MITRE, and per-type syntax.

Field shapes are now confirmed against app/services/detection_rules/
execution.py: resolve_field()'s _DIRECT_FIELDS includes "event_type"
and "user_identifier" (NOT "user_id"), and validate_filter_dsl()/
build_clause() read a filter node's operator key as "op", not
"operator". Two real bugs from the previous pass are fixed here:
_PLACEHOLDER_FILTER used "operator" (silently invalid on every test
that used it), and every correlation/behavioral filler value used
"user_id" (silently invalid) instead of "user_identifier" — both were
masked by membership-style assertions rather than exact-set ones,
so no test was failing despite exercising broken fixtures. Green-path
tests for CORRELATION, BEHAVIORAL, QUERY, and THRESHOLD's group_by/
filter path are now included since the valid-input shape is confirmed.
"""

from __future__ import annotations

from uuid import uuid4

import pytest

import app.services.detection_rule_service as detection_rule_service_module
from app.db.models.detection_rule import DetectionRule, DetectionRuleStatus
from app.services.detection_rule_service import (
    DetectionRuleService,
    RuleValidationError,
)


# ======================================================================
# FAKES
# ======================================================================

class FakeDetectionRuleRepository:
    """In-memory stand-in for DetectionRuleRepository.

    Mirrors only the surface DetectionRuleService.transition() uses:
    get() and update(). update() applies the dict onto the in-memory
    rule and returns it, same shape as the real repo's ORM update.
    """

    def __init__(self, db):
        self._db = db  # unused; matches real repo's __init__(db) signature

    def bind(self, rule: DetectionRule):
        self._rule = rule
        return self

    def get(self, *, tenant_id, rule_id):
        if self._rule.tenant_id != tenant_id or self._rule.id != rule_id:
            return None
        return self._rule

    def update(self, *, tenant_id, rule_id, data):
        for key, value in data.items():
            setattr(self._rule, key, value)
        return self._rule


@pytest.fixture
def fake_repo(monkeypatch):
    """Patch DetectionRuleRepository at the point DetectionRuleService
    imports it, and return the (unbound) fake class instance-to-be so
    each test can bind its own rule.
    """
    holder: dict[str, FakeDetectionRuleRepository] = {}

    def _factory(db):
        repo = FakeDetectionRuleRepository(db)
        holder["repo"] = repo
        return repo

    monkeypatch.setattr(
        detection_rule_service_module,
        "DetectionRuleRepository",
        _factory,
    )
    return holder


TENANT_ID = uuid4()


def make_rule(
    *,
    rule_type: str,
    configuration: dict,
    query: str | None = None,
    mitre_technique_ids: list[str] | None = None,
) -> DetectionRule:
    """A DRAFT rule with no recorded author, so transitioning it to
    TESTING never triggers separation-of-duties checks — isolates
    these tests to content/structure validation only.

    mitre_technique_ids defaults to a valid mapping so MITRE checks
    don't add unrelated issues to tests targeting other validators;
    override explicitly for the MITRE-specific tests.
    """
    return DetectionRule(
        id=uuid4(),
        tenant_id=TENANT_ID,
        name="Test rule",
        rule_type=rule_type,
        severity="medium",
        status=DetectionRuleStatus.DRAFT.value,
        version=1,
        enabled=True,
        query=query,
        configuration=configuration,
        tags=[],
        mitre_technique_ids=(
            mitre_technique_ids
            if mitre_technique_ids is not None
            else ["T1110"]
        ),
        mitre_tactic_ids=[],
        author=None,
        source=None,
        created_by_id=None,
        reviewed_by_id=None,
        reviewed_at=None,
    )


def build_service(fake_repo, rule: DetectionRule) -> DetectionRuleService:
    svc = DetectionRuleService(db=object())
    fake_repo["repo"].bind(rule)
    return svc


def transition_to_testing(fake_repo, rule: DetectionRule):
    """Shared entry point: every test here transitions draft -> testing,
    the first transition where syntax validation runs.
    """
    svc = build_service(fake_repo, rule)
    return svc.transition(
        tenant_id=TENANT_ID,
        rule_id=rule.id,
        target_status="testing",
        actor_id=uuid4(),
    )


def issue_codes(exc_info) -> set[str]:
    return {issue.code for issue in exc_info.value.issues}


# A confirmed-valid filter node: "event_type" is in execution.py's
# _DIRECT_FIELDS, "eq" needs no special value validation, and "op" is
# the actual key validate_filter_dsl()/build_clause() read (NOT
# "operator" — that was the bug in the previous pass).
_VALID_FILTER = {
    "field": "event_type",
    "op": "eq",
    "value": "login_failed",
}


# ======================================================================
# THRESHOLD
# ======================================================================

def test_threshold_bad_metric_rejected(fake_repo):
    rule = make_rule(
        rule_type="threshold",
        configuration={
            "metric": "cpu_usage",  # not in _SUPPORTED_THRESHOLD_METRICS
            "operator": "gt",
            "threshold": 5,
            "window_seconds": 300,
        },
    )

    with pytest.raises(RuleValidationError) as exc_info:
        transition_to_testing(fake_repo, rule)

    assert "bad_metric" in issue_codes(exc_info)


def test_threshold_bad_operator_rejected(fake_repo):
    rule = make_rule(
        rule_type="threshold",
        configuration={
            "metric": "event_count",
            "operator": "between",  # not a supported operator
            "threshold": 5,
            "window_seconds": 300,
        },
    )

    with pytest.raises(RuleValidationError) as exc_info:
        transition_to_testing(fake_repo, rule)

    assert "bad_operator" in issue_codes(exc_info)


@pytest.mark.parametrize(
    "window_seconds",
    [0, -300, "300", True, 4.5],
)
def test_threshold_bad_window_seconds_rejected(fake_repo, window_seconds):
    rule = make_rule(
        rule_type="threshold",
        configuration={
            "metric": "event_count",
            "operator": "gt",
            "threshold": 5,
            "window_seconds": window_seconds,
        },
    )

    with pytest.raises(RuleValidationError) as exc_info:
        transition_to_testing(fake_repo, rule)

    assert "bad_window" in issue_codes(exc_info)


def test_threshold_group_by_wrong_type_rejected(fake_repo):
    rule = make_rule(
        rule_type="threshold",
        configuration={
            "metric": "event_count",
            "operator": "gt",
            "threshold": 5,
            "window_seconds": 300,
            "group_by": "user_id",  # must be a list, not a bare string
        },
    )

    with pytest.raises(RuleValidationError) as exc_info:
        transition_to_testing(fake_repo, rule)

    assert "bad_group_by" in issue_codes(exc_info)


def test_threshold_missing_config_keys_rejected(fake_repo):
    rule = make_rule(
        rule_type="threshold",
        configuration={},  # nothing at all
    )

    with pytest.raises(RuleValidationError) as exc_info:
        transition_to_testing(fake_repo, rule)

    codes = issue_codes(exc_info)
    assert "missing_config_key" in codes


def test_threshold_minimal_valid_config_passes(fake_repo):
    rule = make_rule(
        rule_type="threshold",
        configuration={
            "metric": "event_count",
            "operator": "gt",
            "threshold": 5,
            "window_seconds": 300,
        },
    )

    result = transition_to_testing(fake_repo, rule)

    assert result.rule.status == DetectionRuleStatus.TESTING.value
    assert result.warnings == []


def test_threshold_with_filter_and_group_by_passes(fake_repo):
    """Closes the previously-flagged gap: a real filter clause and a
    real group_by field, both resolving successfully via
    resolve_field()/validate_filter_dsl() against confirmed-valid
    input shapes.
    """
    rule = make_rule(
        rule_type="threshold",
        configuration={
            "metric": "event_count",
            "operator": "gt",
            "threshold": 5,
            "window_seconds": 300,
            "filter": _VALID_FILTER,
            "group_by": ["event_type"],
        },
    )

    result = transition_to_testing(fake_repo, rule)

    assert result.rule.status == DetectionRuleStatus.TESTING.value
    assert result.warnings == []


# ======================================================================
# SIGMA
# ======================================================================

def test_sigma_invalid_yaml_rejected(fake_repo):
    rule = make_rule(
        rule_type="sigma",
        configuration={},
        query="detection: [unclosed",
    )

    with pytest.raises(RuleValidationError) as exc_info:
        transition_to_testing(fake_repo, rule)

    assert "bad_sigma_yaml" in issue_codes(exc_info)


def test_sigma_valid_yaml_passes(fake_repo):
    rule = make_rule(
        rule_type="sigma",
        configuration={},
        query="title: Test\ndetection:\n  condition: selection\n",
    )

    result = transition_to_testing(fake_repo, rule)

    assert result.rule.status == DetectionRuleStatus.TESTING.value


# ======================================================================
# QUERY
# ======================================================================

def test_query_missing_query_text_rejected(fake_repo):
    rule = make_rule(
        rule_type="query",
        configuration={"data_source": "security_events"},
        query=None,
    )

    with pytest.raises(RuleValidationError) as exc_info:
        transition_to_testing(fake_repo, rule)

    assert "missing_query" in issue_codes(exc_info)


def test_query_invalid_json_rejected(fake_repo):
    rule = make_rule(
        rule_type="query",
        configuration={"data_source": "security_events"},
        query="{not valid json",
    )

    with pytest.raises(RuleValidationError) as exc_info:
        transition_to_testing(fake_repo, rule)

    assert "bad_query_dsl" in issue_codes(exc_info)


def test_query_non_dict_root_rejected(fake_repo):
    rule = make_rule(
        rule_type="query",
        configuration={"data_source": "security_events"},
        query="[1, 2, 3]",
    )

    with pytest.raises(RuleValidationError) as exc_info:
        transition_to_testing(fake_repo, rule)

    assert "bad_query_dsl" in issue_codes(exc_info)


def test_query_valid_filter_dsl_passes(fake_repo):
    """Green path: query text is a JSON object matching the filter DSL
    directly (per _validate_query_syntax's use of validate_filter_dsl
    on the parsed root), using the confirmed-valid field/op shape.
    """
    rule = make_rule(
        rule_type="query",
        configuration={"data_source": "security_events"},
        query='{"field": "event_type", "op": "eq", "value": "login_failed"}',
    )

    result = transition_to_testing(fake_repo, rule)

    assert result.rule.status == DetectionRuleStatus.TESTING.value
    assert result.warnings == []


# ======================================================================
# CORRELATION
# ======================================================================

def test_correlation_missing_required_keys_rejected(fake_repo):
    rule = make_rule(
        rule_type="correlation",
        configuration={},
    )

    with pytest.raises(RuleValidationError) as exc_info:
        transition_to_testing(fake_repo, rule)

    codes = issue_codes(exc_info)
    assert "missing_config_key" in codes


def test_correlation_window_must_be_positive_int(fake_repo):
    rule = make_rule(
        rule_type="correlation",
        configuration={
            "correlation_window_seconds": -1,
            "correlation_keys": ["user_identifier"],
            "event_sequence": [
                {"label": "step_a", "filter": _VALID_FILTER},
                {"label": "step_b", "filter": _VALID_FILTER},
            ],
        },
    )

    with pytest.raises(RuleValidationError) as exc_info:
        transition_to_testing(fake_repo, rule)

    assert issue_codes(exc_info) == {"bad_correlation_window"}


def test_correlation_keys_must_be_non_empty_list(fake_repo):
    rule = make_rule(
        rule_type="correlation",
        configuration={
            "correlation_window_seconds": 600,
            "correlation_keys": [],
            "event_sequence": [
                {"label": "step_a", "filter": _VALID_FILTER},
                {"label": "step_b", "filter": _VALID_FILTER},
            ],
        },
    )

    with pytest.raises(RuleValidationError) as exc_info:
        transition_to_testing(fake_repo, rule)

    assert issue_codes(exc_info) == {"bad_correlation_keys"}


def test_correlation_event_sequence_requires_at_least_two_steps(fake_repo):
    rule = make_rule(
        rule_type="correlation",
        configuration={
            "correlation_window_seconds": 600,
            "correlation_keys": ["user_identifier"],
            "event_sequence": [
                {"label": "only_step", "filter": _VALID_FILTER},
            ],
        },
    )

    with pytest.raises(RuleValidationError) as exc_info:
        transition_to_testing(fake_repo, rule)

    assert issue_codes(exc_info) == {"bad_event_sequence"}


def test_correlation_duplicate_step_labels_rejected(fake_repo):
    rule = make_rule(
        rule_type="correlation",
        configuration={
            "correlation_window_seconds": 600,
            "correlation_keys": ["user_identifier"],
            "event_sequence": [
                {"label": "same", "filter": _VALID_FILTER},
                {"label": "same", "filter": _VALID_FILTER},
            ],
        },
    )

    with pytest.raises(RuleValidationError) as exc_info:
        transition_to_testing(fake_repo, rule)

    assert issue_codes(exc_info) == {"duplicate_event_sequence_label"}


def test_correlation_step_missing_filter_rejected(fake_repo):
    rule = make_rule(
        rule_type="correlation",
        configuration={
            "correlation_window_seconds": 600,
            "correlation_keys": ["user_identifier"],
            "event_sequence": [
                {"label": "step_a"},  # no filter key at all
                {"label": "step_b", "filter": _VALID_FILTER},
            ],
        },
    )

    with pytest.raises(RuleValidationError) as exc_info:
        transition_to_testing(fake_repo, rule)

    assert issue_codes(exc_info) == {"missing_event_sequence_filter"}


def test_correlation_step_bad_min_count_rejected(fake_repo):
    rule = make_rule(
        rule_type="correlation",
        configuration={
            "correlation_window_seconds": 600,
            "correlation_keys": ["user_identifier"],
            "event_sequence": [
                {
                    "label": "step_a",
                    "filter": _VALID_FILTER,
                    "min_count": 0,
                },
                {"label": "step_b", "filter": _VALID_FILTER},
            ],
        },
    )

    with pytest.raises(RuleValidationError) as exc_info:
        transition_to_testing(fake_repo, rule)

    assert issue_codes(exc_info) == {"bad_min_count"}


def test_correlation_step_bad_max_gap_seconds_rejected(fake_repo):
    rule = make_rule(
        rule_type="correlation",
        configuration={
            "correlation_window_seconds": 600,
            "correlation_keys": ["user_identifier"],
            "event_sequence": [
                {"label": "step_a", "filter": _VALID_FILTER},
                {
                    "label": "step_b",
                    "filter": _VALID_FILTER,
                    "max_gap_seconds": -30,
                },
            ],
        },
    )

    with pytest.raises(RuleValidationError) as exc_info:
        transition_to_testing(fake_repo, rule)

    assert issue_codes(exc_info) == {"bad_max_gap_seconds"}


def test_correlation_fully_valid_rule_passes(fake_repo):
    """Genuine green path — every field resolves and validates
    successfully. This was not possible in the previous pass without
    a confirmed-valid filter/field shape.
    """
    rule = make_rule(
        rule_type="correlation",
        configuration={
            "correlation_window_seconds": 600,
            "correlation_keys": ["user_identifier"],
            "event_sequence": [
                {
                    "label": "initial_login_failure",
                    "filter": {
                        "field": "event_type",
                        "op": "eq",
                        "value": "login_failed",
                    },
                },
                {
                    "label": "privilege_escalation",
                    "filter": {
                        "field": "event_type",
                        "op": "eq",
                        "value": "privilege_escalation",
                    },
                    "min_count": 1,
                    "max_gap_seconds": 300,
                },
            ],
        },
    )

    result = transition_to_testing(fake_repo, rule)

    assert result.rule.status == DetectionRuleStatus.TESTING.value
    assert result.warnings == []


# ======================================================================
# BEHAVIORAL
# ======================================================================

@pytest.mark.parametrize("baseline_window_days", [0, -5, 400, "30", True])
def test_behavioral_baseline_window_out_of_range_rejected(
    fake_repo, baseline_window_days
):
    rule = make_rule(
        rule_type="behavioral",
        configuration={
            "baseline_window_days": baseline_window_days,
            "entity_field": "user_identifier",
            "metric": "event_count",
            "deviation_method": "stddev_multiplier",
            "deviation_threshold": 3.0,
        },
    )

    with pytest.raises(RuleValidationError) as exc_info:
        transition_to_testing(fake_repo, rule)

    assert "bad_baseline_window" in issue_codes(exc_info)


def test_behavioral_missing_entity_field_rejected(fake_repo):
    rule = make_rule(
        rule_type="behavioral",
        configuration={
            "baseline_window_days": 30,
            "entity_field": "",
            "metric": "event_count",
            "deviation_method": "stddev_multiplier",
            "deviation_threshold": 3.0,
        },
    )

    with pytest.raises(RuleValidationError) as exc_info:
        transition_to_testing(fake_repo, rule)

    assert issue_codes(exc_info) == {"bad_entity_field"}


def test_behavioral_unresolvable_entity_field_rejected(fake_repo):
    """A non-empty but unresolvable field path — distinct from the
    empty-string case above. Confirms resolve_field() is actually
    reached and its rejection surfaces as bad_entity_field, using a
    field genuinely absent from execution.py's _DIRECT_FIELDS.
    """
    rule = make_rule(
        rule_type="behavioral",
        configuration={
            "baseline_window_days": 30,
            "entity_field": "not_a_real_field",
            "metric": "event_count",
            "deviation_method": "stddev_multiplier",
            "deviation_threshold": 3.0,
        },
    )

    with pytest.raises(RuleValidationError) as exc_info:
        transition_to_testing(fake_repo, rule)

    assert issue_codes(exc_info) == {"bad_entity_field"}


def test_behavioral_bad_metric_rejected(fake_repo):
    rule = make_rule(
        rule_type="behavioral",
        configuration={
            "baseline_window_days": 30,
            "entity_field": "user_identifier",
            "metric": "cpu_usage",
            "deviation_method": "stddev_multiplier",
            "deviation_threshold": 3.0,
        },
    )

    with pytest.raises(RuleValidationError) as exc_info:
        transition_to_testing(fake_repo, rule)

    assert issue_codes(exc_info) == {"bad_metric"}


def test_behavioral_bad_deviation_method_rejected(fake_repo):
    rule = make_rule(
        rule_type="behavioral",
        configuration={
            "baseline_window_days": 30,
            "entity_field": "user_identifier",
            "metric": "event_count",
            "deviation_method": "z_score",  # not supported
            "deviation_threshold": 3.0,
        },
    )

    with pytest.raises(RuleValidationError) as exc_info:
        transition_to_testing(fake_repo, rule)

    assert issue_codes(exc_info) == {"bad_deviation_method"}


def test_behavioral_deviation_threshold_must_be_number(fake_repo):
    rule = make_rule(
        rule_type="behavioral",
        configuration={
            "baseline_window_days": 30,
            "entity_field": "user_identifier",
            "metric": "event_count",
            "deviation_method": "stddev_multiplier",
            "deviation_threshold": "high",
        },
    )

    with pytest.raises(RuleValidationError) as exc_info:
        transition_to_testing(fake_repo, rule)

    assert issue_codes(exc_info) == {"bad_deviation_threshold"}


def test_behavioral_percent_increase_threshold_must_be_fraction(fake_repo):
    rule = make_rule(
        rule_type="behavioral",
        configuration={
            "baseline_window_days": 30,
            "entity_field": "user_identifier",
            "metric": "event_count",
            "deviation_method": "percent_increase",
            "deviation_threshold": 5.0,  # must be in (0, 1], this isn't
        },
    )

    with pytest.raises(RuleValidationError) as exc_info:
        transition_to_testing(fake_repo, rule)

    assert issue_codes(exc_info) == {"bad_deviation_threshold_range"}


def test_behavioral_stddev_multiplier_threshold_must_be_positive(fake_repo):
    rule = make_rule(
        rule_type="behavioral",
        configuration={
            "baseline_window_days": 30,
            "entity_field": "user_identifier",
            "metric": "event_count",
            "deviation_method": "stddev_multiplier",
            "deviation_threshold": 0,
        },
    )

    with pytest.raises(RuleValidationError) as exc_info:
        transition_to_testing(fake_repo, rule)

    assert issue_codes(exc_info) == {"bad_deviation_threshold_range"}


def test_behavioral_stddev_multiplier_fully_valid_rule_passes(fake_repo):
    """Genuine green path for the stddev_multiplier deviation method."""
    rule = make_rule(
        rule_type="behavioral",
        configuration={
            "baseline_window_days": 30,
            "entity_field": "user_identifier",
            "metric": "event_count",
            "deviation_method": "stddev_multiplier",
            "deviation_threshold": 3.0,
        },
    )

    result = transition_to_testing(fake_repo, rule)

    assert result.rule.status == DetectionRuleStatus.TESTING.value
    assert result.warnings == []


def test_behavioral_percent_increase_fully_valid_rule_passes(fake_repo):
    """Genuine green path for percent_increase — confirms the (0, 1]
    range check does NOT misfire on a genuinely valid fraction.
    """
    rule = make_rule(
        rule_type="behavioral",
        configuration={
            "baseline_window_days": 14,
            "entity_field": "user_identifier",
            "metric": "event_count",
            "deviation_method": "percent_increase",
            "deviation_threshold": 0.5,
        },
    )

    result = transition_to_testing(fake_repo, rule)

    assert result.rule.status == DetectionRuleStatus.TESTING.value
    assert result.warnings == []


def test_behavioral_with_filter_passes(fake_repo):
    """Behavioral rules also accept an optional top-level filter,
    validated the same way as threshold's."""
    rule = make_rule(
        rule_type="behavioral",
        configuration={
            "baseline_window_days": 30,
            "entity_field": "user_identifier",
            "metric": "event_count",
            "deviation_method": "stddev_multiplier",
            "deviation_threshold": 3.0,
            "filter": _VALID_FILTER,
        },
    )

    result = transition_to_testing(fake_repo, rule)

    assert result.rule.status == DetectionRuleStatus.TESTING.value
    assert result.warnings == []


# ======================================================================
# MITRE mapping — WARNING vs ERROR distinction, cross-cutting
# ======================================================================

def test_missing_mitre_mapping_is_a_warning_not_a_blocking_error(fake_repo):
    """no_mitre_mapping is WARNING-severity — it must not block the
    transition, and it must show up in RuleTransitionResult.warnings.
    """
    rule = make_rule(
        rule_type="threshold",
        configuration={
            "metric": "event_count",
            "operator": "gt",
            "threshold": 5,
            "window_seconds": 300,
        },
        mitre_technique_ids=[],
    )

    result = transition_to_testing(fake_repo, rule)

    assert result.rule.status == DetectionRuleStatus.TESTING.value
    warning_codes = {w.code for w in result.warnings}
    assert "no_mitre_mapping" in warning_codes


def test_invalid_mitre_technique_id_format_rejected(fake_repo):
    rule = make_rule(
        rule_type="threshold",
        configuration={
            "metric": "event_count",
            "operator": "gt",
            "threshold": 5,
            "window_seconds": 300,
        },
        mitre_technique_ids=["not-a-technique-id"],
    )

    with pytest.raises(RuleValidationError) as exc_info:
        transition_to_testing(fake_repo, rule)

    assert "bad_mitre_technique" in issue_codes(exc_info)