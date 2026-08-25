from __future__ import annotations

import hashlib
import json
import math
from copy import deepcopy
from datetime import datetime, timezone
from numbers import Real
from typing import Any, Mapping
from uuid import UUID

from app.ingestion.models import SecurityEventEnvelope
from app.schemas.security_event import SecurityEventCreate


_UNSET = object()

_SEVERITY_BY_NUMBER: dict[int, str] = {
    0: "info",
    1: "low",
    2: "medium",
    3: "high",
    4: "critical",
    5: "critical",
}

_SEVERITY_BY_NAME: dict[str, str] = {
    "info": "info",
    "informational": "info",
    "notice": "info",
    "debug": "info",
    "low": "low",
    "minor": "low",
    "medium": "medium",
    "moderate": "medium",
    "warning": "medium",
    "warn": "medium",
    "high": "high",
    "major": "high",
    "critical": "critical",
    "severe": "critical",
    "fatal": "critical",
}

_DEFAULT_RISK_SCORE: dict[str, int] = {
    "info": 10,
    "low": 25,
    "medium": 50,
    "high": 75,
    "critical": 95,
}

_FIELD_ALIASES: dict[str, tuple[str, ...]] = {
    "event_time": (
        "event_time",
        "timestamp",
        "time",
        "occurred_at",
        "created_at",
        "metadata.event_time",
        "metadata.timestamp",
    ),
    "event_type": (
        "event_type",
        "type",
        "event.name",
        "event.type",
        "metadata.event_type",
    ),
    "event_category": (
        "event_category",
        "category",
        "event.category",
        "metadata.event_category",
    ),
    "action": (
        "action",
        "activity",
        "operation",
        "event.action",
    ),
    "severity": (
        "severity",
        "priority",
        "alert.severity",
        "event.severity",
    ),
    "risk_score": (
        "risk_score",
        "risk.score",
        "score",
        "alert.risk_score",
    ),
    "hostname": (
        "hostname",
        "host.name",
        "device.hostname",
        "endpoint.hostname",
        "computer.name",
    ),
    "source_ip": (
        "source_ip",
        "src_ip",
        "source.ip",
        "src.address",
        "network.source.ip",
    ),
    "source_port": (
        "source_port",
        "src_port",
        "source.port",
        "src.port",
        "network.source.port",
    ),
    "destination_ip": (
        "destination_ip",
        "dst_ip",
        "destination.ip",
        "dest.ip",
        "dst.address",
        "network.destination.ip",
    ),
    "destination_port": (
        "destination_port",
        "dst_port",
        "destination.port",
        "dest.port",
        "dst.port",
        "network.destination.port",
    ),
    "protocol": (
        "protocol",
        "network.protocol",
        "connection.protocol",
    ),
    "username": (
        "username",
        "user.name",
        "account.username",
        "actor.username",
    ),
    "user_id": (
        "user_id",
        "user.id",
        "account.id",
        "actor.id",
    ),
    "process_name": (
        "process_name",
        "process.name",
        "process.executable",
    ),
    "process_id": (
        "process_id",
        "process.pid",
        "process.id",
    ),
    "mitre_tactic": (
        "mitre_tactic",
        "mitre.tactic",
        "attack.tactic",
        "threat.tactic",
    ),
    "mitre_technique": (
        "mitre_technique",
        "mitre.technique",
        "attack.technique",
        "threat.technique",
    ),
    "mitre_technique_id": (
        "mitre_technique_id",
        "mitre.technique_id",
        "attack.technique_id",
        "threat.technique_id",
    ),
    "parent_event_id": (
        "parent_event_id",
        "parent.id",
        "event.parent_id",
    ),
}

_NORMALIZED_FIELDS_EXCLUDED = {
    "event_time",
    "event_type",
    "event_category",
    "action",
    "severity",
    "risk_score",
    "parent_event_id",
}


class SecurityEventNormalizer:
    """Convert an authenticated ingestion envelope to the canonical schema."""

    def normalize(
        self,
        envelope: SecurityEventEnvelope,
    ) -> SecurityEventCreate:
        return normalize_security_event(envelope)

    def __call__(
        self,
        envelope: SecurityEventEnvelope,
    ) -> SecurityEventCreate:
        return self.normalize(envelope)


def normalize_security_event(
    envelope: SecurityEventEnvelope,
) -> SecurityEventCreate:
    """
    Convert an authenticated ingestion envelope into a canonical security event.

    The authenticated envelope is authoritative for tenant and source metadata.
    Vendor-provided tenant identifiers are never trusted.
    """

    payload = envelope.raw_payload

    event_time = _coerce_datetime(
        _first(payload, *_FIELD_ALIASES["event_time"]),
        default=envelope.received_at,
    )
    event_type = _text(
        _first(payload, *_FIELD_ALIASES["event_type"]),
        default="unknown",
    )
    event_category = _text(
        _first(payload, *_FIELD_ALIASES["event_category"]),
        default="unknown",
    )
    action = _text(
        _first(payload, *_FIELD_ALIASES["action"]),
        default=None,
    )
    severity = _normalize_severity(
        _first(payload, *_FIELD_ALIASES["severity"]),
    )
    risk_score = _normalize_risk_score(
        _first(payload, *_FIELD_ALIASES["risk_score"]),
        severity=severity,
    )
    parent_event_id = _normalize_uuid(
        _first(payload, *_FIELD_ALIASES["parent_event_id"]),
    )

    normalized_data = _build_normalized_data(
        payload=payload,
        event_time=event_time,
        event_type=event_type,
        event_category=event_category,
        severity=severity,
        risk_score=risk_score,
    )

    fingerprint = generate_event_fingerprint(
        envelope=envelope,
        event_time=event_time,
        event_type=event_type,
        event_category=event_category,
        action=action,
        normalized_fields=normalized_data,
    )

    username = normalized_data.get("username")
    user_id = normalized_data.get("user_id")
    user_identifier = (
        str(username)
        if username is not None
        else str(user_id)
        if user_id is not None
        else None
    )

    normalized: dict[str, Any] = {
        "tenant_id": envelope.tenant_id,
        "source": envelope.source,
        "source_type": envelope.source_type,
        "source_event_id": envelope.source_event_id,
        "event_fingerprint": fingerprint,
        "correlation_id": envelope.correlation_id,
        "parent_event_id": parent_event_id,
        "event_time": event_time,
        "schema_version": 1,
        "event_category": event_category,
        "event_type": event_type,
        "severity": severity,
        "status": "open",
        "action": action,
        "risk_score": risk_score,
        "source_ip": normalized_data.get("source_ip"),
        "destination_ip": normalized_data.get("destination_ip"),
        "source_port": _normalize_int(
            normalized_data.get("source_port"),
        ),
        "destination_port": _normalize_int(
            normalized_data.get("destination_port"),
        ),
        "protocol": _optional_text(
            normalized_data.get("protocol"),
        ),
        "hostname": _optional_text(
            normalized_data.get("hostname"),
        ),
        "user_identifier": user_identifier,
        "process_name": _optional_text(
            normalized_data.get("process_name"),
        ),
        "process_id": _normalize_int(
            normalized_data.get("process_id"),
        ),
        "mitre_tactic": _optional_text(
            normalized_data.get("mitre_tactic"),
        ),
        "mitre_technique": _optional_text(
            normalized_data.get("mitre_technique"),
        ),
        "mitre_technique_id": _optional_text(
            normalized_data.get("mitre_technique_id"),
        ),
        "message": _extract_message(payload),
        "raw_event": deepcopy(payload),
        "normalized_data": normalized_data,
        "event_metadata": {
            "normalizer": "SecurityEventNormalizer",
            "normalizer_version": 1,
            "ingestion_source": envelope.source,
            "ingestion_source_type": envelope.source_type,
        },
    }

    schema_fields = getattr(SecurityEventCreate, "model_fields", {})
    filtered = {
        key: value
        for key, value in normalized.items()
        if key in schema_fields
    }

    return SecurityEventCreate.model_validate(filtered)


def _build_normalized_data(
    *,
    payload: Mapping[str, Any],
    event_time: datetime,
    event_type: str,
    event_category: str,
    severity: str,
    risk_score: int,
) -> dict[str, Any]:
    normalized_data: dict[str, Any] = {}

    for field_name, aliases in _FIELD_ALIASES.items():
        if field_name in _NORMALIZED_FIELDS_EXCLUDED:
            continue

        value = _first(payload, *aliases)

        if value is not _UNSET and value is not None:
            normalized_data[field_name] = _json_safe(value)

    normalized_data.update(
        {
            "event_time": event_time.isoformat(),
            "event_type": event_type,
            "event_category": event_category,
            "severity": severity,
            "risk_score": risk_score,
        }
    )

    return normalized_data


def generate_event_fingerprint(
    *,
    envelope: SecurityEventEnvelope,
    event_time: datetime,
    event_type: str,
    event_category: str,
    action: str | None,
    normalized_fields: Mapping[str, Any],
) -> str:
    """
    Generate a deterministic SHA-256 fingerprint for event deduplication.

    If source_event_id exists, it is used as the primary source identity.
    Otherwise, stable normalized attributes and the canonicalized payload
    are included.
    """

    identity: dict[str, Any] = {
        "tenant_id": str(envelope.tenant_id),
        "source": envelope.source,
        "source_type": envelope.source_type,
        "source_event_id": _json_safe(envelope.source_event_id),
    }

    if envelope.source_event_id is None:
        identity.update(
            {
                "event_time": event_time.astimezone(
                    timezone.utc,
                ).isoformat(),
                "event_type": event_type,
                "event_category": event_category,
                "action": action,
                "hostname": normalized_fields.get("hostname"),
                "username": normalized_fields.get("username"),
                "user_id": normalized_fields.get("user_id"),
                "process_name": normalized_fields.get("process_name"),
                "process_id": normalized_fields.get("process_id"),
                "source_ip": normalized_fields.get("source_ip"),
                "source_port": normalized_fields.get("source_port"),
                "destination_ip": normalized_fields.get(
                    "destination_ip",
                ),
                "destination_port": normalized_fields.get(
                    "destination_port",
                ),
                "file_hash": normalized_fields.get("file_hash"),
                "raw_payload": _json_safe(envelope.raw_payload),
            }
        )

    canonical = json.dumps(
        identity,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")

    return hashlib.sha256(canonical).hexdigest()


def _first(
    payload: Mapping[str, Any],
    *paths: str,
) -> Any:
    for path in paths:
        value = _get_path(payload, path)

        if value is not _UNSET and value is not None:
            return value

    return _UNSET


def _get_path(
    value: Any,
    path: str,
) -> Any:
    current = value

    for component in path.split("."):
        if not isinstance(current, Mapping):
            return _UNSET

        matching_key = next(
            (
                key
                for key in current
                if isinstance(key, str)
                and key.casefold() == component.casefold()
            ),
            _UNSET,
        )

        if matching_key is _UNSET:
            return _UNSET

        current = current[matching_key]

    return current


def _text(
    value: Any,
    *,
    default: str | None = None,
) -> str | None:
    if value is _UNSET or value is None:
        return default

    text = str(value).strip()
    return text or default


def _optional_text(value: Any) -> str | None:
    return _text(value)


def _coerce_datetime(
    value: Any,
    *,
    default: datetime,
) -> datetime:
    if value is _UNSET or value is None:
        parsed = default

    elif isinstance(value, datetime):
        parsed = value

    elif isinstance(value, Real) and not isinstance(value, bool):
        timestamp = float(value)

        if not math.isfinite(timestamp):
            raise ValueError("event_time must be finite.")

        if abs(timestamp) >= 10_000_000_000:
            timestamp /= 1_000

        parsed = datetime.fromtimestamp(
            timestamp,
            tz=timezone.utc,
        )

    elif isinstance(value, str):
        text = value.strip()

        if text.endswith(("Z", "z")):
            text = f"{text[:-1]}+00:00"

        parsed = datetime.fromisoformat(text)

    else:
        raise ValueError(
            "event_time must be an ISO timestamp, datetime, or epoch.",
        )

    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("event_time must be timezone-aware.")

    return parsed.astimezone(timezone.utc)


def _normalize_severity(value: Any) -> str:
    if value is _UNSET or value is None:
        return "medium"

    if isinstance(value, bool):
        return "medium"

    if isinstance(value, Real):
        numeric = float(value)

        if math.isfinite(numeric):
            return _SEVERITY_BY_NUMBER.get(
                int(numeric),
                "medium",
            )

        return "medium"

    normalized = _text(value, default="medium")
    return _SEVERITY_BY_NAME.get(
        normalized.casefold(),
        "medium",
    )


def _normalize_risk_score(
    value: Any,
    *,
    severity: str,
) -> int:
    if value is not _UNSET and value is not None:
        try:
            score = float(value)
        except (TypeError, ValueError):
            score = math.nan

        if math.isfinite(score):
            return round(max(0.0, min(100.0, score)))

    return _DEFAULT_RISK_SCORE[severity]


def _normalize_int(value: Any) -> int | None:
    if value is None or isinstance(value, bool):
        return None

    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _normalize_uuid(value: Any) -> UUID | None:
    if value is _UNSET or value is None:
        return None

    if isinstance(value, UUID):
        return value

    try:
        return UUID(str(value))
    except (AttributeError, TypeError, ValueError):
        return None


def _extract_message(
    payload: Mapping[str, Any],
) -> str | None:
    value = _first(
        payload,
        "message",
        "msg",
        "description",
        "alert.message",
        "event.message",
    )

    return _optional_text(value)


def _json_safe(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {
            str(key): _json_safe(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]

    if isinstance(value, (datetime, UUID)):
        return str(value)

    if isinstance(value, (str, int, float, bool)) or value is None:
        return value

    return repr(value)
