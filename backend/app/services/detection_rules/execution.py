from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session

from app.db.models.detection_rule import (
    DetectionRule,
    DetectionRuleStatus,
    DetectionRuleType,
)
from app.db.models.security_event import SecurityEvent


class RuleFilterError(ValueError):
    """Malformed filter clause or unsupported field/operator."""


_COMPARISON_OPS = {
    "eq",
    "neq",
    "gt",
    "gte",
    "lt",
    "lte",
    "in",
    "not_in",
    "contains",
}

_SUPPORTED_THRESHOLD_METRICS = {
    "event_count",
}

# Columns that may be filtered or grouped directly.
# Everything else must use a permitted JSONB path.
_DIRECT_FIELDS = {
    "event_type",
    "event_category",
    "severity",
    "status",
    "source",
    "source_type",
    "action",
    "risk_score",
    "source_ip",
    "destination_ip",
    "hostname",
    "user_identifier",
    "process_name",
    "mitre_technique_id",
    "mitre_tactic",
}


def resolve_field(field_path: str):
    """Convert a DSL field path into a SQLAlchemy expression."""
    if not isinstance(field_path, str) or not field_path.strip():
        raise RuleFilterError(
            f"Field path must be a non-empty string: {field_path!r}"
        )

    if field_path in _DIRECT_FIELDS:
        try:
            return getattr(SecurityEvent, field_path)
        except AttributeError as exc:
            raise RuleFilterError(
                f"SecurityEvent does not expose field '{field_path}'"
            ) from exc

    if field_path.startswith(
        ("normalized_data.", "event_metadata.")
    ):
        column_name, _, json_path = field_path.partition(".")

        if not json_path:
            raise RuleFilterError(
                f"JSON field path is incomplete: '{field_path}'"
            )

        try:
            column = getattr(SecurityEvent, column_name)
        except AttributeError as exc:
            raise RuleFilterError(
                f"SecurityEvent does not expose field '{column_name}'"
            ) from exc

        keys = json_path.split(".")

        if any(not key for key in keys):
            raise RuleFilterError(
                f"JSON field path contains an empty key: '{field_path}'"
            )

        expression = column

        for key in keys[:-1]:
            expression = expression[key]

        return expression[keys[-1]].astext

    raise RuleFilterError(
        f"Unknown or disallowed field '{field_path}'"
    )


def _validate_operator_value(
    operator: str,
    value: Any,
) -> None:
    if operator in {"in", "not_in"}:
        if not isinstance(value, list) or not value:
            raise RuleFilterError(
                f"'{operator}' requires a non-empty list value"
            )

    if operator == "contains" and not isinstance(value, str):
        raise RuleFilterError(
            "'contains' requires a string value"
        )


def build_clause(node: Any):
    """Recursively compile a filter DSL node into a SQL expression."""
    if not isinstance(node, dict):
        raise RuleFilterError(
            f"Filter node must be an object: {node!r}"
        )

    logical_keys = [
        key for key in ("and", "or")
        if key in node
    ]

    if len(logical_keys) > 1:
        raise RuleFilterError(
            f"Filter node cannot contain both 'and' and 'or': {node}"
        )

    if logical_keys:
        logical_key = logical_keys[0]
        children = node[logical_key]

        if not isinstance(children, list) or not children:
            raise RuleFilterError(
                f"'{logical_key}' must be a non-empty list: {node}"
            )

        clauses = [
            build_clause(child)
            for child in children
        ]

        if logical_key == "and":
            return and_(*clauses)

        return or_(*clauses)

    field_path = node.get("field")
    operator = node.get("op")

    if not isinstance(field_path, str) or not field_path:
        raise RuleFilterError(
            f"Filter field must be a non-empty string: {node}"
        )

    if operator not in _COMPARISON_OPS:
        raise RuleFilterError(
            f"Unsupported filter operator '{operator}': {node}"
        )

    value = node.get("value")
    _validate_operator_value(operator, value)

    expression = resolve_field(field_path)

    if operator == "eq":
        return expression == value

    if operator == "neq":
        return expression != value

    if operator == "gt":
        return expression > value

    if operator == "gte":
        return expression >= value

    if operator == "lt":
        return expression < value

    if operator == "lte":
        return expression <= value

    if operator == "in":
        return expression.in_(value)

    if operator == "not_in":
        return expression.notin_(value)

    if operator == "contains":
        return expression.contains(value)

    raise RuleFilterError(
        f"Unsupported operator '{operator}'"
    )


def validate_filter_dsl(
    node: Any,
    errors: list[str],
) -> None:
    """Validate filter DSL structure without database access."""
    if not isinstance(node, dict):
        errors.append(
            f"Filter node must be an object: {node!r}"
        )
        return

    logical_keys = [
        key for key in ("and", "or")
        if key in node
    ]

    if len(logical_keys) > 1:
        errors.append(
            f"Filter node cannot contain both 'and' and 'or': {node}"
        )
        return

    if logical_keys:
        logical_key = logical_keys[0]
        children = node[logical_key]

        if not isinstance(children, list) or not children:
            errors.append(
                f"'{logical_key}' must be a non-empty list: {node}"
            )
            return

        for child in children:
            validate_filter_dsl(child, errors)

        return

    field_path = node.get("field")
    operator = node.get("op")

    if not isinstance(field_path, str) or not field_path:
        errors.append(
            f"Filter field must be a non-empty string: {node}"
        )
        return

    if operator not in _COMPARISON_OPS:
        errors.append(
            f"Unsupported filter operator '{operator}': {node}"
        )
        return

    value = node.get("value")

    try:
        _validate_operator_value(operator, value)
        resolve_field(field_path)
    except RuleFilterError as exc:
        errors.append(str(exc))


@dataclass
class MatchCandidate:
    window_start: datetime
    window_end: datetime
    group_key: dict[str, Any]
    metric_value: float
    event_ids: list[UUID]


class RuleExecutor:
    """Execute detection rules against SecurityEvent rows.

    This executor returns candidates only. Persistence of DetectionMatch,
    Alert, and related provenance records belongs to the caller.

    The executor supports:
    - threshold rules using event_count
    - query rules using JSON filter DSL
    - historical backtesting and replay
    - future live execution through production-only execution
    """

    def __init__(
        self,
        session: Session,
        tenant_id: UUID,
    ):
        self.session = session
        self.tenant_id = tenant_id

    def run(
        self,
        rule: DetectionRule,
        window_start: datetime,
        window_end: datetime,
    ) -> list[MatchCandidate]:
        """Run a rule for backtesting or replay."""
        if window_start >= window_end:
            raise ValueError(
                "window_start must be earlier than window_end"
            )

        rule_type = DetectionRuleType(rule.rule_type)

        if rule_type == DetectionRuleType.THRESHOLD:
            return self._run_threshold(
                rule,
                window_start,
                window_end,
            )

        if rule_type == DetectionRuleType.QUERY:
            return self._run_query(
                rule,
                window_start,
                window_end,
            )

        raise NotImplementedError(
            f"Execution for '{rule_type}' is not implemented"
        )

    def run_production_rule(
        self,
        rule: DetectionRule,
        window_start: datetime,
        window_end: datetime,
    ) -> list[MatchCandidate]:
        """Run only an enabled production rule.

        The live P4 detection engine should use this method rather than
        passing arbitrary rule records to run().
        """
        try:
            status = DetectionRuleStatus(rule.status)
        except ValueError as exc:
            raise ValueError(
                f"Unknown detection rule status '{rule.status}'"
            ) from exc

        if status != DetectionRuleStatus.PRODUCTION:
            raise ValueError(
                "Only production rules can be executed live"
            )

        if not getattr(rule, "enabled", False):
            raise ValueError(
                "Disabled rules cannot be executed live"
            )

        return self.run(
            rule,
            window_start,
            window_end,
        )

    def _filter_node(
        self,
        rule: DetectionRule,
    ) -> dict[str, Any] | None:
        """Return the filter node according to rule type."""
        rule_type = DetectionRuleType(rule.rule_type)

        if rule_type == DetectionRuleType.THRESHOLD:
            node = (rule.configuration or {}).get("filter")

            if node is not None and not isinstance(node, dict):
                raise RuleFilterError(
                    "Threshold configuration.filter must be an object"
                )

            return node

        if rule_type == DetectionRuleType.QUERY:
            if not rule.query or not rule.query.strip():
                return None

            try:
                node = json.loads(rule.query)
            except json.JSONDecodeError as exc:
                raise RuleFilterError(
                    f"Query is not valid JSON: {exc.msg}"
                ) from exc

            if not isinstance(node, dict):
                raise RuleFilterError(
                    "Query DSL root must be a JSON object"
                )

            return node

        return None

    def _base_filters(
        self,
        rule: DetectionRule,
        window_start: datetime,
        window_end: datetime,
    ):
        filters = [
            SecurityEvent.tenant_id == self.tenant_id,
            SecurityEvent.event_time >= window_start,
            SecurityEvent.event_time < window_end,
        ]

        filter_node = self._filter_node(rule)

        if filter_node is not None:
            filters.append(build_clause(filter_node))

        return filters

    def _run_query(
        self,
        rule: DetectionRule,
        window_start: datetime,
        window_end: datetime,
    ) -> list[MatchCandidate]:
        """Run a query rule.

        Query rules currently return one ungrouped candidate containing all
        matching events in the requested execution window.
        """
        statement = select(SecurityEvent.id).where(
            *self._base_filters(
                rule,
                window_start,
                window_end,
            )
        )

        event_ids = list(self.session.scalars(statement))

        if not event_ids:
            return []

        return [
            MatchCandidate(
                window_start=window_start,
                window_end=window_end,
                group_key={},
                metric_value=len(event_ids),
                event_ids=event_ids,
            )
        ]

    def _run_threshold(
        self,
        rule: DetectionRule,
        window_start: datetime,
        window_end: datetime,
    ) -> list[MatchCandidate]:
        config = rule.configuration or {}

        metric = config.get("metric")
        threshold = config["threshold"]
        operator = config["operator"]
        window_seconds = config["window_seconds"]
        group_by = config.get("group_by", [])

        if metric not in _SUPPORTED_THRESHOLD_METRICS:
            raise ValueError(
                f"Unsupported threshold metric '{metric}'"
            )

        if not isinstance(window_seconds, int) or isinstance(
            window_seconds,
            bool,
        ):
            raise ValueError(
                "window_seconds must be an integer"
            )

        if window_seconds <= 0:
            raise ValueError(
                "window_seconds must be greater than zero"
            )

        if not isinstance(group_by, list):
            raise ValueError(
                "group_by must be a list"
            )

        group_exprs = [
            resolve_field(field_path)
            for field_path in group_by
        ]

        candidates: list[MatchCandidate] = []
        current_start = window_start
        step = timedelta(seconds=window_seconds)

        while current_start < window_end:
            current_end = min(
                current_start + step,
                window_end,
            )

            filters = self._base_filters(
                rule,
                current_start,
                current_end,
            )

            statement = select(
                *group_exprs,
                func.count(SecurityEvent.id),
                func.array_agg(SecurityEvent.id),
            ).where(*filters)

            if group_exprs:
                statement = statement.group_by(*group_exprs)

            for row in self.session.execute(statement):
                *group_values, count, event_ids = row

                if not self._compare(
                    value=count,
                    operator=operator,
                    threshold=threshold,
                ):
                    continue

                candidates.append(
                    MatchCandidate(
                        window_start=current_start,
                        window_end=current_end,
                        group_key=dict(
                            zip(group_by, group_values)
                        ),
                        metric_value=float(count),
                        event_ids=list(event_ids or []),
                    )
                )

            current_start = current_end

        return candidates

    @staticmethod
    def _compare(
        value: float,
        operator: str,
        threshold: float,
    ) -> bool:
        comparisons = {
            "gt": value > threshold,
            "gte": value >= threshold,
            "lt": value < threshold,
            "lte": value <= threshold,
            "eq": value == threshold,
        }

        try:
            return comparisons[operator]
        except KeyError as exc:
            raise ValueError(
                f"Unsupported threshold operator '{operator}'"
            ) from exc
