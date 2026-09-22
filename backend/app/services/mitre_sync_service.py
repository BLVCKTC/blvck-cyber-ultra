from __future__ import annotations

import logging
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
from mitreattack.stix20 import MitreAttackData
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.mitre import (
    MitreCampaign,
    MitreCampaignGroup,
    MitreCampaignTechnique,
    MitreDomain,
    MitreGroup,
    MitreGroupTechnique,
    MitreMitigation,
    MitreSoftware,
    MitreSoftwareTechnique,
    MitreSyncLog,
    MitreSyncStatus,
    MitreTactic,
    MitreTechnique,
    MitreTechniqueMitigation,
    MitreTechniqueTactic,
)

logger = logging.getLogger(__name__)

BUNDLE_URLS: dict[MitreDomain, str] = {
    MitreDomain.ENTERPRISE: (
        "https://raw.githubusercontent.com/mitre-attack/attack-stix-data/"
        "master/enterprise-attack/enterprise-attack.json"
    ),
    MitreDomain.ICS: (
        "https://raw.githubusercontent.com/mitre-attack/attack-stix-data/"
        "master/ics-attack/ics-attack.json"
    ),
}


class MitreSyncService:
    def __init__(self, db: Session):
        self.db = db

    def sync_domain(self, domain: MitreDomain) -> MitreSyncLog:
        source_url = BUNDLE_URLS[domain]
        sync_log = MitreSyncLog(
            domain=domain,
            source_url=source_url,
            status=MitreSyncStatus.RUNNING,
        )
        self.db.add(sync_log)
        self.db.commit()
        self.db.refresh(sync_log)

        created = 0
        updated = 0
        deprecated = 0

        try:
            bundle_path = self._download_bundle(source_url)
            attack_data = MitreAttackData(str(bundle_path))
            version = self._extract_version(attack_data)

            c, u = self._sync_tactics(attack_data, domain)
            created += c
            updated += u

            c, u, d = self._sync_techniques(attack_data, domain)
            created += c
            updated += u
            deprecated += d

            c, u = self._sync_mitigations(attack_data, domain)
            created += c
            updated += u

            c, u = self._sync_groups(attack_data, domain)
            created += c
            updated += u

            c, u = self._sync_software(attack_data, domain)
            created += c
            updated += u

            c, u = self._sync_campaigns(attack_data, domain)
            created += c
            updated += u

            self._sync_technique_tactic_links(attack_data, domain)
            self._sync_technique_mitigation_links(attack_data)
            self._sync_group_technique_links(attack_data)
            self._sync_software_technique_links(attack_data)
            self._sync_campaign_technique_links(attack_data)
            self._sync_campaign_group_links(attack_data)

            sync_log.status = MitreSyncStatus.SUCCESS
            sync_log.mitre_version = version
            sync_log.objects_created = created
            sync_log.objects_updated = updated
            sync_log.objects_deprecated = deprecated
            sync_log.completed_at = datetime.now(timezone.utc)
            self.db.commit()

        except Exception as exc:
            logger.exception("MITRE sync failed for domain=%s", domain)
            self.db.rollback()
            sync_log.status = MitreSyncStatus.FAILED
            sync_log.error_message = str(exc)[:2000]
            sync_log.completed_at = datetime.now(timezone.utc)
            self.db.add(sync_log)
            self.db.commit()
            raise

        finally:
            try:
                bundle_path.unlink(missing_ok=True)
            except (NameError, OSError):
                pass

        return sync_log

    @staticmethod
    def _download_bundle(url: str) -> Path:
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        tmp.write(response.content)
        tmp.close()
        return Path(tmp.name)

    @staticmethod
    def _extract_version(attack_data: MitreAttackData) -> str | None:
        collections = attack_data.get_objects_by_type("x-mitre-collection")
        if collections:
            return collections[0].get("x_mitre_version")
        return None

    def _sync_tactics(
        self, attack_data: MitreAttackData, domain: MitreDomain
    ) -> tuple[int, int]:
        created = updated = 0

        for obj in attack_data.get_tactics(remove_revoked_deprecated=False):
            stix_id = obj.get("id")

            if not stix_id:
                logger.warning(
                    "Skipping MITRE tactic with missing STIX ID domain=%s",
                    domain.value,
                )
                continue

            mitre_id = self._external_id(obj, "mitre-attack")

            existing = self.db.scalar(
                select(MitreTactic).where(MitreTactic.stix_id == stix_id)
            )

            values = dict(
                mitre_id=mitre_id,
                shortname=obj.get("x_mitre_shortname", ""),
                name=obj.get("name", ""),
                description=obj.get("description"),
                domain=domain,
                url=self._external_ref_url(obj),
                revoked=obj.get("revoked", False),
                deprecated=obj.get("x_mitre_deprecated", False),
            )

            if existing:
                for k, v in values.items():
                    setattr(existing, k, v)
                updated += 1
            else:
                self.db.add(MitreTactic(stix_id=stix_id, **values))
                created += 1

        self.db.commit()
        return created, updated

    def _sync_techniques(
        self, attack_data: MitreAttackData, domain: MitreDomain
    ) -> tuple[int, int, int]:
        created = updated = deprecated = 0
        techniques = attack_data.get_techniques(remove_revoked_deprecated=False)
        technique_stix_ids: set[str] = set()

        for obj in techniques:
            stix_id = obj.get("id")

            if not stix_id:
                logger.warning(
                    "Skipping MITRE technique with missing STIX ID domain=%s name=%s",
                    domain.value,
                    obj.get("name"),
                )
                continue

            technique_stix_ids.add(stix_id)
            mitre_id = self._external_id(obj, "mitre-attack")

            if not mitre_id:
                logger.info(
                    "Importing MITRE technique without ATT&CK ID domain=%s stix_id=%s name=%s",
                    domain.value,
                    stix_id,
                    obj.get("name"),
                )

            existing = self.db.scalar(
                select(MitreTechnique).where(MitreTechnique.stix_id == stix_id)
            )

            is_sub = obj.get("x_mitre_is_subtechnique", False)
            is_deprecated = obj.get("x_mitre_deprecated", False)

            values = dict(
                mitre_id=mitre_id,
                name=obj.get("name", ""),
                description=obj.get("description"),
                domain=domain,
                is_subtechnique=is_sub,
                platforms=obj.get("x_mitre_platforms"),
                data_sources=obj.get("x_mitre_data_sources"),
                detection_guidance=obj.get("x_mitre_detection"),
                url=self._external_ref_url(obj),
                revoked=obj.get("revoked", False),
                deprecated=is_deprecated,
            )

            if existing:
                for k, v in values.items():
                    setattr(existing, k, v)
                updated += 1
                if is_deprecated:
                    deprecated += 1
            else:
                self.db.add(
                    MitreTechnique(
                        stix_id=stix_id,
                        **values,
                    )
                )
                created += 1

        self.db.commit()

        subtechnique_map = attack_data.get_related(
            "attack-pattern",
            "subtechnique-of",
            "attack-pattern",
        )

        for child_stix_id, related in subtechnique_map.items():
            if child_stix_id not in technique_stix_ids or not related:
                continue

            parent_stix_id = related[0]["object"]["id"]

            if parent_stix_id not in technique_stix_ids:
                continue

            child = self.db.scalar(
                select(MitreTechnique).where(
                    MitreTechnique.stix_id == child_stix_id
                )
            )
            parent = self.db.scalar(
                select(MitreTechnique).where(
                    MitreTechnique.stix_id == parent_stix_id
                )
            )

            if child and parent:
                child.parent_technique_id = parent.id

        self.db.commit()

        return created, updated, deprecated

    def _sync_mitigations(
        self, attack_data: MitreAttackData, domain: MitreDomain
    ) -> tuple[int, int]:
        created = updated = 0

        for obj in attack_data.get_mitigations(remove_revoked_deprecated=False):
            stix_id = obj.get("id")

            if not stix_id:
                logger.warning(
                    "Skipping MITRE mitigation with missing STIX ID domain=%s",
                    domain.value,
                )
                continue

            mitre_id = self._external_id(obj, "mitre-attack")

            existing = self.db.scalar(
                select(MitreMitigation).where(MitreMitigation.stix_id == stix_id)
            )

            values = dict(
                mitre_id=mitre_id,
                name=obj.get("name", ""),
                description=obj.get("description"),
                domain=domain,
                url=self._external_ref_url(obj),
                deprecated=obj.get("x_mitre_deprecated", False),
            )

            if existing:
                for k, v in values.items():
                    setattr(existing, k, v)
                updated += 1
            else:
                self.db.add(MitreMitigation(stix_id=stix_id, **values))
                created += 1

        self.db.commit()
        return created, updated

    def _sync_groups(
        self, attack_data: MitreAttackData, domain: MitreDomain
    ) -> tuple[int, int]:
        created = updated = 0

        for obj in attack_data.get_groups(remove_revoked_deprecated=False):
            stix_id = obj.get("id")

            if not stix_id:
                logger.warning(
                    "Skipping MITRE group with missing STIX ID domain=%s",
                    domain.value,
                )
                continue

            mitre_id = self._external_id(obj, "mitre-attack")

            existing = self.db.scalar(
                select(MitreGroup).where(MitreGroup.stix_id == stix_id)
            )

            values = dict(
                mitre_id=mitre_id,
                name=obj.get("name", ""),
                aliases=obj.get("aliases"),
                description=obj.get("description"),
                domain=domain,
                url=self._external_ref_url(obj),
                deprecated=obj.get("x_mitre_deprecated", False),
            )

            if existing:
                for k, v in values.items():
                    setattr(existing, k, v)
                updated += 1
            else:
                self.db.add(MitreGroup(stix_id=stix_id, **values))
                created += 1

        self.db.commit()
        return created, updated

    def _sync_software(
        self, attack_data: MitreAttackData, domain: MitreDomain
    ) -> tuple[int, int]:
        created = updated = 0

        for obj in attack_data.get_software(remove_revoked_deprecated=False):
            stix_id = obj.get("id")

            if not stix_id:
                logger.warning(
                    "Skipping MITRE software with missing STIX ID domain=%s",
                    domain.value,
                )
                continue

            mitre_id = self._external_id(obj, "mitre-attack")

            if not mitre_id:
                logger.info(
                    "Importing MITRE software without ATT&CK ID domain=%s stix_id=%s name=%s",
                    domain.value,
                    stix_id,
                    obj.get("name"),
                )

            existing = self.db.scalar(
                select(MitreSoftware).where(MitreSoftware.stix_id == stix_id)
            )

            values = dict(
                mitre_id=mitre_id,
                name=obj.get("name", ""),
                aliases=obj.get("x_mitre_aliases"),
                software_type="malware" if obj["type"] == "malware" else "tool",
                description=obj.get("description"),
                domain=domain,
                url=self._external_ref_url(obj),
                deprecated=obj.get("x_mitre_deprecated", False),
            )

            if existing:
                for k, v in values.items():
                    setattr(existing, k, v)
                updated += 1
            else:
                self.db.add(MitreSoftware(stix_id=stix_id, **values))
                created += 1

        self.db.commit()
        return created, updated

    def _sync_campaigns(
        self, attack_data: MitreAttackData, domain: MitreDomain
    ) -> tuple[int, int]:
        created = updated = 0

        for obj in attack_data.get_campaigns(remove_revoked_deprecated=False):
            stix_id = obj.get("id")

            if not stix_id:
                logger.warning(
                    "Skipping MITRE campaign with missing STIX ID domain=%s",
                    domain.value,
                )
                continue

            mitre_id = self._external_id(obj, "mitre-attack")

            existing = self.db.scalar(
                select(MitreCampaign).where(MitreCampaign.stix_id == stix_id)
            )

            values = dict(
                mitre_id=mitre_id,
                name=obj.get("name", ""),
                description=obj.get("description"),
                first_seen=obj.get("first_seen"),
                last_seen=obj.get("last_seen"),
                domain=domain,
                url=self._external_ref_url(obj),
                deprecated=obj.get("x_mitre_deprecated", False),
            )

            if existing:
                for k, v in values.items():
                    setattr(existing, k, v)
                updated += 1
            else:
                self.db.add(MitreCampaign(stix_id=stix_id, **values))
                created += 1

        self.db.commit()
        return created, updated

    def _sync_technique_tactic_links(
        self, attack_data: MitreAttackData, domain: MitreDomain
    ) -> None:
        for obj in attack_data.get_techniques(
            remove_revoked_deprecated=False
        ):
            technique = self.db.scalar(
                select(MitreTechnique).where(
                    MitreTechnique.stix_id == obj["id"]
                )
            )

            if not technique:
                continue

            for phase in obj.get("kill_chain_phases", []):
                if phase.get("kill_chain_name") not in (
                    "mitre-attack",
                    "mitre-ics-attack",
                ):
                    continue

                tactic = self.db.scalar(
                    select(MitreTactic).where(
                        MitreTactic.shortname == phase["phase_name"],
                        MitreTactic.domain == domain,
                    )
                )

                if not tactic:
                    continue

                exists = self.db.scalar(
                    select(MitreTechniqueTactic).where(
                        MitreTechniqueTactic.mitre_technique_id == technique.id,
                        MitreTechniqueTactic.mitre_tactic_id == tactic.id,
                    )
                )

                if not exists:
                    self.db.add(
                        MitreTechniqueTactic(
                            mitre_technique_id=technique.id,
                            mitre_tactic_id=tactic.id,
                        )
                    )

        self.db.commit()

    def _sync_technique_mitigation_links(
        self, attack_data: MitreAttackData
    ) -> None:
        related = attack_data.get_related(
            "course-of-action",
            "mitigates",
            "attack-pattern",
        )

        for mitigation_stix_id, entries in related.items():
            mitigation = self.db.scalar(
                select(MitreMitigation).where(
                    MitreMitigation.stix_id == mitigation_stix_id
                )
            )

            if not mitigation:
                continue

            for entry in entries:
                technique = self.db.scalar(
                    select(MitreTechnique).where(
                        MitreTechnique.stix_id == entry["object"]["id"]
                    )
                )

                if not technique:
                    continue

                exists = self.db.scalar(
                    select(MitreTechniqueMitigation).where(
                        MitreTechniqueMitigation.mitre_technique_id == technique.id,
                        MitreTechniqueMitigation.mitre_mitigation_id == mitigation.id,
                    )
                )

                if not exists:
                    rel_desc = (
                        entry["relationships"][0].get("description")
                        if entry["relationships"]
                        else None
                    )

                    self.db.add(
                        MitreTechniqueMitigation(
                            mitre_technique_id=technique.id,
                            mitre_mitigation_id=mitigation.id,
                            description=rel_desc,
                        )
                    )

        self.db.commit()

    def _sync_group_technique_links(
        self, attack_data: MitreAttackData
    ) -> None:
        related = attack_data.get_related(
            "intrusion-set",
            "uses",
            "attack-pattern",
        )

        for group_stix_id, entries in related.items():
            group = self.db.scalar(
                select(MitreGroup).where(
                    MitreGroup.stix_id == group_stix_id
                )
            )

            if not group:
                continue

            for entry in entries:
                technique = self.db.scalar(
                    select(MitreTechnique).where(
                        MitreTechnique.stix_id == entry["object"]["id"]
                    )
                )

                if not technique:
                    continue

                exists = self.db.scalar(
                    select(MitreGroupTechnique).where(
                        MitreGroupTechnique.mitre_group_id == group.id,
                        MitreGroupTechnique.mitre_technique_id == technique.id,
                    )
                )

                if not exists:
                    rel_desc = (
                        entry["relationships"][0].get("description")
                        if entry["relationships"]
                        else None
                    )

                    self.db.add(
                        MitreGroupTechnique(
                            mitre_group_id=group.id,
                            mitre_technique_id=technique.id,
                            description=rel_desc,
                        )
                    )

        self.db.commit()

    def _sync_software_technique_links(
        self, attack_data: MitreAttackData
    ) -> None:
        for source_type in ("malware", "tool"):
            related = attack_data.get_related(
                source_type,
                "uses",
                "attack-pattern",
            )

            for software_stix_id, entries in related.items():
                software = self.db.scalar(
                    select(MitreSoftware).where(
                        MitreSoftware.stix_id == software_stix_id
                    )
                )

                if not software:
                    continue

                for entry in entries:
                    technique = self.db.scalar(
                        select(MitreTechnique).where(
                            MitreTechnique.stix_id == entry["object"]["id"]
                        )
                    )

                    if not technique:
                        continue

                    exists = self.db.scalar(
                        select(MitreSoftwareTechnique).where(
                            MitreSoftwareTechnique.mitre_software_id == software.id,
                            MitreSoftwareTechnique.mitre_technique_id == technique.id,
                        )
                    )

                    if not exists:
                        rel_desc = (
                            entry["relationships"][0].get("description")
                            if entry["relationships"]
                            else None
                        )

                        self.db.add(
                            MitreSoftwareTechnique(
                                mitre_software_id=software.id,
                                mitre_technique_id=technique.id,
                                description=rel_desc,
                            )
                        )

        self.db.commit()

    def _sync_campaign_technique_links(
        self, attack_data: MitreAttackData
    ) -> None:
        related = attack_data.get_related(
            "campaign",
            "uses",
            "attack-pattern",
        )

        for campaign_stix_id, entries in related.items():
            campaign = self.db.scalar(
                select(MitreCampaign).where(
                    MitreCampaign.stix_id == campaign_stix_id
                )
            )

            if not campaign:
                continue

            for entry in entries:
                technique = self.db.scalar(
                    select(MitreTechnique).where(
                        MitreTechnique.stix_id == entry["object"]["id"]
                    )
                )

                if not technique:
                    continue

                exists = self.db.scalar(
                    select(MitreCampaignTechnique).where(
                        MitreCampaignTechnique.mitre_campaign_id == campaign.id,
                        MitreCampaignTechnique.mitre_technique_id == technique.id,
                    )
                )

                if not exists:
                    self.db.add(
                        MitreCampaignTechnique(
                            mitre_campaign_id=campaign.id,
                            mitre_technique_id=technique.id,
                        )
                    )

        self.db.commit()

    def _sync_campaign_group_links(
        self, attack_data: MitreAttackData
    ) -> None:
        related = attack_data.get_related(
            "campaign",
            "attributed-to",
            "intrusion-set",
        )

        for campaign_stix_id, entries in related.items():
            campaign = self.db.scalar(
                select(MitreCampaign).where(
                    MitreCampaign.stix_id == campaign_stix_id
                )
            )

            if not campaign:
                continue

            for entry in entries:
                group = self.db.scalar(
                    select(MitreGroup).where(
                        MitreGroup.stix_id == entry["object"]["id"]
                    )
                )

                if not group:
                    continue

                exists = self.db.scalar(
                    select(MitreCampaignGroup).where(
                        MitreCampaignGroup.mitre_campaign_id == campaign.id,
                        MitreCampaignGroup.mitre_group_id == group.id,
                    )
                )

                if not exists:
                    self.db.add(
                        MitreCampaignGroup(
                            mitre_campaign_id=campaign.id,
                            mitre_group_id=group.id,
                        )
                    )

        self.db.commit()

    @staticmethod
    def _external_id(
        obj: dict[str, Any], source_name: str
    ) -> str | None:
        for ref in obj.get("external_references", []):
            if ref.get("source_name") != source_name:
                continue

            external_id = ref.get("external_id")

            if isinstance(external_id, str):
                external_id = external_id.strip()

                if external_id:
                    return external_id

        return None

    @staticmethod
    def _external_ref_url(
        obj: dict[str, Any]
    ) -> str | None:
        for ref in obj.get("external_references", []):
            if (
                ref.get("source_name") == "mitre-attack"
                and ref.get("url")
            ):
                return ref["url"]

        return None