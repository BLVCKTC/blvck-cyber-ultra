from __future__ import annotations
from datetime import datetime
from typing import Any, Literal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
AlertSeverity = Literal['info','low','medium','high','critical']
AlertStatus = Literal['new','open','acknowledged','investigating','resolved','suppressed','false_positive']
class AlertCreate(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    fingerprint: str = Field(min_length=1, max_length=128)
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=10000)
    severity: AlertSeverity
    status: AlertStatus = 'new'
    detection_rule_id: UUID | None = None
    security_event_id: UUID | None = None
    confidence: int | None = Field(default=None, ge=0, le=100)
    risk_score: int | None = Field(default=None, ge=0, le=100)
    source: str | None = Field(default=None, max_length=255)
    metadata_json: dict[str, Any] = Field(default_factory=dict)
class AlertUpdate(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=10000)
    severity: AlertSeverity | None = None
    status: AlertStatus | None = None
    confidence: int | None = Field(default=None, ge=0, le=100)
    risk_score: int | None = Field(default=None, ge=0, le=100)
    metadata_json: dict[str, Any] | None = None
class AlertRead(AlertCreate):
    model_config = ConfigDict(from_attributes=True, extra='forbid')
    id: UUID
    tenant_id: UUID
    first_seen_at: datetime
    last_seen_at: datetime
    created_at: datetime
    updated_at: datetime
class AlertList(BaseModel):
    items: list[AlertRead]
    total: int = Field(ge=0)
    limit: int = Field(ge=1, le=500)
    offset: int = Field(ge=0)
