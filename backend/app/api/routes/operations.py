# app/api/routes/operations.py

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import inspect, select
from sqlalchemy.orm import Session

from app.api.deps import (
    get_active_membership,
    get_current_user,
    get_db,
    require_permission,
)
from app.db.models.alert import Alert
from app.db.models.membership import Membership
from app.db.models.operations import (
    AlertFeedback,
    DetectionMatch,
    Incident,
    ResponseAction,
)
from app.services.audit_service import record_audit_event


router = APIRouter(
    prefix="/operations",
    tags=["Security Operations"],
)


class FeedbackCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    label: str = Field(
        min_length=1,
        max_length=32,
    )
    comment: str | None = Field(
        default=None,
        max_length=5000,
    )


class ResponseActionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    incident_id: UUID
    action_type: str = Field(
        min_length=1,
        max_length=64,
    )
    parameters: dict[str, Any] = Field(
        default_factory=dict,
    )


class ResponseDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reason: str | None = Field(
        default=None,
        max_length=2000,
    )


def get_tenant_id(membership: Membership) -> UUID:
    return membership.tenant_id


def serialize_model(model_instance: Any) -> dict[str, Any]:
    """
    Convert a SQLAlchemy ORM instance into a dictionary containing
    only mapped database columns.

    Relationships are intentionally excluded.
    """
    mapper = inspect(model_instance).mapper

    return {
        column.key: getattr(model_instance, column.key)
        for column in mapper.column_attrs
    }


def serialize_models(model_instances: list[Any]) -> list[dict[str, Any]]:
    return [
        serialize_model(model_instance)
        for model_instance in model_instances
    ]


def get_response_action(
    db: Session,
    tenant_id: UUID,
    action_id: UUID,
) -> ResponseAction | None:
    statement = select(ResponseAction).where(
        ResponseAction.id == action_id,
        ResponseAction.tenant_id == tenant_id,
    )

    return db.scalar(statement)


@router.get(
    "/detection-matches",
    response_model=None,
    dependencies=[
        Depends(require_permission("security_events.view")),
    ],
)
def list_detection_matches(
    limit: int = Query(
        default=50,
        ge=1,
        le=500,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
    db: Session = Depends(get_db),
    membership: Membership = Depends(get_active_membership),
) -> Any:
    statement = (
        select(DetectionMatch)
        .where(
            DetectionMatch.tenant_id == get_tenant_id(membership),
        )
        .order_by(DetectionMatch.matched_at.desc())
        .offset(offset)
        .limit(limit)
    )

    matches = list(db.scalars(statement).all())

    return serialize_models(matches)


@router.get(
    "/alert-feedback",
    response_model=None,
    dependencies=[
        Depends(require_permission("alerts.view")),
    ],
)
def list_alert_feedback(
    limit: int = Query(
        default=50,
        ge=1,
        le=500,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
    db: Session = Depends(get_db),
    membership: Membership = Depends(get_active_membership),
) -> Any:
    statement = (
        select(AlertFeedback)
        .where(
            AlertFeedback.tenant_id == get_tenant_id(membership),
        )
        .order_by(AlertFeedback.created_at.desc())
        .offset(offset)
        .limit(limit)
    )

    feedback_items = list(db.scalars(statement).all())

    return serialize_models(feedback_items)


@router.post(
    "/alerts/{alert_id}/feedback",
    response_model=None,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(require_permission("alerts.view")),
    ],
)
def create_alert_feedback(
    alert_id: UUID,
    payload: FeedbackCreate,
    db: Session = Depends(get_db),
    membership: Membership = Depends(get_active_membership),
    user: Any = Depends(get_current_user),
) -> Any:
    tenant_id = get_tenant_id(membership)

    alert_statement = select(Alert).where(
        Alert.id == alert_id,
        Alert.tenant_id == tenant_id,
    )
    alert = db.scalar(alert_statement)

    if alert is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found.",
        )

    supported_labels = {
        "true_positive",
        "false_positive",
        "benign",
        "needs_review",
    }

    if payload.label not in supported_labels:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Unsupported feedback label.",
        )

    feedback_statement = select(AlertFeedback).where(
        AlertFeedback.tenant_id == tenant_id,
        AlertFeedback.alert_id == alert_id,
        AlertFeedback.user_id == user.id,
    )
    feedback = db.scalar(feedback_statement)

    if feedback is None:
        feedback = AlertFeedback(
            id=uuid4(),
            tenant_id=tenant_id,
            alert_id=alert_id,
            user_id=user.id,
            label=payload.label,
            comment=payload.comment,
        )
        db.add(feedback)
    else:
        feedback.label = payload.label
        feedback.comment = payload.comment

    db.commit()
    db.refresh(feedback)

    return serialize_model(feedback)


@router.get(
    "/response-actions",
    response_model=None,
    dependencies=[
        Depends(require_permission("incidents.view")),
    ],
)
def list_response_actions(
    limit: int = Query(
        default=50,
        ge=1,
        le=500,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
    db: Session = Depends(get_db),
    membership: Membership = Depends(get_active_membership),
) -> Any:
    statement = (
        select(ResponseAction)
        .where(
            ResponseAction.tenant_id == get_tenant_id(membership),
        )
        .order_by(ResponseAction.created_at.desc())
        .offset(offset)
        .limit(limit)
    )

    response_actions = list(db.scalars(statement).all())

    return serialize_models(response_actions)


@router.post(
    "/response-actions",
    response_model=None,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(require_permission("incidents.update")),
    ],
)
def request_response_action(
    payload: ResponseActionCreate,
    db: Session = Depends(get_db),
    membership: Membership = Depends(get_active_membership),
    user: Any = Depends(get_current_user),
) -> Any:
    tenant_id = get_tenant_id(membership)

    incident_statement = select(Incident).where(
        Incident.id == payload.incident_id,
        Incident.tenant_id == tenant_id,
    )
    incident = db.scalar(incident_statement)

    if incident is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found.",
        )

    response_action = ResponseAction(
        id=uuid4(),
        tenant_id=tenant_id,
        incident_id=incident.id,
        requested_by=user.id,
        action_type=payload.action_type,
        parameters=payload.parameters,
    )

    db.add(response_action)
    db.commit()
    db.refresh(response_action)

    return serialize_model(response_action)


@router.post(
    "/response-actions/{action_id}/approve",
    response_model=None,
    dependencies=[
        Depends(require_permission("incidents.update")),
    ],
)
def approve_response_action(
    action_id: UUID,
    payload: ResponseDecision,
    db: Session = Depends(get_db),
    membership: Membership = Depends(get_active_membership),
    user: Any = Depends(get_current_user),
) -> Any:
    tenant_id = get_tenant_id(membership)

    response_action = get_response_action(
        db,
        tenant_id,
        action_id,
    )

    if response_action is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Response action not found.",
        )

    if response_action.requested_by == user.id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The requester cannot approve their own action.",
        )

    if response_action.status != "pending_approval":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Response action is not pending approval.",
        )

    response_action.status = "approved"
    response_action.approved_by = user.id

    record_audit_event(
        db,
        tenant_id=tenant_id,
        actor_user_id=user.id,
        action="response_action.approved",
        entity_type="response_action",
        entity_id=response_action.id,
        payload={
            "action_type": response_action.action_type,
            "incident_id": str(response_action.incident_id),
            "reason": payload.reason,
        },
    )

    db.commit()
    db.refresh(response_action)

    return serialize_model(response_action)


@router.post(
    "/response-actions/{action_id}/reject",
    response_model=None,
    dependencies=[
        Depends(require_permission("incidents.update")),
    ],
)
def reject_response_action(
    action_id: UUID,
    payload: ResponseDecision,
    db: Session = Depends(get_db),
    membership: Membership = Depends(get_active_membership),
    user: Any = Depends(get_current_user),
) -> Any:
    tenant_id = get_tenant_id(membership)

    response_action = get_response_action(
        db,
        tenant_id,
        action_id,
    )

    if response_action is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Response action not found.",
        )

    if response_action.requested_by == user.id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The requester cannot reject their own action.",
        )

    if response_action.status != "pending_approval":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Response action is not pending approval.",
        )

    response_action.status = "rejected"
    response_action.approved_by = user.id

    record_audit_event(
        db,
        tenant_id=tenant_id,
        actor_user_id=user.id,
        action="response_action.rejected",
        entity_type="response_action",
        entity_id=response_action.id,
        payload={
            "action_type": response_action.action_type,
            "incident_id": str(response_action.incident_id),
            "reason": payload.reason,
        },
    )

    db.commit()
    db.refresh(response_action)

    return serialize_model(response_action)


@router.post(
    "/response-actions/{action_id}/execute",
    response_model=None,
    dependencies=[
        Depends(require_permission("incidents.update")),
    ],
)
def execute_response_action(
    action_id: UUID,
    db: Session = Depends(get_db),
    membership: Membership = Depends(get_active_membership),
) -> Any:
    tenant_id = get_tenant_id(membership)

    response_action = get_response_action(
        db,
        tenant_id,
        action_id,
    )

    if response_action is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Response action not found.",
        )

    if response_action.status != "approved":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only approved actions can execute.",
        )

    response_action.status = "executed"
    response_action.executed_at = datetime.utcnow()

    record_audit_event(
        db,
        tenant_id=tenant_id,
        actor_user_id=None,
        action="response_action.executed",
        entity_type="response_action",
        entity_id=response_action.id,
        payload={
            "action_type": response_action.action_type,
            "incident_id": str(response_action.incident_id),
            "approved_by": (
                str(response_action.approved_by)
                if response_action.approved_by
                else None
            ),
        },
    )

    db.commit()
    db.refresh(response_action)

    return serialize_model(response_action)
