from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from datetime import date, datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID


_VOLATILE_FIELDS = frozenset(
    {
        "id",
        "created_at",
        "updated_at",
        "ingested_at",
        "received_at",
        "normalized_at",
    }
)

_IDENTITY_FIELDS = (
    "tenant_id",
    "source",
    "source_type",
    "source_event_id",
    "event_type",
    "event_category",
    "action",
    "event_time",
    "hostname",
    "user_identifier",
    "source_ip",
    "destination_ip",
    "source_port",
    "destination_port",
    "process_name",
    "process_id",
    "mitre_technique_id",
    "correlation_id",
)


def _is_volatile_field(key: Any) -> bool:
    return str(key).casefold() in _VOLATILE_FIELDS


def _normalize_value(value: Any) -> Any:
    """Convert a value into a deterministic JSON-compatible structure."""
    if value is None or isinstance(value, (str, int, bool)):
        return value

    if isinstance(value, float):
        if value != value or value in (float("inf"), float("-inf")):
            return None
        return value

    if isinstance(value, Enum):
        return _normalize_value(value.value)

    if isinstance(value, datetime):
        if value.tzinfo is not None and value.utcoffset() is not None:
            value = value.astimezone(timezone.utc)

        return value.isoformat()

    if isinstance(value, (date, UUID)):
        return str(value)

    if isinstance(value, Mapping):
        normalized: dict[str, Any] = {}

        for key, item in value.items():
            if _is_volatile_field(key):
                continue

            normalized[str(key)] = _normalize_value(item)

        return dict(sorted(normalized.items()))

    if isinstance(value, (list, tuple)):
        return [_normalize_value(item) for item in value]

    if isinstance(value, set):
        normalized = [_normalize_value(item) for item in value]

        return sorted(
            normalized,
            key=_sort_key,
        )

    return str(value)


def _sort_key(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    )


def canonicalize_event(
    event: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Build the stable representation used for fingerprinting.

    Preferred identity fields are used when at least one is present.
    Otherwise, the complete non-volatile event payload is used.
    """
    identity = {
        field: event[field]
        for field in _IDENTITY_FIELDS
        if field in event and event[field] is not None
    }

    if identity:
        return _normalize_value(identity)

    return _normalize_value(event)


def canonical_json(
    event: Mapping[str, Any],
) -> str:
    """Serialize an event into deterministic JSON."""
    return json.dumps(
        canonicalize_event(event),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def _hash_payload(
    payload: str,
    *,
    algorithm: str = "sha256",
) -> str:
    try:
        hasher = hashlib.new(algorithm)
    except ValueError as exc:
        raise ValueError(
            f"Unsupported fingerprint algorithm: {algorithm}",
        ) from exc

    hasher.update(payload.encode("utf-8"))
    return hasher.hexdigest()


def generate_event_fingerprint(
    event: Mapping[str, Any],
    *,
    algorithm: str = "sha256",
) -> str:
    """
    Generate a deterministic fingerprint for a security event.

    The requested algorithm must be supported by ``hashlib``.
    """
    return _hash_payload(
        canonical_json(event),
        algorithm=algorithm,
    )


def generate_source_fingerprint(
    *,
    tenant_id: Any,
    source: Any,
    source_type: Any,
    source_event_id: Any,
    algorithm: str = "sha256",
) -> str:
    """
    Generate a stable fingerprint from a trusted source event identifier.

    The tenant and source metadata are included to prevent collisions between
    identical source identifiers from different tenants or integrations.
    """
    identity = {
        "tenant_id": _normalize_value(tenant_id),
        "source": _normalize_value(source),
        "source_type": _normalize_value(source_type),
        "source_event_id": _normalize_value(source_event_id),
    }

    payload = json.dumps(
        identity,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )

    return _hash_payload(
        payload,
        algorithm=algorithm,
    )


def fingerprints_match(
    first: Mapping[str, Any],
    second: Mapping[str, Any],
) -> bool:
    """Return whether two events produce the same SHA-256 fingerprint."""
    return generate_event_fingerprint(first) == generate_event_fingerprint(
        second,
    )
