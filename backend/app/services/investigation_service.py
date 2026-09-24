from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models.alert import Alert
from app.db.models.investigation import Evidence, Investigation
from app.schemas.investigation import (
    EvidenceCreate,
    InvestigationCreate,
    InvestigationUpdate,
)


class InvestigationService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(
        self,
        tenant_id: UUID,
        investigation_id: UUID,
    ):
        return self.db.scalar(
            select(Investigation).where(
                Investigation.id == investigation_id,
                Investigation.tenant_id == tenant_id,
            )
        )

    def create(
        self,
        tenant_id: UUID,
        payload: InvestigationCreate,
    ):
        data = payload.model_dump()
        alert_id = data.get("alert_id")

        # Validate that the alert belongs to the current tenant.
        if alert_id is not None:
            alert = self.db.scalar(
                select(Alert).where(
                    Alert.id == alert_id,
                    Alert.tenant_id == tenant_id,
                )
            )

            if alert is None:
                raise ValueError(
                    f"Alert {alert_id} not found for this tenant."
                )

        item = Investigation(
            tenant_id=tenant_id,
            **data,
        )

        self.db.add(item)

        try:
            self.db.commit()

        except IntegrityError:
            # Two concurrent requests may both pass the validation above
            # and attempt to create an investigation for the same alert.
            # The database unique constraint rejects one request. Roll back,
            # retrieve the existing investigation, and return it instead.
            self.db.rollback()

            if alert_id is not None:
                existing = self.get_by_alert_id(
                    tenant_id=tenant_id,
                    alert_id=alert_id,
                )

                if existing is not None:
                    return existing

            # Re-raise unrelated integrity errors.
            raise

        self.db.refresh(item)

        return item

    def update(
        self,
        tenant_id: UUID,
        investigation_id: UUID,
        payload: InvestigationUpdate,
    ):
        item = self.get(
            tenant_id=tenant_id,
            investigation_id=investigation_id,
        )

        if item is None:
            return None

        update_data = payload.model_dump(
            exclude_unset=True,
        )

        # If alert_id is being changed, verify that the new alert belongs
        # to the same tenant.
        alert_id = update_data.get("alert_id")

        if alert_id is not None:
            alert = self.db.scalar(
                select(Alert).where(
                    Alert.id == alert_id,
                    Alert.tenant_id == tenant_id,
                )
            )

            if alert is None:
                raise ValueError(
                    f"Alert {alert_id} not found for this tenant."
                )

        for key, value in update_data.items():
            setattr(item, key, value)

        self.db.commit()
        self.db.refresh(item)

        return item

    def list(
        self,
        tenant_id: UUID,
        *,
        status: str | None = None,
        alert_id: UUID | None = None,
        limit: int = 50,
        offset: int = 0,
    ):
        criteria = [
            Investigation.tenant_id == tenant_id,
        ]

        if status is not None:
            criteria.append(
                Investigation.status == status,
            )

        if alert_id is not None:
            criteria.append(
                Investigation.alert_id == alert_id,
            )

        statement = (
            select(Investigation)
            .where(*criteria)
            .order_by(Investigation.updated_at.desc())
            .limit(limit)
            .offset(offset)
        )

        return list(
            self.db.scalars(statement).all()
        )

    def get_by_alert_id(
        self,
        tenant_id: UUID,
        alert_id: UUID,
    ):
        return self.db.scalar(
            select(Investigation).where(
                Investigation.tenant_id == tenant_id,
                Investigation.alert_id == alert_id,
            )
        )

    def evidence(
        self,
        tenant_id: UUID,
        investigation_id: UUID,
    ):
        return list(
            self.db.scalars(
                select(Evidence)
                .where(
                    Evidence.tenant_id == tenant_id,
                    Evidence.investigation_id == investigation_id,
                )
                .order_by(Evidence.created_at.asc())
            ).all()
        )

    def add_evidence(
        self,
        tenant_id: UUID,
        investigation_id: UUID,
        payload: EvidenceCreate,
    ):
        investigation = self.get(
            tenant_id=tenant_id,
            investigation_id=investigation_id,
        )

        if investigation is None:
            return None

        item = Evidence(
            tenant_id=tenant_id,
            investigation_id=investigation_id,
            **payload.model_dump(),
        )

        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)

        return item
