from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

RuleType = Literal["threshold", "query", "correlation", "behavioral", "sigma"]
RuleSeverity = Literal["info", "low", "medium", "high", "critical"]
RuleStatus = Literal["draft", "testing", "backtested", "canary", "approved", "production", "monitored", "tuned", "retired"]

class DetectionRuleBase(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=4000)
    rule_type: RuleType
    severity: RuleSeverity
    status: RuleStatus = "draft"
    version: int = Field(default=1, ge=1)
    enabled: bool = True
    query: str | None = Field(default=None, max_length=20000)
    configuration: dict[str, Any] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list, max_length=50)
    mitre_technique_ids: list[str] = Field(default_factory=list, max_length=50)
    mitre_tactic_ids: list[str] = Field(default_factory=list, max_length=50)
    author: str | None = Field(default=None, max_length=255)
    source: str | None = Field(default=None, max_length=255)

class DetectionRuleCreate(DetectionRuleBase):
    status: Literal["draft"] = "draft"

class DetectionRuleUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=4000)
    rule_type: RuleType | None = None
    severity: RuleSeverity | None = None
    version: int | None = Field(default=None, ge=1)
    enabled: bool | None = None
    query: str | None = Field(default=None, max_length=20000)
    configuration: dict[str, Any] | None = None
    tags: list[str] | None = Field(default=None, max_length=50)
    mitre_technique_ids: list[str] | None = Field(default=None, max_length=50)
    mitre_tactic_ids: list[str] | None = Field(default=None, max_length=50)
    author: str | None = Field(default=None, max_length=255)
    source: str | None = Field(default=None, max_length=255)

class DetectionRuleRead(DetectionRuleBase):
    model_config = ConfigDict(from_attributes=True, extra="forbid", use_enum_values=True)
    id: UUID
    tenant_id: UUID
    created_at: datetime
    updated_at: datetime
    published_at: datetime | None

class DetectionRuleList(BaseModel):
    model_config = ConfigDict(extra="forbid")
    items: list[DetectionRuleRead]
    total: int = Field(ge=0)
    limit: int = Field(ge=1, le=500)
    offset: int = Field(ge=0)

class DetectionRuleTransition(BaseModel):
    model_config = ConfigDict(extra="forbid")
    target_status: RuleStatus
