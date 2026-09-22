"""
CLI entry point for syncing MITRE ATT&CK reference data.

Run manually or on a schedule (cron / CI job) rather than over HTTP,
since the /v1/mitre/sync/{domain} route is deliberately left ungated
pending the platform-admin primitive (see routes/mitre.py docstring).

Usage:
    python -m scripts.sync_mitre_attack --domain enterprise-attack
    python -m scripts.sync_mitre_attack --domain ics-attack
    python -m scripts.sync_mitre_attack --all
"""

import argparse
import logging
import sys

from app.core.db import SessionLocal  # adjust import to match your actual session factory
from app.db.models.mitre import MitreDomain, MitreSyncStatus
from app.services.mitre_sync_service import MitreSyncService

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def run(domains: list[MitreDomain]) -> int:
    exit_code = 0
    for domain in domains:
        db = SessionLocal()
        try:
            logger.info("Starting MITRE sync for domain=%s", domain.value)
            result = MitreSyncService(db).sync_domain(domain)
            logger.info(
                "Sync finished domain=%s status=%s version=%s created=%d updated=%d deprecated=%d",
                domain.value,
                result.status.value,
                result.mitre_version,
                result.objects_created,
                result.objects_updated,
                result.objects_deprecated,
            )
            if result.status != MitreSyncStatus.SUCCESS:
                exit_code = 1
        except Exception:
            logger.exception("Sync raised for domain=%s", domain.value)
            exit_code = 1
        finally:
            db.close()
    return exit_code


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sync MITRE ATT&CK reference data")
    parser.add_argument("--domain", choices=["enterprise-attack", "ics-attack"], help="Sync one domain")
    parser.add_argument("--all", action="store_true", help="Sync both Enterprise and ICS")
    args = parser.parse_args()

    if args.all:
        target_domains = [MitreDomain.ENTERPRISE, MitreDomain.ICS]
    elif args.domain:
        target_domains = [MitreDomain(args.domain)]
    else:
        parser.error("Pass --domain <enterprise-attack|ics-attack> or --all")
        sys.exit(2)

    sys.exit(run(target_domains))
