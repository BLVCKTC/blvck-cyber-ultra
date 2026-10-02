from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.agents.tools.alert_context import _alert_dict, _event_dict, _rule_dict
from app.db.models.alert import Alert
from app.db.models.detection_rule import DetectionRule
from app.db.models.security_event import SecurityEvent

# Evidence.evidence_type values written by this agent. If EvidenceCreate
# restricts the allowed types, change them here, in one place.
TYPE_ALERT = "alert"
TYPE_RULE = "detection_rule"
TYPE_EVENT = "security_event"

TITLE_MAX = 255
RAW_EVENT_MAX_BYTES = 8192


def _title(text: str) -> str:
    return text if len(text) <= TITLE_MAX else text[: TITLE_MAX - 3] + "..."


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, default=str, separators=(",", ":"))


def build_evidence_items(
    db: Session,
    *,
    tenant_id: UUID,
    alert_id: UUID,
) -> list[dict[str, Any]] | None:
    """
    Build (but do not write) the evidence items for one alert.

    Returns None when the alert is missing or belongs to another tenant.
    Each item is a dict of EvidenceCreate fields, with a stable `reference`
    used for idempotency. Read-only: never writes or commits.
    """
    alert = db.get(Alert, alert_id)
    if alert is None or alert.tenant_id != tenant_id:
        return None

    captured_at = datetime.now(timezone.utc).isoformat()

    items: list[dict[str, Any]] = [
        {
            "evidence_type": TYPE_ALERT,
            "title": _title(f"Alert: {alert.title}"),
            "reference": f"alert:{alert.id}",
            "notes": f"Alert snapshot ({alert.severity}, status {alert.status}) at capture time.",
            "metadata_json": {
                "captured_at": captured_at,
                "snapshot": _alert_dict(alert),
            },
        }
    ]

    if alert.detection_rule_id is not None:
        rule = db.get(DetectionRule, alert.detection_rule_id)
        if rule is not None and rule.tenant_id == tenant_id:
            items.append(
                {
                    "evidence_type": TYPE_RULE,
                    "title": _title(f"Detection rule: {rule.name} v{rule.version}"),
                    "reference": f"detection_rule:{rule.id}",
                    "notes": f"{rule.rule_type} rule, status {rule.status}.",
                    "metadata_json": {
                        "captured_at": captured_at,
                        "snapshot": _rule_dict(rule),
                    },
                }
            )

    if alert.security_event_id is not None:
        event = db.get(SecurityEvent, alert.security_event_id)
        if event is not None and event.tenant_id == tenant_id:
            raw = event.raw_event or {}
            raw_json = _canonical(raw)
            raw_bytes = len(raw_json.encode("utf-8"))
            include_raw = raw_bytes <= RAW_EVENT_MAX_BYTES

            items.append(
                {
                    "evidence_type": TYPE_EVENT,
                    "title": _title(f"Event: {event.event_type}"),
                    "reference": f"security_event:{event.id}",
                    "notes": f"Triggering event from {event.source}.",
                    "metadata_json": {
                        "captured_at": captured_at,
                        "snapshot": _event_dict(event),
                        # The hash is always recorded, even when the body is
                        # omitted, so what was examined can be verified later.
                        "raw_event_sha256": hashlib.sha256(
                            raw_json.encode("utf-8")
                        ).hexdigest(),
                        "raw_event_bytes": raw_bytes,
                        "raw_event": raw if include_raw else None,
                        "raw_event_truncated": not include_raw,
                    },
                }
            )

    return items