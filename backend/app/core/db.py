from __future__ import annotations

from contextvars import ContextVar

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import DATABASE_URL


current_tenant_id: ContextVar[str | None] = ContextVar(
    "current_tenant_id",
    default=None,
)

current_user_id: ContextVar[str | None] = ContextVar(
    "current_user_id",
    default=None,
)


engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


@event.listens_for(Session, "after_begin")
def _apply_rls_session_context(session, transaction, connection):
    """Re-applies RLS context on every new transaction this Session opens,
    including transactions started after a mid-request commit(). Reads
    from session.info rather than a ContextVar, because FastAPI dispatches
    each sync dependency and the endpoint itself as separate threadpool
    calls, each taking its own copy of the current context — a ContextVar
    mutated inside one dependency does not propagate to a later one.
    session.info is a plain dict on this exact Session instance, so it
    survives correctly regardless of which thread touches it."""
    connection.execute(
        text("SELECT set_config('app.user_id', :uid, true)"),
        {"uid": session.info.get("user_id", "")},
    )
    connection.execute(
        text("SELECT set_config('app.tenant_id', :tid, true)"),
        {"tid": session.info.get("tenant_id", "")},
    )