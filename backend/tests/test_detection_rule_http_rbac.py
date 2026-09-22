from __future__ import annotations

from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.deps import get_active_membership, get_current_user, get_db
from app.core.db import SessionLocal
from app.db.models.membership import Membership
from app.main import app
from app.db.models.detection_rule import DetectionRule

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


@pytest.fixture
def http_client(db: Session):
    app.dependency_overrides[get_db] = lambda: db

    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def authenticate_as(
    db: Session,
    membership: Membership,
):
    db.rollback()

    user = membership.user

    db.info["user_id"] = str(user.id)
    db.info["tenant_id"] = str(membership.tenant_id)

    return user, membership


def rule_payload(name: str):
    return {
        "name": name,
        "description": "HTTP RBAC integration test",
        "rule_type": "threshold",
        "severity": "low",
        "status": "draft",
        "version": 1,
        "enabled": True,
        "query": "event_count >= 5",
        "configuration": {
            "field": "event_count",
            "threshold": 5,
            "window_seconds": 300,
        },
        "tags": ["http-rbac-test"],
        "mitre_technique_ids": [],
        "mitre_tactic_ids": [],
        "author": "HTTP RBAC Test",
        "source": "integration-test",
    }


def test_admin_can_use_detection_rule_http_api(
    db: Session,
    http_client: TestClient,
):
    membership = get_membership(db, "ADMIN")
    user, membership = authenticate_as(db, membership)

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_active_membership] = lambda: membership

    try:
        response = http_client.post(
            f"/api/v1/tenants/{TENANT_ID}/detection-rules",
            json=rule_payload("HTTP ADMIN RBAC Test"),
        )

        assert response.status_code == 201, response.text

        rule = response.json()
        rule_id = rule["id"]

        response = http_client.get(
            f"/api/v1/tenants/{TENANT_ID}/detection-rules/{rule_id}"
        )

        assert response.status_code == 200, response.text
        assert response.json()["id"] == rule_id

        response = http_client.patch(
            f"/api/v1/tenants/{TENANT_ID}/detection-rules/{rule_id}",
            json={"description": "Updated by ADMIN"},
        )

        assert response.status_code == 200, response.text
        assert response.json()["description"] == "Updated by ADMIN"

        response = http_client.delete(
            f"/api/v1/tenants/{TENANT_ID}/detection-rules/{rule_id}"
        )

        assert response.status_code == 204, response.text

    finally:
        app.dependency_overrides.clear()


def test_soc_manager_can_use_detection_rule_http_api_but_cannot_delete(
    db: Session,
    http_client: TestClient,
):
    membership = get_membership(db, "SOC_MANAGER")
    user, membership = authenticate_as(db, membership)

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_active_membership] = lambda: membership

    try:
        response = http_client.post(
            f"/api/v1/tenants/{TENANT_ID}/detection-rules",
            json=rule_payload("HTTP SOC MANAGER RBAC Test"),
        )

        assert response.status_code == 201, response.text

        rule = response.json()
        rule_id = rule["id"]

        response = http_client.get(
            f"/api/v1/tenants/{TENANT_ID}/detection-rules/{rule_id}"
        )

        assert response.status_code == 200, response.text
        assert response.json()["id"] == rule_id

        response = http_client.patch(
            f"/api/v1/tenants/{TENANT_ID}/detection-rules/{rule_id}",
            json={"description": "Updated by SOC_MANAGER"},
        )

        assert response.status_code == 200, response.text
        assert response.json()["description"] == "Updated by SOC_MANAGER"

        response = http_client.delete(
            f"/api/v1/tenants/{TENANT_ID}/detection-rules/{rule_id}"
        )

        assert response.status_code == 403, response.text

        body = response.json()

        assert body["detail"]["error"] == "permission_denied"
        assert body["detail"]["required_permission"] == "detections.delete"

    finally:
        app.dependency_overrides.clear()

    cleanup_db = SessionLocal()

    try:
        cleanup_db.info["tenant_id"] = str(TENANT_ID)

        cleanup_db.query(
            __import__(
                "app.db.models.detection_rule",
                fromlist=["DetectionRule"],
            ).DetectionRule
        ).filter(
            __import__(
                "app.db.models.detection_rule",
                fromlist=["DetectionRule"],
            ).DetectionRule.id == UUID(rule_id)
        ).delete(synchronize_session=False)

        cleanup_db.commit()
    finally:
        cleanup_db.rollback()
        cleanup_db.close()