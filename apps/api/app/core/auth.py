from __future__ import annotations

import secrets
from dataclasses import dataclass

from fastapi import Cookie, Depends, Header, HTTPException, status
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from app.core.config import Settings, get_settings

COOKIE_NAME = "brandos_session"


@dataclass(frozen=True)
class UserPrincipal:
    username: str
    display_name: str
    permissions: tuple[str, ...]


def _serializer(settings: Settings) -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(
        settings.session_secret.get_secret_value(),
        salt="mezie-brandos-session-v1",
    )


def verify_credentials(username: str, password: str, settings: Settings) -> bool:
    expected_user = settings.auth_username.encode("utf-8")
    expected_password = settings.auth_password.get_secret_value().encode("utf-8")
    return secrets.compare_digest(
        username.encode("utf-8"), expected_user
    ) and secrets.compare_digest(password.encode("utf-8"), expected_password)


def create_session_token(username: str, settings: Settings) -> str:
    return _serializer(settings).dumps({"sub": username, "version": 1})


def decode_session_token(token: str, settings: Settings) -> UserPrincipal:
    try:
        payload = _serializer(settings).loads(token, max_age=settings.session_ttl_seconds)
    except SignatureExpired as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired."
        ) from exc
    except BadSignature as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session."
        ) from exc

    if payload.get("sub") != settings.auth_username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unknown session user."
        )
    return UserPrincipal(
        username=settings.auth_username,
        display_name="Mr. C. Mezie",
        permissions=("read", "draft", "internal_write", "approve"),
    )


def require_user(
    authorization: str | None = Header(default=None),
    session_cookie: str | None = Cookie(default=None, alias=COOKIE_NAME),
    settings: Settings = Depends(get_settings),
) -> UserPrincipal:
    if settings.auth_mode == "disabled" and settings.app_env == "development":
        return UserPrincipal(
            username=settings.auth_username,
            display_name="Mr. C. Mezie",
            permissions=("read", "draft", "internal_write", "approve"),
        )

    token = session_cookie
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1].strip()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required."
        )
    return decode_session_token(token, settings)
