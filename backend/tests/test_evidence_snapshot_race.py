"""
Concurrency test for the evidence node (open item 4).

Several orchestration runs hit the same investigation at the same moment.
Each snapshot (evidence_type, reference) must land exactly once, and no run
may fail because it lost the race.

Before the partial unique index exists this test can produce duplicate
snapshot rows (check-then-act in code only). After the index plus the
IntegrityError handling in the evidence node, the loser of each race treats
the item as already captured.

Each thread gets its own Session. No Session is shared between threads.
"""

from __future__ import annotations

import threading
from uuid import UUID, uuid4

from sqlalchemy import text

from app.agents.agent_nodes import make_evidence_node
from app.agents.tools.evidence_items import build_evidence_items
from app.core.db import SessionLocal
from app.db.models.alert import Alert
from app.db.models.investigation import Investigation
from app.schemas.investigation import InvestigationCreate
from app.services.investigation_service import InvestigationService

TENANT_ID = UUID("3ea2dc7e-c96f-45d5-8379-ab37092600de")
THREADS = 8
ROUNDS = 5


def _session():
    db = SessionLocal()
    db.info["tenant_id"] = str(TENANT_ID)
    return db


def _create_fixture() -> tuple[UUID, UUID, set[tuple[str, str]]]:
    """Create a temp alert + investigation. Returns (alert_id, inv_id, expected keys)."""
    db = _session()

    try:
        alert = Alert(
            tenant_id=TENANT_ID,
            fingerprint=f"evidence-race-test-{uuid4()}",
            title="Evidence race test alert",
            description="Temporary alert created by evidence race tests.",
            severity="high",
            status="new",
            confidence=90,
            risk_score=80,
            source="test",
            metadata_json={"test": "evidence_snapshot_race"},
        )
        db.add(alert)
        db.commit()
        db.refresh(alert)
        alert_id = alert.id

        investigation = InvestigationService(db).create(
            TENANT_ID,
            InvestigationCreate(
                alert_id=alert_id,
                title="evidence race-test investigation",
                status="investigating",
            ),
        )
        investigation_id = investigation.id

        items = build_evidence_items(
            db,
            tenant_id=TENANT_ID,
            alert_id=alert_id,
        )
        assert items, "fixture alert produced no evidence items"

        expected = {(i["evidence_type"], i["reference"]) for i in items}
        return alert_id, investigation_id, expected

    finally:
        db.rollback()
        db.close()


def _cleanup(ids: dict[str, UUID]) -> None:
    # Guarded: only delete what seeding actually created (lesson 20).
    if not ids:
        return

    db = _session()

    try:
        if "investigation" in ids:
            db.execute(
                text(
                    "DELETE FROM evidence "
                    "WHERE tenant_id = :t AND investigation_id = :i"
                ),
                {"t": TENANT_ID, "i": ids["investigation"]},
            )
            row = db.get(Investigation, ids["investigation"])
            if row is not None:
                db.delete(row)
            db.flush()

        if "alert" in ids:
            alert = db.get(Alert, ids["alert"])
            if alert is not None:
                db.delete(alert)

        db.commit()

    finally:
        db.rollback()
        db.close()


def test_concurrent_evidence_nodes_capture_each_snapshot_once():
    for _ in range(ROUNDS):
        ids: dict[str, UUID] = {}

        try:
            alert_id, investigation_id, expected = _create_fixture()
            ids["alert"] = alert_id
            ids["investigation"] = investigation_id

            barrier = threading.Barrier(THREADS)
            outputs: list[dict] = []
            errors: list[str] = []
            lock = threading.Lock()

            def worker() -> None:
                db = _session()

                try:
                    barrier.wait(timeout=10)

                    node = make_evidence_node(db)
                    out = node(
                        {
                            "tenant_id": str(TENANT_ID),
                            "alert_id": str(alert_id),
                            "investigation_id": str(investigation_id),
                            "plan": [],
                            "completed_steps": [],
                            "findings": {},
                        }
                    )

                    with lock:
                        outputs.append(out)

                except Exception as exc:
                    with lock:
                        errors.append(f"{type(exc).__name__}: {exc}")

                finally:
                    db.rollback()
                    db.close()

            threads = [
                threading.Thread(target=worker, name=f"evidence-race-{n}")
                for n in range(THREADS)
            ]

            for t in threads:
                t.start()
            for t in threads:
                t.join(timeout=30)

            alive = [t.name for t in threads if t.is_alive()]
            assert not alive, f"threads did not finish: {alive}"
            assert not errors, f"worker exceptions: {errors}"
            assert len(outputs) == THREADS

            failed = [o.get("error") for o in outputs if o.get("error")]
            assert not failed, f"runs failed after losing the race: {failed}"

            for out in outputs:
                assert "evidence" in out["completed_steps"]

            check = _session()

            try:
                rows = InvestigationService(check).evidence(
                    TENANT_ID,
                    investigation_id,
                )
                keys = [
                    (e.evidence_type, e.reference)
                    for e in rows
                    if e.reference
                ]
            finally:
                check.rollback()
                check.close()

            assert len(keys) == len(set(keys)), f"duplicate snapshots: {keys}"
            assert set(keys) == expected

        finally:
            _cleanup(ids)