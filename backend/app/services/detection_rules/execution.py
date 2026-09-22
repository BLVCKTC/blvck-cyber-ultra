from __future__ import annotations

import json
import statistics
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy import and_, func, not_, or_, select
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
    "startswith",
    "endswith",
    "regex",
}

_SUPPORTED_THRESHOLD_METRICS = {
    "event_count",
}

_SUPPORTED_BEHAVIORAL_METRICS = {
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

    if operator in {"contains", "startswith", "endswith", "regex"} and not isinstance(
        value, str
    ):
        raise RuleFilterError(
            f"'{operator}' requires a string value"
        )


def build_clause(node: Any):
    """Recursively compile a filter DSL node into a SQL expression."""
    if not isinstance(node, dict):
        raise RuleFilterError(
            f"Filter node must be an object: {node!r}"
        )

    logical_keys = [
        key for key in ("and", "or", "not")
        if key in node
    ]

    if len(logical_keys) > 1 or (
        logical_keys and len(node) != 1
    ):
        raise RuleFilterError(
            f"Filter node must contain exactly one of 'and'/'or'/'not' "
            f"and nothing else: {node}"
        )

    if logical_keys and logical_keys[0] == "not":
        return not_(build_clause(node["not"]))

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

    if operator == "startswith":
        return expression.startswith(value)

    if operator == "endswith":
        return expression.endswith(value)

    if operator == "regex":
        # Postgres POSIX case-sensitive regex match. No case-insensitive
        # variant exposed yet — add "iregex" -> ~* if that's needed later.
        return expression.op("~")(value)

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
        key for key in ("and", "or", "not")
        if key in node
    ]

    if len(logical_keys) > 1 or (
        logical_keys and len(node) != 1
    ):
        errors.append(
            "Filter node must contain exactly one of 'and'/'or'/'not' "
            f"and nothing else: {node}"
        )
        return

    if logical_keys and logical_keys[0] == "not":
        validate_filter_dsl(node["not"], errors)
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

    Supports: threshold, query, correlation, behavioral, and a scoped
    subset of sigma (flat selections + and/or/not conditions only, no
    parentheses/aggregations/timeframes, and no Sigma-field-taxonomy
    mapping — sigma rules must be written against this system's own
    field names, not public Sigma rule field names like Image/EventID).
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
            return self._run_threshold(rule, window_start, window_end)

        if rule_type == DetectionRuleType.QUERY:
            return self._run_query(rule, window_start, window_end)

        if rule_type == DetectionRuleType.CORRELATION:
            return self._run_correlation(rule, window_start, window_end)

        if rule_type == DetectionRuleType.BEHAVIORAL:
            return self._run_behavioral(rule, window_start, window_end)

        if rule_type == DetectionRuleType.SIGMA:
            return self._run_sigma(rule, window_start, window_end)

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

        return self.run(rule, window_start, window_end)

    def _filter_node(
        self,
        rule: DetectionRule,
    ) -> dict[str, Any] | None:
        """Return the filter node according to rule type."""
        rule_type = DetectionRuleType(rule.rule_type)

        if rule_type in {
            DetectionRuleType.THRESHOLD,
            DetectionRuleType.BEHAVIORAL,
        }:
            node = (rule.configuration or {}).get("filter")

            if node is not None and not isinstance(node, dict):
                raise RuleFilterError(
                    f"{rule_type} configuration.filter must be an object"
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
            *self._base_filters(rule, window_start, window_end)
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
            raise ValueError(f"Unsupported threshold metric '{metric}'")

        if not isinstance(window_seconds, int) or isinstance(window_seconds, bool):
            raise ValueError("window_seconds must be an integer")

        if window_seconds <= 0:
            raise ValueError("window_seconds must be greater than zero")

        if not isinstance(group_by, list):
            raise ValueError("group_by must be a list")

        group_exprs = [resolve_field(field_path) for field_path in group_by]

        candidates: list[MatchCandidate] = []
        current_start = window_start
        step = timedelta(seconds=window_seconds)

        while current_start < window_end:
            current_end = min(current_start + step, window_end)

            filters = self._base_filters(rule, current_start, current_end)

            statement = select(
                *group_exprs,
                func.count(SecurityEvent.id),
                func.array_agg(SecurityEvent.id),
            ).where(*filters)

            if group_exprs:
                statement = statement.group_by(*group_exprs)

            for row in self.session.execute(statement):
                *group_values, count, event_ids = row

                if not self._compare(value=count, operator=operator, threshold=threshold):
                    continue

                candidates.append(
                    MatchCandidate(
                        window_start=current_start,
                        window_end=current_end,
                        group_key=dict(zip(group_by, group_values)),
                        metric_value=float(count),
                        event_ids=list(event_ids or []),
                    )
                )

            current_start = current_end

        return candidates

    @staticmethod
    def _compare(value: float, operator: str, threshold: float) -> bool:
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
            raise ValueError(f"Unsupported threshold operator '{operator}'") from exc

    # ------------------------------------------------------------------
    # Correlation
    # ------------------------------------------------------------------

    def _run_correlation(
        self,
        rule: DetectionRule,
        window_start: datetime,
        window_end: datetime,
    ) -> list[MatchCandidate]:
        """Ordered multi-step sequence correlation.

        Semantics (not specified elsewhere — this is this executor's
        interpretation):
        - Steps must be satisfied in order.
        - Each step needs `min_count` (default 1) matching events that
          occur strictly after the previous step's last-consumed event.
        - `max_gap_seconds` on a step (if set) bounds the gap between the
          previous step's last-consumed event and this step's *first*
          consumed event.
        - `correlation_window_seconds` bounds the total span from the
          first event of step 0 to the last consumed event overall.
        - Matching is greedy: the first valid full sequence per
          correlation-key group is taken, then the search resumes after
          it. This can under-match in overlapping/adversarial cases but
          will not fabricate matches that don't structurally exist.
        """
        config = rule.configuration or {}
        correlation_window_seconds = config["correlation_window_seconds"]
        correlation_key_paths = config["correlation_keys"]
        steps = config["event_sequence"]

        correlation_key_exprs = [resolve_field(p) for p in correlation_key_paths]

        base_filters = [
            SecurityEvent.tenant_id == self.tenant_id,
            SecurityEvent.event_time >= window_start,
            SecurityEvent.event_time < window_end,
        ]

        # Per step: list of (event_id, event_time, *correlation_key_values),
        # ordered by time, grouped by correlation-key tuple.
        step_by_key: list[dict[tuple, list[tuple]]] = []

        for step in steps:
            step_filter = build_clause(step["filter"])
            statement = (
                select(
                    SecurityEvent.id,
                    SecurityEvent.event_time,
                    *correlation_key_exprs,
                )
                .where(*base_filters, step_filter)
                .order_by(SecurityEvent.event_time)
            )

            grouped: dict[tuple, list[tuple]] = defaultdict(list)
            for row in self.session.execute(statement):
                event_id, event_time, *key_values = row
                grouped[tuple(key_values)].append((event_id, event_time))

            step_by_key.append(grouped)

        candidates: list[MatchCandidate] = []
        max_span = timedelta(seconds=correlation_window_seconds)

        for group_key_tuple, first_step_events in step_by_key[0].items():
            idx = 0
            min_count0 = steps[0].get("min_count", 1)
            n0 = len(first_step_events)

            while idx + min_count0 <= n0:
                anchor_events = first_step_events[idx: idx + min_count0]
                sequence_start = anchor_events[0][1]
                position_time = anchor_events[-1][1]
                matched_event_ids = [e[0] for e in anchor_events]
                valid = True

                for step_idx in range(1, len(steps)):
                    step = steps[step_idx]
                    min_count = step.get("min_count", 1)
                    max_gap_seconds = step.get("max_gap_seconds")

                    candidate_events = step_by_key[step_idx].get(group_key_tuple, [])
                    eligible = [e for e in candidate_events if e[1] > position_time]

                    if max_gap_seconds is not None and eligible:
                        gap = (eligible[0][1] - position_time).total_seconds()
                        if gap > max_gap_seconds:
                            eligible = []

                    if len(eligible) < min_count:
                        valid = False
                        break

                    consumed = eligible[:min_count]
                    matched_event_ids.extend(e[0] for e in consumed)
                    position_time = consumed[-1][1]

                if valid and (position_time - sequence_start) <= max_span:
                    candidates.append(
                        MatchCandidate(
                            window_start=sequence_start,
                            window_end=position_time,
                            group_key=dict(zip(correlation_key_paths, group_key_tuple)),
                            metric_value=float(len(matched_event_ids)),
                            event_ids=matched_event_ids,
                        )
                    )
                    idx += min_count0
                    continue

                idx += 1

        return candidates

    # ------------------------------------------------------------------
    # Behavioral
    # ------------------------------------------------------------------

    def _run_behavioral(
        self,
        rule: DetectionRule,
        window_start: datetime,
        window_end: datetime,
    ) -> list[MatchCandidate]:
        """Per-entity baseline deviation detection.

        Semantics (interpreted, not specified elsewhere):
        - Baseline = daily event counts for `entity_field` over the
          `baseline_window_days` immediately before window_start,
          missing days counted as 0.
        - Actual = event count in [window_start, window_end), normalized
          to a per-day rate so windows of any length are comparable to
          the daily baseline.
        - Deviation is one-sided: only increases are flagged, not drops.
        - An entity with no baseline history (mean=0) will trip
          percent_increase/absolute_diff on any activity at all — this
          is intentional (new-entity-sudden-activity is a real pattern)
          but will be noisy for legitimately new, benign entities.
        """
        config = rule.configuration or {}
        baseline_window_days = config["baseline_window_days"]
        entity_field = config["entity_field"]
        metric = config.get("metric")
        deviation_method = config["deviation_method"]
        deviation_threshold = config["deviation_threshold"]

        if metric not in _SUPPORTED_BEHAVIORAL_METRICS:
            raise ValueError(f"Unsupported behavioral metric '{metric}'")

        entity_expr = resolve_field(entity_field)
        filter_node = self._filter_node(rule)
        optional_filter = [build_clause(filter_node)] if filter_node else []

        baseline_start = window_start - timedelta(days=baseline_window_days)
        day_expr = func.date_trunc("day", SecurityEvent.event_time)

        baseline_statement = (
            select(entity_expr, day_expr, func.count(SecurityEvent.id))
            .where(
                SecurityEvent.tenant_id == self.tenant_id,
                SecurityEvent.event_time >= baseline_start,
                SecurityEvent.event_time < window_start,
                *optional_filter,
            )
            .group_by(entity_expr, day_expr)
        )

        # entity_value -> {date: count}
        baseline_counts: dict[Any, dict[date, int]] = defaultdict(dict)
        for entity_value, day, count in self.session.execute(baseline_statement):
            baseline_counts[entity_value][day.date()] = count

        all_days = [
            (baseline_start + timedelta(days=i)).date()
            for i in range(baseline_window_days)
        ]

        actual_statement = (
            select(
                entity_expr,
                func.count(SecurityEvent.id),
                func.array_agg(SecurityEvent.id),
            )
            .where(
                SecurityEvent.tenant_id == self.tenant_id,
                SecurityEvent.event_time >= window_start,
                SecurityEvent.event_time < window_end,
                *optional_filter,
            )
            .group_by(entity_expr)
        )

        window_days = (window_end - window_start).total_seconds() / 86400.0

        candidates: list[MatchCandidate] = []

        for entity_value, actual_count, event_ids in self.session.execute(actual_statement):
            daily_values = [
                baseline_counts.get(entity_value, {}).get(day, 0)
                for day in all_days
            ]
            mean = statistics.mean(daily_values) if daily_values else 0.0
            stddev = statistics.pstdev(daily_values) if daily_values else 0.0

            actual_rate = actual_count / window_days if window_days > 0 else float(actual_count)

            flagged = False

            if deviation_method == "stddev_multiplier":
                flagged = actual_rate > mean + stddev * deviation_threshold
            elif deviation_method == "percent_increase":
                flagged = actual_rate > mean * (1 + deviation_threshold)
            elif deviation_method == "absolute_diff":
                flagged = (actual_rate - mean) > deviation_threshold
            else:
                raise ValueError(f"Unsupported deviation_method '{deviation_method}'")

            if flagged:
                candidates.append(
                    MatchCandidate(
                        window_start=window_start,
                        window_end=window_end,
                        group_key={entity_field: entity_value},
                        metric_value=float(actual_rate),
                        event_ids=list(event_ids or []),
                    )
                )

        return candidates

    # ------------------------------------------------------------------
    # Sigma (scoped subset — see class docstring)
    # ------------------------------------------------------------------

    def _run_sigma(
        self,
        rule: DetectionRule,
        window_start: datetime,
        window_end: datetime,
    ) -> list[MatchCandidate]:
        import yaml

        try:
            parsed = yaml.safe_load(rule.query or "")
        except Exception as exc:
            raise RuleFilterError(f"Sigma rule is not valid YAML: {exc}") from exc

        if not isinstance(parsed, dict):
            raise RuleFilterError("Sigma rule must be a YAML mapping")

        detection = parsed.get("detection")

        if not isinstance(detection, dict) or "condition" not in detection:
            raise RuleFilterError(
                "Sigma rule must have a 'detection' block with a 'condition'"
            )

        condition = detection["condition"]

        if not isinstance(condition, str):
            raise NotImplementedError(
                "Only single-string Sigma conditions are supported "
                "(no condition lists)"
            )

        selections = {
            name: _sigma_selection_to_filter_node(value)
            for name, value in detection.items()
            if name != "condition"
        }

        if not selections:
            raise RuleFilterError("Sigma detection block has no selections")

        filter_node = _parse_sigma_condition(condition, selections)

        statement = select(SecurityEvent.id).where(
            SecurityEvent.tenant_id == self.tenant_id,
            SecurityEvent.event_time >= window_start,
            SecurityEvent.event_time < window_end,
            build_clause(filter_node),
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


def _sigma_selection_to_filter_node(selection: Any) -> dict[str, Any]:
    """Translate one Sigma selection map into our filter DSL.

    Supports: {field: value}, {field: [v1, v2]} (OR of values), and
    {field|contains/startswith/endswith/re: value}. Multiple fields in
    one selection map are ANDed together (standard Sigma semantics).
    Anything else (numeric comparison modifiers, |all, wildcards without
    an explicit modifier, nested lists of maps) is not supported.
    """
    if not isinstance(selection, dict) or not selection:
        raise NotImplementedError(
            f"Only flat field-map Sigma selections are supported, got: {selection!r}"
        )

    _MODIFIER_TO_OP = {
        "contains": "contains",
        "startswith": "startswith",
        "endswith": "endswith",
        "re": "regex",
    }

    clauses: list[dict[str, Any]] = []

    for raw_field, value in selection.items():
        field_path, _, modifier = raw_field.partition("|")

        if modifier and modifier not in _MODIFIER_TO_OP:
            raise NotImplementedError(
                f"Unsupported Sigma field modifier '|{modifier}' on '{raw_field}'"
            )

        op = _MODIFIER_TO_OP.get(modifier, "in" if isinstance(value, list) else "eq")

        if op == "in" and not isinstance(value, list):
            value = [value]

        clauses.append({"field": field_path, "op": op, "value": value})

    if len(clauses) == 1:
        return clauses[0]

    return {"and": clauses}


def _parse_sigma_condition(
    condition: str,
    selections: dict[str, Any],
) -> dict[str, Any]:
    """Very limited Sigma condition grammar: a single selection name, an
    optional leading 'not', or a uniform and/or chain with no
    parentheses. Everything else (parens, mixed and/or, '1 of them',
    'all of them', counting, timeframes) raises rather than guesses.
    """
    if "(" in condition or ")" in condition:
        raise NotImplementedError(
            f"Parenthesized Sigma conditions are not supported: '{condition}'"
        )

    tokens = condition.strip().split()

    if not tokens:
        raise RuleFilterError("Sigma condition is empty")

    negate = False
    if tokens[0].lower() == "not":
        negate = True
        tokens = tokens[1:]

    if not tokens:
        raise RuleFilterError("Sigma condition is empty after 'not'")

    if len(tokens) == 1:
        name = tokens[0]
        if name not in selections:
            raise RuleFilterError(f"Unknown Sigma selection '{name}'")
        node = selections[name]
    else:
        if len(tokens) % 2 == 0:
            raise NotImplementedError(
                f"Cannot parse Sigma condition: '{condition}'"
            )

        names = tokens[0::2]
        ops = {t.lower() for t in tokens[1::2]}

        if len(ops) != 1 or next(iter(ops)) not in {"and", "or"}:
            raise NotImplementedError(
                f"Only uniform 'and'/'or' chains are supported, got: '{condition}'"
            )

        op = next(iter(ops))
        missing = [n for n in names if n not in selections]

        if missing:
            raise RuleFilterError(f"Unknown Sigma selection(s): {missing}")

        node = {op: [selections[n] for n in names]}

    if negate:
        node = {"not": node}

    return node