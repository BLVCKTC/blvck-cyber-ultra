from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_active_membership, get_db, require_permission
from app.db.models.membership import Membership
from app.schemas.security_event import (
    SecurityEventCreate,
    SecurityEventList,
    SecurityEventRead,
    SecurityEventUpdate,
)
from app.services.security_event_service import SecurityEventService

router = APIRouter(
    prefix="/security-events",
    tags=["Security Events"],
    dependencies=[Depends(require_permission("security.events.view"))],
)

def get_security_service(db: Session = Depends(get_db)) -> SecurityEventService:
    return SecurityEventService(db)

@router.post(
    "",
    response_model=SecurityEventRead,
    status_code=status.HTTP_201_CREATED,
)
def create_security_event(
    payload: SecurityEventCreate,
    membership: Membership = Depends(get_active_membership),
    service: SecurityEventService = Depends(get_security_service),
) -> SecurityEventRead:
    return service.create(tenant_id=membership.tenant_id, payload=payload)

@router.get("", response_model=SecurityEventList)
def list_security_events(
    q: str | None = Query(default=None, max_length=100, description="Global search across all event fields"),
    severity: str | None = Query(default=None, pattern="^(low|medium|high|critical)$"),
    start_time: datetime | None = Query(default=None),
    end_time: datetime | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    membership: Membership = Depends(get_active_membership),
    service: SecurityEventService = Depends(get_security_service),
) -> SecurityEventList:
    # All filtering is now consolidated into a single service call
    # The service layer should implement a SQL OR for the 'q' parameter
    items, total = service.list(
        tenant_id=membership.tenant_id,
        q=q,
        severity=severity,
        start_time=start_time,
        end_time=end_time,
        limit=limit,
        offset=offset,
    )

    return SecurityEventList(items=items, total=total, limit=limit, offset=offset)

@router.get("/{event_id}", response_model=SecurityEventRead)
def get_security_event(
    event_id: UUID,
    membership: Membership = Depends(get_active_membership),
    service: SecurityEventService = Depends(get_security_service),
) -> SecurityEventRead:
    event = service.get(tenant_id=membership.tenant_id, event_id=event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Security event not found.")
    return event

@router.patch("/{event_id}", response_model=SecurityEventRead)
def update_security_event(
    event_id: UUID,
    payload: SecurityEventUpdate,
    membership: Membership = Depends(get_active_membership),
    service: SecurityEventService = Depends(get_security_service),
) -> SecurityEventRead:
    # Production SOCs update status (triage) rather than deleting records
    updated_event = service.update(
        tenant_id=membership.tenant_id, 
        event_id=event_id, 
        payload=payload
    )
    if not updated_event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Security event not found.")
    return updated_event

@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_security_event(
    event_id: UUID,
    membership: Membership = Depends(get_active_membership),
    service: SecurityEventService = Depends(get_security_service),
) -> None:
    if not service.delete(tenant_id=membership.tenant_id, event_id=event_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Security event not found.")

