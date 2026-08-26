from __future__ import annotations
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.models.investigation import Evidence, Investigation
from app.schemas.investigation import EvidenceCreate, InvestigationCreate, InvestigationUpdate

class InvestigationService:
    def __init__(self, db: Session) -> None: self.db = db
    def get(self, tenant_id: UUID, investigation_id: UUID): return self.db.scalar(select(Investigation).where(Investigation.id == investigation_id, Investigation.tenant_id == tenant_id))
    def create(self, tenant_id: UUID, payload: InvestigationCreate):
        item = Investigation(tenant_id=tenant_id, **payload.model_dump()); self.db.add(item); self.db.commit(); self.db.refresh(item); return item
    def update(self, tenant_id: UUID, investigation_id: UUID, payload: InvestigationUpdate):
        item = self.get(tenant_id, investigation_id)
        if not item: return None
        for key, value in payload.model_dump(exclude_unset=True).items(): setattr(item, key, value)
        self.db.commit(); self.db.refresh(item); return item
    def evidence(self, tenant_id: UUID, investigation_id: UUID):
        return list(self.db.scalars(select(Evidence).where(Evidence.tenant_id == tenant_id, Evidence.investigation_id == investigation_id).order_by(Evidence.created_at.asc())).all())
    def add_evidence(self, tenant_id: UUID, investigation_id: UUID, payload: EvidenceCreate):
        if not self.get(tenant_id, investigation_id): return None
        item = Evidence(tenant_id=tenant_id, investigation_id=investigation_id, **payload.model_dump()); self.db.add(item); self.db.commit(); self.db.refresh(item); return item
