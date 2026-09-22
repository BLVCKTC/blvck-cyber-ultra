from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models.detection_rule import DetectionRule, DetectionRuleStatus
from app.db.models.mitre import (
    DetectionRuleTechnique,
    MitreDomain,
    MitreSyncLog,
    MitreTactic,
    MitreTechnique,
)


class MitreRepo:
    def __init__(self, db: Session):
        self.db = db

    def list_tactics(
        self,
        domain: MitreDomain,
    ) -> list[MitreTactic]:
        stmt = (
            select(MitreTactic)
            .where(
                MitreTactic.domain == domain,
                MitreTactic.deprecated.is_(False),
            )
            .order_by(MitreTactic.mitre_id)
        )
        return list(self.db.scalars(stmt).all())

    def list_techniques(
        self,
        domain: MitreDomain,
        include_subtechniques: bool = True,
        include_deprecated: bool = False,
    ) -> list[MitreTechnique]:
        stmt = select(MitreTechnique).where(
            MitreTechnique.domain == domain
        )

        if not include_subtechniques:
            stmt = stmt.where(
                MitreTechnique.is_subtechnique.is_(False)
            )

        if not include_deprecated:
            stmt = stmt.where(
                MitreTechnique.deprecated.is_(False),
                MitreTechnique.revoked.is_(False),
            )

        stmt = stmt.order_by(MitreTechnique.mitre_id)

        return list(self.db.scalars(stmt).all())

    def get_technique_by_mitre_id(
        self,
        mitre_id: str,
        domain: MitreDomain,
    ) -> MitreTechnique | None:
        stmt = select(MitreTechnique).where(
            MitreTechnique.mitre_id == mitre_id,
            MitreTechnique.domain == domain,
        )
        return self.db.scalar(stmt)

    def get_technique_by_id(
        self,
        technique_id: uuid.UUID,
    ) -> MitreTechnique | None:
        return self.db.get(MitreTechnique, technique_id)

    def latest_sync(
        self,
        domain: MitreDomain,
    ) -> MitreSyncLog | None:
        stmt = (
            select(MitreSyncLog)
            .where(MitreSyncLog.domain == domain)
            .order_by(MitreSyncLog.started_at.desc())
            .limit(1)
        )
        return self.db.scalar(stmt)

    def sync_history(
        self,
        domain: MitreDomain,
        limit: int = 20,
    ) -> list[MitreSyncLog]:
        stmt = (
            select(MitreSyncLog)
            .where(MitreSyncLog.domain == domain)
            .order_by(MitreSyncLog.started_at.desc())
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    def get_rule(
        self,
        detection_rule_id: uuid.UUID,
    ) -> DetectionRule | None:
        return self.db.get(DetectionRule, detection_rule_id)

    def list_techniques_for_rule(
        self,
        detection_rule_id: uuid.UUID,
    ) -> list[MitreTechnique]:
        stmt = (
            select(MitreTechnique)
            .join(
                DetectionRuleTechnique,
                DetectionRuleTechnique.mitre_technique_id
                == MitreTechnique.id,
            )
            .where(
                DetectionRuleTechnique.detection_rule_id
                == detection_rule_id
            )
            .order_by(MitreTechnique.mitre_id)
        )

        return list(self.db.scalars(stmt).all())

    def list_rule_technique_links(
        self,
        detection_rule_id: uuid.UUID,
    ) -> list[DetectionRuleTechnique]:
        stmt = (
            select(DetectionRuleTechnique)
            .where(
                DetectionRuleTechnique.detection_rule_id
                == detection_rule_id
            )
            .order_by(DetectionRuleTechnique.created_at)
        )

        return list(self.db.scalars(stmt).all())

    def link_rule_to_technique(
        self,
        detection_rule_id: uuid.UUID,
        mitre_technique_id: uuid.UUID,
        created_by: uuid.UUID | None,
    ) -> DetectionRuleTechnique:
        technique = self.get_technique_by_id(
            mitre_technique_id
        )

        if technique is None:
            raise ValueError("MITRE technique not found.")

        existing = self.db.scalar(
            select(DetectionRuleTechnique).where(
                DetectionRuleTechnique.detection_rule_id
                == detection_rule_id,
                DetectionRuleTechnique.mitre_technique_id
                == mitre_technique_id,
            )
        )

        if existing:
            return existing

        link = DetectionRuleTechnique(
            detection_rule_id=detection_rule_id,
            mitre_technique_id=mitre_technique_id,
            created_by=created_by,
        )

        self.db.add(link)
        self.db.commit()
        self.db.refresh(link)

        return link

    def unlink_rule_from_technique(
        self,
        detection_rule_id: uuid.UUID,
        mitre_technique_id: uuid.UUID,
    ) -> bool:
        existing = self.db.scalar(
            select(DetectionRuleTechnique).where(
                DetectionRuleTechnique.detection_rule_id
                == detection_rule_id,
                DetectionRuleTechnique.mitre_technique_id
                == mitre_technique_id,
            )
        )

        if not existing:
            return False

        self.db.delete(existing)
        self.db.commit()

        return True

    def copy_rule_techniques(
        self,
        source_rule_id: uuid.UUID,
        target_rule_id: uuid.UUID,
        created_by: uuid.UUID | None,
    ) -> list[DetectionRuleTechnique]:
        source = self.get_rule(source_rule_id)

        if source is None:
            raise ValueError("Source detection rule not found.")

        target = self.get_rule(target_rule_id)

        if target is None:
            raise ValueError("Target detection rule not found.")

        source_links = self.list_rule_technique_links(
            source_rule_id
        )

        created: list[DetectionRuleTechnique] = []

        for source_link in source_links:
            existing = self.db.scalar(
                select(DetectionRuleTechnique).where(
                    DetectionRuleTechnique.detection_rule_id
                    == target_rule_id,
                    DetectionRuleTechnique.mitre_technique_id
                    == source_link.mitre_technique_id,
                )
            )

            if existing:
                continue

            link = DetectionRuleTechnique(
                detection_rule_id=target_rule_id,
                mitre_technique_id=source_link.mitre_technique_id,
                created_by=created_by,
            )

            self.db.add(link)
            created.append(link)

        self.db.commit()

        for link in created:
            self.db.refresh(link)

        return created

    def technique_coverage(
        self,
        *,
        tenant_id: uuid.UUID,
        domain: MitreDomain,
        include_subtechniques: bool = True,
    ) -> list[dict]:
        techniques = self.list_techniques(
            domain,
            include_subtechniques=include_subtechniques,
            include_deprecated=False,
        )

        technique_ids = [technique.id for technique in techniques]

        if not technique_ids:
            return []

        coverage_counts = dict(
            self.db.execute(
                select(
                    DetectionRuleTechnique.mitre_technique_id,
                    func.count(
                        func.distinct(
                            DetectionRuleTechnique.detection_rule_id
                        )
                    ),
                )
                .join(
                    DetectionRule,
                    DetectionRule.id
                    == DetectionRuleTechnique.detection_rule_id,
                )
                .where(
                    DetectionRule.tenant_id == tenant_id,
                    DetectionRule.status
                    == DetectionRuleStatus.PRODUCTION.value,
                    DetectionRule.enabled.is_(True),
                    DetectionRuleTechnique.mitre_technique_id.in_(
                        technique_ids
                    ),
                )
                .group_by(
                    DetectionRuleTechnique.mitre_technique_id
                )
            ).all()
        )

        return [
            {
                "technique": technique,
                "covering_rule_count": coverage_counts.get(
                    technique.id,
                    0,
                ),
                "covered": coverage_counts.get(
                    technique.id,
                    0,
                )
                > 0,
            }
            for technique in techniques
        ]