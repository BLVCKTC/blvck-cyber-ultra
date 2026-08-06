from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.db.models.enums import MembershipRole
from app.db.models.tenant import Tenant
from app.db.repositories.membership_repo import MembershipRepo
from app.db.repositories.tenant_repo import TenantRepo
from app.schemas.tenant import TenantCreate, TenantUpdate


class TenantService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = TenantRepo(db)
        self.membership_repo = MembershipRepo(db)

    def list(self) -> list[Tenant]:
        return self.repo.list()

    def get(self, tenant_id: str) -> Tenant:
        tenant = self.repo.get(tenant_id)

        if tenant is None:
            raise HTTPException(
                status_code=404,
                detail="tenant_not_found",
            )

        return tenant

    def create(
        self,
        payload: TenantCreate,
        owner_id: int,
    ) -> Tenant:

        if self.repo.get_by_slug(payload.slug):
            raise HTTPException(
                status_code=409,
                detail="tenant_slug_exists",
            )

        tenant = self.repo.create(
            name=payload.name.strip(),
            slug=payload.slug.strip().lower(),
        )

        self.membership_repo.create(
            user_id=owner_id,
            tenant_id=tenant.id,
            role=MembershipRole.OWNER,
            is_default=True,
        )

        return tenant

    def update(
        self,
        tenant_id: str,
        payload: TenantUpdate,
    ) -> Tenant:

        tenant = self.get(tenant_id)

        if payload.slug:
            existing = self.repo.get_by_slug(
                payload.slug.lower(),
            )

            if existing and existing.id != tenant.id:
                raise HTTPException(
                    status_code=409,
                    detail="tenant_slug_exists",
                )

            tenant.slug = payload.slug.strip().lower()

        if payload.name:
            tenant.name = payload.name.strip()

        return self.repo.update(tenant)

    def delete(
        self,
        tenant_id: str,
    ) -> None:

        tenant = self.get(tenant_id)

        self.repo.delete(tenant)