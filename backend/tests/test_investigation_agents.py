import json
from contextlib import contextmanager
from datetime import datetime, timezone
from uuid import UUID, uuid4

import pytest
from sqlalchemy import delete, select

from app.agents import orchestrator as orch
from app.agents.tools.alert_context import collect_alert_context
from app.agents.tools.mitre_context import collect_mitre_context
from app.agents.tools.threat_intel_context import collect_threat_intel_context
from app.core.db import SessionLocal
from app.db.models.alert import Alert
from app.db.models.detection_rule import DetectionRule
from app.db.models.intelligence import Indicator
from app.db.models.investigation import Evidence, Investigation
from app.db.models.mitre import DetectionRuleTechnique, MitreTechnique
from app.db.models.security_event import SecurityEvent
from app.services.investigation_orchestrator_service import (
    InvestigationOrchestratorService,
    OrchestrationError,
)

# Take both from tests/test_investigation_race.py (the working pair).
# USER_ID must be a real user with a membership in TENANT_ID.
TENANT_ID = UUID("3ea2dc7e-c96f-45d5-8379-ab37092600de")
USER_ID = UUID("5f9e8b7d-2c4a-4d8e-9b6f-1a2b3c4d5e6f")  # VERIFY: likely placeholder


def _session():
    db = SessionLocal()
    # Strings are safe for set_config; if the race test sets UUID objects
    # here instead, match it.
    db.info["tenant_id"] = str(TENANT_ID)
    db.info["user_id"] = str(USER_ID)
    return db


@contextmanager
def seeded_alert(*, with_rule=True, with_event=True, rule_mitre=False,
                 event_extra=None, indicator_value=None):
    """Seed rows for one alert, yield (db, tenant_id, ids), always clean up."""
    tid = TENANT_ID
    db = _session()
    ids = {}
    try:
        rule = event = None

        if with_rule:
            rule = DetectionRule(
                tenant_id=tid,
                name=f"t-rule-{uuid4().hex[:8]}",
                rule_type="query",
                severity="high",
                query="x",
            )
            db.add(rule)
            db.flush()
            ids["rule"] = rule.id

            if rule_mitre:
                tech = db.scalars(select(MitreTechnique).limit(1)).first()
                if tech is None:
                    pytest.skip("MITRE sync has not been run on this DB")
                db.add(DetectionRuleTechnique(
                    detection_rule_id=rule.id,
                    mitre_technique_id=tech.id,
                ))

        if with_event:
            event = SecurityEvent(
                tenant_id=tid,
                source="pytest",
                source_type="test",
                event_type="auth.failure",
                event_time=datetime.now(timezone.utc),
                source_ip="203.0.113.7",
                hostname="pytest-host",
                raw_event=event_extra or {},
            )
            db.add(event)
            db.flush()
            ids["event"] = event.id

        alert = Alert(
            tenant_id=tid,
            fingerprint=uuid4().hex,
            title="pytest alert",
            severity="high",
            detection_rule_id=rule.id if rule else None,
            security_event_id=event.id if event else None,
        )
        db.add(alert)

        if indicator_value:
            db.add(Indicator(
                tenant_id=tid,
                indicator_type="ip",
                value=indicator_value,
                verdict="malicious",
                confidence=90,
                source="pytest",
            ))

        db.flush()
        ids["alert"] = alert.id
        db.commit()

        yield db, tid, ids

    finally:
        db.rollback()

        # Every delete is guarded: a failed seed must never widen into a
        # delete of unrelated tenant rows (e.g. alert_id IS NULL).
        if "alert" in ids:
            db.execute(delete(Investigation).where(
                Investigation.tenant_id == tid,
                Investigation.alert_id == ids["alert"]))  # evidence cascades
            db.execute(delete(Alert).where(Alert.id == ids["alert"]))
        if "event" in ids:
            db.execute(delete(SecurityEvent).where(
                SecurityEvent.id == ids["event"]))
        if "rule" in ids:
            db.execute(delete(DetectionRuleTechnique).where(
                DetectionRuleTechnique.detection_rule_id == ids["rule"]))
            db.execute(delete(DetectionRule).where(
                DetectionRule.id == ids["rule"]))
        if indicator_value:
            db.execute(delete(Indicator).where(
                Indicator.tenant_id == tid,
                Indicator.source == "pytest",
                Indicator.value == indicator_value))
        db.commit()
        db.close()


def _evidence_counts(db, tid, alert_id):
    inv = db.scalar(select(Investigation).where(
        Investigation.tenant_id == tid, Investigation.alert_id == alert_id))
    rows = db.scalars(select(Evidence).where(
        Evidence.tenant_id == tid, Evidence.investigation_id == inv.id)).all()
    counts = {}
    for r in rows:
        counts[r.evidence_type] = counts.get(r.evidence_type, 0) + 1
    return counts


# ---------------- collectors ----------------

def test_alert_context_is_json_safe_and_complete():
    with seeded_alert() as (db, tid, ids):
        result = collect_alert_context(db, tenant_id=tid, alert_id=ids["alert"])
        json.dumps(result["data"])  # must not raise
        assert result["data"]["alert"]["id"] == str(ids["alert"])
        assert result["data"]["rule"]["id"] == str(ids["rule"])
        assert result["data"]["triggering_event"]["id"] == str(ids["event"])
        assert result["data"]["gaps"] == []


def test_collectors_return_none_for_wrong_tenant():
    with seeded_alert() as (db, tid, ids):
        other = uuid4()
        for fn in (collect_alert_context, collect_mitre_context,
                   collect_threat_intel_context):
            assert fn(db, tenant_id=other, alert_id=ids["alert"]) is None


def test_alert_with_no_rule_or_event_reports_gaps():
    with seeded_alert(with_rule=False, with_event=False) as (db, tid, ids):
        result = collect_alert_context(db, tenant_id=tid, alert_id=ids["alert"])
        assert {"no_rule_linked", "no_event_linked"} <= set(result["data"]["gaps"])


def test_mitre_context_empty_mapping_is_ok_with_gap():
    with seeded_alert(rule_mitre=False) as (db, tid, ids):
        result = collect_mitre_context(db, tenant_id=tid, alert_id=ids["alert"])
        json.dumps(result["data"])
        assert "rule_has_no_mitre_mapping" in result["data"]["gaps"]


def test_mitre_context_enriches_mapped_technique():
    with seeded_alert(rule_mitre=True) as (db, tid, ids):
        result = collect_mitre_context(db, tenant_id=tid, alert_id=ids["alert"])
        json.dumps(result["data"])
        assert result["data"]["techniques_total"] == 1
        assert result["data"]["techniques"][0]["domain"] in (
            "enterprise-attack", "ics-attack", "mobile-attack")


def test_threat_intel_matches_typed_column():
    with seeded_alert(indicator_value="203.0.113.7") as (db, tid, ids):
        result = collect_threat_intel_context(
            db, tenant_id=tid, alert_id=ids["alert"])
        json.dumps(result["data"])
        assert result["data"]["matches_total"] == 1
        assert result["data"]["matches"][0]["matched_on"] == ["source_ip"]
        assert result["data"]["matches"][0]["verdict"] == "malicious"


def test_threat_intel_matches_nested_payload_value():
    payload = {"file": {"hash": "abc123def456"}}
    with seeded_alert(event_extra=payload, indicator_value="ABC123DEF456") as (
            db, tid, ids):
        result = collect_threat_intel_context(
            db, tenant_id=tid, alert_id=ids["alert"])
        assert result["data"]["matches_total"] == 1  # case-insensitive
        assert result["data"]["matches"][0]["matched_on"] == ["raw_event.file.hash"]


def test_threat_intel_no_match_carries_caveat():
    with seeded_alert() as (db, tid, ids):
        result = collect_threat_intel_context(
            db, tenant_id=tid, alert_id=ids["alert"])
        assert result["data"]["matches_total"] == 0
        assert "not evidence the values are benign" in result["note"]


# ---------------- full graph ----------------

def test_full_run_fully_linked_alert():
    with seeded_alert() as (db, tid, ids):
        result = InvestigationOrchestratorService(db).run_for_alert(
            tenant_id=tid, alert_id=ids["alert"])
        assert result["completed_steps"] == [
            "planner", "query", "evidence", "mitre", "threat_intel", "reporting"]
        assert result["findings"]["query"]["status"] == "ok"
        assert result["findings"]["query"]["data"]["alert"]["id"] == str(ids["alert"])
        assert "ot_context" not in result["findings"]
        counts = _evidence_counts(db, tid, ids["alert"])
        assert counts["alert"] == 1
        assert counts["detection_rule"] == 1
        assert counts["security_event"] == 1
        assert counts["agent_summary"] == 1


def test_full_run_alert_without_rule_or_event():
    with seeded_alert(with_rule=False, with_event=False) as (db, tid, ids):
        result = InvestigationOrchestratorService(db).run_for_alert(
            tenant_id=tid, alert_id=ids["alert"])
        assert result["completed_steps"] == [
            "planner", "query", "evidence", "reporting"]
        counts = _evidence_counts(db, tid, ids["alert"])
        assert counts == {"alert": 1, "agent_summary": 1}


def test_rerun_is_idempotent_for_snapshot_evidence():
    with seeded_alert() as (db, tid, ids):
        svc = InvestigationOrchestratorService(db)
        svc.run_for_alert(tenant_id=tid, alert_id=ids["alert"])
        svc.run_for_alert(tenant_id=tid, alert_id=ids["alert"])
        counts = _evidence_counts(db, tid, ids["alert"])
        assert counts["alert"] == 1
        assert counts["detection_rule"] == 1
        assert counts["security_event"] == 1
        assert counts["agent_summary"] == 2  # one per run, by design
        invs = db.scalars(select(Investigation).where(
            Investigation.tenant_id == tid,
            Investigation.alert_id == ids["alert"])).all()
        assert len(invs) == 1


def test_oversized_raw_event_keeps_hash_but_drops_body():
    big = {"blob": "x" * 20000}
    with seeded_alert(event_extra=big) as (db, tid, ids):
        InvestigationOrchestratorService(db).run_for_alert(
            tenant_id=tid, alert_id=ids["alert"])
        row = db.scalars(select(Evidence).where(
            Evidence.tenant_id == tid,
            Evidence.evidence_type == "security_event",
            Evidence.reference == f"security_event:{ids['event']}")).one()
        meta = row.metadata_json
        assert meta["raw_event_truncated"] is True
        assert meta["raw_event"] is None
        assert len(meta["raw_event_sha256"]) == 64


# ---------------- failure behavior ----------------

def test_missing_alert_raises_orchestration_error():
    db = _session()
    try:
        with pytest.raises(OrchestrationError):
            InvestigationOrchestratorService(db).run_for_alert(
                tenant_id=TENANT_ID, alert_id=uuid4())
    finally:
        db.close()


def test_node_error_carries_run_context(monkeypatch):
    def failing_factory(db):
        def node(state):
            return {**state, "error": "boom", "failed_step": "query"}
        node.__name__ = "query"
        return node

    monkeypatch.setitem(orch._AGENT_FACTORIES, "query", failing_factory)
    with seeded_alert() as (db, tid, ids):
        with pytest.raises(OrchestrationError) as exc:
            InvestigationOrchestratorService(db).run_for_alert(
                tenant_id=tid, alert_id=ids["alert"])
        assert exc.value.failed_step == "query"
        assert exc.value.investigation_id is not None
        assert exc.value.run_id is not None
        assert exc.value.completed_steps == ["planner"]


def test_node_that_never_completes_hits_loop_backstop(monkeypatch):
    def looping_factory(db):
        def node(state):
            return state  # neither completes nor errors
        node.__name__ = "query"
        return node

    monkeypatch.setitem(orch._AGENT_FACTORIES, "query", looping_factory)
    with seeded_alert() as (db, tid, ids):
        with pytest.raises(OrchestrationError, match="step limit"):
            InvestigationOrchestratorService(db).run_for_alert(
                tenant_id=tid, alert_id=ids["alert"])