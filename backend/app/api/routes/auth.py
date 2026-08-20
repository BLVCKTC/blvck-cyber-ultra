from __future__ import annotations

from urllib.parse import urlencode
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Request,
    Response,
)
from fastapi.responses import JSONResponse, RedirectResponse

from app.api.deps import get_current_user, get_db
from app.core.config import settings
from app.schemas.auth import MeResponse, MembershipOut, UserOut
from app.schemas.tenant import SetTenantIn
from app.services.auth_service import AuthService


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


REFRESH_COOKIE = "session_kc_refresh"
PKCE_COOKIE = "pkce_attempt"

ACCESS_COOKIE_MAX_AGE = 300
PKCE_COOKIE_MAX_AGE = 600
LONG_LIVED_COOKIE_AGE = 60 * 60 * 24 * 30


def _is_secure_request(request: Request) -> bool:
    forwarded_proto = request.headers.get("x-forwarded-proto")

    if forwarded_proto:
        return (
            forwarded_proto.split(",")[0]
            .strip()
            .lower()
            == "https"
        )

    return request.url.scheme.lower() == "https"


def _cookie_options(request: Request) -> dict:
    return {
        "httponly": True,
        "secure": (
            settings.COOKIE_SECURE
            or _is_secure_request(request)
        ),
        "samesite": settings.COOKIE_SAMESITE,
        "path": "/",
    }


def _set_cookie(
    response: Response,
    request: Request,
    key: str,
    value: str | None,
    max_age: int,
) -> None:
    if value is None:
        return

    response.set_cookie(
        key=key,
        value=value,
        max_age=max_age,
        **_cookie_options(request),
    )


def _delete_cookie(
    response: Response,
    key: str,
) -> None:
    response.delete_cookie(
        key=key,
        path="/",
    )


def _set_auth_cookies(
    *,
    response: Response,
    request: Request,
    access_token: str,
    refresh_token: str | None,
    default_tenant_id: UUID | str | None,
) -> None:
    _set_cookie(
        response=response,
        request=request,
        key=settings.SESSION_COOKIE_NAME,
        value=access_token,
        max_age=ACCESS_COOKIE_MAX_AGE,
    )

    _set_cookie(
        response=response,
        request=request,
        key=REFRESH_COOKIE,
        value=refresh_token,
        max_age=LONG_LIVED_COOKIE_AGE,
    )

    if default_tenant_id:
        _set_cookie(
            response=response,
            request=request,
            key=settings.ACTIVE_TENANT_COOKIE_NAME,
            value=str(default_tenant_id),
            max_age=LONG_LIVED_COOKIE_AGE,
        )


@router.get("/login")
def login(
    request: Request,
    tenant_id: UUID = Query(...),
    db=Depends(get_db),
):
    auth = AuthService(db)

    login_request = auth.start_login(
        tenant_id=tenant_id
    )

    response = RedirectResponse(
        url=login_request["authorization_url"],
        status_code=302,
    )

    _set_cookie(
        response=response,
        request=request,
        key=PKCE_COOKIE,
        value=login_request["attempt_id"],
        max_age=PKCE_COOKIE_MAX_AGE,
    )

    return response


@router.get("/callback")
async def callback(
    request: Request,
    code: str | None = None,
    state: str | None = None,
    db=Depends(get_db),
):
    if not code:
        raise HTTPException(
            status_code=400,
            detail="missing_code",
        )

    if not state:
        raise HTTPException(
            status_code=400,
            detail="missing_state",
        )

    auth = AuthService(db)

    result = await auth.exchange_code(
        code=code,
        attempt_id=state,
    )

    default_tenant_id = result.get(
        "default_tenant_id"
    )

    if not default_tenant_id:
        raise HTTPException(
            status_code=403,
            detail="user_has_no_tenant_membership",
        )

    response = RedirectResponse(
        url=(
            f"{settings.FRONTEND_URL}"
            f"/dashboard/{default_tenant_id}"
        ),
        status_code=302,
    )

    _set_auth_cookies(
        response=response,
        request=request,
        access_token=result["access_token"],
        refresh_token=result.get("refresh_token"),
        default_tenant_id=default_tenant_id,
    )

    _delete_cookie(
        response,
        PKCE_COOKIE,
    )

    return response


@router.post("/refresh")
async def refresh(
    request: Request,
    db=Depends(get_db),
):
    refresh_token = request.cookies.get(
        REFRESH_COOKIE
    )

    if not refresh_token:
        raise HTTPException(
            status_code=401,
            detail="missing_refresh_token",
        )

    auth = AuthService(db)

    session = await auth.refresh_session(
        refresh_token
    )

    tenant_id = session.get(
        "default_tenant_id"
    )

    response = JSONResponse(
        content={
            "ok": True,
            "default_tenant_id": (
                str(tenant_id)
                if tenant_id
                else None
            ),
        },
        status_code=200,
    )

    _set_auth_cookies(
        response=response,
        request=request,
        access_token=session["access_token"],
        refresh_token=session.get(
            "refresh_token"
        ),
        default_tenant_id=tenant_id,
    )

    return response


@router.get(
    "/me",
    response_model=MeResponse,
)
def me(
    user=Depends(get_current_user),
    db=Depends(get_db),
):
    auth = AuthService(db)

    payload = auth.build_me_response(user)

    tenant_id = payload[
        "default_tenant_id"
    ]

    permissions = auth.get_user_permissions(
        user_id=user.id,
        tenant_id=tenant_id,
    )

    return MeResponse(
        user=UserOut(
            **payload["user"]
        ),
        memberships=[
            MembershipOut(**membership)
            for membership in payload[
                "memberships"
            ]
        ],
        default_tenant_id=tenant_id,
        permissions=permissions,
    )


@router.post("/tenant")
def set_active_tenant(
    payload: SetTenantIn,
    request: Request,
    user=Depends(get_current_user),
    db=Depends(get_db),
):
    auth = AuthService(db)

    auth.set_default_tenant(
        user_id=user.id,
        tenant_id=payload.tenant_id,
    )

    response = JSONResponse(
        content={
            "ok": True,
            "tenant_id": str(
                payload.tenant_id
            ),
        },
        status_code=200,
    )

    _set_cookie(
        response=response,
        request=request,
        key=settings.ACTIVE_TENANT_COOKIE_NAME,
        value=str(payload.tenant_id),
        max_age=LONG_LIVED_COOKIE_AGE,
    )

    return response


@router.get("/logout")
async def logout(
    request: Request,
    db=Depends(get_db),
):
    refresh_token = request.cookies.get(
        REFRESH_COOKIE
    )

    auth = AuthService(db)

    if refresh_token:
        try:
            await auth.token_service.logout(
                refresh_token
            )
        except Exception:
            pass

    keycloak_logout_url = (
        f"{settings.computed_issuer}"
        "/protocol/openid-connect/logout"
    )

    params = urlencode(
        {
            "post_logout_redirect_uri": (
                f"{settings.FRONTEND_URL}/login"
            ),
            "client_id": settings.KEYCLOAK_CLIENT_ID,
        }
    )

    response = RedirectResponse(
        url=f"{keycloak_logout_url}?{params}",
        status_code=302,
    )

    cookies_to_clear = (
        settings.SESSION_COOKIE_NAME,
        REFRESH_COOKIE,
        settings.ACTIVE_TENANT_COOKIE_NAME,
        PKCE_COOKIE,
    )

    for cookie in cookies_to_clear:
        _delete_cookie(
            response,
            cookie,
        )

    return response