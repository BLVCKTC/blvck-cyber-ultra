from __future__ import annotations
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_active_membership, get_db, require_permission
from app.db.models.membership import Membership
from app.schemas.investigation import EvidenceCreate, EvidenceRead, InvestigationCreate, InvestigationRead, InvestigationUpdate
from app.services.investigation_service import InvestigationService
router = APIRouter(prefix='/investigations', tags=['Investigations'])
def svc(db: Session = Depends(get_db)): return InvestigationService(db)
@router.post('', response_model=InvestigationRead, status_code=201, dependencies=[Depends(require_permission('investigations.create'))])
def create(payload: InvestigationCreate, membership: Membership = Depends(get_active_membership), service: InvestigationService = Depends(svc)): return service.create(membership.tenant_id, payload)
@router.get('/{investigation_id}', response_model=InvestigationRead, dependencies=[Depends(require_permission('investigations.view'))])
def get(investigation_id: UUID, membership: Membership = Depends(get_active_membership), service: InvestigationService = Depends(svc)):
    item = service.get(membership.tenant_id, investigation_id)
    if not item: raise HTTPException(404, 'Investigation not found.')
    return item
@router.patch('/{investigation_id}', response_model=InvestigationRead, dependencies=[Depends(require_permission('investigations.update'))])
def update(investigation_id: UUID, payload: InvestigationUpdate, membership: Membership = Depends(get_active_membership), service: InvestigationService = Depends(svc)):
    item = service.update(membership.tenant_id, investigation_id, payload)
    if not item: raise HTTPException(404, 'Investigation not found.')
    return item
@router.get('/{investigation_id}/evidence', response_model=list[EvidenceRead], dependencies=[Depends(require_permission('investigations.view'))])
def list_evidence(investigation_id: UUID, membership: Membership = Depends(get_active_membership), service: InvestigationService = Depends(svc)):
    if not service.get(membership.tenant_id, investigation_id): raise HTTPException(404, 'Investigation not found.')
    return service.evidence(membership.tenant_id, investigation_id)
@router.post('/{investigation_id}/evidence', response_model=EvidenceRead, status_code=201, dependencies=[Depends(require_permission('investigations.update'))])
def add_evidence(investigation_id: UUID, payload: EvidenceCreate, membership: Membership = Depends(get_active_membership), service: InvestigationService = Depends(svc)):
    item = service.add_evidence(membership.tenant_id, investigation_id, payload)
    if not item: raise HTTPException(404, 'Investigation not found.')
    return item
