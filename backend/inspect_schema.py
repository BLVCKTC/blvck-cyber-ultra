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

print("=== mitre* tables ===")

cur.execute("""
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name LIKE 'mitre%'
ORDER BY table_name
""")

for row in cur.fetchall():
    print(row[0])

print()

print("=== detection_rule_technique exists? ===")

cur.execute("""
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name = 'detection_rule_technique'
""")

print(bool(cur.fetchall()))

print()

print("=== mitre_technique columns ===")

cur.execute("""
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = 'mitre_technique'
ORDER BY ordinal_position
""")

for row in cur.fetchall():
    print(row)

print()

print("=== detection_rule_technique columns (if exists) ===")

cur.execute("""
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = 'detection_rule_technique'
ORDER BY ordinal_position
""")

for row in cur.fetchall():
    print(row)

print("=== detection_rule_technique foreign keys ===")

cur.execute("""
SELECT
    tc.constraint_name,
    kcu.column_name,
    ccu.table_name AS referenced_table,
    ccu.column_name AS referenced_column
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage AS ccu
    ON tc.constraint_name = ccu.constraint_name
    AND tc.table_schema = ccu.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY'
  AND tc.table_schema = 'public'
  AND tc.table_name = 'detection_rule_technique'
ORDER BY kcu.column_name
""")

for row in cur.fetchall():
    print(row)

print()

print("=== detection rule tables ===")

cur.execute("""
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name LIKE 'detection_rule%'
ORDER BY table_name
""")

for row in cur.fetchall():
    print(row[0])

print()

print("=== user tables ===")

cur.execute("""
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name LIKE '%user%'
ORDER BY table_name
""")

for row in cur.fetchall():
    print(row[0])

print()

print("=== orphaned detection_rule_id rows ===")

cur.execute("""
SELECT COUNT(*)
FROM detection_rule_technique drt
LEFT JOIN detection_rules dr ON dr.id = drt.detection_rule_id
WHERE dr.id IS NULL
""")

print(cur.fetchone()[0])

print()

print("=== orphaned mitre_technique_id rows ===")

cur.execute("""
SELECT COUNT(*)
FROM detection_rule_technique drt
LEFT JOIN mitre_technique mt ON mt.id = drt.mitre_technique_id
WHERE mt.id IS NULL
""")

print(cur.fetchone()[0])

print()

print("=== orphaned created_by rows ===")

cur.execute("""
SELECT COUNT(*)
FROM detection_rule_technique drt
LEFT JOIN users u ON u.id = drt.created_by
WHERE drt.created_by IS NOT NULL
  AND u.id IS NULL
""")

print(cur.fetchone()[0])

conn.close()