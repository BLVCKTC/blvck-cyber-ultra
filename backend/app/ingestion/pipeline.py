from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from sqlalchemy.orm import Session

from app.ingestion.models import IngestionResult, SecurityEventEnvelope
from app.ingestion.normalizer import SecurityEventNormalizer
from app.ingestion.validators import SecurityEventValidator
from app.schemas.security_event import SecurityEventCreate
from app.services.security_event_service import SecurityEventService


class SecurityEventIngestionPipeline:
    """
    Normalize, validate, and persist security events.

    Pipeline:

        SecurityEventEnvelope
                ↓
        SecurityEventNormalizer
                ↓
        SecurityEventCreate
                ↓
        SecurityEventValidator
                ↓
        validated mapping
                ↓
        SecurityEventCreate
                ↓
        SecurityEventService
                ↓
        PostgreSQL

    The tenant ID from the authenticated envelope is authoritative and is
    validated before persistence.
    """

    def __init__(
        self,
        db: Session,
    ) -> None:
        self.db = db
        self.normalizer = SecurityEventNormalizer()
        self.events = SecurityEventService(db)

    def ingest(
        self,
        envelope: SecurityEventEnvelope,
    ) -> IngestionResult:
        """Process and persist one security-event envelope."""

        tenant_id = envelope.tenant_id

        try:

            normalized = self.normalizer.normalize(envelope)

            payload = self._model_to_mapping(normalized)

            validator = SecurityEventValidator(
                authenticated_tenant_id=tenant_id,
            )

            validated_payload = validator.validate(payload)

            validated_event = SecurityEventCreate.model_validate(
                validated_payload,
            )

            fingerprint = self._extract_fingerprint(
                validated_event.model_dump(
                    mode="python",
                ),
            )

            event = self.events.create(
                tenant_id=tenant_id,
                payload=validated_event,
            )

            return IngestionResult.accepted_event(
                event_id=event.id,
                tenant_id=tenant_id,
                fingerprint=fingerprint,
            )

        except Exception as exc:
            self.db.rollback()

            return IngestionResult.rejected_event(
                tenant_id=tenant_id,
                message=str(exc),
            )

    @staticmethod
    def _model_to_mapping(
        value: Any,
    ) -> dict[str, Any]:
        """
        Convert a Pydantic model or mapping into a mutable dictionary.
        """

        if hasattr(value, "model_dump"):
            data = value.model_dump(
                mode="python",
                exclude_none=False,
            )

        elif isinstance(value, Mapping):
            data = dict(value)

        else:
            raise TypeError(
                "Normalizer must return a mapping or Pydantic model.",
            )

        if not isinstance(data, dict):
            raise TypeError(
                "Normalized event must serialize to a dictionary.",
            )

        return data

    @staticmethod
    def _extract_fingerprint(
        event: Mapping[str, Any],
    ) -> str:
        """Return the validated event fingerprint."""

        fingerprint = event.get("event_fingerprint")

        if not isinstance(fingerprint, str) or not fingerprint.strip():
            raise ValueError(
                "Validated event does not contain event_fingerprint.",
            )

        return fingerprint.strip()

    def ingest_many(
        self,
        envelopes: list[SecurityEventEnvelope],
    ) -> list[IngestionResult]:
        """
        Process multiple envelopes independently.

        A failed event is rolled back without discarding results for other
        envelopes.
        """

        return [
            self.ingest(envelope)
            for envelope in envelopes
        ]


def ingest_security_event(
    db: Session,
    envelope: SecurityEventEnvelope,
) -> IngestionResult:
    """Convenience entry point for application services and API routes."""

    return SecurityEventIngestionPipeline(db).ingest(envelope)