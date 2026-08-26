from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.health import router as health_router
from app.api.routes.auth import router as auth_router
from app.api.routes.tenants import router as tenants_router
from app.api.routes.dashboard import router as dashboard_router
from app.api.routes.memberships import router as memberships_router
from app.api.routes.security_events import router as security_events_router
from app.api.routes.detection_rules import router as detection_rules_router

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
    "http://127.0.0.1:3000",

    # Next.js network access
    "http://172.16.0.2:3000",
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
