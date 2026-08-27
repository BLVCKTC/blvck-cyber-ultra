from __future__ import annotations
from uuid import UUID, uuid4
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.deps import get_active_membership, get_db, require_permission
from app.db.models.membership import Membership
from app.db.models.operations import Incident

router = APIRouter(prefix="/incidents", tags=["Incidents"])

class IncidentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    severity: str = Field(min_length=1, max_length=16)
    summary: str | None = None

class IncidentRead(IncidentCreate):
    id: UUID
    tenant_id: UUID
    status: str

@router.post("", response_model=IncidentRead, status_code=201, dependencies=[Depends(require_permission("incidents.create"))])
def create_incident(payload: IncidentCreate, membership: Membership = Depends(get_active_membership), db: Session = Depends(get_db)):
    item = Incident(id=uuid4(), tenant_id=membership.tenant_id, title=payload.title, severity=payload.severity, summary=payload.summary)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@router.get("", response_model=list[IncidentRead], dependencies=[Depends(require_permission("incidents.view"))])
def list_incidents(membership: Membership = Depends(get_active_membership), db: Session = Depends(get_db)):
    return list(db.scalars(select(Incident).where(Incident.tenant_id == membership.tenant_id).order_by(Incident.created_at.desc())))

@router.get("/{incident_id}", response_model=IncidentRead, dependencies=[Depends(require_permission("incidents.view"))])
def get_incident(incident_id: UUID, membership: Membership = Depends(get_active_membership), db: Session = Depends(get_db)):
    item = db.scalar(select(Incident).where(Incident.id == incident_id, Incident.tenant_id == membership.tenant_id))
    if item is None:
        raise HTTPException(status_code=404, detail="Incident not found.")
    return item
