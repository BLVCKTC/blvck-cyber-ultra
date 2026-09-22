from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from app.db.models.detection_rule import (
    DetectionRule,
    DetectionRuleStatus,
    DetectionRuleType,
)
from app.services.detection_rules.execution import (
    resolve_field,
    validate_filter_dsl,
)


class ValidationSeverity(StrEnum):
    ERROR = "error"      # blocks the transition
    WARNING = "warning"  # surfaced, non-blocking


@dataclass
class ValidationIssue:
    code: str
    message: str
    severity: ValidationSeverity
    field: str | None = None


@dataclass
class ValidationResult:
    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def errors(self) -> list[ValidationIssue]:
        return [
            issue
            for issue in self.issues
            if issue.severity == ValidationSeverity.ERROR
        ]

    @property
    def warnings(self) -> list[ValidationIssue]:
        return [
            issue
            for issue in self.issues
            if issue.severity == ValidationSeverity.WARNING
        ]

    @property
    def passed(self) -> bool:
        return not self.errors

    def add(
        self,
        code: str,
        message: str,
        severity: ValidationSeverity,
        field: str | None = None,
    ) -> None:
        self.issues.append(
            ValidationIssue(
                code=code,
                message=message,
                severity=severity,
                field=field,
            )
        )


_ALLOWED_TRANSITIONS: dict[
    DetectionRuleStatus,
    set[DetectionRuleStatus],
] = {
    DetectionRuleStatus.DRAFT: {
        DetectionRuleStatus.TESTING,
    },
    DetectionRuleStatus.TESTING: {
        DetectionRuleStatus.BACKTESTED,
        DetectionRuleStatus.DRAFT,
    },
    DetectionRuleStatus.BACKTESTED: {
        DetectionRuleStatus.CANARY,
        DetectionRuleStatus.TESTING,
    },
    DetectionRuleStatus.CANARY: {
        DetectionRuleStatus.APPROVED,
        DetectionRuleStatus.BACKTESTED,
    },
    DetectionRuleStatus.APPROVED: {
        DetectionRuleStatus.PRODUCTION,
    },
    DetectionRuleStatus.PRODUCTION: {
        DetectionRuleStatus.MONITORED,
    },
    DetectionRuleStatus.MONITORED: {
        DetectionRuleStatus.TUNED,
        DetectionRuleStatus.PRODUCTION,
    },
    DetectionRuleStatus.TUNED: {
        DetectionRuleStatus.PRODUCTION,
        DetectionRuleStatus.CANARY,
    },
}

_RETIREMENT_ELIGIBLE = set(DetectionRuleStatus) - {
    DetectionRuleStatus.RETIRED,
}

_MITRE_TECHNIQUE_RE = re.compile(
    r"^T\d{4}(\.\d{3})?$"
)
_MITRE_TACTIC_RE = re.compile(
    r"^TA\d{4}$"
)

_SUPPORTED_THRESHOLD_METRICS = {
    "event_count",
}

_SUPPORTED_BEHAVIORAL_METRICS = {
    "event_count",
}

_SUPPORTED_DEVIATION_METHODS = {
    "stddev_multiplier",
    "percent_increase",
    "absolute_diff",
}

_REQUIRED_CONFIG_KEYS: dict[
    DetectionRuleType,
    set[str],
] = {
    DetectionRuleType.THRESHOLD: {
        "metric",
        "operator",
        "threshold",
        "window_seconds",
    },
    DetectionRuleType.QUERY: {
        "data_source",
    },
    DetectionRuleType.CORRELATION: {
        "event_sequence",
        "correlation_window_seconds",
        "correlation_keys",
    },
    DetectionRuleType.BEHAVIORAL: {
        "baseline_window_days",
        "entity_field",
        "metric",
        "deviation_method",
        "deviation_threshold",
    },
    DetectionRuleType.SIGMA: set(),
}


class RuleValidator:
    """Pure validation logic for detection rules."""

    def validate_for_transition(
        self,
        rule: DetectionRule,
        target_status: DetectionRuleStatus,
    ) -> ValidationResult:
        result = ValidationResult()

        self._validate_transition_allowed(
            rule,
            target_status,
            result,
        )

        if target_status == DetectionRuleStatus.RETIRED:
            return result

        self._validate_structure(rule, result)
        self._validate_mitre_ids(rule, result)

        if target_status != DetectionRuleStatus.DRAFT:
            self._validate_syntax(rule, result)

        return result

    def _validate_transition_allowed(
        self,
        rule: DetectionRule,
        target_status: DetectionRuleStatus,
        result: ValidationResult,
    ) -> None:
        current = DetectionRuleStatus(rule.status)

        if target_status == DetectionRuleStatus.RETIRED:
            if current not in _RETIREMENT_ELIGIBLE:
                result.add(
                    "invalid_transition",
                    f"Cannot retire from '{current}'",
                    ValidationSeverity.ERROR,
                    "status",
                )
            return

        allowed = _ALLOWED_TRANSITIONS.get(current, set())

        if target_status not in allowed:
            result.add(
                "invalid_transition",
                (
                    f"'{current}' -> '{target_status}' "
                    "is not a permitted transition"
                ),
                ValidationSeverity.ERROR,
                "status",
            )

    def _validate_structure(
        self,
        rule: DetectionRule,
        result: ValidationResult,
    ) -> None:
        if not rule.name or not rule.name.strip():
            result.add(
                "missing_name",
                "Rule name is required",
                ValidationSeverity.ERROR,
                "name",
            )

        try:
            rule_type = DetectionRuleType(rule.rule_type)
        except ValueError:
            result.add(
                "unknown_rule_type",
                f"Unknown rule_type '{rule.rule_type}'",
                ValidationSeverity.ERROR,
                "rule_type",
            )
            return

        required_keys = _REQUIRED_CONFIG_KEYS.get(
            rule_type,
            set(),
        )
        config = rule.configuration or {}

        for key in sorted(required_keys - config.keys()):
            result.add(
                "missing_config_key",
                (
                    f"'{key}' is required in configuration "
                    f"for rule_type '{rule_type}'"
                ),
                ValidationSeverity.ERROR,
                f"configuration.{key}",
            )

        needs_query_text = rule_type in {
            DetectionRuleType.QUERY,
            DetectionRuleType.SIGMA,
        }

        if needs_query_text and not (
            rule.query and rule.query.strip()
        ):
            result.add(
                "missing_query",
                (
                    f"'query' text is required for "
                    f"rule_type '{rule_type}'"
                ),
                ValidationSeverity.ERROR,
                "query",
            )

    def _validate_mitre_ids(
        self,
        rule: DetectionRule,
        result: ValidationResult,
    ) -> None:
        for technique_id in rule.mitre_technique_ids or []:
            if not _MITRE_TECHNIQUE_RE.match(technique_id):
                result.add(
                    "bad_mitre_technique",
                    (
                        f"'{technique_id}' is not a valid "
                        "MITRE technique ID"
                    ),
                    ValidationSeverity.ERROR,
                    "mitre_technique_ids",
                )

        for tactic_id in rule.mitre_tactic_ids or []:
            if not _MITRE_TACTIC_RE.match(tactic_id):
                result.add(
                    "bad_mitre_tactic",
                    (
                        f"'{tactic_id}' is not a valid "
                        "MITRE tactic ID"
                    ),
                    ValidationSeverity.ERROR,
                    "mitre_tactic_ids",
                )

        if not rule.mitre_technique_ids:
            result.add(
                "no_mitre_mapping",
                "Rule has no MITRE technique mapping",
                ValidationSeverity.WARNING,
                "mitre_technique_ids",
            )

    def _validate_syntax(
        self,
        rule: DetectionRule,
        result: ValidationResult,
    ) -> None:
        try:
            rule_type = DetectionRuleType(rule.rule_type)
        except ValueError:
            return

        validator = _SYNTAX_VALIDATORS.get(rule_type)

        if validator is not None:
            validator(rule, result)


def _validate_threshold_syntax(
    rule: DetectionRule,
    result: ValidationResult,
) -> None:
    config = rule.configuration or {}

    metric = config.get("metric")

    if metric not in _SUPPORTED_THRESHOLD_METRICS:
        result.add(
            "bad_metric",
            (
                f"'{metric}' is not a supported threshold "
                "metric; expected 'event_count'"
            ),
            ValidationSeverity.ERROR,
            "configuration.metric",
        )

    operator = config.get("operator")

    if operator not in {
        "gt",
        "gte",
        "lt",
        "lte",
        "eq",
    }:
        result.add(
            "bad_operator",
            f"'{operator}' is not a supported operator",
            ValidationSeverity.ERROR,
            "configuration.operator",
        )

    window_seconds = config.get("window_seconds")

    if (
        not isinstance(window_seconds, int)
        or isinstance(window_seconds, bool)
        or window_seconds <= 0
    ):
        result.add(
            "bad_window",
            "window_seconds must be a positive integer",
            ValidationSeverity.ERROR,
            "configuration.window_seconds",
        )

    filter_node = config.get("filter")

    if filter_node is not None:
        errors: list[str] = []
        validate_filter_dsl(filter_node, errors)

        for message in errors:
            result.add(
                "bad_filter_clause",
                message,
                ValidationSeverity.ERROR,
                "configuration.filter",
            )

    group_by = config.get("group_by", [])

    if not isinstance(group_by, list):
        result.add(
            "bad_group_by",
            "group_by must be a list of field names",
            ValidationSeverity.ERROR,
            "configuration.group_by",
        )
        return

    for field_path in group_by:
        if not isinstance(field_path, str):
            result.add(
                "bad_group_by_field",
                "Each group_by field must be a string",
                ValidationSeverity.ERROR,
                "configuration.group_by",
            )
            continue

        try:
            resolve_field(field_path)
        except ValueError as exc:
            result.add(
                "bad_group_by_field",
                str(exc),
                ValidationSeverity.ERROR,
                "configuration.group_by",
            )


def _validate_sigma_syntax(
    rule: DetectionRule,
    result: ValidationResult,
) -> None:
    try:
        import yaml

        yaml.safe_load(rule.query or "")
    except Exception as exc:
        result.add(
            "bad_sigma_yaml",
            f"Sigma rule is not valid YAML: {exc}",
            ValidationSeverity.ERROR,
            "query",
        )


def _parse_query_dsl(
    query: str | None,
) -> Any | None:
    if not query or not query.strip():
        return None

    try:
        node = json.loads(query)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Query is not valid JSON: {exc.msg}"
        ) from exc

    if not isinstance(node, dict):
        raise ValueError(
            "Query DSL root must be a JSON object"
        )

    return node


def _validate_query_syntax(
    rule: DetectionRule,
    result: ValidationResult,
) -> None:
    try:
        node = _parse_query_dsl(rule.query)
    except ValueError as exc:
        result.add(
            "bad_query_dsl",
            str(exc),
            ValidationSeverity.ERROR,
            "query",
        )
        return

    if node is None:
        return

    errors: list[str] = []
    validate_filter_dsl(node, errors)

    for message in errors:
        result.add(
            "bad_filter_clause",
            message,
            ValidationSeverity.ERROR,
            "query",
        )


def _validate_correlation_syntax(
    rule: DetectionRule,
    result: ValidationResult,
) -> None:
    config = rule.configuration or {}

    window = config.get("correlation_window_seconds")

    if (
        not isinstance(window, int)
        or isinstance(window, bool)
        or window <= 0
    ):
        result.add(
            "bad_correlation_window",
            "correlation_window_seconds must be a positive integer",
            ValidationSeverity.ERROR,
            "configuration.correlation_window_seconds",
        )

    correlation_keys = config.get("correlation_keys")

    if not isinstance(correlation_keys, list) or not correlation_keys:
        result.add(
            "bad_correlation_keys",
            "correlation_keys must be a non-empty list of field names",
            ValidationSeverity.ERROR,
            "configuration.correlation_keys",
        )
    else:
        for field_path in correlation_keys:
            if not isinstance(field_path, str):
                result.add(
                    "bad_correlation_key_field",
                    "Each correlation_keys entry must be a string",
                    ValidationSeverity.ERROR,
                    "configuration.correlation_keys",
                )
                continue

            try:
                resolve_field(field_path)
            except ValueError as exc:
                result.add(
                    "bad_correlation_key_field",
                    str(exc),
                    ValidationSeverity.ERROR,
                    "configuration.correlation_keys",
                )

    event_sequence = config.get("event_sequence")

    if not isinstance(event_sequence, list) or len(event_sequence) < 2:
        result.add(
            "bad_event_sequence",
            "event_sequence must be a list of at least 2 steps",
            ValidationSeverity.ERROR,
            "configuration.event_sequence",
        )
        return

    seen_labels: set[str] = set()

    for idx, step in enumerate(event_sequence):
        step_field = f"configuration.event_sequence[{idx}]"

        if not isinstance(step, dict):
            result.add(
                "bad_event_sequence_step",
                f"Step {idx} must be an object",
                ValidationSeverity.ERROR,
                step_field,
            )
            continue

        label = step.get("label")

        if not isinstance(label, str) or not label.strip():
            result.add(
                "bad_event_sequence_step_label",
                f"Step {idx} requires a non-empty 'label'",
                ValidationSeverity.ERROR,
                f"{step_field}.label",
            )
        elif label in seen_labels:
            result.add(
                "duplicate_event_sequence_label",
                f"Step label '{label}' is used more than once",
                ValidationSeverity.ERROR,
                f"{step_field}.label",
            )
        else:
            seen_labels.add(label)

        step_filter = step.get("filter")

        if step_filter is None:
            result.add(
                "missing_event_sequence_filter",
                f"Step {idx} requires a 'filter'",
                ValidationSeverity.ERROR,
                f"{step_field}.filter",
            )
        else:
            errors: list[str] = []
            validate_filter_dsl(step_filter, errors)

            for message in errors:
                result.add(
                    "bad_filter_clause",
                    f"Step {idx}: {message}",
                    ValidationSeverity.ERROR,
                    f"{step_field}.filter",
                )

        min_count = step.get("min_count", 1)

        if (
            not isinstance(min_count, int)
            or isinstance(min_count, bool)
            or min_count < 1
        ):
            result.add(
                "bad_min_count",
                f"Step {idx} min_count must be a positive integer",
                ValidationSeverity.ERROR,
                f"{step_field}.min_count",
            )

        max_gap_seconds = step.get("max_gap_seconds")

        if max_gap_seconds is not None and (
            not isinstance(max_gap_seconds, int)
            or isinstance(max_gap_seconds, bool)
            or max_gap_seconds <= 0
        ):
            result.add(
                "bad_max_gap_seconds",
                f"Step {idx} max_gap_seconds must be a positive integer if set",
                ValidationSeverity.ERROR,
                f"{step_field}.max_gap_seconds",
            )


def _validate_behavioral_syntax(
    rule: DetectionRule,
    result: ValidationResult,
) -> None:
    config = rule.configuration or {}

    baseline_window_days = config.get("baseline_window_days")

    if (
        not isinstance(baseline_window_days, int)
        or isinstance(baseline_window_days, bool)
        or not (1 <= baseline_window_days <= 365)
    ):
        result.add(
            "bad_baseline_window",
            "baseline_window_days must be an integer between 1 and 365",
            ValidationSeverity.ERROR,
            "configuration.baseline_window_days",
        )

    entity_field = config.get("entity_field")

    if not isinstance(entity_field, str) or not entity_field.strip():
        result.add(
            "bad_entity_field",
            "entity_field is required and must be a string",
            ValidationSeverity.ERROR,
            "configuration.entity_field",
        )
    else:
        try:
            resolve_field(entity_field)
        except ValueError as exc:
            result.add(
                "bad_entity_field",
                str(exc),
                ValidationSeverity.ERROR,
                "configuration.entity_field",
            )

    metric = config.get("metric")

    if metric not in _SUPPORTED_BEHAVIORAL_METRICS:
        result.add(
            "bad_metric",
            (
                f"'{metric}' is not a supported behavioral metric; "
                f"expected one of {sorted(_SUPPORTED_BEHAVIORAL_METRICS)}"
            ),
            ValidationSeverity.ERROR,
            "configuration.metric",
        )

    deviation_method = config.get("deviation_method")

    if deviation_method not in _SUPPORTED_DEVIATION_METHODS:
        result.add(
            "bad_deviation_method",
            (
                f"'{deviation_method}' is not a supported deviation_method; "
                f"expected one of {sorted(_SUPPORTED_DEVIATION_METHODS)}"
            ),
            ValidationSeverity.ERROR,
            "configuration.deviation_method",
        )

    deviation_threshold = config.get("deviation_threshold")

    if not isinstance(deviation_threshold, (int, float)) or isinstance(
        deviation_threshold, bool
    ):
        result.add(
            "bad_deviation_threshold",
            "deviation_threshold must be a number",
            ValidationSeverity.ERROR,
            "configuration.deviation_threshold",
        )
    elif (
        deviation_method == "percent_increase"
        and not (0 < deviation_threshold <= 1)
    ):
        result.add(
            "bad_deviation_threshold_range",
            (
                "deviation_threshold for percent_increase must be between "
                "0 and 1 (e.g. 0.5 = 50% increase)"
            ),
            ValidationSeverity.ERROR,
            "configuration.deviation_threshold",
        )
    elif (
        deviation_method in {"stddev_multiplier", "absolute_diff"}
        and deviation_threshold <= 0
    ):
        result.add(
            "bad_deviation_threshold_range",
            f"deviation_threshold for {deviation_method} must be greater than 0",
            ValidationSeverity.ERROR,
            "configuration.deviation_threshold",
        )

    filter_node = config.get("filter")

    if filter_node is not None:
        errors: list[str] = []
        validate_filter_dsl(filter_node, errors)

        for message in errors:
            result.add(
                "bad_filter_clause",
                message,
                ValidationSeverity.ERROR,
                "configuration.filter",
            )


_SYNTAX_VALIDATORS = {
    DetectionRuleType.THRESHOLD: _validate_threshold_syntax,
    DetectionRuleType.SIGMA: _validate_sigma_syntax,
    DetectionRuleType.QUERY: _validate_query_syntax,
    DetectionRuleType.CORRELATION: _validate_correlation_syntax,
    DetectionRuleType.BEHAVIORAL: _validate_behavioral_syntax,
}