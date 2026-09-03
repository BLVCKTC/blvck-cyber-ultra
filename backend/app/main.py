from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.health import router as health_router
from app.api.routes.auth import router as auth_router
from app.api.routes.tenants import router as tenants_router
from app.api.routes.dashboard import router as dashboard_router
from app.api.routes.memberships import router as memberships_router
from app.api.routes.security_events import router as security_events_router
from app.api.routes.detection_rules import router as detection_rules_router
from app.api.routes.alerts_api import router as alerts_router
from app.api.routes.investigations import router as investigations_router
from app.api.routes.incidents import router as incidents_router
from app.api.routes.intelligence import router as intelligence_router
from app.api.routes.operations import router as operations_router
from app.api.routes.audit import router as audit_router
from app.api.routes.teams import router as teams_router

from app.core.config import settings


app = FastAPI(
    title="BLVCK CYBER API",
    version="1.0.0",
)


# ==========================================================
# CORS CONFIGURATION
# ==========================================================

origins = [
    # Next.js local development
    "http://localhost:3000",

]


app.add_middleware(
    CORSMiddleware,

    allow_origins=origins,

    # REQUIRED for cookie authentication
    allow_credentials=True,

    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "OPTIONS",
    ],

    allow_headers=[
        "*",
    ],
)


# ==========================================================
# API ROUTES
# ==========================================================


app.include_router(
    health_router,
    prefix=settings.API_PREFIX,
)


app.include_router(
    auth_router,
    prefix=settings.API_PREFIX,
)


app.include_router(
    tenants_router,
    prefix=settings.API_PREFIX,
)


app.include_router(
    dashboard_router,
    prefix=settings.API_PREFIX,
)


app.include_router(
    memberships_router,
    prefix=settings.API_PREFIX,
)


app.include_router(
    security_events_router,
    prefix=settings.API_PREFIX,
)

app.include_router(
    detection_rules_router,
    prefix=settings.API_PREFIX,
)

app.include_router(
    alerts_router,
    prefix=settings.API_PREFIX,
)

app.include_router(
    investigations_router,
    prefix=settings.API_PREFIX,
)

app.include_router(
    incidents_router,
    prefix=settings.API_PREFIX,
)

app.include_router(
    intelligence_router,
    prefix=settings.API_PREFIX,
)

app.include_router(
    operations_router,
    prefix=settings.API_PREFIX,
)

app.include_router(
    audit_router,
    prefix=settings.API_PREFIX,
)

app.include_router(
    teams_router,
    prefix=settings.API_PREFIX,
)

# Canonical tenant-scoped resource namespace. Routers continue to expose their
# legacy paths above, while this mount reuses the same handlers, services, and
# authorization dependencies under /api/v1/tenants/{tenant_id}.
for tenant_router in (
    alerts_router,
    security_events_router,
    detection_rules_router,
    investigations_router,
    incidents_router,
    intelligence_router,
    operations_router,
    audit_router,
):
    app.include_router(
        tenant_router,
        prefix=f"{settings.API_PREFIX}/v1/tenants/{{tenant_id}}",
    )

# Teams and memberships already include /tenants/{tenant_id} in their router
# paths, so their canonical namespace is mounted one level higher.
for tenant_collection_router in (teams_router, memberships_router):
    app.include_router(
        tenant_collection_router,
        prefix=f"{settings.API_PREFIX}/v1",
    )

# ==========================================================
# ROOT HEALTH CHECK
# ==========================================================


@app.get("/")
def root():

    return {
        "ok": True,
        "service": "BLVCK CYBER API",
        "version": "1.0.0",
    }
