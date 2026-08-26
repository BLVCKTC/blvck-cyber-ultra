from __future__ import annotations
from typing import Any, Mapping
from uuid import UUID
from sqlalchemy import delete, func, or_, select
from sqlalchemy.orm import Session
from app.db.models.alert import Alert

class AlertRepository:
    def __init__(self, db: Session) -> None: self.db = db
    def _filters(self, tenant_id: UUID, filters: Mapping[str, Any]):
        criteria = [Alert.tenant_id == tenant_id]
        for key in ('severity','status','detection_rule_id','security_event_id','source'):
            value = filters.get(key)
            if value not in (None, ''): criteria.append(getattr(Alert, key) == value)
        q = str(filters.get('q') or '').strip()
        if q:
            pattern = f"%{q.replace('%','\\%').replace('_','\\_')}%"
            criteria.append(or_(Alert.title.ilike(pattern, escape='\\'), Alert.description.ilike(pattern, escape='\\')))
        return criteria
    def get(self, *, tenant_id: UUID, alert_id: UUID): return self.db.scalar(select(Alert).where(Alert.id == alert_id, Alert.tenant_id == tenant_id))
    def list(self, *, tenant_id: UUID, limit: int, offset: int, **filters): return list(self.db.scalars(select(Alert).where(*self._filters(tenant_id, filters)).order_by(Alert.updated_at.desc(), Alert.id.desc()).limit(limit).offset(offset)).all())
    def count(self, *, tenant_id: UUID, **filters): return int(self.db.scalar(select(func.count()).select_from(Alert).where(*self._filters(tenant_id, filters))) or 0)
    def create(self, *, tenant_id: UUID, data: Mapping[str, Any]):
        item = Alert(tenant_id=tenant_id, **dict(data)); self.db.add(item); self.db.commit(); self.db.refresh(item); return item
    def update(self, *, tenant_id: UUID, alert_id: UUID, data: Mapping[str, Any]):
        item = self.get(tenant_id=tenant_id, alert_id=alert_id)
        if item is None: return None
        for key, value in data.items(): setattr(item, key, value)
        self.db.commit(); self.db.refresh(item); return item
    def delete(self, *, tenant_id: UUID, alert_id: UUID) -> bool:
        result = self.db.execute(delete(Alert).where(Alert.id == alert_id, Alert.tenant_id == tenant_id)); self.db.commit(); return bool(result.rowcount)
