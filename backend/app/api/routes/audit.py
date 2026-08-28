from __future__ import annotations

from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.deps import get_active_membership, get_db, require_permission
from app.db.models.foundation import AuditLogEntry

router = APIRouter(prefix="/audit", tags=["Audit"])

@router.get("", dependencies=[Depends(require_permission("audit.view"))])
def list_audit_logs(limit: int = Query(50, ge=1, le=500), offset: int = Query(0, ge=0), action: str | None = Query(None, max_length=120), entity_type: str | None = Query(None, max_length=80), db: Session = Depends(get_db), membership=Depends(get_active_membership)):
    query = select(AuditLogEntry).where(AuditLogEntry.tenant_id == membership.tenant_id)
    if action: query = query.where(AuditLogEntry.action == action)
    if entity_type: query = query.where(AuditLogEntry.entity_type == entity_type)
    return db.scalars(query.order_by(AuditLogEntry.created_at.desc()).offset(offset).limit(limit)).all()
