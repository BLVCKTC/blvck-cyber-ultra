from __future__ import annotations

from app.db.seeds.permissions import PERMISSIONS
from app.db.seeds.role_permissions import ROLE_PERMISSIONS

AI_PERMISSION = "ai.assistant.use"
EVIDENCE_WRITE_PERMISSION = "forensics.manage"
SUPER_PERMISSION = "platform.all"

# Product decision: who may trigger the investigation orchestrator.
# Adding a role here (or granting the permission elsewhere) must be a
# deliberate act, because the orchestrator writes investigations/evidence.
INTENDED_ROLES = {
    "OWNER",
    "ADMIN",
    "SOC_MANAGER",
    "SOC_ANALYST",
    "INCIDENT_RESPONDER",
}


def _effective(role: str, key: str) -> bool:
    permissions = ROLE_PERMISSIONS[role]
    return key in permissions or SUPER_PERMISSION in permissions


def _granted_roles() -> set[str]:
    return {
        role
        for role, permissions in ROLE_PERMISSIONS.items()
        if AI_PERMISSION in permissions
    }


def test_ai_assistant_permission_is_seeded() -> None:
    permission_keys = {permission[0] for permission in PERMISSIONS}

    assert AI_PERMISSION in permission_keys
    assert EVIDENCE_WRITE_PERMISSION in permission_keys


def test_ai_assistant_permission_is_granted_to_intended_roles_only() -> None:
    granted = _granted_roles()

    assert granted == INTENDED_ROLES, (
        f"ai.assistant.use is granted to {sorted(granted)}; "
        f"intended {sorted(INTENDED_ROLES)}. "
        f"Unexpected: {sorted(granted - INTENDED_ROLES)}; "
        f"missing: {sorted(INTENDED_ROLES - granted)}"
    )


def test_viewer_cannot_trigger_the_orchestrator() -> None:
    assert AI_PERMISSION not in ROLE_PERMISSIONS["VIEWER"]
    assert SUPER_PERMISSION not in ROLE_PERMISSIONS["VIEWER"]


def test_orchestrator_permission_never_exceeds_evidence_write_authority() -> None:
    """
    The orchestrator writes investigations and evidence. Any role that can
    trigger it must already be able to write evidence directly, otherwise
    the agent route would grant authority the human does not hold.
    """
    escalations = sorted(
        role
        for role in _granted_roles()
        if not _effective(role, EVIDENCE_WRITE_PERMISSION)
    )

    assert not escalations, (
        f"roles can trigger the orchestrator but cannot write evidence "
        f"directly ({EVIDENCE_WRITE_PERMISSION}): {escalations}"
    )


def test_every_granted_permission_is_a_defined_permission() -> None:
    permission_keys = {permission[0] for permission in PERMISSIONS}

    for role, permissions in ROLE_PERMISSIONS.items():
        undefined = sorted(set(permissions) - permission_keys)
        assert not undefined, f"{role} holds undefined permissions: {undefined}"