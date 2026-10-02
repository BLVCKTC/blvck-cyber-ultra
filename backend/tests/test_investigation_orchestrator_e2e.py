"""
End-to-end integration tests for the investigation orchestrator.

These tests exercise the real InvestigationOrchestratorService against the
real database and the real LangGraph investigation graph.

The planner is deterministic and narrows the default plan according to the
records linked to the Alert. The fully-linked case seeds a real
DetectionRule and SecurityEvent so it is not pretending that an unlinked
Alert is fully linked.

Notes on what the persisted records contain:

- The summary text and the agent_summary metadata are built BEFORE the
  reporting node appends "reporting" to completed_steps, so they list the
  steps up to and including the last agent, but not "reporting" itself.
- ot_context is always skipped until site/zone modeling exists, so even the
  fully-linked planner finding has a non-empty "skipped" mapping.

Tests:

1. test_orchestrator_end_to_end_writes_real_rows (fully linked, run twice)
2. test_orchestrator_alert_without_rule_or_event_uses_minimal_plan
3. test_collect_alert_context_is_json_serializable
4. test_collect_alert_context_rejects_cross_tenant_alert
5. test_orchestrator_unknown_alert_raises_and_creates_nothing
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from uuid import UUID, uuid4

import pytest
from sqlalchemy import delete, select

from app.agents.tools.alert_context import collect_alert_context
from app.core.db import SessionLocal
from app.db.models.alert import Alert
from app.db.models.detection_rule import DetectionRule
from app.db.models.investigation import Evidence, Investigation
from app.db.models.security_event import SecurityEvent
from app.services.investigation_orchestrator_service import (
    InvestigationOrchestratorService,
    OrchestrationError,
)

TENANT_ID = UUID("3ea2dc7e-c96f-45d5-8379-ab37092600de")

EXPECTED_FULL_PLAN = ["query", "evidence", "mitre", "threat_intel"]

# Final state: includes reporting.
EXPECTED_FULL_COMPLETED_STEPS = [
    "planner",
    "query",
    "evidence",
    "mitre",
    "threat_intel",
    "reporting",
]

# Persisted summary/metadata: reporting has not been appended yet.
EXPECTED_FULL_PERSISTED_STEPS = EXPECTED_FULL_COMPLETED_STEPS[:-1]

EXPECTED_MINIMAL_PLAN = ["query", "evidence"]

EXPECTED_MINIMAL_COMPLETED_STEPS = [
    "planner",
    "query",
    "evidence",
    "reporting",
]

EXPECTED_MINIMAL_PERSISTED_STEPS = EXPECTED_MINIMAL_COMPLETED_STEPS[:-1]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _session():
    db = SessionLocal()
    db.info["tenant_id"] = str(TENANT_ID)
    return db


def _create_test_alert(
    db,
    *,
    detection_rule_id: UUID | None = None,
    security_event_id: UUID | None = None,
) -> Alert:
    alert = Alert(
        tenant_id=TENANT_ID,
        fingerprint=f"investigation-orchestrator-test-{uuid4()}",
        title="Investigation orchestrator test alert",
        description="Temporary alert created by orchestrator tests.",
        severity="high",
        status="new",
        confidence=90,
        risk_score=80,
        source="test",
        detection_rule_id=detection_rule_id,
        security_event_id=security_event_id,
        metadata_json={"test": "investigation_orchestrator_e2e"},
    )

    db.add(alert)
    db.commit()
    db.refresh(alert)

    return alert


def _create_fully_linked_alert(db) -> tuple[Alert, UUID, UUID]:
    """
    Seed a real DetectionRule and SecurityEvent, then an Alert linked to
    both. Returns (alert, rule_id, event_id) so cleanup can remove all three.
    """
    rule = DetectionRule(
        tenant_id=TENANT_ID,
        name=f"e2e-rule-{uuid4().hex[:8]}",
        rule_type="query",
        severity="high",
        query="x",
    )
    event = SecurityEvent(
        tenant_id=TENANT_ID,
        source="pytest",
        source_type="test",
        event_type="auth.failure",
        event_time=datetime.now(timezone.utc),
        source_ip="203.0.113.7",
        hostname="pytest-host",
        raw_event={},
    )
    db.add_all([rule, event])
    db.flush()

    rule_id, event_id = rule.id, event.id
    db.commit()

    alert = _create_test_alert(
        db,
        detection_rule_id=rule_id,
        security_event_id=event_id,
    )

    return alert, rule_id, event_id


def _investigations_for(db, alert_id: UUID) -> list[Investigation]:
    db.expire_all()

    return list(
        db.scalars(
            select(Investigation).where(
                Investigation.tenant_id == TENANT_ID,
                Investigation.alert_id == alert_id,
            )
        ).all()
    )


def _evidence_for(db, investigation_id: UUID) -> list[Evidence]:
    db.expire_all()

    return list(
        db.scalars(
            select(Evidence).where(
                Evidence.tenant_id == TENANT_ID,
                Evidence.investigation_id == investigation_id,
            )
        ).all()
    )


def _evidence_for_run(rows: list[Evidence], run_id: str) -> list[Evidence]:
    return [
        evidence
        for evidence in rows
        if (evidence.metadata_json or {}).get("run_id") == run_id
    ]


def _type_counts(rows: list[Evidence]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        counts[row.evidence_type] = counts.get(row.evidence_type, 0) + 1
    return counts


def _summary_steps(summary: str) -> list[str]:
    """
    Step names from the '- step: note' lines of an investigation summary.

    Substring checks are unreliable here: the planner line legitimately
    mentions skipped steps ("skipped: mitre, threat_intel, ...").
    """
    return [
        line[2:].split(":", 1)[0]
        for line in summary.splitlines()
        if line.startswith("- ")
    ]


def _cleanup(
    db,
    alert_id: UUID,
    *,
    rule_id: UUID | None = None,
    event_id: UUID | None = None,
) -> None:
    """
    Remove everything a test created. Every delete is scoped to this
    alert's own rows, so a failed setup can never widen into other data.
    """
    try:
        db.rollback()

        investigation_ids = list(
            db.scalars(
                select(Investigation.id).where(
                    Investigation.tenant_id == TENANT_ID,
                    Investigation.alert_id == alert_id,
                )
            ).all()
        )

        if investigation_ids:
            db.execute(
                delete(Evidence).where(
                    Evidence.investigation_id.in_(investigation_ids)
                )
            )
            db.execute(
                delete(Investigation).where(
                    Investigation.id.in_(investigation_ids)
                )
            )

        db.execute(delete(Alert).where(Alert.id == alert_id))

        if event_id is not None:
            db.execute(
                delete(SecurityEvent).where(SecurityEvent.id == event_id)
            )

        if rule_id is not None:
            db.execute(
                delete(DetectionRule).where(DetectionRule.id == rule_id)
            )

        db.commit()

    finally:
        db.rollback()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_orchestrator_end_to_end_writes_real_rows():
    """
    A fully linked Alert executes the planner-selected full path, and a
    second run adds exactly one new summary row without duplicating the
    snapshot evidence.
    """
    db = _session()

    alert_id: UUID | None = None
    rule_id: UUID | None = None
    event_id: UUID | None = None

    try:
        alert, rule_id, event_id = _create_fully_linked_alert(db)
        alert_id = alert.id

        assert alert.detection_rule_id is not None
        assert alert.security_event_id is not None

        service = InvestigationOrchestratorService(db)

        # ----------------------------- run 1 -----------------------------
        result1 = service.run_for_alert(
            tenant_id=TENANT_ID,
            alert_id=alert.id,
        )

        assert result1.get("error") is None
        assert result1.get("failed_step") is None
        assert result1.get("investigation_id")
        assert result1.get("run_id")

        assert result1["completed_steps"] == EXPECTED_FULL_COMPLETED_STEPS
        assert result1["plan"] == EXPECTED_FULL_PLAN

        assert set(result1["findings"]) == {
            "planner",
            "query",
            "evidence",
            "mitre",
            "threat_intel",
        }
        assert "ot_context" not in result1["findings"]
        assert "reporting" not in result1["findings"]

        for step in ("planner", "query", "evidence", "mitre", "threat_intel"):
            assert result1["findings"][step]["status"] == "ok", (
                f"{step} is still a stub or failed: "
                f"{result1['findings'][step]}"
            )

        planner_finding = result1["findings"]["planner"]
        assert planner_finding["data"]["selected"] == EXPECTED_FULL_PLAN
        # ot_context is always skipped until site/zone modeling exists.
        assert set(planner_finding["data"]["skipped"]) == {"ot_context"}
        assert planner_finding["note"].startswith(
            "plan: query, evidence, mitre, threat_intel"
        )

        assert (
            result1["findings"]["query"]["data"]["alert"]["id"]
            == str(alert.id)
        )

        investigations = _investigations_for(db, alert.id)
        assert len(investigations) == 1

        investigation = investigations[0]

        assert str(investigation.id) == result1["investigation_id"]
        assert investigation.alert_id == alert.id
        assert investigation.tenant_id == TENANT_ID
        assert investigation.summary is not None
        assert investigation.summary.startswith(
            "Automated investigation pass completed."
        )
        assert _summary_steps(investigation.summary) == (
            EXPECTED_FULL_PERSISTED_STEPS
        )

        all_evidence = _evidence_for(db, investigation.id)

        # Snapshot evidence from the Evidence node plus one summary row.
        assert _type_counts(all_evidence) == {
            "alert": 1,
            "detection_rule": 1,
            "security_event": 1,
            "agent_summary": 1,
        }

        first_run_evidence = _evidence_for_run(all_evidence, result1["run_id"])
        assert len(first_run_evidence) == 1

        first_evidence = first_run_evidence[0]
        first_meta = first_evidence.metadata_json or {}

        assert first_evidence.tenant_id == TENANT_ID
        assert first_evidence.investigation_id == investigation.id
        assert first_evidence.evidence_type == "agent_summary"
        assert first_evidence.title == "Orchestrator run summary"
        assert first_meta.get("run_id") == result1["run_id"]
        assert first_meta.get("completed_steps") == (
            EXPECTED_FULL_PERSISTED_STEPS
        )
        assert first_meta.get("plan") == EXPECTED_FULL_PLAN
        assert set(first_meta.get("findings", {})) == set(
            EXPECTED_FULL_PERSISTED_STEPS
        )

        # ----------------------------- run 2 -----------------------------
        result2 = service.run_for_alert(
            tenant_id=TENANT_ID,
            alert_id=alert.id,
        )

        assert result2.get("error") is None
        assert result2.get("failed_step") is None
        assert result2["run_id"] != result1["run_id"]
        assert result2["investigation_id"] == result1["investigation_id"]
        assert result2["completed_steps"] == EXPECTED_FULL_COMPLETED_STEPS
        assert result2["plan"] == EXPECTED_FULL_PLAN

        for step in ("planner", "query", "evidence", "mitre", "threat_intel"):
            assert result2["findings"][step]["status"] == "ok"

        # The second run found everything already captured.
        assert result2["findings"]["evidence"]["data"]["created"] == []
        assert len(
            result2["findings"]["evidence"]["data"]["skipped_existing"]
        ) == 3

        investigations = _investigations_for(db, alert.id)
        assert len(investigations) == 1
        assert str(investigations[0].id) == result1["investigation_id"]

        all_evidence = _evidence_for(db, investigation.id)

        # Snapshots are not duplicated; only summaries accumulate.
        assert _type_counts(all_evidence) == {
            "alert": 1,
            "detection_rule": 1,
            "security_event": 1,
            "agent_summary": 2,
        }

        assert len(_evidence_for_run(all_evidence, result1["run_id"])) == 1

        second_run_evidence = _evidence_for_run(
            all_evidence, result2["run_id"]
        )
        assert len(second_run_evidence) == 1

        second_evidence = second_run_evidence[0]
        second_meta = second_evidence.metadata_json or {}

        assert second_evidence.id != first_evidence.id
        assert second_evidence.evidence_type == "agent_summary"
        assert second_meta.get("run_id") == result2["run_id"]
        assert second_meta.get("completed_steps") == (
            EXPECTED_FULL_PERSISTED_STEPS
        )
        assert second_meta.get("plan") == EXPECTED_FULL_PLAN

    finally:
        if alert_id is not None:
            _cleanup(db, alert_id, rule_id=rule_id, event_id=event_id)

        db.close()


def test_orchestrator_alert_without_rule_or_event_uses_minimal_plan():
    db = _session()

    alert_id: UUID | None = None

    try:
        alert = _create_test_alert(db)
        alert_id = alert.id

        assert alert.detection_rule_id is None
        assert alert.security_event_id is None

        service = InvestigationOrchestratorService(db)

        result = service.run_for_alert(
            tenant_id=TENANT_ID,
            alert_id=alert.id,
        )

        assert result.get("error") is None
        assert result.get("failed_step") is None
        assert result.get("investigation_id")
        assert result.get("run_id")

        assert result["plan"] == EXPECTED_MINIMAL_PLAN
        assert result["completed_steps"] == EXPECTED_MINIMAL_COMPLETED_STEPS

        assert set(result["findings"]) == {"planner", "query", "evidence"}

        for step in ("mitre", "threat_intel", "ot_context"):
            assert step not in result["findings"]

        planner_finding = result["findings"]["planner"]

        assert planner_finding["status"] == "ok"
        assert planner_finding["data"]["selected"] == EXPECTED_MINIMAL_PLAN

        skipped = planner_finding["data"]["skipped"]
        for step in ("mitre", "threat_intel", "ot_context"):
            assert step in skipped

        assert "plan: query, evidence" in planner_finding["note"]
        assert "mitre" in planner_finding["note"]
        assert "threat_intel" in planner_finding["note"]

        query_finding = result["findings"]["query"]
        assert query_finding["status"] == "ok"
        assert query_finding["data"]["alert"]["id"] == str(alert.id)

        assert result["findings"]["evidence"]["status"] == "ok"

        investigations = _investigations_for(db, alert.id)
        assert len(investigations) == 1

        investigation = investigations[0]

        assert investigation.summary is not None

        # Line-based, not substring: the planner line names skipped steps.
        assert _summary_steps(investigation.summary) == (
            EXPECTED_MINIMAL_PERSISTED_STEPS
        )

        all_evidence = _evidence_for(db, investigation.id)

        # Only the alert snapshot plus the run summary: no rule, no event.
        assert _type_counts(all_evidence) == {
            "alert": 1,
            "agent_summary": 1,
        }

        run_evidence = _evidence_for_run(all_evidence, result["run_id"])
        assert len(run_evidence) == 1

        meta = run_evidence[0].metadata_json or {}

        assert meta.get("plan") == EXPECTED_MINIMAL_PLAN
        assert meta.get("completed_steps") == EXPECTED_MINIMAL_PERSISTED_STEPS
        assert set(meta.get("findings", {})) == set(
            EXPECTED_MINIMAL_PERSISTED_STEPS
        )

    finally:
        if alert_id is not None:
            _cleanup(db, alert_id)

        db.close()


def test_collect_alert_context_is_json_serializable():
    db = _session()

    alert_id: UUID | None = None

    try:
        alert = _create_test_alert(db)
        alert_id = alert.id

        context = collect_alert_context(
            db,
            tenant_id=TENANT_ID,
            alert_id=alert.id,
        )

        assert context is not None
        assert context.get("data") is not None

        json.dumps(context["data"])

    finally:
        if alert_id is not None:
            _cleanup(db, alert_id)

        db.close()


def test_collect_alert_context_rejects_cross_tenant_alert():
    db = _session()

    alert_id: UUID | None = None

    try:
        alert = _create_test_alert(db)
        alert_id = alert.id

        context = collect_alert_context(
            db,
            tenant_id=uuid4(),
            alert_id=alert.id,
        )

        assert context is None

    finally:
        if alert_id is not None:
            _cleanup(db, alert_id)

        db.close()


def test_orchestrator_unknown_alert_raises_and_creates_nothing():
    db = _session()

    try:
        missing_alert_id = uuid4()

        service = InvestigationOrchestratorService(db)

        with pytest.raises(OrchestrationError, match="not found"):
            service.run_for_alert(
                tenant_id=TENANT_ID,
                alert_id=missing_alert_id,
            )

        assert _investigations_for(db, missing_alert_id) == []

    finally:
        db.rollback()
        db.close()