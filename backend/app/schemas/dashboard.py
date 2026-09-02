from pydantic import BaseModel, Field

class KPIData(BaseModel):
    openAlerts: int = 0
    activeIncidents: int = 0
    mitreCoverage: float = 0
    meanTimeToTriage: float = 0

class KPIResponse(BaseModel):
    data: KPIData

class BreakdownItem(BaseModel):
    severity: str | None = None
    name: str | None = None
    count: int | None = None
    value: int | None = None

class VolumeBucket(BaseModel):
    label: str
    total: int
    escalated: int

class AlertVolumeResponse(BaseModel):
    buckets: list[VolumeBucket]

class SeverityResponse(BaseModel):
    data: list[BreakdownItem]

class SourceResponse(BaseModel):
    data: list[BreakdownItem]

class CoverageResponse(BaseModel):
    covered: int
    uncovered: int
    total: int

class DashboardSummary(BaseModel):
    tenant_id: str
    role: str
    data: str

class DashboardRange(str):
    pass

class DashboardWindow(str):
    pass

class DashboardGranularity(str):
    pass
