from __future__ import annotations

from collections.abc import Mapping
from typing import Any
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.ingestion.models import IngestionResult, SecurityEventEnvelope
from app.ingestion.normalizer import SecurityEventNormalizer
from app.ingestion.validators import SecurityEventValidator
from app.schemas.security_event import SecurityEventCreate
from app.services.security_event_service import SecurityEventService


class SecurityEventIngestionPipeline:
    """Normalize, validate, deduplicate, and persist security events."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.normalizer = SecurityEventNormalizer()
        self.events = SecurityEventService(db)

    def ingest(
        self,
        envelope: SecurityEventEnvelope,
    ) -> IngestionResult:
        tenant_id = envelope.tenant_id

        try:
            normalized = self.normalizer.normalize(envelope)
            payload = self._model_to_mapping(normalized)

            validated_payload = SecurityEventValidator(
                authenticated_tenant_id=tenant_id,
            ).validate(payload)

            event_payload = SecurityEventCreate.model_validate(
                validated_payload,
            )
            event_mapping = event_payload.model_dump(
                mode="python",
                exclude_none=False,
            )

            fingerprint = self._extract_fingerprint(event_mapping)
            source_event_id = self._extract_source_event_id(event_mapping)

            duplicate = self._find_duplicate(
                tenant_id=tenant_id,
                source=envelope.source,
                source_event_id=source_event_id,
                fingerprint=fingerprint,
            )
            if duplicate is not None:
                return self._duplicate_result(
                    duplicate,
                    tenant_id=tenant_id,
                    fingerprint=fingerprint,
                )

            try:
                event = self.events.create(
                    tenant_id=tenant_id,
                    payload=event_payload,
                )
            except IntegrityError:
                self.db.rollback()

                duplicate = self._find_duplicate(
                    tenant_id=tenant_id,
                    source=envelope.source,
                    source_event_id=source_event_id,
                    fingerprint=fingerprint,
                )
                if duplicate is None:
                    raise

                return self._duplicate_result(
                    duplicate,
                    tenant_id=tenant_id,
                    fingerprint=fingerprint,
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

    def _find_duplicate(
        self,
        *,
        tenant_id: UUID,
        source: str,
        source_event_id: str | None,
        fingerprint: str,
    ) -> Any | None:
        if source_event_id is not None:
            event = self.events.get_by_source_event_id(
                tenant_id=tenant_id,
                source=source,
                source_event_id=source_event_id,
            )
            if event is not None:
                return event

        return self.events.get_by_fingerprint(
            tenant_id=tenant_id,
            fingerprint=fingerprint,
        )

    @staticmethod
    def _duplicate_result(
        event: Any,
        *,
        tenant_id: UUID,
        fingerprint: str,
    ) -> IngestionResult:
        return IngestionResult.duplicate_event(
            event_id=event.id,
            tenant_id=tenant_id,
            fingerprint=event.event_fingerprint or fingerprint,
        )

    @staticmethod
    def _model_to_mapping(value: Any) -> dict[str, Any]:
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
        fingerprint = event.get("event_fingerprint")

        if not isinstance(fingerprint, str):
            raise ValueError(
                "Validated event does not contain event_fingerprint.",
            )

        fingerprint = fingerprint.strip()
        if not fingerprint:
            raise ValueError(
                "Validated event does not contain event_fingerprint.",
            )

        return fingerprint

    @staticmethod
    def _extract_source_event_id(
        event: Mapping[str, Any],
    ) -> str | None:
        source_event_id = event.get("source_event_id")

        if source_event_id is None:
            return None

        if not isinstance(source_event_id, str):
            raise ValueError("source_event_id must be a string.")

        source_event_id = source_event_id.strip()
        return source_event_id or None

    def ingest_many(
        self,
        envelopes: list[SecurityEventEnvelope],
    ) -> list[IngestionResult]:
        return [self.ingest(envelope) for envelope in envelopes]


def ingest_security_event(
    db: Session,
    envelope: SecurityEventEnvelope,
) -> IngestionResult:
    return SecurityEventIngestionPipeline(db).ingest(envelope)
