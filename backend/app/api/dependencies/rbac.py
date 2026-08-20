from __future__ import annotations

from collections.abc import Callable
from fastapi import Depends, HTTPException
from starlette.status import HTTP_403_FORBIDDEN

from app.api.deps import get_active_membership
from app.db.models.enums import MembershipRole
from app.db.models.membership import Membership

# Capability Sets: Define who can do what in one place
# This makes it trivial to add new roles to a capability across the whole app
ADMIN_ROLES = {MembershipRole.OWNER, MembershipRole.ADMIN}
INCIDENT_ROLES = {
    MembershipRole.OWNER, 
    MembershipRole.ADMIN, 
    MembershipRole.SOC_MANAGER, 
    MembershipRole.INCIDENT_RESPONDER
}
SETTINGS_ROLES = {MembershipRole.OWNER}


def require_roles(*roles: MembershipRole) -> Callable[..., Membership]:
    """
    FastAPI dependency factory that requires the active tenant
    membership to have one of the supplied roles.
    """
    allowed_roles = frozenset(roles)

    def dependency(
        membership: Membership = Depends(get_active_membership),
    ) -> Membership:
        if membership.role not in allowed_roles:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail="forbidden",
            )
        return membership

    return dependency


def require_owner() -> Callable[..., Membership]:
    """Require OWNER role."""
    return require_roles(*SETTINGS_ROLES)


def require_admin() -> Callable[..., Membership]:
    """Require OWNER or ADMIN role."""
    return require_roles(*ADMIN_ROLES)


def require_member() -> Callable[..., Membership]:
    """Require any valid authenticated tenant membership."""
    return require_roles(*MembershipRole)


def can_manage_members(membership: Membership) -> bool:
    """Return True when the member can manage tenant members."""
    return membership.role in ADMIN_ROLES


def can_manage_incidents(membership: Membership) -> bool:
    """Return True when the member can manage incidents."""
    return membership.role in INCIDENT_ROLES


def can_manage_settings(membership: Membership) -> bool:
    """Return True when the member can manage tenant settings."""
    return membership.role in SETTINGS_ROLES
