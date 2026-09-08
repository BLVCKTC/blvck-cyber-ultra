from __future__ import annotations

import logging
from uuid import UUID

from fastapi import Depends, HTTPException, Path, Request
from sqlalchemy import text
from sqlalchemy.orm import Session
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

from app.core.config import (
    ACTIVE_TENANT_COOKIE_NAME,
    SESSION_COOKIE_NAME,
)
from app.core.db import (
    SessionLocal,
    current_tenant_id,
    current_user_id,
)
from app.core.security.jwt_verify import verify_keycloak_access_token
from app.db.models.enums import MembershipRole
from app.db.repositories.membership_repo import MembershipRepo
from app.db.repositories.user_repo import UserRepo
from app.services.rbac import RBACService


logger = logging.getLogger(__name__)


def get_db():
    """
    Provide one SQLAlchemy Session per request.
    """
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def _set_session_context(
    db: Session,
    *,
    user_id: str,
    tenant_id: str | None,
) -> None:
    """
    Store the RLS values on this Session instance for all future
    transactions it opens, and apply them immediately to whatever
    transaction is currently active.
    """
    normalized_user_id = str(user_id)
    normalized_tenant_id = tenant_id or ""

    db.info["user_id"] = normalized_user_id
    db.info["tenant_id"] = normalized_tenant_id

    db.execute(
        text("SELECT set_config('app.user_id', :uid, true)"),
        {"uid": normalized_user_id},
    )
    db.execute(
        text("SELECT set_config('app.tenant_id', :tid, true)"),
        {"tid": normalized_tenant_id},
    )


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
):
    token = request.cookies.get(SESSION_COOKIE_NAME)

    if not token:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="not_authenticated",
        )

    claims = verify_keycloak_access_token(token)
    sub = claims.get("sub")

    if not sub:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="invalid_token",
        )

    user = UserRepo(db).get_by_keycloak_sub(sub)

    if not user:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="user_not_found",
        )

    # The user lookup may already have opened a transaction. This applies the
    # values immediately to that transaction and stores them for future ones.
    _set_session_context(
        db,
        user_id=str(user.id),
        tenant_id=None,
    )

    return user


def get_tenant_membership(
    tenant_id: UUID = Path(...),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Authorize the URL tenant using the user's existing membership relationship.

    The path tenant is intentionally independent of the active-tenant cookie,
    so direct links work for every authorized tenant. The tenant-specific RLS
    context is applied only after membership authorization succeeds.
    """
    membership = MembershipRepo(db).get_membership(
        user.id,
        tenant_id,
    )

    if membership is None:
        logger.warning(
            "Tenant authorization denied: "
            "user_id=%s keycloak_sub=%s requested_tenant_id=%s "
            "reason=not_a_member",
            user.id,
            user.keycloak_sub,
            tenant_id,
        )

        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="not_a_member",
        )

    role = (
        membership.role.value
        if hasattr(membership.role, "value")
        else str(membership.role)
    )

    allowed_roles = {
        MembershipRole.OWNER.value,
        MembershipRole.ADMIN.value,
        MembershipRole.SOC_MANAGER.value,
        MembershipRole.SOC_ANALYST.value,
    }

    if role not in allowed_roles:
        logger.warning(
            "Tenant authorization denied: "
            "user_id=%s keycloak_sub=%s requested_tenant_id=%s "
            "membership_tenant_id=%s membership_role=%s "
            "reason=invalid_role",
            user.id,
            user.keycloak_sub,
            tenant_id,
            membership.tenant_id,
            role,
        )

        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="forbidden",
        )

    _set_session_context(
        db,
        user_id=str(user.id),
        tenant_id=str(membership.tenant_id),
    )

    return membership


def get_active_membership(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Resolve the tenant from the URL when present, otherwise use the legacy
    active-tenant cookie.

    Tenant-scoped routes authorize the tenant from the path and do not trust a
    client-controlled active-tenant cookie. Legacy routes retain cookie-based
    behavior for compatibility.
    """
    tenant_id = (
        request.path_params.get("tenant_id")
        or request.cookies.get(ACTIVE_TENANT_COOKIE_NAME)
    )

    if not tenant_id:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="tenant_not_selected",
        )

    try:
        tenant_uuid = UUID(str(tenant_id))
    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=422,
            detail="invalid_tenant_id",
        ) from exc

    membership = MembershipRepo(db).get_membership(
        user.id,
        tenant_uuid,
    )

    if membership is None:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="not_a_member",
        )

    _set_session_context(
        db,
        user_id=str(user.id),
        tenant_id=str(membership.tenant_id),
    )

    return membership


def require_roles(allowed_roles: list[str]):
    def dependency(
        membership=Depends(get_active_membership),
    ):
        role = (
            membership.role.value
            if hasattr(membership.role, "value")
            else str(membership.role)
        )

        if role not in allowed_roles:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail="forbidden",
            )

        return membership

    return dependency


def require_permission(permission_key: str):
    def dependency(
        membership=Depends(get_active_membership),
        db: Session = Depends(get_db),
    ):
        rbac = RBACService(db)

        allowed = rbac.has_permission(
            user_id=membership.user_id,
            tenant_id=membership.tenant_id,
            permission_key=permission_key,
        )

        if not allowed:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail={
                    "error": "permission_denied",
                    "required_permission": permission_key,
                },
            )

        return membership

    return dependency
