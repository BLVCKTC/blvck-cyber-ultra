# app/db/repositories/canary_match_repo.py
from __future__ import annotations
from typing import Any, Mapping
from uuid import UUID
from sqlalchemy.orm import Session
from backend.app.db.models.canary import CanaryMatch

class CanaryMatchRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, *, tenant_id: UUID, data: Mapping[str, Any]) -> CanaryMatch:
        match = CanaryMatch(tenant_id=tenant_id, **dict(data))
        self.db.add(match)
        self.db.commit()
        self.db.refresh(match)
        return match