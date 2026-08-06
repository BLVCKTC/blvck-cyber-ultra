from __future__ import annotations

from fastapi import Depends, HTTPException
from starlette.status import HTTP_403_FORBIDDEN

from app.api.deps import get_active_membership
from app.db.models.enums import MembershipRole
from app.db.models.membership import Membership


def require_roles(*roles: MembershipRole):
    """
    FastAPI dependency factory enforcing that the caller's active membership
    role is one of the allowed roles.
    """
    allowed = set(roles)

    def dependency(membership: Membership = Depends(get_active_membership)) -> Membership:
        if membership.role not in allowed:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail="forbidden",
            )
        return membership

    return dependency


def require_owner():
    """OWNER only."""
    return require_roles(MembershipRole.OWNER)


def require_admin():
    """OWNER + ADMIN."""
    return require_roles(MembershipRole.OWNER, MembershipRole.ADMIN)


def require_member():
    """Any authenticated tenant member."""
    return require_roles(*list(MembershipRole))  # requires get_active_membership to validate tenancy


def can_manage_members(membership: Membership) -> bool:
    return membership.role in {MembershipRole.OWNER, MembershipRole.ADMIN}


def can_manage_incidents(membership: Membership) -> bool:
    return membership.role in {
        MembershipRole.OWNER,
        MembershipRole.ADMIN,
        MembershipRole.SOC_MANAGER,
        MembershipRole.INCIDENT_RESPONDER,
    }


def can_manage_settings(membership: Membership) -> bool:
    return membership.role is MembershipRole.OWNER
