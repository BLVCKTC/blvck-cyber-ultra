from __future__ import annotations
from datetime import datetime, timedelta, timezone
from uuid import UUID
from sqlalchemy import func, select, case
from sqlalchemy.orm import Session
from app.db.models.alert import Alert
from app.db.models.security_event import SecurityEvent
from app.db.models.detection_rule import DetectionRule
from app.db.models.operations import Incident

OPEN_ALERT_STATUSES = ("new", "open", "acknowledged", "investigating")
ESCALATED_SEVERITIES = ("high", "critical")
ACTIVE_INCIDENT_STATUSES = ("open", "investigating", "contained")

class DashboardRepo:
    def __init__(self, db: Session, tenant_id: UUID):
        self.db, self.tenant_id = db, tenant_id

    def kpis(self, since: datetime):
        open_alerts = self.db.scalar(select(func.count()).select_from(Alert).where(Alert.tenant_id == self.tenant_id, Alert.status.in_(OPEN_ALERT_STATUSES))) or 0
        incidents = self.db.scalar(select(func.count()).select_from(Incident).where(Incident.tenant_id == self.tenant_id, Incident.status.in_(ACTIVE_INCIDENT_STATUSES))) or 0
        rule_ids = self.db.scalars(select(DetectionRule.mitre_technique_ids).where(DetectionRule.tenant_id == self.tenant_id, DetectionRule.enabled.is_(True), DetectionRule.status.in_(("production", "monitored", "tuned")))).all()
        event_ids = self.db.scalars(select(SecurityEvent.mitre_technique_id).where(SecurityEvent.tenant_id == self.tenant_id, SecurityEvent.event_time >= since, SecurityEvent.mitre_technique_id.is_not(None))).all()
        rules = {x for row in rule_ids for x in (row or [])}; events = set(event_ids)
        total = len(rules | events); covered = len(rules & events)
        return open_alerts, incidents, round(covered / total * 100, 2) if total else 0, 0

    def volume(self, since: datetime, granularity: str):
        bucket = func.date_trunc(granularity, Alert.updated_at).label("bucket")
        rows = self.db.execute(select(bucket, func.count().label("total"), func.sum(case((Alert.severity.in_(ESCALATED_SEVERITIES), 1), else_=0)).label("escalated")).where(Alert.tenant_id == self.tenant_id, Alert.updated_at >= since).group_by(bucket).order_by(bucket)).all()
        return [{"label": row.bucket.isoformat(), "total": row.total, "escalated": int(row.escalated or 0)} for row in rows]

    def severity(self, since: datetime):
        rows = self.db.execute(select(Alert.severity, func.count()).where(Alert.tenant_id == self.tenant_id, Alert.updated_at >= since).group_by(Alert.severity).order_by(Alert.severity)).all()
        return [{"severity": severity, "count": count} for severity, count in rows]

    def sources(self, since: datetime):
        rows = self.db.execute(select(SecurityEvent.source, func.count()).where(SecurityEvent.tenant_id == self.tenant_id, SecurityEvent.event_time >= since).group_by(SecurityEvent.source).order_by(func.count().desc())).all()
        return [{"name": name, "value": count} for name, count in rows]

    def coverage(self, since: datetime):
        rule_rows = self.db.scalars(select(DetectionRule.mitre_technique_ids).where(DetectionRule.tenant_id == self.tenant_id, DetectionRule.enabled.is_(True), DetectionRule.status.in_(("production", "monitored", "tuned")))).all()
        event_rows = self.db.scalars(select(SecurityEvent.mitre_technique_id).where(SecurityEvent.tenant_id == self.tenant_id, SecurityEvent.event_time >= since, SecurityEvent.mitre_technique_id.is_not(None))).all()
        all_ids = {x for row in rule_rows for x in (row or [])}; observed = set(event_rows); total = len(all_ids | observed)
        return {"covered": len(all_ids & observed), "uncovered": len((all_ids | observed) - (all_ids & observed)), "total": total}

def start_time(value: str, default_hours: int = 24) -> datetime:
    try:
        hours = {"24h": 24, "7d": 168, "30d": 720, "90d": 2160}[value]
    except KeyError:
        hours = default_hours
    return datetime.now(timezone.utc) - timedelta(hours=hours)
