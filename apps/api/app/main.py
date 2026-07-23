from __future__ import annotations

from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.routers import (
    agent,
    approvals,
    auth,
    brand,
    content,
    dashboard,
    health,
    ideas,
    integrations,
    studio,
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
