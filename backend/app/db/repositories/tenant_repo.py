from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.tenant import Tenant


class TenantRepo:
    def __init__(self, db: Session):
        self.db = db

    def list(self) -> list[Tenant]:
        return self.db.scalars(
            select(Tenant).order_by(Tenant.name)
        ).all()

    def get(self, tenant_id: str) -> Tenant | None:
        return self.db.get(Tenant, tenant_id)

    def get_by_slug(self, slug: str) -> Tenant | None:
        return self.db.scalar(
            select(Tenant).where(Tenant.slug == slug)
        )

    def create(
        self,
        *,
        name: str,
        slug: str,
    ) -> Tenant:
        tenant = Tenant(
            name=name,
            slug=slug,
        )

        self.db.add(tenant)
        self.db.commit()
        self.db.refresh(tenant)

        return tenant

    def update(self, tenant: Tenant) -> Tenant:
        self.db.commit()
        self.db.refresh(tenant)
        return tenant

    def delete(self, tenant: Tenant) -> None:
        self.db.delete(tenant)
        self.db.commit()