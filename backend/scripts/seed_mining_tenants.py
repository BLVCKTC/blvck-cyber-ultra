from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.db import SessionLocal
from app.db.models.tenant import Tenant
from app.db.seeds.seed import SeedRunner


MINING_TENANTS = [
    {
        "name": "Great Dyke Mining Corporation",
        "slug": "great-dyke-mining",
    },
    {
        "name": "Hwange Minerals & Resources",
        "slug": "hwange-minerals",
    },
    {
        "name": "Midlands Chrome Mining",
        "slug": "midlands-chrome",
    },
    {
        "name": "Matabeleland Gold Resources",
        "slug": "matabeleland-gold",
    },
]


def seed_mining_tenants(db: Session) -> None:
    print("----------------------------------------")
    print("Seeding mining tenants...")
    print("----------------------------------------")

    created = 0
    existing = 0

    for data in MINING_TENANTS:
        tenant = (
            db.query(Tenant)
            .filter(Tenant.slug == data["slug"])
            .first()
        )

        if tenant:
            print(
                f"EXISTS: {tenant.name} "
                f"({tenant.id})"
            )
            existing += 1
            continue

        tenant = Tenant(
            name=data["name"],
            slug=data["slug"],
        )

        db.add(tenant)
        db.flush()

        print(
            f"CREATED: {tenant.name} "
            f"({tenant.id})"
        )

        created += 1

    db.commit()

    print("----------------------------------------")
    print(f"Created: {created}")
    print(f"Existing: {existing}")
    print("----------------------------------------")


def main() -> None:
    db = SessionLocal()

    try:
        seed_mining_tenants(db)

        print()
        print("Running tenant role/permission seed...")
        print()

        SeedRunner(db).seed_tenant_roles()
        SeedRunner(db).seed_tenant_role_permissions()

        print()
        print("----------------------------------------")
        print("Mining tenant seed complete.")
        print("----------------------------------------")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()