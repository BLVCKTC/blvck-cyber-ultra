from typing import Annotated, Literal
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_tenant_membership, require_roles
from app.db.repositories.dashboard_repo import DashboardRepo, start_time
from app.schemas.dashboard import KPIResponse, AlertVolumeResponse, SeverityResponse, SourceResponse, CoverageResponse

router = APIRouter(tags=["dashboard"])

@router.get("/dashboard/summary")
def summary(m=Depends(require_roles(["OWNER", "ADMIN", "SOC_MANAGER", "SOC_ANALYST"]))):
    return {"tenant_id": str(m.tenant_id), "role": m.role.value if hasattr(m.role, "value") else str(m.role), "data": "secret tenant dashboard data"}

TenantAccess = Annotated[object, Depends(get_tenant_membership)]

@router.get("/v1/tenants/{tenant_id}/dashboard/kpis", response_model=KPIResponse)
def kpis(tenant_id: UUID, _: TenantAccess, db: Session = Depends(get_db), window: Literal["24h", "7d", "30d", "90d"] = Query("24h")):
    values = DashboardRepo(db, tenant_id).kpis(start_time(window))
    return {"data": {"openAlerts": values[0], "activeIncidents": values[1], "mitreCoverage": values[2], "meanTimeToTriage": values[3]}}

@router.get("/v1/tenants/{tenant_id}/dashboard/alert-volume", response_model=AlertVolumeResponse, include_in_schema=False)
@router.get("/v1/tenants/{tenant_id}/alerts/volume", response_model=AlertVolumeResponse)
def alert_volume(tenant_id: UUID, _: TenantAccess, db: Session = Depends(get_db), range: Literal["hourly", "daily", "weekly", "monthly", "yearly", "24h", "7d", "30d", "90d"] = Query("daily"), granularity: Literal["hour", "day", "week", "month"] | None = Query(None)):
    range_to_window = {"hourly": "24h", "daily": "7d", "weekly": "30d", "monthly": "90d", "yearly": "90d"}
    range_to_granularity = {"hourly": "hour", "daily": "day", "weekly": "week", "monthly": "month", "yearly": "month"}
    window = range_to_window.get(range, range)
    bucket_granularity = granularity or range_to_granularity.get(range, "hour")
    return {"buckets": DashboardRepo(db, tenant_id).volume(start_time(window), bucket_granularity)}

@router.get("/v1/tenants/{tenant_id}/dashboard/severity-breakdown", response_model=SeverityResponse, include_in_schema=False)
@router.get("/v1/tenants/{tenant_id}/alerts/severity-breakdown", response_model=SeverityResponse)
def severity_breakdown(tenant_id: UUID, _: TenantAccess, db: Session = Depends(get_db), window: Literal["24h", "7d", "30d", "90d"] = Query("24h")):
    return {"data": DashboardRepo(db, tenant_id).severity(start_time(window))}

@router.get("/v1/tenants/{tenant_id}/dashboard/source-breakdown", response_model=SourceResponse)
@router.get("/v1/tenants/{tenant_id}/events/source-breakdown", response_model=SourceResponse, include_in_schema=False)
def source_breakdown(tenant_id: UUID, _: TenantAccess, db: Session = Depends(get_db), window: Literal["24h", "7d", "30d", "90d"] = Query("24h")):
    return {"data": DashboardRepo(db, tenant_id).sources(start_time(window))}

@router.get("/v1/tenants/{tenant_id}/dashboard/mitre/coverage", response_model=CoverageResponse)
@router.get("/v1/tenants/{tenant_id}/mitre/coverage", response_model=CoverageResponse, include_in_schema=False)
def mitre_coverage(tenant_id: UUID, _: TenantAccess, db: Session = Depends(get_db), window: Literal["24h", "7d", "30d", "90d"] = Query("24h")):
    return DashboardRepo(db, tenant_id).coverage(start_time(window))
