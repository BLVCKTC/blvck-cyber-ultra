from __future__ import annotations
 
from uuid import UUID
 
from sqlalchemy.orm import Session
 
from app.agents.orchestrator import build_investigation_graph
 
 
class OrchestrationError(Exception):
    pass
 
 
class InvestigationOrchestratorService:
    """Thin wrapper triggering the investigation graph. Deliberately
    explicit-call-only for this skeleton — NOT wired into ingest().
    There's no background/async execution mechanism anywhere in this
    codebase yet, and running an agent graph inline in the request that
    creates an Alert would couple ingestion latency to however long
    orchestration takes. Wiring this into ingestion automatically is a
    separate, later decision that needs a queue or background task
    first, not a default to fall into here.
    """
 
    def __init__(self, db: Session):
        self.db = db
 
    def run_for_alert(self, *, tenant_id: UUID, alert_id: UUID) -> dict:
        graph = build_investigation_graph(self.db)
 
        result = graph.invoke(
            {
                "tenant_id": str(tenant_id),
                "alert_id": str(alert_id),
            }
        )
 
        if result.get("error"):
            raise OrchestrationError(result["error"])
 
        return result