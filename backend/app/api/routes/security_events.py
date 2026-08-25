from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import (
    get_active_membership,
    get_db,
    require_permission,
)
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
)


def get_security_service(
    db: Session = Depends(get_db),
) -> SecurityEventService:
    return SecurityEventService(db)


def event_not_found() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Security event not found.",
    )


# ----------------------------------------------------------------------
# Create
# ----------------------------------------------------------------------

@router.post(
    "",
    response_model=SecurityEventRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(require_permission("security.events.create")),
    ],
)
def create_security_event(
    payload: SecurityEventCreate,
    membership: Membership = Depends(get_active_membership),
    service: SecurityEventService = Depends(get_security_service),
) -> SecurityEventRead:
    return service.create(
        tenant_id=membership.tenant_id,
        payload=payload,
    )


# ----------------------------------------------------------------------
# List
# ----------------------------------------------------------------------

@router.get(
    "",
    response_model=SecurityEventList,
    dependencies=[
        Depends(require_permission("security.events.view")),
    ],
)
def list_security_events(
    q: str | None = Query(
        default=None,
        max_length=100,
        description="Search across normalized event fields.",
    ),
    severity: str | None = Query(
        default=None,
        pattern="^(info|low|medium|high|critical)$",
    ),
    event_status: str | None = Query(
        default=None,
        alias="status",
        pattern="^(open|processing|processed|failed|suppressed)$",
    ),
    event_category: str | None = Query(
        default=None,
        max_length=100,
    ),
    event_type: str | None = Query(
        default=None,
        max_length=150,
    ),
    source: str | None = Query(
        default=None,
        max_length=255,
    ),
    source_type: str | None = Query(
        default=None,
        max_length=100,
    ),
    hostname: str | None = Query(
        default=None,
        max_length=255,
    ),
    user_identifier: str | None = Query(
        default=None,
        max_length=255,
    ),
    mitre_technique_id: str | None = Query(
        default=None,
        max_length=50,
    ),
    start_time: datetime | None = Query(
        default=None,
        description="Return events occurring on or after this timestamp.",
    ),
    end_time: datetime | None = Query(
        default=None,
        description="Return events occurring on or before this timestamp.",
    ),
    limit: int = Query(
        default=50,
        ge=1,
        le=500,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
    membership: Membership = Depends(get_active_membership),
    service: SecurityEventService = Depends(get_security_service),
) -> SecurityEventList:
    if (
        start_time is not None
        and end_time is not None
        and start_time > end_time
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_time must be earlier than or equal to end_time.",
        )

    items, total = service.list(
        tenant_id=membership.tenant_id,
        limit=limit,
        offset=offset,
        q=q,
        severity=severity,
        status=event_status,
        event_category=event_category,
        event_type=event_type,
        source=source,
        source_type=source_type,
        hostname=hostname,
        user_identifier=user_identifier,
        mitre_technique_id=mitre_technique_id,
        start_time=start_time,
        end_time=end_time,
    )

    return SecurityEventList(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
    )


# ----------------------------------------------------------------------
# Get
# ----------------------------------------------------------------------

@router.get(
    "/{event_id}",
    response_model=SecurityEventRead,
    dependencies=[
        Depends(require_permission("security.events.view")),
    ],
)
def get_security_event(
    event_id: UUID,
    membership: Membership = Depends(get_active_membership),
    service: SecurityEventService = Depends(get_security_service),
) -> SecurityEventRead:
    event = service.get(
        tenant_id=membership.tenant_id,
        event_id=event_id,
    )

    if event is None:
        raise event_not_found()

    return event


# ----------------------------------------------------------------------
# Update
# ----------------------------------------------------------------------

@router.patch(
    "/{event_id}",
    response_model=SecurityEventRead,
    dependencies=[
        Depends(require_permission("security.events.update")),
    ],
)
def update_security_event(
    event_id: UUID,
    payload: SecurityEventUpdate,
    membership: Membership = Depends(get_active_membership),
    service: SecurityEventService = Depends(get_security_service),
) -> SecurityEventRead:
    if not payload.model_dump(exclude_unset=True):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="At least one field is required.",
        )

    event = service.update(
        tenant_id=membership.tenant_id,
        event_id=event_id,
        payload=payload,
    )

    if event is None:
        raise event_not_found()

    return event


# ----------------------------------------------------------------------
# Delete
# ----------------------------------------------------------------------

@router.delete(
    "/{event_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(require_permission("security.events.delete")),
    ],
)
def delete_security_event(
    event_id: UUID,
    membership: Membership = Depends(get_active_membership),
    service: SecurityEventService = Depends(get_security_service),
) -> None:
    deleted = service.delete(
        tenant_id=membership.tenant_id,
        event_id=event_id,
    )

    if not deleted:
        raise event_not_found()

    return None
