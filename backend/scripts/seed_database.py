from __future__ import annotations

from app.core.db import SessionLocal
from app.db.seeds.seed import SeedRunner


def main() -> None:
    db = SessionLocal()

    try:
        SeedRunner(db).run()
    finally:
        db.close()


if __name__ == "__main__":
    main()