"""Seed runner that bypasses psycopg via pg8000.

Temporary workaround for the Application Control DLL block — not a
replacement for fixing the environment, since app/core/db.py still
builds its engine with psycopg and the API won't start without it.
"""
import re

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import DATABASE_URL
from app.db.seeds.seed import SeedRunner

url = re.sub(r"^postgres(ql)?(\+\w+)?://", "postgresql+pg8000://", DATABASE_URL)

engine = create_engine(url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

db = SessionLocal()
try:
    SeedRunner(db).run()
finally:
    db.close()