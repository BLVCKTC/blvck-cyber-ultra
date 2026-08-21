from __future__ import annotations

from app.db.seeds.permissions import PERMISSIONS
from app.db.seeds.role_permissions import ROLE_PERMISSIONS


SECURITY_EVENTS_PERMISSION = "security.events.view"


def test_security_events_permission_is_seeded() -> None:
    permission_keys = {permission[0] for permission in PERMISSIONS}

    assert SECURITY_EVENTS_PERMISSION in permission_keys


def test_security_events_permission_is_granted_to_intended_roles_only() -> None:
    intended_roles = {
        "OWNER",
        "ADMIN",
        "SOC_MANAGER",
        "SOC_ANALYST",
        "INCIDENT_RESPONDER",
    }

    for role in intended_roles:
        assert SECURITY_EVENTS_PERMISSION in ROLE_PERMISSIONS[role]

    assert SECURITY_EVENTS_PERMISSION not in ROLE_PERMISSIONS["VIEWER"]


def test_role_permission_keys_are_defined_permissions() -> None:
    permission_keys = {permission[0] for permission in PERMISSIONS}

    seeded_role_permissions = {
        permission
        for permissions in ROLE_PERMISSIONS.values()
        for permission in permissions
    }

    assert seeded_role_permissions <= permission_keys
    assert "platform.all" in ROLE_PERMISSIONS["OWNER"]


def test_security_events_permission_is_read_only() -> None:
    permission = next(
        permission for permission in PERMISSIONS if permission[0] == SECURITY_EVENTS_PERMISSION
    )

    assert permission[2] == "Security"
    assert permission[4] == "low"
