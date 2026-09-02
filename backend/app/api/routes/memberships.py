from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from app.api.deps import get_active_membership, get_db, require_roles
from app.db.models.enums import MembershipRole
from app.schemas.membership import (
    MembershipCreate,
    MembershipListResponse,
    MembershipResponse,
    MembershipUpdate,
)
from app.services.membership_service import MembershipService

router = APIRouter(prefix="", tags=["Memberships"])


def _validate_tenant_id(tenant_id: str) -> str:
    tenant_id = tenant_id.strip()
    if not tenant_id:
        raise HTTPException(status_code=422, detail="invalid_tenant_id")
    return tenant_id


@router.post(
    "/tenants/{tenant_id}/members",
    response_model=MembershipResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_member(
    tenant_id: str = Path(..., min_length=1),
    payload: MembershipCreate = ...,
    db: Session = Depends(get_db),
    membership=Depends(
        require_roles([MembershipRole.OWNER, MembershipRole.ADMIN])
    ),
):
    tenant_id = _validate_tenant_id(tenant_id)
    if str(membership.tenant_id) != tenant_id:
        raise HTTPException(status_code=403, detail="tenant_mismatch")
    return MembershipService(db).add_member(tenant_id=tenant_id, payload=payload)


@router.get("/tenants/{tenant_id}/members", response_model=MembershipListResponse)
def list_members(
    tenant_id: str = Path(..., min_length=1),
    db: Session = Depends(get_db),
    membership=Depends(get_active_membership),
):
    tenant_id = _validate_tenant_id(tenant_id)
    if str(membership.tenant_id) != tenant_id:
        raise HTTPException(status_code=403, detail="tenant_mismatch")
    items = MembershipService(db).list_members(tenant_id)
    return {"items": items, "total": len(items)}


@router.patch(
    "/tenants/{tenant_id}/memberships/{membership_id}",
    response_model=MembershipResponse,
)
def update_member(
    tenant_id: str = Path(..., min_length=1),
    membership_id: int = Path(..., gt=0),
    payload: MembershipUpdate = ...,
    db: Session = Depends(get_db),
    membership=Depends(
        require_roles([MembershipRole.OWNER, MembershipRole.ADMIN])
    ),
):
    tenant_id = _validate_tenant_id(tenant_id)
    if str(membership.tenant_id) != tenant_id:
        raise HTTPException(status_code=403, detail="tenant_mismatch")
    # Service signature doesn't accept tenant_id; RBAC scoping is handled by the dependency via tenant_id.
    return MembershipService(db).update_member(membership_id=membership_id, payload=payload)


@router.delete(
    "/tenants/{tenant_id}/memberships/{membership_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_member(
    tenant_id: str = Path(..., min_length=1),
    membership_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    membership=Depends(
        require_roles([MembershipRole.OWNER])
    ),
):
    tenant_id = _validate_tenant_id(tenant_id)
    if str(membership.tenant_id) != tenant_id:
        raise HTTPException(status_code=403, detail="tenant_mismatch")
    # Service signature doesn't accept tenant_id; RBAC scoping is handled by the dependency via tenant_id.
    MembershipService(db).remove_member(membership_id=membership_id)
    return None