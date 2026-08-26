from __future__ import annotations
from uuid import UUID
from sqlalchemy.orm import Session
from app.db.repositories.detection_rule_repo import DetectionRuleRepository
from app.schemas.detection_rule import DetectionRuleCreate, DetectionRuleUpdate

TRANSITIONS = {
    "draft": {"testing", "retired"}, "testing": {"backtested"}, "backtested": {"canary"},
    "canary": {"approved"}, "approved": {"production", "retired"}, "production": {"monitored", "retired"},
    "monitored": {"tuned"}, "tuned": {"testing"}, "retired": set(),
}

class DetectionRuleService:
    MAX_LIMIT = 500
    def __init__(self, db: Session): self.rules = DetectionRuleRepository(db)
    def create(self, *, tenant_id: UUID, payload: DetectionRuleCreate): return self.rules.create(tenant_id=tenant_id, data=payload.model_dump(mode="python"))
    def get(self, *, tenant_id: UUID, rule_id: UUID): return self.rules.get(tenant_id=tenant_id, rule_id=rule_id)
    def list(self, *, tenant_id: UUID, limit=50, offset=0, **filters):
        if not 1 <= limit <= self.MAX_LIMIT: raise ValueError("limit must be between 1 and 500")
        if offset < 0: raise ValueError("offset must be greater than or equal to 0")
        return self.rules.list(tenant_id=tenant_id, limit=limit, offset=offset, **filters), self.rules.count(tenant_id=tenant_id, **filters)
    def update(self, *, tenant_id: UUID, rule_id: UUID, payload: DetectionRuleUpdate):
        data = payload.model_dump(mode="python", exclude_unset=True)
        if not data: raise ValueError("update payload must contain at least one field")
        return self.rules.update(tenant_id=tenant_id, rule_id=rule_id, data=data)
    def delete(self, *, tenant_id: UUID, rule_id: UUID): return self.rules.delete(tenant_id=tenant_id, rule_id=rule_id)
    def transition(self, *, tenant_id: UUID, rule_id: UUID, target_status: str):
        rule = self.get(tenant_id=tenant_id, rule_id=rule_id)
        if rule is None: return None
        if target_status not in TRANSITIONS.get(rule.status, set()): raise ValueError(f"Invalid lifecycle transition: {rule.status} -> {target_status}")
        data = {"status": target_status}
        if target_status == "production":
            from datetime import datetime, timezone
            data["published_at"] = datetime.now(timezone.utc)
        return self.rules.update(tenant_id=tenant_id, rule_id=rule_id, data=data)
    def list_production_rules(self, *, tenant_id: UUID, limit=500, offset=0): return self.rules.list_production_rules(tenant_id=tenant_id, limit=limit, offset=offset)
