from __future__ import annotations

from typing import Any, Mapping
from uuid import UUID
from sqlalchemy import delete, func, or_, select
from sqlalchemy.orm import Session
from app.db.models.detection_rule import DetectionRule

class DetectionRuleRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def _filters(self, tenant_id: UUID, filters: Mapping[str, Any]):
        criteria = [DetectionRule.tenant_id == tenant_id]
        for key in ("rule_type", "severity", "status", "enabled", "author", "source"):
            value = filters.get(key)
            if value is not None and value != "": criteria.append(getattr(DetectionRule, key) == value)
        q = filters.get("q")
        if q and str(q).strip():
            pattern = f"%{str(q).strip().replace('%', '\\%').replace('_', '\\_')}%"
            criteria.append(or_(DetectionRule.name.ilike(pattern, escape="\\"), DetectionRule.description.ilike(pattern, escape="\\")))
        return criteria

    def get(self, *, tenant_id: UUID, rule_id: UUID):
        return self.db.scalar(select(DetectionRule).where(DetectionRule.id == rule_id, DetectionRule.tenant_id == tenant_id))

    def list(self, *, tenant_id: UUID, limit: int = 50, offset: int = 0, **filters):
        return list(self.db.scalars(select(DetectionRule).where(*self._filters(tenant_id, filters)).order_by(DetectionRule.updated_at.desc(), DetectionRule.id.desc()).limit(limit).offset(offset)).all())

    def count(self, *, tenant_id: UUID, **filters) -> int:
        return int(self.db.scalar(select(func.count()).select_from(DetectionRule).where(*self._filters(tenant_id, filters))) or 0)

    def create(self, *, tenant_id: UUID, data: Mapping[str, Any]):
        rule = DetectionRule(tenant_id=tenant_id, **dict(data))
        self.db.add(rule); self.db.commit(); self.db.refresh(rule); return rule

    def update(self, *, tenant_id: UUID, rule_id: UUID, data: Mapping[str, Any]):
        rule = self.get(tenant_id=tenant_id, rule_id=rule_id)
        if rule is None: return None
        for key, value in data.items(): setattr(rule, key, value)
        self.db.commit(); self.db.refresh(rule); return rule

    def delete(self, *, tenant_id: UUID, rule_id: UUID) -> bool:
        result = self.db.execute(delete(DetectionRule).where(DetectionRule.id == rule_id, DetectionRule.tenant_id == tenant_id))
        self.db.commit(); return bool(result.rowcount)

    def list_production_rules(self, *, tenant_id: UUID, limit: int = 500, offset: int = 0):
        return self.list(tenant_id=tenant_id, limit=limit, offset=offset, status="production", enabled=True)
