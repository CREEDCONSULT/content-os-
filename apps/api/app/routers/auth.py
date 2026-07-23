from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status

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


@router.post("/login", response_model=AuthResponse)
def login(
    payload: LoginRequest, response: Response, settings: Settings = Depends(get_settings)
) -> AuthResponse:
    if not verify_credentials(payload.username, payload.password, settings):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")
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
