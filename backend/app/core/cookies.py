from fastapi import Request, Response

from app.core.config import settings


def _is_secure_request(request: Request) -> bool:
    """Determine whether the original request used HTTPS."""
    forwarded_proto = request.headers.get("x-forwarded-proto")

    if forwarded_proto:
        return (
            forwarded_proto.split(",")[0]
            .strip()
            .lower()
            == "https"
        )

    return request.url.scheme.lower() == "https"


def set_auth_cookie(
    response: Response,
    request: Request,
    token: str,
) -> None:
    """Set the short-lived access-token cookie."""
    response.set_cookie(
        key=settings.SESSION_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=(
            settings.COOKIE_SECURE
            or _is_secure_request(request)
        ),
        samesite=settings.COOKIE_SAMESITE,
        max_age=300,
        path="/",
    )


def clear_auth_cookie(response: Response) -> None:
    """Clear the access-token cookie."""
    response.delete_cookie(
        key=settings.SESSION_COOKIE_NAME,
        path="/",
    )