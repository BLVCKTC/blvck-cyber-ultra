"""
HTTP-level RBAC and error-mapping tests for the investigation orchestrator
route: POST /api/v1/tenants/{tenant_id}/investigations/orchestrate/{alert_id}

Follows the pattern of test_detection_rule_http_rbac.py: get_db,
get_current_user and get_active_membership are overridden with a real
session, user and membership, so the real RBACService checks the real
seeded permissions.
"""

from __future__ import annotations

from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.agents import orchestrator as orch
from app.api import deps
from app.api.deps import get_active_membership, get_current_user, get_db
from app.core.db import SessionLocal
from app.db.models.investigation import Investigation
from app.db.models.membership import Membership
from app.main import app
from app.services.investigation_orchestrator_service import (
    InvestigationOrchestratorService,
)
from tests.test_investigation_agents import seeded_alert

TENANT_ID = UUID("3ea2dc7e-c96f-45d5-8379-ab37092600de")

ORCHESTRATE_URL = (
    f"/api/v1/tenants/{TENANT_ID}/investigations/orchestrate"
)

# Must never appear in a response body.
SECRET = "password=hunter2-must-never-leave-the-server"


# ----------------------------------------------------------------------
# Fixtures and helpers
# ----------------------------------------------------------------------

@pytest.fixture
def db():
    session = SessionLocal()
    session.info["tenant_id"] = str(TENANT_ID)

    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def http_client(db: Session):
    app.dependency_overrides[get_db] = lambda: db

    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def orchestrator_calls(monkeypatch):
    """Record every real call to the orchestrator, then run it."""
    calls: list[dict] = []
    real = InvestigationOrchestratorService.run_for_alert

    def spy(self, **kwargs):
        calls.append(kwargs)
        return real(self, **kwargs)

    monkeypatch.setattr(InvestigationOrchestratorService, "run_for_alert", spy)
    return calls


def login_as(db: Session, role_key: str, *, skip_if_missing: bool = False):
    membership = (
        db.query(Membership)
        .filter(
            Membership.tenant_id == TENANT_ID,
            Membership.role == role_key,
        )
        .first()
    )

    if membership is None:
        if skip_if_missing:
            pytest.skip(f"no {role_key} membership in tenant {TENANT_ID}")
        raise AssertionError(
            f"No {role_key} membership found for tenant {TENANT_ID}"
        )

    db.rollback()

    user = membership.user

    db.info["user_id"] = str(user.id)
    db.info["tenant_id"] = str(membership.tenant_id)

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_active_membership] = lambda: membership

    return membership


def rbac_denying(*denied: str):
    """RBACService stand-in that denies exactly the given permission keys."""

    class Rbac:
        def __init__(self, db):
            pass

        def has_permission(self, *, user_id, tenant_id, permission_key):
            return permission_key not in denied

    return Rbac


# ----------------------------------------------------------------------
# Authorized path
# ----------------------------------------------------------------------

def test_authorized_role_can_orchestrate_over_http(
    db: Session,
    http_client: TestClient,
    orchestrator_calls,
):
    login_as(db, "ADMIN")

    with seeded_alert() as (_seed_db, _tid, ids):
        response = http_client.post(f"{ORCHESTRATE_URL}/{ids['alert']}")
        db.rollback()

        assert response.status_code == 200, response.text

        body = response.json()

        assert set(body) == {
            "investigation_id",
            "run_id",
            "completed_steps",
            "findings",
        }
        assert body["investigation_id"]
        assert body["run_id"]
        assert body["completed_steps"][0] == "planner"
        assert body["completed_steps"][-1] == "reporting"

        for step in ("planner", "query", "evidence", "mitre", "threat_intel"):
            assert body["findings"][step]["status"] == "ok", (
                f"{step}: {body['findings'][step]}"
            )

        assert len(orchestrator_calls) == 1
        assert orchestrator_calls[0]["tenant_id"] == TENANT_ID
        assert orchestrator_calls[0]["alert_id"] == ids["alert"]


# ----------------------------------------------------------------------
# Permission enforcement
# ----------------------------------------------------------------------

def test_role_without_ai_permission_is_forbidden_and_orchestrator_not_called(
    db: Session,
    http_client: TestClient,
    orchestrator_calls,
):
    login_as(db, "VIEWER", skip_if_missing=True)

    response = http_client.post(f"{ORCHESTRATE_URL}/{uuid4()}")

    assert response.status_code == 403, response.text

    detail = response.json()["detail"]

    assert detail["error"] == "permission_denied"
    assert detail["required_permission"] == "ai.assistant.use"
    assert orchestrator_calls == []


@pytest.mark.parametrize(
    "denied_key",
    ["ai.assistant.use", "forensics.manage"],
)
def test_each_required_permission_is_enforced_independently(
    db: Session,
    http_client: TestClient,
    orchestrator_calls,
    monkeypatch,
    denied_key: str,
):
    login_as(db, "ADMIN")
    monkeypatch.setattr(deps, "RBACService", rbac_denying(denied_key))

    response = http_client.post(f"{ORCHESTRATE_URL}/{uuid4()}")

    assert response.status_code == 403, response.text

    detail = response.json()["detail"]

    assert detail["error"] == "permission_denied"
    assert detail["required_permission"] == denied_key
    assert orchestrator_calls == []


# ----------------------------------------------------------------------
# Error mapping
# ----------------------------------------------------------------------

def test_unknown_alert_returns_404_and_creates_nothing(
    db: Session,
    http_client: TestClient,
    orchestrator_calls,
):
    login_as(db, "ADMIN")

    missing_alert_id = uuid4()

    response = http_client.post(f"{ORCHESTRATE_URL}/{missing_alert_id}")
    db.rollback()

    assert response.status_code == 404, response.text
    assert response.json()["detail"] == "Alert not found."

    created = db.scalars(
        select(Investigation).where(
            Investigation.alert_id == missing_alert_id
        )
    ).all()

    assert created == []


def test_node_failure_returns_500_with_run_ids_but_no_exception_text(
    db: Session,
    http_client: TestClient,
    monkeypatch,
):
    def failing_factory(_db):
        def node(state):
            return {
                **state,
                "error": f"database exploded: {SECRET}",
                "failed_step": "query",
            }

        node.__name__ = "query"
        return node

    monkeypatch.setitem(orch._AGENT_FACTORIES, "query", failing_factory)

    login_as(db, "ADMIN")

    with seeded_alert() as (_seed_db, _tid, ids):
        response = http_client.post(f"{ORCHESTRATE_URL}/{ids['alert']}")
        db.rollback()

    assert response.status_code == 500, response.text

    detail = response.json()["detail"]

    assert detail["error"] == "orchestration_failed"
    assert detail["failed_step"] == "query"
    assert detail["investigation_id"]
    assert detail["run_id"]
    assert detail["completed_steps"] == ["planner"]

    assert SECRET not in response.text