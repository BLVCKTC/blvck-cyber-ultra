from sqlalchemy.engine import make_url
import psycopg

from app.core.config import settings

database_url = make_url(settings.DATABASE_URL)

conn = psycopg.connect(
    host=database_url.host,
    port=database_url.port or 5432,
    dbname=database_url.database,
    user=database_url.username,
    password=database_url.password,
)

cur = conn.cursor()

print("=== detection_rule_technique foreign keys (pg_constraint) ===")

cur.execute("""
    SELECT
        conname,
        confrelid::regclass AS references_table,
        pg_get_constraintdef(oid) AS definition
    FROM pg_constraint
    WHERE conrelid = 'detection_rule_technique'::regclass
      AND contype = 'f'
    ORDER BY conname
""")

for row in cur.fetchall():
    print(row)

conn.close()