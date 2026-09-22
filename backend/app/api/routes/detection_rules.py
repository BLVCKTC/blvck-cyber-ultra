from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import (
    get_active_membership,
    get_db,
    require_permission,
)
from app.schemas.detection_rule import CanaryPromotionStatusOut
from app.services.canary_promotion_service import CanaryPromotionService

from app.db.models.membership import Membership
from app.schemas.detection_rule import (
    DetectionRuleCreate,
    DetectionRuleList,
    DetectionRuleRead,
    DetectionRuleTransition,
    DetectionRuleUpdate,
    ValidationWarningOut,
    DetectionRuleTransitionResult,
)
from app.schemas.backtest import BacktestCreate, BacktestMatchList, BacktestRead

from app.services.detection_rule_service import (
    DetectionRuleService,
    RuleLockedError,
    SeparationOfDutiesError,
    RuleValidationError,
)
from app.services.backtest_service import BacktestNotFoundError, BacktestService

router = APIRouter(
    prefix="/detection-rules",
    tags=["Detection Rules"],
)


def service(db: Session = Depends(get_db)) -> DetectionRuleService:
    return DetectionRuleService(db)


def missing() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Detection rule not found.",
    )


@router.get(
    "",
    response_model=DetectionRuleList,
    dependencies=[Depends(require_permission("detections.view"))],
)
def list_rules(
    q: str | None = Query(None, max_length=100),
    rule_type: str | None = Query(None),
    severity: str | None = Query(None),
    rule_status: str | None = Query(None, alias="status"),
    enabled: bool | None = Query(None),
    author: str | None = Query(None),
    source: str | None = Query(None),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    membership: Membership = Depends(get_active_membership),
    svc: DetectionRuleService = Depends(service),
):
    items, total = svc.list(
        tenant_id=membership.tenant_id,
        limit=limit,
        offset=offset,
        q=q,
        rule_type=rule_type,
        severity=severity,
        status=rule_status,
        enabled=enabled,
        author=author,
        source=source,
    )

    return DetectionRuleList(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/production",
    response_model=list[DetectionRuleRead],
    dependencies=[Depends(require_permission("detections.view"))],
)
def production(
    membership: Membership = Depends(get_active_membership),
    svc: DetectionRuleService = Depends(service),
):
    return svc.list_production_rules(
        tenant_id=membership.tenant_id,
    )


@router.post(
    "",
    response_model=DetectionRuleRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("detections.create"))],
)
def create(
    payload: DetectionRuleCreate,
    membership: Membership = Depends(get_active_membership),
    svc: DetectionRuleService = Depends(service),
):
    return svc.create(
        tenant_id=membership.tenant_id,
        payload=payload,
        actor_id=membership.user_id,
    )


@router.get(
    "/{rule_id}",
    response_model=DetectionRuleRead,
    dependencies=[Depends(require_permission("detections.view"))],
)
def get(
    rule_id: UUID,
    membership: Membership = Depends(get_active_membership),
    svc: DetectionRuleService = Depends(service),
):
    item = svc.get(
        tenant_id=membership.tenant_id,
        rule_id=rule_id,
    )

    if item is None:
        raise missing()

    return item


@router.patch(
    "/{rule_id}",
    response_model=DetectionRuleRead,
    dependencies=[Depends(require_permission("detections.update"))],
)
def update(
    rule_id: UUID,
    payload: DetectionRuleUpdate,
    membership: Membership = Depends(get_active_membership),
    svc: DetectionRuleService = Depends(service),
):
    try:
        item = svc.update(
            tenant_id=membership.tenant_id,
            rule_id=rule_id,
            data=payload.model_dump(exclude_unset=True),
            actor_id=membership.user_id,
        )
    except RuleLockedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    if item is None:
        raise missing()

    return item


@router.post(
    "/{rule_id}/revise",
    response_model=DetectionRuleRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("detections.create"))],
)
def revise(
    rule_id: UUID,
    payload: DetectionRuleUpdate,
    membership: Membership = Depends(get_active_membership),
    svc: DetectionRuleService = Depends(service),
):
    try:
        item = svc.propose_revision(
            tenant_id=membership.tenant_id,
            rule_id=rule_id,
            payload=payload,
            actor_id=membership.user_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    if item is None:
        raise missing()

    return item


@router.post(
    "/{rule_id}/transition",
    response_model=DetectionRuleTransitionResult,
    dependencies=[Depends(require_permission("detections.transition"))],
)
def transition(
    rule_id: UUID,
    payload: DetectionRuleTransition,
    membership: Membership = Depends(get_active_membership),
    svc: DetectionRuleService = Depends(service),
):
    try:
        result = svc.transition(
            tenant_id=membership.tenant_id,
            rule_id=rule_id,
            target_status=payload.target_status,
            actor_id=membership.user_id,
            notes=payload.notes,
        )
    except SeparationOfDutiesError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
    except RuleValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=[
                {
                    "code": issue.code,
                    "message": issue.message,
                    "field": issue.field,
                }
                for issue in exc.issues
            ],
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    if result is None:
        raise missing()

    return DetectionRuleTransitionResult(
        rule=result.rule,
        warnings=[
            ValidationWarningOut(
                code=w.code,
                message=w.message,
                field=w.field,
            )
            for w in result.warnings
        ],
    )

@router.delete(
    "/{rule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("detections.delete"))],
)
def remove(
    rule_id: UUID,
    membership: Membership = Depends(get_active_membership),
    svc: DetectionRuleService = Depends(service),
):
    try:
        deleted = svc.delete(
            tenant_id=membership.tenant_id,
            rule_id=rule_id,
        )
    except RuleLockedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    if not deleted:
        raise missing()

def backtest_service(db: Session = Depends(get_db)) -> BacktestService:
    return BacktestService(db)


def backtest_missing() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Backtest run not found.",
    )


@router.post(
    "/{rule_id}/backtests",
    response_model=BacktestRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("detections.backtest"))],
)
def create_backtest(
    rule_id: UUID,
    payload: BacktestCreate,
    membership: Membership = Depends(get_active_membership),
    svc: BacktestService = Depends(backtest_service),
):
    if payload.window_start >= payload.window_end:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="window_start must be earlier than window_end",
        )

    try:
        run = svc.run_backtest(
            tenant_id=membership.tenant_id,
            rule_id=rule_id,
            window_start=payload.window_start,
            window_end=payload.window_end,
            requested_by_id=membership.user_id,
        )
    except BacktestNotFoundError:
        raise missing()

    # Returns 201 even if run.status ends up "failed" — the request to
    # backtest succeeded; the rule's own execution failing (e.g. an
    # unsupported Sigma construct) is data on the run, not an HTTP error.
    return run


@router.get(
    "/{rule_id}/backtests/{backtest_id}",
    response_model=BacktestRead,
    dependencies=[Depends(require_permission("detections.view"))],
)
def get_backtest(
    rule_id: UUID,
    backtest_id: UUID,
    membership: Membership = Depends(get_active_membership),
    svc: BacktestService = Depends(backtest_service),
):
    run = svc.get_backtest(tenant_id=membership.tenant_id, run_id=backtest_id)

    if run is None or run.detection_rule_id != rule_id:
        raise backtest_missing()

    return run


@router.get(
    "/{rule_id}/backtests/{backtest_id}/matches",
    response_model=BacktestMatchList,
    dependencies=[Depends(require_permission("detections.view"))],
)
def list_backtest_matches(
    rule_id: UUID,
    backtest_id: UUID,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    membership: Membership = Depends(get_active_membership),
    svc: BacktestService = Depends(backtest_service),
):
    run = svc.get_backtest(tenant_id=membership.tenant_id, run_id=backtest_id)

    if run is None or run.detection_rule_id != rule_id:
        raise backtest_missing()

    # Pagination happens in Python here — list_matches() fetches every
    # match for the run first, same limitation as before. Push this into
    # real SQL LIMIT/OFFSET in BacktestService if runs start producing
    # thousands of candidates.
    all_matches = svc.list_matches(tenant_id=membership.tenant_id, run_id=backtest_id)

    return BacktestMatchList(
        items=all_matches[offset : offset + limit],
        total=len(all_matches),
        limit=limit,
        offset=offset,
    )

def canary_promotion_service(db: Session = Depends(get_db)) -> CanaryPromotionService:
    return CanaryPromotionService(db)
 
 
@router.get(
    "/{rule_id}/canary-promotion-status",
    response_model=CanaryPromotionStatusOut,
    dependencies=[Depends(require_permission("detections.view"))],
)
def canary_promotion_status(
    rule_id: UUID,
    membership: Membership = Depends(get_active_membership),
    svc: CanaryPromotionService = Depends(canary_promotion_service),
):
    try:
        result = svc.get_status(tenant_id=membership.tenant_id, rule_id=rule_id)
    except ValueError:
        raise missing()
 
    return result