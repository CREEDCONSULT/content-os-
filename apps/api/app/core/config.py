from __future__ import annotations

from functools import lru_cache
from typing import Annotated

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../../.env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_env: str = "development"
    app_name: str = "Mezie BrandOS"
    api_base_url: str = "http://localhost:8000"
    cors_origins: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: ["http://localhost:3100"]
    )
    log_level: str = "INFO"

    database_url: str = "sqlite+pysqlite:///./brandos-dev.db"
    source_documents_path: str | None = None
    object_storage_path: str = "./storage"
    brandos_vault_path: str = "./vault"

    auth_mode: str = "local"
    auth_username: str = "mezie"
    auth_password: SecretStr = SecretStr("brandos-local-dev")
    session_secret: SecretStr = SecretStr("brandos-local-session-secret-change-me")
    session_ttl_seconds: int = 43_200
    secure_cookies: bool = False

    ai_provider: str = "mock"
    openai_api_key: SecretStr | None = None
    openai_base_url: str = "https://api.openai.com/v1"
    openai_timeout_seconds: float = 60.0
    brand_quality_model: str | None = None
    brand_fast_model: str | None = None
    brand_vision_model: str | None = None
    brand_transcription_model: str | None = None
    brand_embedding_model: str | None = None
    daily_model_budget_usd: float = 1.0
    weekly_research_budget_usd: float = 5.0

    telegram_enabled: bool = False
    telegram_bot_token: SecretStr | None = None
    telegram_webhook_secret: SecretStr | None = None
    telegram_allowed_user_ids: Annotated[list[int], NoDecode] = Field(default_factory=list)

    apify_enabled: bool = False
    apify_token: SecretStr | None = None
    apify_approved_actor_ids: Annotated[list[str], NoDecode] = Field(default_factory=list)
    apify_daily_budget_usd: float = 0.0

    creed_memory_enabled: bool = False
    creed_memory_url: str = "http://localhost:8788"
    creedai_memory_api_key: SecretStr | None = None
    creed_memory_scope: str = "founder"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def split_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [part.strip() for part in value.split(",") if part.strip()]
        return value

    @field_validator("telegram_allowed_user_ids", mode="before")
    @classmethod
    def split_user_ids(cls, value: object) -> object:
        if isinstance(value, str):
            return [int(part.strip()) for part in value.split(",") if part.strip()]
        return value

    @field_validator("apify_approved_actor_ids", mode="before")
    @classmethod
    def split_actor_ids(cls, value: object) -> object:
        if isinstance(value, str):
            return [part.strip() for part in value.split(",") if part.strip()]
        return value

    def assert_safe_runtime(self) -> None:
        if self.app_env.lower() != "production":
            return
        if self.auth_password.get_secret_value() == "brandos-local-dev":
            raise RuntimeError("AUTH_PASSWORD must be changed in production.")
        if self.session_secret.get_secret_value() == "brandos-local-session-secret-change-me":
            raise RuntimeError("SESSION_SECRET must be changed in production.")
        if not self.secure_cookies:
            raise RuntimeError("SECURE_COOKIES must be true in production.")


@lru_cache
def get_settings() -> Settings:
    return Settings()
