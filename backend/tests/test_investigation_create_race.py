"""
Integration tests for the InvestigationService.create() race-condition fix.

These tests create their own temporary Alert fixtures because the seeded
tenant is not required to contain production-like alert data.

The tests prove two different properties:

1. test_duplicate_create_recovers_via_integrity_error

   Deterministically exercises the IntegrityError recovery path:

       first create
           -> database INSERT succeeds

       second create
           -> unique constraint raises IntegrityError
           -> service rolls back
           -> service queries the existing investigation
           -> existing investigation is returned

2. test_concurrent_creates_yield_one_row

   Uses independent SQLAlchemy Sessions across multiple threads to exercise
   the real concurrent race against the PostgreSQL unique constraint.

Each thread gets its own Session. No Session is shared between threads.

All Alerts and Investigations created by these tests are removed during
cleanup.
"""

from __future__ import annotations

import threading
from uuid import UUID, uuid4

from sqlalchemy import select

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


def _create_test_alert(db) -> Alert:
    alert = Alert(
        tenant_id=TENANT_ID,
        fingerprint=f"investigation-race-test-{uuid4()}",
        title="Investigation race test alert",
        description="Temporary alert created by investigation race tests.",
        severity="high",
        status="new",
        confidence=90,
        risk_score=80,
        source="test",
        metadata_json={
            "test": "investigation_create_race",
        },
    )

    db.add(alert)
    db.commit()
    db.refresh(alert)

    return alert


def _payload(alert_id: UUID) -> InvestigationCreate:
    return InvestigationCreate(
        alert_id=alert_id,
        title="race-test investigation",
        status="investigating",
    )


def _rows_for(db, alert_id: UUID) -> list[Investigation]:
    db.expire_all()

    return list(
        db.scalars(
            select(Investigation).where(
                Investigation.tenant_id == TENANT_ID,
                Investigation.alert_id == alert_id,
            )
        ).all()
    )


def _cleanup(
    alert_ids: list[UUID],
    investigation_ids: set[UUID] | None = None,
) -> None:
    if not alert_ids:
        return

    db = _session()

    try:
        for alert_id in alert_ids:
            rows = _rows_for(db, alert_id)

            for row in rows:
                if (
                    investigation_ids is None
                    or row.id in investigation_ids
                ):
                    db.delete(row)

        db.flush()

        for alert_id in alert_ids:
            alert = db.get(Alert, alert_id)

            if alert is not None:
                db.delete(alert)

        db.commit()

    finally:
        db.rollback()
        db.close()


def test_duplicate_create_recovers_via_integrity_error():
    db = _session()
    alert_id: UUID | None = None
    investigation_ids: set[UUID] = set()

    try:
        alert = _create_test_alert(db)
        alert_id = alert.id

        service = InvestigationService(db)

        first = service.create(
            TENANT_ID,
            _payload(alert_id),
        )
        first_id = first.id
        investigation_ids.add(first_id)

        second = service.create(
            TENANT_ID,
            _payload(alert_id),
        )

        assert second.id == first_id

        rows = _rows_for(db, alert_id)

        assert len(rows) == 1
        assert rows[0].id == first_id

        recovered = service.get_by_alert_id(
            tenant_id=TENANT_ID,
            alert_id=alert_id,
        )

        assert recovered is not None
        assert recovered.id == first_id

    finally:
        db.rollback()
        db.close()

        if alert_id is not None:
            _cleanup(
                [alert_id],
                investigation_ids,
            )


def test_concurrent_creates_yield_one_row():
    setup_db = _session()
    alert_ids: list[UUID] = []

    try:
        for _ in range(ROUNDS):
            alert = _create_test_alert(setup_db)
            alert_ids.append(alert.id)

    finally:
        setup_db.rollback()
        setup_db.close()

    created_investigation_ids: set[UUID] = set()

    try:
        for alert_id in alert_ids:
            barrier = threading.Barrier(THREADS)

            results: list[UUID] = []
            errors: list[str] = []
            lock = threading.Lock()

            def worker() -> None:
                db = _session()

                try:
                    barrier.wait(timeout=10)

                    item = InvestigationService(db).create(
                        TENANT_ID,
                        _payload(alert_id),
                    )

                    with lock:
                        results.append(item.id)

                except Exception as exc:
                    with lock:
                        errors.append(
                            f"{type(exc).__name__}: {exc}"
                        )

                finally:
                    db.rollback()
                    db.close()

            threads = [
                threading.Thread(
                    target=worker,
                    name=f"investigation-race-{index}",
                )
                for index in range(THREADS)
            ]

            for thread in threads:
                thread.start()

            for thread in threads:
                thread.join(timeout=30)

            alive_threads = [
                thread.name
                for thread in threads
                if thread.is_alive()
            ]

            assert not alive_threads, (
                f"alert {alert_id}: worker threads did not finish: "
                f"{alive_threads}"
            )

            assert not errors, (
                f"alert {alert_id}: concurrent create errors: {errors}"
            )

            assert len(results) == THREADS

            assert len(set(results)) == 1, (
                f"alert {alert_id}: multiple investigation IDs returned: "
                f"{set(results)}"
            )

            created_investigation_ids.add(results[0])

            check_db = _session()

            try:
                rows = _rows_for(
                    check_db,
                    alert_id,
                )

                assert len(rows) == 1
                assert rows[0].id == results[0]

            finally:
                check_db.rollback()
                check_db.close()

    finally:
        _cleanup(
            alert_ids,
            created_investigation_ids,
        )
