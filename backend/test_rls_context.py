from app.core.db import SessionLocal
from sqlalchemy import text
from uuid import UUID

TENANT_ID = UUID("3ea2dc7e-c96f-45d5-8379-ab37092600de")

db = SessionLocal()

try:
    print("1:", db.scalar(text("SELECT current_setting('app.tenant_id', true)")))

    db.execute(
        text("SELECT set_config('app.tenant_id', :tid, false)"),
        {"tid": str(TENANT_ID)},
    )

    print("2:", db.scalar(text("SELECT current_setting('app.tenant_id', true)")))

    db.commit()

    print("3:", db.scalar(text("SELECT current_setting('app.tenant_id', true)")))

finally:
    db.close()

db = SessionLocal()

try:
    print("4:", db.scalar(text("SELECT current_setting('app.tenant_id', true)")))
finally:
    db.close()
