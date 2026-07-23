from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Protocol

import httpx

from app.core.config import Settings


class ProviderConfigurationError(RuntimeError):
    pass


class ProviderResponseError(RuntimeError):
    pass


@dataclass(frozen=True)
class ProviderResult:
    provider: str
    model_alias: str
    output: dict[str, Any]
    usage: dict[str, Any]


class ModelProvider(Protocol):
    def generate(
        self,
        *,
        intent: str,
        raw_input: dict[str, Any],
        context_markdown: str,
        selected_skills: list[str],
    ) -> ProviderResult: ...


class MockProvider:
    def generate(
        self,
        *,
        intent: str,
        raw_input: dict[str, Any],
        context_markdown: str,
        selected_skills: list[str],
    ) -> ProviderResult:
        context_state = "loaded" if context_markdown else "missing"
        return ProviderResult(
            provider="mock",
            model_alias="mock_brand_fast_model",
            output={
                "summary": (
                    f"Prepared a governed BrandOS response for: {intent}. "
                    f"Canonical context was {context_state}; no external model was called."
                ),
                "classifications": [
                    {
                        "statement": "The response is a deterministic development result.",
                        "type": "verified_fact",
                        "evidence": "provider=mock",
                    },
                    {
                        "statement": f"Selected skills: {', '.join(selected_skills)}",
                        "type": "model_inference",
                        "evidence": "deterministic keyword router",
                    },
                ],
                "proposed_writes": [],
                "warnings": ["Mock output must not be represented as live AI generation."],
                "next_actions": ["Review the selected skills and context sources."],
                "confidence": 1.0,
                "echo": raw_input,
            },
            usage={"input_tokens": 0, "output_tokens": 0},
        )


class OpenAIResponsesProvider:
    def __init__(self, settings: Settings):
        self.settings = settings

    def generate(
        self,
        *,
        intent: str,
        raw_input: dict[str, Any],
        context_markdown: str,
        selected_skills: list[str],
    ) -> ProviderResult:
        key = (
            self.settings.openai_api_key.get_secret_value().strip()
            if self.settings.openai_api_key
            else ""
        )
        model = (self.settings.brand_fast_model or "").strip()
        if not key:
            raise ProviderConfigurationError("OPENAI_API_KEY is required for AI_PROVIDER=openai.")
        if not model:
            raise ProviderConfigurationError(
                "BRAND_FAST_MODEL is required for AI_PROVIDER=openai."
            )

        output_schema = {
            "type": "object",
            "properties": {
                "summary": {"type": "string"},
                "classifications": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "statement": {"type": "string"},
                            "type": {
                                "type": "string",
                                "enum": [
                                    "verified_fact",
                                    "approved_strategy",
                                    "working_hypothesis",
                                    "model_inference",
                                    "missing_information",
                                ],
                            },
                            "evidence": {"type": "string"},
                        },
                        "required": ["statement", "type", "evidence"],
                        "additionalProperties": False,
                    },
                },
                "proposed_writes": {"type": "array", "items": {"type": "object"}},
                "warnings": {"type": "array", "items": {"type": "string"}},
                "next_actions": {"type": "array", "items": {"type": "string"}},
                "confidence": {"type": "number", "minimum": 0, "maximum": 1},
            },
            "required": [
                "summary",
                "classifications",
                "proposed_writes",
                "warnings",
                "next_actions",
                "confidence",
            ],
            "additionalProperties": False,
        }
        payload = {
            "model": model,
            "store": False,
            "input": [
                {
                    "role": "system",
                    "content": (
                        "You are the Mezie Brand Director. Use only supplied context. "
                        "Separate verified fact, approved strategy, working hypothesis, "
                        "model inference, and missing information. Never claim a public, "
                        "paid, destructive, or canonical write occurred."
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "intent": intent,
                            "raw_input": raw_input,
                            "selected_skills": selected_skills,
                            "context": context_markdown,
                        },
                        ensure_ascii=False,
                    ),
                },
            ],
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": "brandos_agent_output",
                    "strict": True,
                    "schema": output_schema,
                }
            },
        }
        try:
            with httpx.Client(timeout=self.settings.openai_timeout_seconds) as client:
                response = client.post(
                    f"{self.settings.openai_base_url.rstrip('/')}/responses",
                    headers={
                        "Authorization": f"Bearer {key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
                response.raise_for_status()
        except httpx.HTTPError as exc:
            raise ProviderResponseError("OpenAI Responses API request failed.") from exc

        body = response.json()
        text = body.get("output_text")
        if not text:
            for item in body.get("output", []):
                if item.get("type") != "message":
                    continue
                for content in item.get("content", []):
                    if content.get("type") == "output_text":
                        text = content.get("text")
                        break
        if not text:
            raise ProviderResponseError("OpenAI response contained no structured output.")
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ProviderResponseError("OpenAI structured output could not be decoded.") from exc
        return ProviderResult(
            provider="openai",
            model_alias=model,
            output=parsed,
            usage=body.get("usage", {}),
        )


def provider_for(settings: Settings) -> ModelProvider:
    if settings.ai_provider.lower() == "mock":
        return MockProvider()
    if settings.ai_provider.lower() == "openai":
        return OpenAIResponsesProvider(settings)
    raise ProviderConfigurationError(
        f"Unsupported AI_PROVIDER={settings.ai_provider!r}; use mock or openai."
    )
