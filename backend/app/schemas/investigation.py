from __future__ import annotations
from datetime import datetime
from typing import Any, Literal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
InvestigationStatus = Literal['open','investigating','resolved','closed']
class InvestigationCreate(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    title: str = Field(min_length=1, max_length=255)
    summary: str | None = Field(default=None, max_length=10000)
    alert_id: UUID | None = None
    status: InvestigationStatus = 'open'
    assignee_id: UUID | None = None
    metadata_json: dict[str, Any] = Field(default_factory=dict)
class InvestigationUpdate(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    title: str | None = Field(default=None, min_length=1, max_length=255)
    summary: str | None = Field(default=None, max_length=10000)
    status: InvestigationStatus | None = None
    assignee_id: UUID | None = None
    metadata_json: dict[str, Any] | None = None
class EvidenceCreate(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    evidence_type: str = Field(min_length=1, max_length=32)
    title: str = Field(min_length=1, max_length=255)
    reference: str | None = Field(default=None, max_length=512)
    notes: str | None = Field(default=None, max_length=10000)
    metadata_json: dict[str, Any] = Field(default_factory=dict)
class EvidenceRead(EvidenceCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID; tenant_id: UUID; investigation_id: UUID; created_at: datetime
class InvestigationRead(InvestigationCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID; tenant_id: UUID; created_at: datetime; updated_at: datetime
