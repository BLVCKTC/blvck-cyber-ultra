from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class BacktestCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    window_start: datetime
    window_end: datetime


class BacktestRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    detection_rule_id: UUID
    window_start: datetime
    window_end: datetime
    status: str
    total_candidates: int
    error_message: str | None
    requested_by_id: UUID | None
    started_at: datetime
    completed_at: datetime | None


class BacktestMatchRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    backtest_run_id: UUID
    window_start: datetime
    window_end: datetime
    group_key: dict[str, Any]
    metric_value: float
    event_ids: list[UUID]
    created_at: datetime


class BacktestMatchList(BaseModel):
    model_config = ConfigDict(extra="forbid")
    items: list[BacktestMatchRead]
    total: int
    limit: int
    offset: int