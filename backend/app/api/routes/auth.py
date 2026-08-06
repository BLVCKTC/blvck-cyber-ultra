from __future__ import annotations

from urllib.parse import urlencode

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Request,
    Response,
)

from fastapi.responses import RedirectResponse

from app.api.deps import (
    get_current_user,
    get_db,
)

from app.core.config import (
    ACTIVE_TENANT_COOKIE_NAME,
    COOKIE_SAMESITE,
    SESSION_COOKIE_NAME,
)

from app.schemas.auth import (
    MeResponse,
    MembershipOut,
    UserOut,
)

from app.schemas.tenant import SetTenantIn
from app.services.auth_service import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

COOKIE_DOMAIN = "localhost"

REFRESH_COOKIE = "session_kc_refresh"


def _cookie_secure_for_request(request: Request) -> bool:
    forwarded_proto = request.headers.get("x-forwarded-proto")

    if forwarded_proto:
        return (
            forwarded_proto.split(",")[0]
            .strip()
            .lower()
            == "https"
        )

    return False


def _set_auth_cookies(
    *,
    response: Response,
    request: Request,
    access_token: str,
    refresh_token: str,
    default_tenant_id: str | None,
):
    secure = _cookie_secure_for_request(request)

    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=access_token,
        httponly=True,
        secure=secure,
        samesite=COOKIE_SAMESITE,
        domain=COOKIE_DOMAIN,
        path="/",
        max_age=300,
    )

    response.set_cookie(
        key=REFRESH_COOKIE,
        value=refresh_token,
        httponly=True,
        secure=secure,
        samesite=COOKIE_SAMESITE,
        domain=COOKIE_DOMAIN,
        path="/",
        max_age=60 * 60 * 24 * 30,
    )

    if default_tenant_id:
        response.set_cookie(
            key=ACTIVE_TENANT_COOKIE_NAME,
            value=default_tenant_id,
            httponly=True,
            secure=secure,
            samesite=COOKIE_SAMESITE,
            domain=COOKIE_DOMAIN,
            path="/",
            max_age=60 * 60 * 24 * 30,
        )


@router.get("/login")
def login(
    request: Request,
    tenant_id: str = Query(...),
    db=Depends(get_db),
):
    auth = AuthService(db)

    login_request = auth.start_login(tenant_id)

    response = RedirectResponse(
        url=login_request["authorization_url"],
        status_code=302,
    )

    response.set_cookie(
        key="pkce_attempt",
        value=login_request["attempt_id"],
        httponly=True,
        secure=_cookie_secure_for_request(request),
        samesite=COOKIE_SAMESITE,
        domain=COOKIE_DOMAIN,
        path="/",
        max_age=600,
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
        raise HTTPException(status_code=400, detail="missing_code")

    if not state:
        raise HTTPException(status_code=400, detail="missing_state")

    auth = AuthService(db)

    result = await auth.exchange_code(
        code=code,
        attempt_id=state,
    )

    tenant = result.get("default_tenant_id") or "BLVCK-CYBER"

    response = RedirectResponse(
        url=f"http://localhost:3000/dashboard/{tenant}",
        status_code=302,
    )

    _set_auth_cookies(
        response=response,
        request=request,
        access_token=result["access_token"],
        refresh_token=result["refresh_token"],
        default_tenant_id=result["default_tenant_id"],
    )

    response.delete_cookie(
        "pkce_attempt",
        domain=COOKIE_DOMAIN,
        path="/",
    )

    return response


@router.post("/refresh")
async def refresh(
    request: Request,
    db=Depends(get_db),
):
    refresh_token = request.cookies.get(REFRESH_COOKIE)

    if not refresh_token:
        raise HTTPException(
            status_code=401,
            detail="missing_refresh_token",
        )

    auth = AuthService(db)

    session = await auth.refresh_session(refresh_token)

    response = Response(status_code=200)

    _set_auth_cookies(
        response=response,
        request=request,
        access_token=session["access_token"],
        refresh_token=session["refresh_token"],
        default_tenant_id=session["default_tenant_id"],
    )

    return {"ok": True}


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

    permissions = auth.get_user_permissions(
        user_id=user.id,
        tenant_id=payload["default_tenant_id"],
    )

    return MeResponse(
        user=UserOut(**payload["user"]),
        memberships=[
            MembershipOut(**m)
            for m in payload["memberships"]
        ],
        default_tenant_id=payload["default_tenant_id"],
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
        user.id,
        payload.tenant_id,
    )

    response = Response(status_code=200)

    response.set_cookie(
        key=ACTIVE_TENANT_COOKIE_NAME,
        value=payload.tenant_id,
        httponly=True,
        secure=_cookie_secure_for_request(request),
        samesite=COOKIE_SAMESITE,
        domain=COOKIE_DOMAIN,
        path="/",
        max_age=60 * 60 * 24 * 30,
    )

    return response


@router.get("/logout")
async def logout(
    request: Request,
    db=Depends(get_db),
):
    refresh_token = request.cookies.get(REFRESH_COOKIE)

    auth = AuthService(db)

    if refresh_token:
        try:
            await auth.token_service.logout(refresh_token)
        except Exception:
            pass

    keycloak_logout_url = (
        "http://localhost:8080/realms/blvck-cyber/protocol/openid-connect/logout"
    )

    params = urlencode(
        {
            "post_logout_redirect_uri": "http://localhost:3000/login",
            "client_id": "blvck-cyber-api",
        }
    )

    response = RedirectResponse(
        url=f"{keycloak_logout_url}?{params}",
        status_code=302,
    )

    for cookie in (
        SESSION_COOKIE_NAME,
        REFRESH_COOKIE,
        ACTIVE_TENANT_COOKIE_NAME,
        "pkce_attempt",
    ):
        response.delete_cookie(
            cookie,
            domain=COOKIE_DOMAIN,
            path="/",
        )

    return response