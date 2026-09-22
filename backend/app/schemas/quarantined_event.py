from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class QuarantinedEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    source: str
    source_type: str
    failure_stage: str
    failure_reason: str
    raw_payload: dict[str, Any]
    partial_normalized: dict[str, Any] | None
    received_at: datetime
    quarantined_at: datetime
    resolved_at: datetime | None
    resolution_note: str | None