from fastapi import Response

from app.core.config import settings


def set_auth_cookie(response: Response, token: str):
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="lax",
        max_age=3600,
        path="/",
    )


def clear_auth_cookie(response: Response):
    response.delete_cookie(
        "access_token",
        path="/",
    )