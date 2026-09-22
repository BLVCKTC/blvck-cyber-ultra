from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.permissions import require_platform_admin  # adjust to your actual dependency
from app.db.repositories.quarantined_event_repo import QuarantinedEventRepository
from app.schemas.quarantined_event import QuarantinedEventRead

router = APIRouter(prefix="/admin/quarantine", tags=["quarantine"])


@router.get("", response_model=list[QuarantinedEventRead])
def list_quarantined_events(
    tenant_id: UUID | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    _admin=Depends(require_platform_admin),
) -> list[QuarantinedEventRead]:
    repo = QuarantinedEventRepository(db)
    return repo.list_unresolved(tenant_id=tenant_id, limit=limit)