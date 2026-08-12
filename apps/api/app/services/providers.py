from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
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
    @staticmethod
    def _campaign_payload() -> dict[str, Any]:
        start = datetime.now(UTC).date() + timedelta(days=1)
        pillars = [
            ("Build", "Building Creed", "LinkedIn", "Founder post"),
            ("Leverage", "Built With AI", "Instagram", "Reel"),
            ("Lead", "Builder Walks", "YouTube Shorts", "Short"),
            ("See", "Africa Can Build", "LinkedIn", "Essay"),
            ("Own", "Ownership School", "LinkedIn", "Carousel"),
        ]
        day_templates = [
            (
                "The OS behind consistent builders",
                "Consistency is not a personality trait. It is a system design problem.",
                "Show the BrandOS command center as the proof surface.",
            ),
            (
                "AI is leverage, not identity",
                "The builder keeps judgment; the system absorbs coordination strain.",
                "Show an agent run becoming a governed proposal.",
            ),
            (
                "The rough-work room",
                "Telegram is for messy thinking; BrandOS is for governed conversion.",
                "Show the Action Inbox boundary between brainstorm and execution.",
            ),
            (
                "Evidence before aesthetics",
                "A beautiful brand without proof becomes performance theatre.",
                "Reference proof-of-work records and production readiness gates.",
            ),
            (
                "Benchmark without becoming a copy",
                "Extract mechanics, never identity.",
                "Use creator teardown rules and protected-expression safeguards.",
            ),
            (
                "A 10-day content sprint should have a spine",
                "Cadence works when every day has one job in the story arc.",
                "Show the campaign map and calendar blocks.",
            ),
            (
                "The founder becomes the operating system",
                "Your brand compounds when your decisions become reusable infrastructure.",
                "Connect brand memory, knowledge graph, and scripts.",
            ),
            (
                "Do not publish what has not passed the gate",
                "Speed is useful only when risk boundaries stay intact.",
                "Show approvals, script review, and public-publishing gates.",
            ),
            (
                "Build in public without leaking the engine",
                "Show enough process to build trust, not enough to compromise privacy.",
                "Use internal/public sensitivity labels.",
            ),
            (
                "From dashboard to movement",
                "BrandOS is not a content folder; it is the operating layer for ownership.",
                "End with the 10-day recap and next experiment.",
            ),
        ]
        days: list[dict[str, Any]] = []
        for index, (title, message, proof) in enumerate(day_templates, 1):
            pillar, series, platform, format_name = pillars[(index - 1) % len(pillars)]
            days.append(
                {
                    "day": index,
                    "date": (start + timedelta(days=index - 1)).isoformat(),
                    "title": title,
                    "platform": platform,
                    "format": format_name,
                    "pillar": pillar,
                    "series": series,
                    "audience": "Emerging builders and operators",
                    "objective": (
                        "Convert curiosity about BrandOS into trust in Mr. C. Mezie's "
                        "builder intelligence operating method."
                    ),
                    "hook": f"Day {index}: {message}",
                    "core_message": message,
                    "proof_angle": proof,
                    "research_angle": (
                        "Grounded in canonical BrandOS positioning, stored benchmark mechanics, "
                        "and local analytics hypotheses; external freshness must be added before "
                        "time-sensitive public claims."
                    ),
                    "production_notes": (
                        "Founder-led direct-to-camera with one restrained product evidence insert; "
                        "capture a clean hook variant and a proof close."
                    ),
                    "cta": "Tell me what system you are building next.",
                    "success_metric": "Qualified saves, replies, and benchmarkable comments.",
                    "status": "brief",
                    "priority": "high",
                }
            )
        return {
            "campaign_name": "10-Day BrandOS Builder Intelligence Rollout",
            "campaign_start": start.isoformat(),
            "campaign_end": (start + timedelta(days=9)).isoformat(),
            "thesis": (
                "Make BrandOS visible as the operating system that turns rough thinking, "
                "agent judgment, memory, and proof into a consistent founder brand."
            ),
            "audience": "Emerging builders, operators, founders, and ambitious creators.",
            "channels": ["LinkedIn", "Instagram", "YouTube Shorts", "Telegram"],
            "research_basis": [
                {
                    "source": "canonical_brand_positioning",
                    "type": "approved_strategy",
                    "finding": (
                        "Mr. C. Mezie should own Builder Intelligence: seeing possibility, "
                        "building systems, and becoming evidence."
                    ),
                    "impact": "The campaign should show operating proof, not generic motivation.",
                    "confidence": 0.95,
                },
                {
                    "source": "creator_benchmark_library",
                    "type": "working_hypothesis",
                    "finding": (
                        "Useful creator references should be mined for transferable mechanics "
                        "while protecting identity and wording."
                    ),
                    "impact": "Every post uses an original Mezie proof angle.",
                    "confidence": 0.8,
                },
                {
                    "source": "brandos_analytics",
                    "type": "model_inference",
                    "finding": (
                        "Proof-led system-building content should be measured by saves, "
                        "substantive replies, shares, and conversion into ideas/scripts."
                    ),
                    "impact": (
                        "The rollout includes controlled experiments instead of vanity-only goals."
                    ),
                    "confidence": 0.75,
                },
            ],
            "rollout_strategy": {
                "objective": (
                    "Create a visible proof arc from why BrandOS exists to how it operates."
                ),
                "narrative_arc": (
                    "Days 1-3 explain the problem and interface, Days 4-7 prove the system, "
                    "Days 8-10 set boundaries, recap, and invite serious builders."
                ),
                "cadence": (
                    "One flagship LinkedIn post or essay plus one short-form proof cut each day."
                ),
                "content_mix": (
                    "40% operating philosophy, 40% product/process proof, 20% invitation/recap."
                ),
                "measurement": (
                    "Track save rate, replies with concrete use cases, shares, and idea captures."
                ),
            },
            "days": days,
            "experiments": [
                {
                    "title": "Proof hook versus identity hook",
                    "question": (
                        "Do proof-led hooks create more qualified saves than identity-led hooks?"
                    ),
                    "hypothesis": (
                        "Proof-led hooks will increase saves because the audience can reuse "
                        "the system."
                    ),
                    "variable": "hook framing",
                    "control_conditions": ["Same topic", "Same format", "Same posting window"],
                    "platform": "LinkedIn",
                    "content_type": "Founder post",
                    "expected_outcome": "Higher save rate and more specific builder replies.",
                    "success_metric": "Save rate and substantive replies",
                    "measurement_start": start.isoformat(),
                    "measurement_end": (start + timedelta(days=10)).isoformat(),
                },
                {
                    "title": "Dashboard proof versus founder monologue",
                    "question": (
                        "Does showing the BrandOS interface produce more idea captures than "
                        "direct-to-camera explanation alone?"
                    ),
                    "hypothesis": (
                        "A restrained product proof insert will make the promise more believable "
                        "and increase conversion into rough ideas."
                    ),
                    "variable": "proof insert style",
                    "control_conditions": ["Same thesis", "Same CTA", "Same founder framing"],
                    "platform": "Instagram",
                    "content_type": "Reel",
                    "expected_outcome": (
                        "More replies naming a concrete system the viewer wants to build."
                    ),
                    "success_metric": "Idea captures and qualified replies",
                    "measurement_start": start.isoformat(),
                    "measurement_end": (start + timedelta(days=10)).isoformat(),
                },
                {
                    "title": "Builder CTA specificity",
                    "question": (
                        "Does a specific builder prompt outperform a broad inspirational prompt?"
                    ),
                    "hypothesis": (
                        "Specific CTAs should improve response quality because they ask for "
                        "a concrete system, not applause."
                    ),
                    "variable": "CTA specificity",
                    "control_conditions": ["Same topic", "Same proof angle", "Same channel"],
                    "platform": "LinkedIn",
                    "content_type": "Founder post",
                    "expected_outcome": (
                        "Higher percentage of replies with actionable builder context."
                    ),
                    "success_metric": "Substantive reply ratio",
                    "measurement_start": start.isoformat(),
                    "measurement_end": (start + timedelta(days=10)).isoformat(),
                },
            ],
            "approval_boundaries": [
                "No public publishing occurs from this campaign creation action.",
                "Scheduling to external platforms remains approval-gated.",
                "Financial, client, private founder, and canonical memory claims require review.",
                "External trend freshness must be verified before time-sensitive public claims.",
            ],
            "confidence": 0.84,
        }

    def generate(
        self,
        *,
        intent: str,
        raw_input: dict[str, Any],
        context_markdown: str,
        selected_skills: list[str],
    ) -> ProviderResult:
        context_state = "loaded" if context_markdown else "missing"
        wants_campaign = "campaign" in intent.lower() and (
            "10" in intent or "ten" in intent.lower() or "day" in intent.lower()
        )
        proposed_writes = []
        next_actions = ["Review the selected skills and context sources."]
        if wants_campaign:
            campaign_payload = self._campaign_payload()
            proposed_writes = [
                {
                    "record_type": "campaign_plan",
                    "action": "create_campaign_plan",
                    "rationale": (
                        "A 10-day campaign is an internal orchestration artifact. It should "
                        "be staged for review before any external scheduling or publishing."
                    ),
                    "payload_json": json.dumps(campaign_payload, ensure_ascii=False),
                }
            ]
            next_actions = [
                "Open Action Inbox and execute the safe campaign-plan proposal.",
                "Review the generated content records and calendar planning blocks.",
                "Add live external evidence before making freshness claims in public copy.",
            ]
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
                "proposed_writes": proposed_writes,
                "warnings": ["Mock output must not be represented as live AI generation."],
                "next_actions": next_actions,
                "confidence": 1.0,
                "echo": raw_input,
            },
            usage={"input_tokens": 0, "output_tokens": 0},
        )


class OpenAIResponsesProvider:
    def __init__(self, settings: Settings):
        self.settings = settings

    @staticmethod
    def _extract_output_text(body: dict[str, Any]) -> str | None:
        text = body.get("output_text")
        if text:
            return str(text)
        for item in body.get("output", []):
            if item.get("type") != "message":
                continue
            for content in item.get("content", []):
                if content.get("type") == "output_text":
                    return str(content.get("text") or "")
        return None

    @staticmethod
    def _research_schema() -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "summary": {"type": "string"},
                "research_basis": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "source": {"type": "string"},
                            "type": {
                                "type": "string",
                                "enum": [
                                    "verified_fact",
                                    "working_hypothesis",
                                    "model_inference",
                                ],
                            },
                            "finding": {"type": "string"},
                            "impact": {"type": "string"},
                            "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                        },
                        "required": [
                            "source",
                            "type",
                            "finding",
                            "impact",
                            "confidence",
                        ],
                        "additionalProperties": False,
                    },
                },
                "freshness_notes": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["summary", "research_basis", "freshness_notes"],
            "additionalProperties": False,
        }

    def _generate_campaign(
        self,
        *,
        key: str,
        model: str,
        intent: str,
        raw_input: dict[str, Any],
        context_markdown: str,
        selected_skills: list[str],
    ) -> ProviderResult:
        campaign_payload = MockProvider._campaign_payload()
        warnings: list[str] = []
        usage: dict[str, Any] = {"mode": "local_campaign_planner"}
        research_summary = (
            "BrandOS used the canonical brand context and local benchmark hypotheses."
        )
        research_timeout = min(float(self.settings.openai_timeout_seconds), 25.0)
        research_payload = {
            "model": model,
            "store": False,
            "input": [
                {
                    "role": "system",
                    "content": (
                        "You are the Mezie BrandOS research scout. Use web search for "
                        "current, high-level creator and AI workflow patterns, then return "
                        "only compact JSON. Do not copy creator expression, private details, "
                        "or platform-protected wording. Treat findings as inputs to an "
                        "internal campaign strategy, not public claims."
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "intent": intent,
                            "raw_input": raw_input,
                            "selected_skills": selected_skills,
                            "brand_context_excerpt": context_markdown[:6000],
                            "needed_output": (
                                "3 concise research_basis items for a 10-day founder-led "
                                "BrandOS campaign: creator content mechanics, AI workflow "
                                "positioning, and rollout measurement strategy."
                            ),
                        },
                        ensure_ascii=False,
                    ),
                },
            ],
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": "brandos_campaign_research",
                    "strict": True,
                    "schema": self._research_schema(),
                }
            },
            "tools": [{"type": "web_search"}],
            "tool_choice": "required",
            "include": ["web_search_call.action.sources"],
        }
        try:
            with httpx.Client(timeout=research_timeout) as client:
                response = client.post(
                    f"{self.settings.openai_base_url.rstrip('/')}/responses",
                    headers={
                        "Authorization": f"Bearer {key}",
                        "Content-Type": "application/json",
                    },
                    json=research_payload,
                )
                response.raise_for_status()
            body = response.json()
            usage = body.get("usage", {})
            text = self._extract_output_text(body)
            if not text:
                raise ProviderResponseError("OpenAI campaign research returned no text.")
            research = json.loads(text)
            research_summary = str(research.get("summary") or research_summary)
            web_basis = [
                item
                for item in research.get("research_basis", [])
                if isinstance(item, dict)
            ][:4]
            if web_basis:
                campaign_payload["research_basis"] = [
                    *web_basis,
                    *campaign_payload["research_basis"],
                ][:8]
            freshness_notes = [
                str(item)
                for item in research.get("freshness_notes", [])
                if str(item).strip()
            ]
            if freshness_notes:
                campaign_payload["freshness_notes"] = freshness_notes[:6]
        except (httpx.HTTPError, json.JSONDecodeError, ProviderResponseError):
            warnings.append(
                "OpenAI web research was unavailable or exceeded the short campaign "
                "research window; BrandOS used canonical local context fallback."
            )

        output = {
            "summary": (
                "Prepared a 10-day BrandOS campaign proposal with research-informed "
                "positioning, content briefs, measurement experiments, and approval "
                "boundaries. "
                f"Research note: {research_summary}"
            ),
            "classifications": [
                {
                    "statement": "The campaign is an internal planning artifact.",
                    "type": "approved_strategy",
                    "evidence": "BrandOS approval policy gates public scheduling and publishing.",
                },
                {
                    "statement": "The 10-day rollout uses campaign strategy and research signals.",
                    "type": "working_hypothesis",
                    "evidence": research_summary,
                },
                {
                    "statement": "External claims still require fact-checking before publication.",
                    "type": "approved_strategy",
                    "evidence": "Campaign execution creates briefs and planning blocks only.",
                },
            ],
            "proposed_writes": [
                {
                    "record_type": "campaign_plan",
                    "action": "create_campaign_plan",
                    "rationale": (
                        "A 10-day campaign is a safe internal orchestration artifact. "
                        "It should be staged for review before external scheduling or publishing."
                    ),
                    "payload_json": json.dumps(campaign_payload, ensure_ascii=False),
                }
            ],
            "warnings": warnings,
            "next_actions": [
                "Open Action Inbox and execute the safe campaign-plan proposal.",
                "Review the generated content briefs, calendar blocks, and experiments.",
                "Fact-check external or time-sensitive claims before drafting public copy.",
            ],
            "confidence": float(campaign_payload.get("confidence") or 0.82),
        }
        return ProviderResult(
            provider="openai",
            model_alias=model,
            output=output,
            usage=usage,
        )

    @staticmethod
    def _output_schema() -> dict[str, Any]:
        return {
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
                "proposed_writes": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "record_type": {"type": "string"},
                            "action": {"type": "string"},
                            "rationale": {"type": "string"},
                            "payload_json": {
                                "type": "string",
                                "description": (
                                    "A JSON object string containing the action payload. "
                                    "Use {} when no payload is needed."
                                ),
                            },
                        },
                        "required": ["record_type", "action", "rationale", "payload_json"],
                        "additionalProperties": False,
                    },
                },
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
            raise ProviderConfigurationError("BRAND_FAST_MODEL is required for AI_PROVIDER=openai.")

        lowered_intent = intent.lower()
        lowered_input = json.dumps(raw_input, ensure_ascii=False).lower()
        wants_campaign = "campaign" in lowered_intent or "rollout" in lowered_intent
        if wants_campaign:
            return self._generate_campaign(
                key=key,
                model=model,
                intent=intent,
                raw_input=raw_input,
                context_markdown=context_markdown,
                selected_skills=selected_skills,
            )
        needs_research = any(
            term in f"{lowered_intent}\n{lowered_input}"
            for term in (
                "research",
                "trend",
                "current",
                "benchmark",
                "campaign",
                "rollout",
                "10 day",
                "ten day",
            )
        )
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
                        "paid, destructive, or canonical write occurred. When the user "
                        "gives a useful rough idea, propose record_type='idea' and "
                        "action='create_rough_idea' in proposed_writes. When the user asks "
                        "for a campaign or rollout plan, propose record_type='campaign_plan' "
                        "and action='create_campaign_plan' with payload_json containing a "
                        "JSON object with campaign_name, campaign_start, campaign_end, thesis, "
                        "audience, channels, research_basis, rollout_strategy, exactly 10 days, "
                        "experiments, approval_boundaries, and confidence. Each day must include "
                        "day, date, title, platform, format, pillar, series, audience, objective, "
                        "hook, core_message, proof_angle, research_angle, production_notes, cta, "
                        "success_metric, status, and priority. The application will execute or "
                        "approval-gate proposals separately."
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
                    "schema": self._output_schema(),
                }
            },
        }
        if needs_research:
            payload["tools"] = [{"type": "web_search"}]
            payload["tool_choice"] = "auto"
            payload["include"] = ["web_search_call.action.sources"]
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
        text = self._extract_output_text(body)
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
