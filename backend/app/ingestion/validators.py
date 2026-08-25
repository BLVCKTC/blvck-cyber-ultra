from __future__ import annotations

import math
from collections.abc import Mapping
from datetime import datetime
from numbers import Real
from typing import Any
from uuid import UUID


class IngestionValidationError(ValueError):
    """Raised when a normalized event fails ingestion validation."""


class SecurityEventValidator:
    """
    Validate normalized security events before persistence.

    Tenant identity is NOT part of the SecurityEventCreate payload.

    The authenticated tenant comes from SecurityEventEnvelope.tenant_id
    and is passed separately through the ingestion pipeline.

    Vendor payload data is never trusted for tenant identity.
    """

    REQUIRED_FIELDS = frozenset(
        {
            "event_time",
            "event_type",
            "event_category",
            "source",
            "source_type",
            "event_fingerprint",
        }
    )

    SEVERITIES = frozenset(
        {
            "info",
            "low",
            "medium",
            "high",
            "critical",
        }
    )

    MIN_RISK_SCORE = 0
    MAX_RISK_SCORE = 100
    FINGERPRINT_LENGTH = 64

    def __init__(
        self,
        *,
        authenticated_tenant_id: UUID | str,
    ) -> None:
        self.authenticated_tenant_id = str(
            authenticated_tenant_id,
        ).casefold()

    def validate(
        self,
        event: Mapping[str, Any],
    ) -> dict[str, Any]:
        """
        Validate and sanitize a normalized event.

        Tenant identity is validated through the separately supplied
        authenticated tenant context.

        The returned dictionary contains only canonical event data and
        is safe to pass to SecurityEventCreate.
        """
        values = dict(event)

        self._validate_required_fields(values)
        self._validate_event_time(values)
        self._validate_source_identity(values)
        self._validate_severity(values)
        self._validate_risk_score(values)
        self._validate_fingerprint(values)
        self._validate_raw_event(values)

        return values

    def validate_tenant(
        self,
        tenant_id: UUID | str,
    ) -> None:
        """
        Validate the authenticated tenant context.

        This is intentionally separate from the normalized event payload.
        """
        supplied_tenant = str(tenant_id).casefold()

        if supplied_tenant != self.authenticated_tenant_id:
            raise IngestionValidationError(
                "tenant_id does not match the authenticated ingestion context",
            )

    def _validate_required_fields(
        self,
        event: Mapping[str, Any],
    ) -> None:
        missing = sorted(
            field
            for field in self.REQUIRED_FIELDS
            if _is_missing(event.get(field))
        )

        if missing:
            raise IngestionValidationError(
                "Missing required normalized fields: "
                + ", ".join(missing),
            )

    def _validate_event_time(
        self,
        event: Mapping[str, Any],
    ) -> None:
        event_time = event.get("event_time")

        if not isinstance(event_time, datetime):
            raise IngestionValidationError(
                "event_time must be a datetime",
            )

        if event_time.tzinfo is None or event_time.utcoffset() is None:
            raise IngestionValidationError(
                "event_time must be timezone-aware",
            )

        if not math.isfinite(event_time.timestamp()):
            raise IngestionValidationError(
                "event_time must be finite",
            )

    def _validate_source_identity(
        self,
        event: Mapping[str, Any],
    ) -> None:
        for field in ("source", "source_type"):
            value = event.get(field)

            if not isinstance(value, str) or not value.strip():
                raise IngestionValidationError(
                    f"{field} must be a non-empty string",
                )

        source_event_id = event.get("source_event_id")

        if source_event_id is None:
            return

        if not isinstance(source_event_id, str):
            raise IngestionValidationError(
                "source_event_id must be a string when supplied",
            )

        if not source_event_id.strip():
            raise IngestionValidationError(
                "source_event_id cannot be blank",
            )

    def _validate_severity(
        self,
        event: Mapping[str, Any],
    ) -> None:
        severity = event.get("severity")

        if severity is None:
            return

        value = getattr(severity, "value", severity)

        if not isinstance(value, str):
            raise IngestionValidationError(
                "severity must be a string",
            )

        if value.strip().casefold() not in self.SEVERITIES:
            raise IngestionValidationError(
                f"Unsupported severity: {severity}",
            )

    def _validate_risk_score(
        self,
        event: Mapping[str, Any],
    ) -> None:
        risk_score = event.get("risk_score")

        if risk_score is None:
            return

        if isinstance(risk_score, bool) or not isinstance(
            risk_score,
            Real,
        ):
            raise IngestionValidationError(
                "risk_score must be numeric",
            )

        score = float(risk_score)

        if not math.isfinite(score):
            raise IngestionValidationError(
                "risk_score must be finite",
            )

        if not (
            self.MIN_RISK_SCORE
            <= score
            <= self.MAX_RISK_SCORE
        ):
            raise IngestionValidationError(
                "risk_score must be between "
                f"{self.MIN_RISK_SCORE} and {self.MAX_RISK_SCORE}",
            )

    def _validate_fingerprint(
        self,
        event: Mapping[str, Any],
    ) -> None:
        fingerprint = event.get("event_fingerprint")

        if not isinstance(fingerprint, str):
            raise IngestionValidationError(
                "event_fingerprint must be a string",
            )

        fingerprint = fingerprint.strip()

        if not fingerprint:
            raise IngestionValidationError(
                "event_fingerprint cannot be blank",
            )

        if len(fingerprint) != self.FINGERPRINT_LENGTH:
            raise IngestionValidationError(
                "event_fingerprint must be a SHA-256 hexadecimal digest",
            )

        if fingerprint != fingerprint.casefold():
            raise IngestionValidationError(
                "event_fingerprint must use lowercase hexadecimal characters",
            )

        if any(
            character not in "0123456789abcdef"
            for character in fingerprint
        ):
            raise IngestionValidationError(
                "event_fingerprint must contain only hexadecimal characters",
            )

    def _validate_raw_event(
        self,
        event: Mapping[str, Any],
    ) -> None:
        raw_event = event.get("raw_event")

        if raw_event is None:
            raise IngestionValidationError(
                "raw_event must be preserved",
            )

        if not isinstance(raw_event, Mapping):
            raise IngestionValidationError(
                "raw_event must be a mapping",
            )


def validate_security_event(
    event: Mapping[str, Any],
    *,
    authenticated_tenant_id: UUID | str,
) -> dict[str, Any]:
    """
    Validate one normalized security event.

    The authenticated tenant is supplied separately and is never expected
    inside the normalized SecurityEventCreate payload.
    """
    validator = SecurityEventValidator(
        authenticated_tenant_id=authenticated_tenant_id,
    )

    return validator.validate(event)

def _is_missing(value: Any) -> bool:
    """Return True when a required normalized value is absent or blank."""
    return value is None or (
        isinstance(value, str)
        and not value.strip()
    )