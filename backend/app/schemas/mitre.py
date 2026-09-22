import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.db.models.mitre import MitreDomain, MitreSyncStatus


class MitreTacticOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    mitre_id: str
    shortname: str
    name: str
    domain: MitreDomain
    url: str | None = None


class MitreTechniqueOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    mitre_id: str
    name: str
    domain: MitreDomain
    is_subtechnique: bool
    parent_technique_id: uuid.UUID | None = None
    platforms: list[str] | None = None
    url: str | None = None


class MitreSyncLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    domain: MitreDomain
    mitre_version: str | None = None
    status: MitreSyncStatus
    objects_created: int
    objects_updated: int
    objects_deprecated: int
    error_message: str | None = None
    started_at: datetime
    completed_at: datetime | None = None


class DetectionRuleTechniqueLinkIn(BaseModel):
    mitre_technique_id: uuid.UUID

class MitreCoverageItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    technique: MitreTechniqueOut
    covering_rule_count: int
    covered: bool


class MitreCoverageOut(BaseModel):
    model_config = ConfigDict(extra="forbid")

    domain: MitreDomain
    items: list[MitreCoverageItemOut]
    total_techniques: int
    covered_count: int
    uncovered_count: int
    coverage_percent: float