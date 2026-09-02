from __future__ import annotations

from typing import Literal
from pydantic import field_validator, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Keycloak
    KEYCLOAK_URL: str
    KEYCLOAK_REALM: str
    KEYCLOAK_CLIENT_ID: str
    KEYCLOAK_CLIENT_SECRET: str
    KEYCLOAK_ISSUER: str | None = None
    KEYCLOAK_ALLOWED_AUDIENCE: str | None = None

    # Application
    BASE_URL: str = "http://localhost:8000"
    FRONTEND_URL: str = "http://localhost:3000"
    KEYCLOAK_REDIRECT_URI: str | None = None
    API_PREFIX: str = "/api"

    # Database
    DATABASE_URL: str
    ALEMBIC_DATABASE_URL: str

    # Cookies
    SESSION_COOKIE_NAME: str = "session_kc_access"
    ACTIVE_TENANT_COOKIE_NAME: str = "tenant_id"
    COOKIE_SECURE: bool = False
    COOKIE_SAMESITE: Literal["lax", "strict", "none"] = "lax"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator(
        "KEYCLOAK_URL",
        "BASE_URL",
        "FRONTEND_URL",
        "KEYCLOAK_ISSUER",
        mode="after",
    )
    @classmethod
    def rstrip_slashes(cls, v: str | None) -> str | None:
        return v.rstrip("/") if v else v

    @field_validator("API_PREFIX", mode="after")
    @classmethod
    def validate_api_prefix(cls, v: str) -> str:
        # Ensure prefix starts with / and ends without /
        v = v.rstrip("/")
        if not v.startswith("/"):
            v = f"/{v}"
        return v

    @computed_field
    @property
    def computed_issuer(self) -> str:
        return (
            self.KEYCLOAK_ISSUER
            or f"{self.KEYCLOAK_URL}/realms/{self.KEYCLOAK_REALM}"
        )

    @computed_field
    @property
    def computed_audience(self) -> str:
        return (
            self.KEYCLOAK_ALLOWED_AUDIENCE
            or self.KEYCLOAK_CLIENT_ID
        )

    @computed_field
    @property
    def computed_auth_redirect_uri(self) -> str:
        return (
            self.KEYCLOAK_REDIRECT_URI
            or f"{self.BASE_URL}{self.API_PREFIX}/auth/callback"
        )


settings = Settings()

# Keycloak
KEYCLOAK_URL = settings.KEYCLOAK_URL
KEYCLOAK_REALM = settings.KEYCLOAK_REALM
KEYCLOAK_CLIENT_ID = settings.KEYCLOAK_CLIENT_ID
KEYCLOAK_CLIENT_SECRET = settings.KEYCLOAK_CLIENT_SECRET
KEYCLOAK_ISSUER = settings.computed_issuer
KEYCLOAK_ALLOWED_AUDIENCE = settings.computed_audience

# Application
BASE_URL = settings.BASE_URL
FRONTEND_URL = settings.FRONTEND_URL
API_PREFIX = settings.API_PREFIX
AUTH_REDIRECT_URI = settings.computed_auth_redirect_uri

# Database
DATABASE_URL = settings.DATABASE_URL
ALEMBIC_DATABASE_URL = settings.ALEMBIC_DATABASE_URL

# Cookies
SESSION_COOKIE_NAME = settings.SESSION_COOKIE_NAME
ACTIVE_TENANT_COOKIE_NAME = settings.ACTIVE_TENANT_COOKIE_NAME
COOKIE_SECURE = settings.COOKIE_SECURE
COOKIE_SAMESITE = settings.COOKIE_SAMESITE
