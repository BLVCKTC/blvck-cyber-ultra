from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session

from app.api.deps import get_active_membership, get_db, require_roles
from app.db.models.enums import MembershipRole
from app.schemas.api_key import ApiKeyCreate, ApiKeyCreateResponse, ApiKeyListResponse
from app.services.api_key_service import ApiKeyService

router = APIRouter(prefix="/v1", tags=["API Keys"])


def _assert_tenant_matches(membership, tenant_id: str) -> None:
    from fastapi import HTTPException
    if str(membership.tenant_id) != tenant_id:
        raise HTTPException(status_code=403, detail="tenant_mismatch")


def service(db: Session = Depends(get_db)) -> ApiKeyService:
    return ApiKeyService(db)


@router.get("/tenants/{tenant_id}/api-keys", response_model=ApiKeyListResponse)
def list_api_keys(
    tenant_id: str = Path(..., min_length=1),
    membership=Depends(get_active_membership),
    svc: ApiKeyService = Depends(service),
):
    _assert_tenant_matches(membership, tenant_id)
    items = svc.list_keys(membership.tenant_id)
    return {"items": items, "total": len(items)}


@router.post(
    "/tenants/{tenant_id}/api-keys",
    response_model=ApiKeyCreateResponse,
    status_code=201,
)
def create_api_key(
    payload: ApiKeyCreate,
    tenant_id: str = Path(..., min_length=1),
    membership=Depends(require_roles([MembershipRole.OWNER, MembershipRole.ADMIN])),
    svc: ApiKeyService = Depends(service),
):
    _assert_tenant_matches(membership, tenant_id)
    row, raw_key = svc.create_key(membership.tenant_id, membership.user_id, payload)
    return ApiKeyCreateResponse(
        id=row.id,
        name=row.name,
        key_prefix=row.key_prefix,
        api_key=raw_key,
        scopes=row.scopes,
        created_at=row.created_at,
    )


@router.delete("/tenants/{tenant_id}/api-keys/{key_id}", status_code=204)
def revoke_api_key(
    tenant_id: str = Path(..., min_length=1),
    key_id: UUID = Path(...),
    membership=Depends(require_roles([MembershipRole.OWNER, MembershipRole.ADMIN])),
    svc: ApiKeyService = Depends(service),
):
    _assert_tenant_matches(membership, tenant_id)
    svc.revoke_key(key_id, membership.tenant_id)
    return None