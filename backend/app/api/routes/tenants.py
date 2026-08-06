from __future__ import annotations

from fastapi import APIRouter, Depends, Request, Response

from app.api.deps import get_current_user, get_db
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


@router.get(
    "",
    response_model=TenantListResponse,
)
def list_tenants(
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = TenantService(db)

    return {
        "items": service.list(),
    }


@router.get(
    "/{tenant_id}",
    response_model=TenantResponse,
)
def get_tenant(
    tenant_id: str,
    db=Depends(get_db),
):
    return TenantService(db).get(tenant_id)


@router.post(
    "",
    response_model=TenantResponse,
    status_code=201,
)
def create_tenant(
    payload: TenantCreate,
    request: Request,
    db=Depends(get_db),
):
    user = get_current_user(request, db=db)

    service = TenantService(db)

    return service.create(
        payload,
        owner_id=user.id,
    )

@router.patch(
    "/{tenant_id}",
    response_model=TenantResponse,
)
def update_tenant(
    tenant_id: str,
    payload: TenantUpdate,
    db=Depends(get_db),
):
    return TenantService(db).update(
        tenant_id,
        payload,
    )


@router.delete(
    "/{tenant_id}",
    status_code=204,
)
def delete_tenant(
    tenant_id: str,
    db=Depends(get_db),
):
    TenantService(db).delete(tenant_id)

    return Response(status_code=204)