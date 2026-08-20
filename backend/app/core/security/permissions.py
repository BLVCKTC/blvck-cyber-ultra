from __future__ import annotations

"""
BLVCV CK CYBER — Security Role Helpers

This module provides role-based convenience helpers for the RBAC layer.

Authentication and tenant resolution are handled by:
    app.api.deps.get_current_user()
    app.api.deps.get_active_membership()

Permission-based authorization is handled by:
    app.api.deps.require_permission()
"""

from app.db.models.enums import MembershipRole
from app.db.models.membership import Membership

# =========================================================
# ROLE GROUPINGS
# =========================================================

# Define role sets to avoid repeating the same lists across multiple functions
_OWNER_ONLY = {MembershipRole.OWNER}
_ADMIN_PLUS = {MembershipRole.OWNER, MembershipRole.ADMIN}
_SOC_LEAD_PLUS = {MembershipRole.OWNER, MembershipRole.ADMIN, MembershipRole.SOC_MANAGER}
_INCIDENT_PLUS = {MembershipRole.OWNER, MembershipRole.ADMIN, MembershipRole.SOC_MANAGER, MembershipRole.INCIDENT_RESPONDER}


# =========================================================
# ROLE CHECKS
# =========================================================

def is_owner(membership: Membership) -> bool:
    """Return True when the membership belongs to an OWNER."""
    return membership.role in _OWNER_ONLY


def is_admin(membership: Membership) -> bool:
    """Return True when the membership has OWNER or ADMIN privileges."""
    return membership.role in _ADMIN_PLUS


def is_soc_manager(membership: Membership) -> bool:
    """Return True when the membership belongs to a SOC Manager."""
    return membership.role is MembershipRole.SOC_MANAGER


def is_soc_analyst(membership: Membership) -> bool:
    """Return True when the membership belongs to a SOC Analyst."""
    return membership.role is MembershipRole.SOC_ANALYST


def is_incident_responder(membership: Membership) -> bool:
    """Return True when the membership belongs to an Incident Responder."""
    return membership.role is MembershipRole.INCIDENT_RESPONDER


def is_viewer(membership: Membership) -> bool:
    """Return True when the membership belongs to a read-only Viewer."""
    return membership.role is MembershipRole.VIEWER


# =========================================================
# MANAGEMENT CAPABILITIES
# =========================================================

def can_manage_members(membership: Membership) -> bool:
    """Determine whether the user can manage tenant members (Invite/Remove/Role change)."""
    return is_admin(membership)


def can_manage_settings(membership: Membership) -> bool:
    """Determine whether the user can manage tenant security settings."""
    return is_owner(membership)


def can_manage_incidents(membership: Membership) -> bool:
    """Determine whether the user can manage security incidents."""
    return membership.role in _INCIDENT_PLUS


def can_manage_detections(membership: Membership) -> bool:
    """Determine whether the user can manage detection engineering."""
    return membership.role in _SOC_LEAD_PLUS


def can_manage_threat_intelligence(membership: Membership) -> bool:
    """Determine whether the user can manage threat intelligence."""
    return membership.role in _SOC_LEAD_PLUS


def can_manage_forensics(membership: Membership) -> bool:
    """Determine whether the user can manage forensic investigations."""
    return membership.role in _SOC_LEAD_PLUS


# =========================================================
# ROLE UTILITIES
# =========================================================

def has_role(membership: Membership, *roles: MembershipRole) -> bool:
    """Return True when the membership has one of the supplied roles."""
    return membership.role in roles


def is_authenticated_member(membership: Membership) -> bool:
    """Return True when the membership represents a valid tenant role."""
    return membership.role in MembershipRole
