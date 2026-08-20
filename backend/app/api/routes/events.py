from __future__ import annotations

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_active_membership, get_db, require_permission
from app.db.models.membership import Membership
from app.schemas.security_event import SecurityEventCreate, SecurityEventList, SecurityEventRead
from app.services.security_event_service import SecurityEventService

router = APIRouter(
    prefix="/events",
    tags=["Security Events"],
)

# Dependency to provide the service directly to routes
def get_event_service(db: Session = Depends(get_db)) -> SecurityEventService:
    return SecurityEventService(db)

@router.post(
    "",
    response_model=SecurityEventRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("events.ingest"))],
)
def create_event(
    payload: SecurityEventCreate,
    membership: Membership = Depends(get_active_membership),
    service: SecurityEventService = Depends(get_event_service),
):
    return service.create(tenant_id=membership.tenant_id, payload=payload)

@router.get(
    "/{event_id}",
    response_model=SecurityEventRead,
    dependencies=[Depends(require_permission("events.view"))],
)
def get_event(
    event_id: UUID,
    membership: Membership = Depends(get_active_membership),
    service: SecurityEventService = Depends(get_event_service),
):
    event = service.get(tenant_id=membership.tenant_id, event_id=event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="security_event_not_found",
        )
    return event

@router.get(
    "",
    response_model=SecurityEventList,
    dependencies=[Depends(require_permission("events.view"))],
)
def list_events(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    severity: str | None = Query(default=None, pattern="^(low|medium|high|critical)$"),
    event_type: str | None = Query(default=None, max_length=150),
    source: str | None = Query(default=None, max_length=255),
    membership: Membership = Depends(get_active_membership),
    service: SecurityEventService = Depends(get_event_service),
):
    items, total = service.list(
        tenant_id=membership.tenant_id,
        limit=limit,
        offset=offset,
        severity=severity,
        event_type=event_type,
        source=source,
    )

    return SecurityEventList(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
    )
