from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response

from app.api.deps import get_current_user, get_db
from app.db.repositories.membership_repo import MembershipRepo
from app.schemas.tenant import (
    TenantCreate,
    TenantListResponse,
    TenantResponse,
    TenantUpdate,
)
from app.services.tenant_service import TenantService


router = APIRouter(
    prefix="/tenants",
    tags=["Tenants"],
)


def _require_membership(
    db,
    user_id: UUID,
    tenant_id: UUID,
) -> None:
    """
    Ensure the authenticated user belongs to the requested tenant.

    Tenant isolation is enforced here before any tenant data is returned.
    """
    membership_repo = MembershipRepo(db)

    membership = membership_repo.get_membership(
        user_id=user_id,
        tenant_id=tenant_id,
    )

    if not membership:
        raise HTTPException(
            status_code=403,
            detail="not_a_member",
        )


@router.get(
    "",
    response_model=TenantListResponse,
)
def list_tenants(
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Return tenants available to the authenticated user.
    """
    return {
        "items": TenantService(db).list_for_user(
            current_user.id
        )
    }


@router.get(
    "/{tenant_id}",
    response_model=TenantResponse,
)
def get_tenant(
    tenant_id: UUID,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Return a single tenant.

    The authenticated user must have a membership in the tenant.
    """
    _require_membership(
        db=db,
        user_id=current_user.id,
        tenant_id=tenant_id,
    )

    tenant = TenantService(db).get(
        str(tenant_id)
    )

    if not tenant:
        raise HTTPException(
            status_code=404,
            detail="tenant_not_found",
        )

    return tenant


@router.post(
    "",
    response_model=TenantResponse,
    status_code=201,
)
def create_tenant(
    payload: TenantCreate,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Create a tenant and assign the authenticated user as owner.
    """
    return TenantService(db).create(
        payload,
        owner_id=current_user.id,
    )


@router.patch(
    "/{tenant_id}",
    response_model=TenantResponse,
)
def update_tenant(
    tenant_id: UUID,
    payload: TenantUpdate,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Update a tenant belonging to the authenticated user.
    """
    _require_membership(
        db=db,
        user_id=current_user.id,
        tenant_id=tenant_id,
    )

    tenant = TenantService(db).update(
        str(tenant_id),
        payload,
    )

    if not tenant:
        raise HTTPException(
            status_code=404,
            detail="tenant_not_found",
        )

    return tenant


@router.delete(
    "/{tenant_id}",
    status_code=204,
)
def delete_tenant(
    tenant_id: UUID,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Delete a tenant belonging to the authenticated user.
    """
    _require_membership(
        db=db,
        user_id=current_user.id,
        tenant_id=tenant_id,
    )

    TenantService(db).delete(
        str(tenant_id)
    )

    return Response(status_code=204)

