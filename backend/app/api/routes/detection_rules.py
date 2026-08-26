from __future__ import annotations
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.api.deps import get_active_membership, get_db, require_permission
from app.db.models.membership import Membership
from app.schemas.detection_rule import DetectionRuleCreate, DetectionRuleList, DetectionRuleRead, DetectionRuleTransition, DetectionRuleUpdate
from app.services.detection_rule_service import DetectionRuleService
router = APIRouter(prefix="/detection-rules", tags=["Detection Rules"])
def service(db: Session = Depends(get_db)): return DetectionRuleService(db)
def missing(): return HTTPException(status_code=404, detail="Detection rule not found.")
@router.get("", response_model=DetectionRuleList, dependencies=[Depends(require_permission("detection_rules.view"))])
def list_rules(q: str | None = Query(None, max_length=100), rule_type: str | None = Query(None), severity: str | None = Query(None), rule_status: str | None = Query(None, alias="status"), enabled: bool | None = Query(None), author: str | None = Query(None), source: str | None = Query(None), limit: int = Query(50, ge=1, le=500), offset: int = Query(0, ge=0), membership: Membership = Depends(get_active_membership), svc: DetectionRuleService = Depends(service)):
    items, total = svc.list(tenant_id=membership.tenant_id, limit=limit, offset=offset, q=q, rule_type=rule_type, severity=severity, status=rule_status, enabled=enabled, author=author, source=source)
    return DetectionRuleList(items=items, total=total, limit=limit, offset=offset)
@router.get("/production", response_model=list[DetectionRuleRead], dependencies=[Depends(require_permission("detection_rules.view"))])
def production(membership: Membership = Depends(get_active_membership), svc: DetectionRuleService = Depends(service)): return svc.list_production_rules(tenant_id=membership.tenant_id)
@router.post("", response_model=DetectionRuleRead, status_code=201, dependencies=[Depends(require_permission("detection_rules.create"))])
def create(payload: DetectionRuleCreate, membership: Membership = Depends(get_active_membership), svc: DetectionRuleService = Depends(service)): return svc.create(tenant_id=membership.tenant_id, payload=payload)
@router.get("/{rule_id}", response_model=DetectionRuleRead, dependencies=[Depends(require_permission("detection_rules.view"))])
def get(rule_id: UUID, membership: Membership = Depends(get_active_membership), svc: DetectionRuleService = Depends(service)):
    item = svc.get(tenant_id=membership.tenant_id, rule_id=rule_id)
    if item is None: raise missing()
    return item
@router.patch("/{rule_id}", response_model=DetectionRuleRead, dependencies=[Depends(require_permission("detection_rules.update"))])
def update(rule_id: UUID, payload: DetectionRuleUpdate, membership: Membership = Depends(get_active_membership), svc: DetectionRuleService = Depends(service)):
    try: item = svc.update(tenant_id=membership.tenant_id, rule_id=rule_id, payload=payload)
    except ValueError as exc: raise HTTPException(422, str(exc)) from exc
    if item is None: raise missing()
    return item
@router.post("/{rule_id}/transition", response_model=DetectionRuleRead, dependencies=[Depends(require_permission("detection_rules.transition"))])
def transition(rule_id: UUID, payload: DetectionRuleTransition, membership: Membership = Depends(get_active_membership), svc: DetectionRuleService = Depends(service)):
    try: item = svc.transition(tenant_id=membership.tenant_id, rule_id=rule_id, target_status=payload.target_status)
    except ValueError as exc: raise HTTPException(409, str(exc)) from exc
    if item is None: raise missing()
    return item
@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("detection_rules.delete"))])
def remove(rule_id: UUID, membership: Membership = Depends(get_active_membership), svc: DetectionRuleService = Depends(service)):
    if not svc.delete(tenant_id=membership.tenant_id, rule_id=rule_id): raise missing()
