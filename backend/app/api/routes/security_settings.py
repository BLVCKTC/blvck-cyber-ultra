from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session

from app.api.deps import get_active_membership, get_db, require_roles
from app.db.models.enums import MembershipRole
from app.schemas.security_setting import SecuritySettingResponse, SecuritySettingUpdate
from app.services.security_setting_service import SecuritySettingService

router = APIRouter(prefix="/v1", tags=["Security Settings"])


def _assert_tenant_matches(membership, tenant_id: str) -> None:
    if str(membership.tenant_id) != tenant_id:
        raise HTTPException(status_code=403, detail="tenant_mismatch")


def service(db: Session = Depends(get_db)) -> SecuritySettingService:
    return SecuritySettingService(db)


@router.get("/tenants/{tenant_id}/security-settings", response_model=SecuritySettingResponse)
def get_security_settings(
    tenant_id: str = Path(..., min_length=1),
    membership=Depends(get_active_membership),
    svc: SecuritySettingService = Depends(service),
):
    _assert_tenant_matches(membership, tenant_id)
    return svc.get(membership.tenant_id)


@router.patch("/tenants/{tenant_id}/security-settings", response_model=SecuritySettingResponse)
def update_security_settings(
    payload: SecuritySettingUpdate,
    tenant_id: str = Path(..., min_length=1),
    membership=Depends(require_roles([MembershipRole.OWNER, MembershipRole.ADMIN])),
    svc: SecuritySettingService = Depends(service),
):
    _assert_tenant_matches(membership, tenant_id)
    return svc.update(membership.tenant_id, payload, actor_user_id=membership.user_id)