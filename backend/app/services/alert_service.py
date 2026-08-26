from __future__ import annotations
from uuid import UUID
from sqlalchemy.orm import Session
from app.db.repositories.alert_repo import AlertRepository
from app.schemas.alert import AlertCreate, AlertUpdate

class AlertService:
    MAX_LIMIT = 500
    def __init__(self, db: Session) -> None: self.alerts = AlertRepository(db)
    def create(self, *, tenant_id: UUID, payload: AlertCreate): return self.alerts.create(tenant_id=tenant_id, data=payload.model_dump())
    def get(self, *, tenant_id: UUID, alert_id: UUID): return self.alerts.get(tenant_id=tenant_id, alert_id=alert_id)
    def list(self, *, tenant_id: UUID, limit: int = 50, offset: int = 0, **filters):
        if not 1 <= limit <= self.MAX_LIMIT: raise ValueError('limit must be between 1 and 500')
        if offset < 0: raise ValueError('offset must be non-negative')
        return self.alerts.list(tenant_id=tenant_id, limit=limit, offset=offset, **filters), self.alerts.count(tenant_id=tenant_id, **filters)
    def update(self, *, tenant_id: UUID, alert_id: UUID, payload: AlertUpdate):
        data = payload.model_dump(exclude_unset=True)
        if not data: raise ValueError('update payload must contain at least one field')
        return self.alerts.update(tenant_id=tenant_id, alert_id=alert_id, data=data)
    def delete(self, *, tenant_id: UUID, alert_id: UUID): return self.alerts.delete(tenant_id=tenant_id, alert_id=alert_id)
