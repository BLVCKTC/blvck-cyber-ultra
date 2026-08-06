from __future__ import annotations

import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.core.config import DATABASE_URL
from app.db.base import Base

# Import models so Base.metadata contains all tables for autogenerate
from app.db.models.user import User  # noqa: F401
from app.db.models.tenant import Tenant  # noqa: F401
from app.db.models.membership import Membership  # noqa: F401
from app.db.models.pkce_attempt import PKCEAttempt  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = DATABASE_URL

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section) or {}

    # Ensure Alembic uses your app's DATABASE_URL
    configuration["sqlalchemy.url"] = DATABASE_URL

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            # if you ever run into batch/alter issues with Postgres,
            # you can toggle this via env var
            render_as_batch=os.getenv("ALEMBIC_BATCH_MODE") == "1",
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
