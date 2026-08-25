from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.enums import MembershipRole
from app.db.models.membership import Membership
from app.db.models.tenant import Tenant
from app.schemas.tenant import TenantCreate, TenantUpdate


class TenantService:
    def __init__(self, db: Session):
        self.db = db

    def list(self) -> list[Tenant]:
        return list(self.db.scalars(select(Tenant).order_by(Tenant.name.asc())))

    def get(self, tenant_id: str | UUID) -> Tenant:
        try:
            uuid_id = UUID(str(tenant_id)) if not isinstance(tenant_id, UUID) else tenant_id
        except ValueError:
            raise HTTPException(status_code=400, detail="invalid_tenant_id")

        tenant = self.db.get(Tenant, uuid_id)
        if not tenant:
            raise HTTPException(status_code=404, detail="tenant_not_found")
        return tenant

    def create(self, payload: TenantCreate, *, owner_id: UUID) -> Tenant:
        if self.db.scalar(select(Tenant).where(Tenant.slug == payload.slug)):
            raise HTTPException(status_code=409, detail="tenant_slug_already_exists")

        tenant = Tenant(**payload.model_dump())
        self.db.add(tenant)
        self.db.flush()

        membership = Membership(
            user_id=owner_id,
            tenant_id=tenant.id,
            role=MembershipRole.OWNER,
            is_default=True,
        )
        self.db.add(membership)
        self.db.commit()
        self.db.refresh(tenant)
        return tenant

    def update(self, tenant_id: str | UUID, payload: TenantUpdate) -> Tenant:
        tenant = self.get(tenant_id)
        update_data = payload.model_dump(exclude_unset=True)

        if "slug" in update_data:
            if self.db.scalar(select(Tenant).where(Tenant.slug == update_data["slug"], Tenant.id != tenant.id)):
                raise HTTPException(status_code=409, detail="tenant_slug_already_exists")

        for field, value in update_data.items():
            setattr(tenant, field, value)

        self.db.commit()
        self.db.refresh(tenant)
        return tenant

    def delete(self, tenant_id: str | UUID) -> None:
        tenant = self.get(tenant_id)
        self.db.delete(tenant)
        self.db.commit()
