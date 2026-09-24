# app/ingestion/pipeline.py

from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models.detection_rule import DetectionRule, DetectionRuleType
from app.db.repositories.alert_repo import AlertRepository
from app.db.repositories.canary_match_repo import CanaryMatchRepository
from app.db.repositories.detection_match_repo import DetectionMatchRepository
from app.db.repositories.detection_rule_repo import DetectionRuleRepository
from app.db.repositories.quarantined_event_repo import (
    QuarantinedEventRepository,
)
from app.ingestion.models import IngestionResult, SecurityEventEnvelope
from app.ingestion.normalizer import SecurityEventNormalizer
from app.ingestion.validators import SecurityEventValidator
from app.schemas.alert import AlertCreate
from app.schemas.security_event import SecurityEventCreate
from app.services.audit_service import record_audit_event
from app.services.detection_rules.matching import (
    build_fingerprint,
    evaluate_rule_for_event,
)
from app.services.security_event_service import SecurityEventService


logger = logging.getLogger(__name__)

_ALERT_TERMINAL_STATUSES = {
    "resolved",
    "false_positive",
}
_ALERT_REOPEN_STATUS = "open"


class SecurityEventIngestionPipeline:
    """Normalize, validate, deduplicate, and persist security events."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.normalizer = SecurityEventNormalizer()
        self.events = SecurityEventService(db)
        self.quarantine = QuarantinedEventRepository(db)
        self.rules = DetectionRuleRepository(db)
        self.alerts = AlertRepository(db)
        self.detection_matches = DetectionMatchRepository(db)
        self.canary_matches = CanaryMatchRepository(db)

    def ingest(
        self,
        envelope: SecurityEventEnvelope,
    ) -> IngestionResult:
        tenant_id = envelope.tenant_id
        stage = "normalization"
        normalized_payload: dict[str, Any] | None = None

        try:
            normalized = self.normalizer.normalize(envelope)
            normalized_payload = self._model_to_mapping(normalized)

            stage = "validation"

            validated_payload = SecurityEventValidator(
                authenticated_tenant_id=tenant_id,
            ).validate(normalized_payload)

            stage = "persistence"

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

            try:
                self._evaluate_detection_rules(event)
            except Exception:
                logger.exception(
                    "Detection rule evaluation crashed for event %s",
                    event.id,
                )

            return IngestionResult.accepted_event(
                event_id=event.id,
                tenant_id=tenant_id,
                fingerprint=fingerprint,
            )

        except Exception as exc:
            self.db.rollback()

            self._quarantine(
                envelope=envelope,
                stage=stage,
                reason=str(exc),
                normalized_payload=normalized_payload,
            )

            return IngestionResult.rejected_event(
                tenant_id=tenant_id,
                message=str(exc),
            )

    def ingest_many(
        self,
        envelopes: list[SecurityEventEnvelope],
    ) -> list[IngestionResult]:
        return [
            self.ingest(envelope)
            for envelope in envelopes
        ]

    def _quarantine(
        self,
        *,
        envelope: SecurityEventEnvelope,
        stage: str,
        reason: str,
        normalized_payload: dict[str, Any] | None,
    ) -> None:
        try:
            self.quarantine.create(
                tenant_id=envelope.tenant_id,
                source=envelope.source,
                source_type=envelope.source_type,
                failure_stage=stage,
                failure_reason=reason,
                raw_payload=envelope.raw_payload,
                received_at=envelope.received_at,
                partial_normalized=normalized_payload,
            )
            self.db.commit()
        except Exception:
            self.db.rollback()

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
            raise ValueError(
                "source_event_id must be a string.",
            )

        source_event_id = source_event_id.strip()

        return source_event_id or None

    def _evaluate_detection_rules(
        self,
        event: Any,
    ) -> None:
        """Run CANARY and PRODUCTION rules against a persisted event."""
        tenant_id = event.tenant_id

        try:
            canary_rules = self.rules.list(
                tenant_id=tenant_id,
                status="canary",
                enabled=True,
            )
        except Exception:
            logger.exception(
                "Failed to list canary rules for tenant %s "
                "(event %s)",
                tenant_id,
                event.id,
            )
            canary_rules = []

        for rule in canary_rules:
            try:
                self._evaluate_canary_rule(
                    rule,
                    event,
                )
            except Exception:
                logger.exception(
                    "Canary rule %s evaluation failed for event %s "
                    "(tenant %s)",
                    rule.id,
                    event.id,
                    tenant_id,
                )

        try:
            production_rules = self.rules.list_production_rules(
                tenant_id=tenant_id,
            )
        except Exception:
            logger.exception(
                "Failed to list production rules for tenant %s "
                "(event %s)",
                tenant_id,
                event.id,
            )
            production_rules = []

        for rule in production_rules:
            try:
                self._evaluate_production_rule(
                    rule,
                    event,
                )
            except Exception:
                logger.exception(
                    "Production rule %s evaluation failed for event %s "
                    "(tenant %s)",
                    rule.id,
                    event.id,
                    tenant_id,
                )

    def _evaluate_canary_rule(
        self,
        rule: DetectionRule,
        event: Any,
    ) -> None:
        tenant_id = event.tenant_id

        candidates = evaluate_rule_for_event(
            session=self.db,
            tenant_id=tenant_id,
            rule=rule,
            event=event,
        )

        for candidate in candidates:
            self.canary_matches.create(
                tenant_id=tenant_id,
                data={
                    "detection_rule_id": rule.id,
                    "group_key": candidate.group_key,
                    "metric_value": candidate.metric_value,
                    "event_ids": candidate.event_ids,
                },
            )

    def _evaluate_production_rule(
        self,
        rule: DetectionRule,
        event: Any,
    ) -> None:
        tenant_id = event.tenant_id
        rule_type = DetectionRuleType(rule.rule_type)

        candidates = evaluate_rule_for_event(
            session=self.db,
            tenant_id=tenant_id,
            rule=rule,
            event=event,
        )

        for candidate in candidates:
            match = self.detection_matches.create(
                tenant_id=tenant_id,
                data={
                    "security_event_id": event.id,
                    "detection_rule_id": rule.id,
                    "match_data": {
                        "group_key": candidate.group_key,
                        "metric_value": candidate.metric_value,
                        "event_ids": [
                            str(event_id)
                            for event_id in candidate.event_ids
                        ],
                        "window_start": (
                            candidate.window_start.isoformat()
                        ),
                        "window_end": (
                            candidate.window_end.isoformat()
                        ),
                    },
                },
            )

            fingerprint = build_fingerprint(
                rule_id=rule.id,
                rule_type=rule_type,
                candidate=candidate,
                event=event,
            )

            existing = self.alerts.get_by_fingerprint(
                tenant_id=tenant_id,
                fingerprint=fingerprint,
            )

            if existing is not None:
                self._append_match_to_alert(
                    existing,
                    match,
                    event,
                )
                continue

            payload = AlertCreate(
                fingerprint=fingerprint,
                title=f"{rule.name} triggered",
                description=rule.description,
                severity=rule.severity,
                detection_rule_id=rule.id,
                security_event_id=event.id,
                source="detection_engine",
                metadata_json={
                    "detection_match_ids": [str(match.id)],
                    "match_count": 1,
                    "group_key": candidate.group_key,
                },
            )

            try:
                self.alerts.create(
                    tenant_id=tenant_id,
                    data=payload.model_dump(),
                )
            except IntegrityError:
                self.db.rollback()

                existing = self.alerts.get_by_fingerprint(
                    tenant_id=tenant_id,
                    fingerprint=fingerprint,
                )

                if existing is None:
                    raise

                self._append_match_to_alert(
                    existing,
                    match,
                    event,
                )

    def _append_match_to_alert(
        self,
        existing: Any,
        match: Any,
        event: Any,
    ) -> None:
        metadata = dict(existing.metadata_json or {})

        match_ids = metadata.get(
            "detection_match_ids",
            [],
        )
        match_ids.append(str(match.id))

        metadata["detection_match_ids"] = match_ids[-50:]
        metadata["match_count"] = (
            metadata.get("match_count", 0) + 1
        )

        update_data: dict[str, Any] = {
            "last_seen_at": event.event_time,
            "metadata_json": metadata,
        }

        # Only reopen and audit an actual state change. Routine match
        # updates on an already-open alert do not create audit noise.
        was_reopened = existing.status in _ALERT_TERMINAL_STATUSES
        previous_status = existing.status

        if was_reopened:
            update_data["status"] = _ALERT_REOPEN_STATUS

        self.alerts.update(
            tenant_id=existing.tenant_id,
            alert_id=existing.id,
            data=update_data,
        )

        if was_reopened:
            # alerts.update() commits internally in this codebase.
            # record_audit_event() does not commit, so commit the audit
            # record explicitly in its own transaction.
            record_audit_event(
                self.db,
                tenant_id=existing.tenant_id,
                actor_user_id=None,
                action="alert.reopened",
                entity_type="alert",
                entity_id=existing.id,
                payload={
                    "previous_status": previous_status,
                    "new_status": _ALERT_REOPEN_STATUS,
                    "triggering_detection_match_id": str(match.id),
                },
            )
            self.db.commit()


def ingest_security_event(
    db: Session,
    envelope: SecurityEventEnvelope,
) -> IngestionResult:
    return SecurityEventIngestionPipeline(db).ingest(envelope)
