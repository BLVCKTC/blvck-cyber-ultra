from fastapi import APIRouter, Depends

from app.api.deps import require_roles

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary")
def summary(
    m=Depends(require_roles(["SOC_ADMIN", "SOC_ANALYST"]))
):
    return {
        "tenant_id": m.tenant_id,
        "role": m.role,
        "data": "secret tenant dashboard data",
    }
