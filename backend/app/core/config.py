from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    KEYCLOAK_URL: str
    KEYCLOAK_REALM: str
    KEYCLOAK_CLIENT_ID: str
    KEYCLOAK_CLIENT_SECRET: str

    KEYCLOAK_ISSUER: str | None = None
    KEYCLOAK_ALLOWED_AUDIENCE: str | None = None

    BASE_URL: str = "http://localhost:8000"
    KEYCLOAK_REDIRECT_URI: str | None = None

    DATABASE_URL: str

    SESSION_COOKIE_NAME: str = "session_kc_access"
    ACTIVE_TENANT_COOKIE_NAME: str = "tenant_id"

    COOKIE_SECURE: bool = False
    COOKIE_SAMESITE: str = "lax"

    # Add this
    api_prefix: str = "/api"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()


KEYCLOAK_URL = settings.KEYCLOAK_URL
KEYCLOAK_REALM = settings.KEYCLOAK_REALM
KEYCLOAK_CLIENT_ID = settings.KEYCLOAK_CLIENT_ID
KEYCLOAK_CLIENT_SECRET = settings.KEYCLOAK_CLIENT_SECRET

KEYCLOAK_ISSUER = (
    settings.KEYCLOAK_ISSUER
    or f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}"
)

KEYCLOAK_ALLOWED_AUDIENCE = (
    settings.KEYCLOAK_ALLOWED_AUDIENCE
    or KEYCLOAK_CLIENT_ID
)

BASE_URL = settings.BASE_URL

AUTH_REDIRECT_URI = (
    settings.KEYCLOAK_REDIRECT_URI
    or f"{BASE_URL}{settings.api_prefix}/auth/callback"
)

DATABASE_URL = settings.DATABASE_URL

SESSION_COOKIE_NAME = settings.SESSION_COOKIE_NAME

ACTIVE_TENANT_COOKIE_NAME = settings.ACTIVE_TENANT_COOKIE_NAME

COOKIE_SECURE = settings.COOKIE_SECURE

COOKIE_SAMESITE = settings.COOKIE_SAMESITE