from __future__ import annotations

from fastapi import APIRouter, Depends
from app.api.deps import get_active_membership, require_permission
from app.db.models.membership import Membership

router = APIRouter(
    prefix="/security/events",
    tags=["Security Events"],
)

@router.get(
    "",
    summary="List security events",
    dependencies=[Depends(require_permission("security.events.view"))],
)
def list_security_events(
    membership: Membership = Depends(get_active_membership),
):
    return {
        "items": [],
        "total": 0,
        "tenant_id": str(membership.tenant_id),
    }
