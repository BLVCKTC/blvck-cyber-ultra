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
    },
    DetectionRuleType.BEHAVIORAL: {
        "baseline_window_days",
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


_SYNTAX_VALIDATORS = {
    DetectionRuleType.THRESHOLD: _validate_threshold_syntax,
    DetectionRuleType.SIGMA: _validate_sigma_syntax,
    DetectionRuleType.QUERY: _validate_query_syntax,
}
