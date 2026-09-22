from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models.detection_rule import DetectionRule, DetectionRuleType
from app.db.models.security_event import SecurityEvent
from app.services.detection_rules.execution import MatchCandidate, RuleExecutor

logger = logging.getLogger(__name__)

_last_evaluated: dict[tuple[UUID, UUID], datetime] = {}

DEFAULT_DEBOUNCE_SECONDS = 30
DEFAULT_BEHAVIORAL_WINDOW_SECONDS = 300

_WINDOWED_TYPES = {
    DetectionRuleType.THRESHOLD,
    DetectionRuleType.CORRELATION,
    DetectionRuleType.BEHAVIORAL,
}


def _debounce_ok(
    tenant_id: UUID,
    rule_id: UUID,
    now: datetime,
    cooldown_seconds: int,
) -> bool:
    key = (tenant_id, rule_id)
    last = _last_evaluated.get(key)
    if last is not None and (now - last).total_seconds() < cooldown_seconds:
        return False
    _last_evaluated[key] = now
    return True


def _window_for_rule(
    rule: DetectionRule,
    now: datetime,
) -> tuple[datetime, datetime]:
    config = rule.configuration or {}
    rule_type = DetectionRuleType(rule.rule_type)

    if rule_type == DetectionRuleType.THRESHOLD:
        window_seconds = config["window_seconds"]
    elif rule_type == DetectionRuleType.CORRELATION:
        window_seconds = config["correlation_window_seconds"]
    elif rule_type == DetectionRuleType.BEHAVIORAL:
        window_seconds = config.get(
            "detection_window_seconds",
            DEFAULT_BEHAVIORAL_WINDOW_SECONDS,
        )
    else:
        raise ValueError(
            f"_window_for_rule called for non-windowed type {rule_type}",
        )

    return now - timedelta(seconds=window_seconds), now


def evaluate_rule_for_event(
    *,
    session: Session,
    tenant_id: UUID,
    rule: DetectionRule,
    event: SecurityEvent,
    cooldown_seconds: int = DEFAULT_DEBOUNCE_SECONDS,
) -> list[MatchCandidate]:
    """Evaluate one rule against live traffic triggered by a new event."""
    rule_type = DetectionRuleType(rule.rule_type)
    executor = RuleExecutor(session, tenant_id)

    if rule_type == DetectionRuleType.SIGMA:
        return []

    if rule_type == DetectionRuleType.QUERY:
        window_start = event.event_time
        window_end = event.event_time + timedelta(microseconds=1)
        candidates = executor.run(rule, window_start, window_end)
        return [
            replace(
                candidate,
                event_ids=[event.id],
                metric_value=1.0,
            )
            for candidate in candidates
            if event.id in candidate.event_ids
        ]

    if rule_type in _WINDOWED_TYPES:
        wall_now = datetime.now(timezone.utc)

        if not _debounce_ok(
            tenant_id,
            rule.id,
            wall_now,
            cooldown_seconds,
        ):
            return []

        window_start, window_end = _window_for_rule(
            rule,
            event.event_time,
        )
        return executor.run(
            rule,
            window_start,
            window_end,
        )

    raise NotImplementedError(
        f"Live evaluation not implemented for rule type {rule_type}",
    )


def build_fingerprint(
    *,
    rule_id: UUID,
    rule_type: DetectionRuleType,
    candidate: MatchCandidate,
    event: SecurityEvent,
) -> str:
    """Build a stable fingerprint for alert deduplication."""
    if rule_type == DetectionRuleType.QUERY:
        entity_repr = "query"
    elif not candidate.group_key:
        entity_repr = "default"
    else:
        canonical = json.dumps(
            sorted(
                candidate.group_key.items(),
                key=lambda kv: kv[0],
            ),
            default=str,
        )
        entity_repr = hashlib.sha256(
            canonical.encode(),
        ).hexdigest()[:32]

    return f"rule:{rule_id}:{entity_repr}"[:128]