from __future__ import annotations

from fastapi import Depends, HTTPException, Request
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN
from sqlalchemy.orm import Session

from app.core.config import SESSION_COOKIE_NAME, ACTIVE_TENANT_COOKIE_NAME
from app.core.db import SessionLocal
from app.core.security.jwt_verify import verify_keycloak_access_token

from app.db.repositories.user_repo import UserRepo
from app.db.repositories.membership_repo import MembershipRepo
from app.services.rbac import RBACService

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
):
    token = None
    auth_header = request.headers.get("Authorization")

    if auth_header and auth_header.lower().startswith("bearer "):
        token = auth_header[7:].strip()
    
    if not token:
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

    return user

def get_active_membership(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    tenant_id = request.cookies.get(ACTIVE_TENANT_COOKIE_NAME)

    if not tenant_id:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="tenant_not_selected",
        )

    membership = MembershipRepo(db).get_membership(user.id, tenant_id)
    if membership is None:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="not_a_member",
        )

    return membership

def require_roles(allowed_roles: list[str]):
    def dependency(membership=Depends(get_active_membership)):
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
