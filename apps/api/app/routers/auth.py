from __future__ import annotations

from collections import defaultdict, deque
from threading import Lock
from time import monotonic

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from app.core.auth import (
    COOKIE_NAME,
    UserPrincipal,
    create_session_token,
    require_user,
    verify_credentials,
)
from app.core.config import Settings, get_settings
from app.schemas.contracts import AuthResponse, AuthUser, LoginRequest

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])
_attempts: dict[str, deque[float]] = defaultdict(deque)
_attempts_lock = Lock()


def _client_key(request: Request) -> str:
    return request.client.host if request.client else "unknown"


def _is_rate_limited(client_key: str, settings: Settings) -> bool:
    cutoff = monotonic() - settings.login_rate_limit_window_seconds
    with _attempts_lock:
        attempts = _attempts[client_key]
        while attempts and attempts[0] < cutoff:
            attempts.popleft()
        return len(attempts) >= settings.login_rate_limit_attempts


def _record_failure(client_key: str) -> None:
    with _attempts_lock:
        _attempts[client_key].append(monotonic())


def _clear_failures(client_key: str) -> None:
    with _attempts_lock:
        _attempts.pop(client_key, None)


@router.post("/login", response_model=AuthResponse)
def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    settings: Settings = Depends(get_settings),
) -> AuthResponse:
    client_key = _client_key(request)
    if _is_rate_limited(client_key, settings):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Try again later.",
            headers={"Retry-After": str(settings.login_rate_limit_window_seconds)},
        )
    if not verify_credentials(payload.username, payload.password, settings):
        _record_failure(client_key)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")
    _clear_failures(client_key)
    token = create_session_token(payload.username, settings)
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        max_age=settings.session_ttl_seconds,
        httponly=True,
        secure=settings.secure_cookies,
        samesite="lax",
        path="/",
    )
    return AuthResponse(
        user=AuthUser(
            username=settings.auth_username,
            display_name="Mr. C. Mezie",
            permissions=["read", "draft", "internal_write", "approve"],
        ),
        expires_in=settings.session_ttl_seconds,
    )


@router.get("/me", response_model=AuthUser)
def me(user: UserPrincipal = Depends(require_user)) -> AuthUser:
    return AuthUser(
        username=user.username,
        display_name=user.display_name,
        permissions=list(user.permissions),
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response) -> Response:
    response.delete_cookie(COOKIE_NAME, path="/")
    return response
