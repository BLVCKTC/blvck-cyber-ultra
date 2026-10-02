from __future__ import annotations
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session
from app.api.deps import get_active_membership, get_db, require_permission
from app.db.models.membership import Membership
from app.schemas.alert import AlertCreate, AlertList, AlertRead, AlertUpdate
from app.services.alert_service import AlertService
router = APIRouter(prefix='/alerts', tags=['Alerts'])
def service(db: Session = Depends(get_db)): return AlertService(db)
def missing(): return HTTPException(status_code=404, detail='Alert not found.')
@router.get('', response_model=AlertList, dependencies=[Depends(require_permission('alerts.view'))])
def list_alerts(q: str | None = Query(None, max_length=200), severity: str | None = None, alert_status: str | None = Query(None, alias='status'), limit: int = Query(50, ge=1, le=500), offset: int = Query(0, ge=0), membership: Membership = Depends(get_active_membership), svc: AlertService = Depends(service)):
    items, total = svc.list(tenant_id=membership.tenant_id, limit=limit, offset=offset, q=q, severity=severity, status=alert_status)
    return AlertList(items=items, total=total, limit=limit, offset=offset)
@router.post('', response_model=AlertRead, status_code=201, dependencies=[Depends(require_permission('alerts.create'))])
def create_alert(payload: AlertCreate, membership: Membership = Depends(get_active_membership), svc: AlertService = Depends(service)): return svc.create(tenant_id=membership.tenant_id, payload=payload)
@router.get('/{alert_id}', response_model=AlertRead, dependencies=[Depends(require_permission('alerts.view'))])
def get_alert(alert_id: UUID, membership: Membership = Depends(get_active_membership), svc: AlertService = Depends(service)):
    item = svc.get(tenant_id=membership.tenant_id, alert_id=alert_id)
    if item is None: raise missing()
    return item
@router.patch('/{alert_id}', response_model=AlertRead, dependencies=[Depends(require_permission('alerts.update'))])
def update_alert(alert_id: UUID, payload: AlertUpdate, membership: Membership = Depends(get_active_membership), svc: AlertService = Depends(service)):
    try: item = svc.update(tenant_id=membership.tenant_id, alert_id=alert_id, payload=payload)
    except ValueError as exc: raise HTTPException(422, str(exc)) from exc
    if item is None: raise missing()
    return item
@router.delete('/{alert_id}', status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission('alerts.delete'))])
def delete_alert(alert_id: UUID, membership: Membership = Depends(get_active_membership), svc: AlertService = Depends(service)):
    if not svc.delete(tenant_id=membership.tenant_id, alert_id=alert_id): raise missing()
    return Response(status_code=204)
