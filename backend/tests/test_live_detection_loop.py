# tests/test_live_detection_loop.py
from __future__ import annotations

import json
from uuid import UUID

import pytest
from sqlalchemy.orm import Session

from app.core.db import SessionLocal
from app.db.models.alert import Alert
from app.db.models.detection_rule import DetectionRule
from app.db.models.membership import Membership
from app.db.models.operations import DetectionMatch
from app.db.models.security_event import SecurityEvent
from app.ingestion.models import SecurityEventEnvelope
from app.ingestion.pipeline import SecurityEventIngestionPipeline

TENANT_ID = UUID("3ea2dc7e-c96f-45d5-8379-ab37092600de")


@pytest.fixture
def db():
    session = SessionLocal()
    session.info["tenant_id"] = str(TENANT_ID)

    try:
        yield session
    finally:
        session.rollback()
        session.close()


def get_membership(db: Session, role_key: str) -> Membership:
    membership = (
        db.query(Membership)
        .filter(
            Membership.tenant_id == TENANT_ID,
            Membership.role == role_key,
        )
        .first()
    )

    assert membership is not None, (
        f"No {role_key} membership found for tenant {TENANT_ID}"
    )

    return membership


def make_envelope(*, source_event_id: str, event_type: str = "suspicious_login"):
    return SecurityEventEnvelope(
        tenant_id=TENANT_ID,
        source="test-source",
        source_type="test",
        source_event_id=source_event_id,
        raw_payload={"event_type": event_type, "message": "live detection loop test"},
    )


def test_production_query_rule_creates_alert_then_dedupes_on_second_match(db: Session):
    membership = get_membership(db, "ADMIN")
    db.info["user_id"] = str(membership.user_id)

    rule = DetectionRule(
        tenant_id=TENANT_ID,
        name="Live Loop Test - suspicious login",
        description="Verification rule for the live detection loop test",
        rule_type="query",
        severity="high",
        query=json.dumps({"field": "event_type", "op": "eq", "value": "suspicious_login"}),
        configuration={},
        status="production",
        enabled=True,
        author="live-detection-loop-test",
        source="integration-test",
        created_by_id=membership.user_id,
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)

    pipeline = SecurityEventIngestionPipeline(db)

    try:
        # First matching event: expect a new Alert + one DetectionMatch.
        result_1 = pipeline.ingest(make_envelope(source_event_id="live-loop-test-evt-1"))
        assert result_1.accepted and not result_1.duplicate, result_1.message

        alerts = (
            db.query(Alert)
            .filter(Alert.tenant_id == TENANT_ID, Alert.detection_rule_id == rule.id)
            .all()
        )
        assert len(alerts) == 1, f"expected 1 alert, got {len(alerts)}"
        first_alert = alerts[0]
        assert first_alert.metadata_json.get("match_count") == 1

        # Second, distinct matching event: expect the SAME alert updated
        # (fingerprint dedup), not a second row -- this is the path that
        # would otherwise hit the UNIQUE(tenant_id, fingerprint) constraint
        # on a naive insert.
        result_2 = pipeline.ingest(make_envelope(source_event_id="live-loop-test-evt-2"))
        assert result_2.accepted and not result_2.duplicate, result_2.message

        db.refresh(first_alert)
        alerts_after = (
            db.query(Alert)
            .filter(Alert.tenant_id == TENANT_ID, Alert.detection_rule_id == rule.id)
            .all()
        )
        assert len(alerts_after) == 1, "expected dedup, not a second alert row"
        assert first_alert.metadata_json.get("match_count") == 2
        assert len(first_alert.metadata_json.get("detection_match_ids", [])) == 2

        matches = (
            db.query(DetectionMatch)
            .filter(DetectionMatch.tenant_id == TENANT_ID, DetectionMatch.detection_rule_id == rule.id)
            .all()
        )
        assert len(matches) == 2, f"expected 2 DetectionMatch rows, got {len(matches)}"

    finally:
        # Manual cleanup, matching this repo's convention (repo methods
        # commit internally, so session rollback alone won't undo this).
        cleanup_db = SessionLocal()
        try:
            cleanup_db.info["tenant_id"] = str(TENANT_ID)

            cleanup_db.query(DetectionMatch).filter(
                DetectionMatch.tenant_id == TENANT_ID,
                DetectionMatch.detection_rule_id == rule.id,
            ).delete(synchronize_session=False)

            cleanup_db.query(Alert).filter(
                Alert.tenant_id == TENANT_ID,
                Alert.detection_rule_id == rule.id,
            ).delete(synchronize_session=False)

            cleanup_db.query(SecurityEvent).filter(
                SecurityEvent.tenant_id == TENANT_ID,
                SecurityEvent.source_event_id.in_(
                    ["live-loop-test-evt-1", "live-loop-test-evt-2"]
                ),
            ).delete(synchronize_session=False)

            cleanup_db.query(DetectionRule).filter(
                DetectionRule.id == rule.id,
            ).delete(synchronize_session=False)

            cleanup_db.commit()
        finally:
            cleanup_db.rollback()
            cleanup_db.close()