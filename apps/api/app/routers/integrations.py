from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Depends

from app.core.auth import require_user
from app.core.config import Settings, get_settings
from app.schemas.contracts import IntegrationList, IntegrationState

router = APIRouter(
    prefix="/api/v1/integrations",
    tags=["integrations"],
    dependencies=[Depends(require_user)],
)


def state(enabled: bool, configured: bool, mock_default: bool = False) -> str:
    if not enabled:
        return "mock" if mock_default else "disabled"
    return "configured" if configured else "error"


@router.get("/status", response_model=IntegrationList)
def integration_status(settings: Settings = Depends(get_settings)) -> IntegrationList:
    checked = datetime.now(UTC)
    items = [
        IntegrationState(
            id="openai",
            label="OpenAI",
            state=state(
                settings.ai_provider == "openai",
                bool(settings.openai_api_key and settings.openai_api_key.get_secret_value()),
                mock_default=settings.ai_provider == "mock",
            ),
            detail="Responses adapter"
            if settings.ai_provider == "openai"
            else "Deterministic mock provider",
            last_checked_at=checked,
        ),
        IntegrationState(
            id="telegram",
            label="Telegram",
            state=state(
                settings.telegram_enabled,
                bool(
                    settings.telegram_bot_token
                    and settings.telegram_bot_token.get_secret_value()
                    and settings.telegram_allowed_user_ids
                ),
            ),
            detail="Capture adapter; sender allowlist required",
            last_checked_at=checked,
        ),
        IntegrationState(
            id="apify",
            label="Apify",
            state=state(
                settings.apify_enabled,
                bool(
                    settings.apify_token
                    and settings.apify_token.get_secret_value()
                    and settings.apify_approved_actor_ids
                ),
            ),
            detail="Approved Actors and budget required",
            last_checked_at=checked,
        ),
        IntegrationState(
            id="creed-memory",
            label="Creed Memory",
            state=state(
                settings.creed_memory_enabled,
                bool(
                    settings.creedai_memory_api_key
                    and settings.creedai_memory_api_key.get_secret_value()
                ),
            ),
            detail="Read-only context adapter",
            last_checked_at=checked,
        ),
        IntegrationState(
            id="vault",
            label="BrandOS Vault",
            state="configured",
            detail=settings.brandos_vault_path,
            last_checked_at=checked,
        ),
    ]
    return IntegrationList(items=items)
