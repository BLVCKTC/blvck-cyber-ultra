from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.db.models.alert import Alert
from app.db.models.detection_rule import DetectionRule
from app.db.models.security_event import SecurityEvent

# Bounds keep findings small enough to persist as Evidence metadata and
# keep this tool cheap on large tenants.
NEARBY_WINDOW = timedelta(minutes=15)
NEARBY_LIMIT = 50
MESSAGE_MAX = 500
RULE_QUERY_MAX = 2000


def _iso(value: datetime | None) -> str | None:
    return value.isoformat() if value is not None else None


def _s(value: Any) -> str | None:
    """JSON-safe string. INET columns may come back as ipaddress objects."""
    return str(value) if value is not None else None


def _trunc(value: str | None, limit: int) -> str | None:
    if value is None:
        return None
    return value if len(value) <= limit else value[:limit] + "...[truncated]"


def _alert_dict(alert: Alert) -> dict[str, Any]:
    return {
        "id": str(alert.id),
        "title": alert.title,
        "description": _trunc(alert.description, MESSAGE_MAX),
        "severity": str(alert.severity),
        "status": str(alert.status),
        "confidence": alert.confidence,
        "risk_score": alert.risk_score,
        "source": alert.source,
        "first_seen_at": _iso(alert.first_seen_at),
        "last_seen_at": _iso(alert.last_seen_at),
    }


def _rule_dict(rule: DetectionRule) -> dict[str, Any]:
    return {
        "id": str(rule.id),
        "name": rule.name,
        "description": _trunc(rule.description, MESSAGE_MAX),
        "rule_type": str(rule.rule_type),
        "severity": str(rule.severity),
        "status": str(rule.status),
        "version": rule.version,
        "forked_from_id": _s(rule.forked_from_id),
        "mitre_technique_ids": list(rule.mitre_technique_ids or []),
        "mitre_tactic_ids": list(rule.mitre_tactic_ids or []),
        "query": _trunc(rule.query, RULE_QUERY_MAX),
    }


def _event_dict(event: SecurityEvent) -> dict[str, Any]:
    # raw_event / normalized_data are deliberately excluded: they can be
    # large and may carry sensitive payloads. The Evidence agent can fetch
    # them explicitly, under its own bounds, if needed.
    return {
        "id": str(event.id),
        "event_time": _iso(event.event_time),
        "source": event.source,
        "source_type": event.source_type,
        "event_type": event.event_type,
        "event_category": event.event_category,
        "severity": str(event.severity),
        "action": event.action,
        "source_ip": _s(event.source_ip),
        "destination_ip": _s(event.destination_ip),
        "source_port": event.source_port,
        "destination_port": event.destination_port,
        "protocol": event.protocol,
        "hostname": event.hostname,
        "user_identifier": event.user_identifier,
        "process_name": event.process_name,
        "mitre_technique_id": event.mitre_technique_id,
        "message": _trunc(event.message, MESSAGE_MAX),
    }


def _nearby_events(
    db: Session,
    *,
    tenant_id: UUID,
    anchor: SecurityEvent,
) -> list[SecurityEvent]:
    """
    Events within +/- NEARBY_WINDOW of the anchor that share at least one
    entity (host, user, or source IP). The window is anchored on event_time,
    not wall-clock time, because this is a historical lookup.
    """
    entity_filters = []
    if anchor.hostname:
        entity_filters.append(SecurityEvent.hostname == anchor.hostname)
    if anchor.user_identifier:
        entity_filters.append(
            SecurityEvent.user_identifier == anchor.user_identifier
        )
    if anchor.source_ip:
        entity_filters.append(SecurityEvent.source_ip == anchor.source_ip)

    if not entity_filters:
        return []

    stmt = (
        select(SecurityEvent)
        .where(
            SecurityEvent.tenant_id == tenant_id,
            SecurityEvent.id != anchor.id,
            SecurityEvent.event_time >= anchor.event_time - NEARBY_WINDOW,
            SecurityEvent.event_time <= anchor.event_time + NEARBY_WINDOW,
            or_(*entity_filters),
        )
        .order_by(SecurityEvent.event_time.asc())
        .limit(NEARBY_LIMIT)
    )
    return list(db.execute(stmt).scalars())


def collect_alert_context(
    db: Session,
    *,
    tenant_id: UUID,
    alert_id: UUID,
) -> dict[str, Any] | None:
    """
    Read-only context retrieval for one alert.

    Returns {"note": str, "data": JSON-safe dict}, or None when the alert
    does not exist or belongs to another tenant. Never writes or commits.
    Tenant ownership is re-checked explicitly even though RLS also enforces
    it, so a misconfigured session cannot silently widen the read.
    """
    alert = db.get(Alert, alert_id)
    if alert is None or alert.tenant_id != tenant_id:
        return None

    rule: DetectionRule | None = None
    if alert.detection_rule_id is not None:
        rule = db.get(DetectionRule, alert.detection_rule_id)
        if rule is not None and rule.tenant_id != tenant_id:
            rule = None

    event: SecurityEvent | None = None
    if alert.security_event_id is not None:
        event = db.get(SecurityEvent, alert.security_event_id)
        if event is not None and event.tenant_id != tenant_id:
            event = None

    nearby: list[SecurityEvent] = []
    if event is not None:
        nearby = _nearby_events(db, tenant_id=tenant_id, anchor=event)

    data: dict[str, Any] = {
        "alert": _alert_dict(alert),
        "rule": _rule_dict(rule) if rule is not None else None,
        "triggering_event": _event_dict(event) if event is not None else None,
        "nearby_events": [_event_dict(e) for e in nearby],
        "nearby_window_minutes": int(NEARBY_WINDOW.total_seconds() // 60),
        "nearby_truncated": len(nearby) >= NEARBY_LIMIT,
        "gaps": [
            gap
            for gap, missing in (
                ("rule_missing_or_deleted", alert.detection_rule_id and rule is None),
                ("no_rule_linked", alert.detection_rule_id is None),
                ("event_missing_or_deleted", alert.security_event_id and event is None),
                ("no_event_linked", alert.security_event_id is None),
            )
            if missing
        ],
    }

    rule_part = f"rule '{rule.name}' (v{rule.version})" if rule else "no rule context"
    event_part = (
        f"triggering event {event.event_type}"
        if event
        else "no triggering event"
    )
    note = (
        f"{alert.severity} alert '{alert.title}'; {rule_part}; {event_part}; "
        f"{len(nearby)} related event(s) within "
        f"{data['nearby_window_minutes']} min"
        + (" (capped)" if data["nearby_truncated"] else "")
    )

    return {"note": note, "data": data}