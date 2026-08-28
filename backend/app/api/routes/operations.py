from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_active_membership, get_current_user, get_db, require_permission
from app.db.models.alert import Alert
from app.db.models.membership import Membership
from app.db.models.operations import AlertFeedback, DetectionMatch, Incident, ResponseAction, RuleVersion

router = APIRouter(prefix="/operations", tags=["Security Operations"])

class FeedbackCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    label: str = Field(min_length=1, max_length=32)
    comment: str | None = Field(default=None, max_length=5000)

class ResponseActionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    incident_id: UUID
    action_type: str = Field(min_length=1, max_length=64)
    parameters: dict = Field(default_factory=dict)

class ResponseDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")
    reason: str | None = Field(default=None, max_length=2000)


def _tenant(membership: Membership):
    return membership.tenant_id


def _action(db: Session, tenant_id: UUID, action_id: UUID):
    return db.scalar(select(ResponseAction).where(ResponseAction.id == action_id, ResponseAction.tenant_id == tenant_id))

@router.get("/rule-versions", dependencies=[Depends(require_permission("detection_rules.view"))])
def list_rule_versions(limit: int = Query(50, ge=1, le=500), offset: int = Query(0, ge=0), db: Session = Depends(get_db), membership=Depends(get_active_membership)):
    return db.scalars(select(RuleVersion).where(RuleVersion.tenant_id == _tenant(membership)).order_by(RuleVersion.created_at.desc()).offset(offset).limit(limit)).all()

@router.get("/detection-matches", dependencies=[Depends(require_permission("security_events.view"))])
def list_detection_matches(limit: int = Query(50, ge=1, le=500), offset: int = Query(0, ge=0), db: Session = Depends(get_db), membership=Depends(get_active_membership)):
    return db.scalars(select(DetectionMatch).where(DetectionMatch.tenant_id == _tenant(membership)).order_by(DetectionMatch.matched_at.desc()).offset(offset).limit(limit)).all()

@router.get("/alert-feedback", dependencies=[Depends(require_permission("alerts.view"))])
def list_alert_feedback(limit: int = Query(50, ge=1, le=500), offset: int = Query(0, ge=0), db: Session = Depends(get_db), membership=Depends(get_active_membership)):
    return db.scalars(select(AlertFeedback).where(AlertFeedback.tenant_id == _tenant(membership)).order_by(AlertFeedback.created_at.desc()).offset(offset).limit(limit)).all()

@router.post("/alerts/{alert_id}/feedback", status_code=201, dependencies=[Depends(require_permission("alerts.view"))])
def create_feedback(alert_id: UUID, payload: FeedbackCreate, db: Session = Depends(get_db), membership=Depends(get_active_membership), user=Depends(get_current_user)):
    alert = db.scalar(select(Alert).where(Alert.id == alert_id, Alert.tenant_id == _tenant(membership)))
    if alert is None:
        raise HTTPException(404, "Alert not found.")
    if payload.label not in {"true_positive", "false_positive", "benign", "needs_review"}:
        raise HTTPException(422, "Unsupported feedback label.")
    item = db.scalar(select(AlertFeedback).where(AlertFeedback.tenant_id == _tenant(membership), AlertFeedback.alert_id == alert_id, AlertFeedback.user_id == user.id))
    if item:
        item.label, item.comment = payload.label, payload.comment
    else:
        item = AlertFeedback(id=uuid4(), tenant_id=_tenant(membership), alert_id=alert_id, user_id=user.id, label=payload.label, comment=payload.comment)
        db.add(item)
    db.commit(); db.refresh(item)
    return item

@router.get("/response-actions", dependencies=[Depends(require_permission("incidents.view"))])
def list_response_actions(limit: int = Query(50, ge=1, le=500), offset: int = Query(0, ge=0), db: Session = Depends(get_db), membership=Depends(get_active_membership)):
    return db.scalars(select(ResponseAction).where(ResponseAction.tenant_id == _tenant(membership)).order_by(ResponseAction.created_at.desc()).offset(offset).limit(limit)).all()

@router.post("/response-actions", status_code=201, dependencies=[Depends(require_permission("incidents.update"))])
def request_response_action(payload: ResponseActionCreate, db: Session = Depends(get_db), membership=Depends(get_active_membership), user=Depends(get_current_user)):
    incident = db.scalar(select(Incident).where(Incident.id == payload.incident_id, Incident.tenant_id == _tenant(membership)))
    if incident is None: raise HTTPException(404, "Incident not found.")
    item = ResponseAction(id=uuid4(), tenant_id=_tenant(membership), incident_id=incident.id, requested_by=user.id, action_type=payload.action_type, parameters=payload.parameters)
    db.add(item); db.commit(); db.refresh(item)
    return item

@router.post("/response-actions/{action_id}/approve", dependencies=[Depends(require_permission("incidents.update"))])
def approve_response_action(action_id: UUID, payload: ResponseDecision, db: Session = Depends(get_db), membership=Depends(get_active_membership), user=Depends(get_current_user)):
    item = _action(db, _tenant(membership), action_id)
    if item is None: raise HTTPException(404, "Response action not found.")
    if item.requested_by == user.id: raise HTTPException(409, "The requester cannot approve their own action.")
    if item.status != "pending_approval": raise HTTPException(409, "Response action is not pending approval.")
    item.status, item.approved_by = "approved", user.id
    db.commit(); db.refresh(item); return item

@router.post("/response-actions/{action_id}/reject", dependencies=[Depends(require_permission("incidents.update"))])
def reject_response_action(action_id: UUID, payload: ResponseDecision, db: Session = Depends(get_db), membership=Depends(get_active_membership), user=Depends(get_current_user)):
    item = _action(db, _tenant(membership), action_id)
    if item is None: raise HTTPException(404, "Response action not found.")
    if item.requested_by == user.id: raise HTTPException(409, "The requester cannot reject their own action.")
    if item.status != "pending_approval": raise HTTPException(409, "Response action is not pending approval.")
    item.status = "rejected"; item.approved_by = user.id
    db.commit(); db.refresh(item); return item

@router.post("/response-actions/{action_id}/execute", dependencies=[Depends(require_permission("incidents.update"))])
def execute_response_action(action_id: UUID, db: Session = Depends(get_db), membership=Depends(get_active_membership)):
    item = _action(db, _tenant(membership), action_id)
    if item is None: raise HTTPException(404, "Response action not found.")
    if item.status != "approved": raise HTTPException(409, "Only approved actions can execute.")
    item.status, item.executed_at = "executed", datetime.utcnow()
    db.commit(); db.refresh(item); return item
