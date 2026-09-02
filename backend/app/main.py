"""FastAPI application factory.

``create_app`` builds a fully configured app from settings. Tests call it
with overrides; ``app`` at module level is what uvicorn and Lambda import.
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth import build_verifier
from app.config import Settings, get_settings
from app.logging import configure_logging
from app.routers import health, me

log = logging.getLogger(__name__)


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    configure_logging(settings.log_level, settings.log_format)

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        docs_url="/docs" if not settings.is_deployed or settings.app_env == "dev" else None,
    )

    if settings.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    app.state.token_verifier = build_verifier(settings)

    app.include_router(health.router)
    app.include_router(me.router)

    log.info("app configured", extra={"env": settings.app_env})
    return app


app = create_app()
