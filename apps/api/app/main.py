from __future__ import annotations

from contextlib import asynccontextmanager
from uuid import uuid4

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.routers import (
    agent,
    analytics,
    approvals,
    assets,
    auth,
    brand,
    calendar,
    content,
    creator_intelligence,
    dashboard,
    health,
    heartbeat,
    ideas,
    integrations,
    memory,
    production,
    proof,
    search,
    studio,
    telegram,
)

settings = get_settings()
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings.assert_safe_runtime()
    logger.info("brandos_api_starting", environment=settings.app_env, provider=settings.ai_provider)
    yield
    logger.info("brandos_api_stopping")


app = FastAPI(
    title="Mezie BrandOS API",
    version="0.1.0",
    description="Local-first operating API for the Mezie BrandOS command center.",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    request_id = str(uuid4())
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store"
    if settings.app_env.lower() == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


app.include_router(health.router)
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(brand.router)
app.include_router(ideas.router)
app.include_router(content.router)
app.include_router(approvals.router)
app.include_router(integrations.router)
app.include_router(agent.router)
app.include_router(studio.router)
app.include_router(calendar.router)
app.include_router(production.router)
app.include_router(assets.router)
app.include_router(proof.router)
app.include_router(memory.router)
app.include_router(creator_intelligence.router)
app.include_router(telegram.router)
app.include_router(heartbeat.router)
app.include_router(analytics.router)
app.include_router(search.router)
