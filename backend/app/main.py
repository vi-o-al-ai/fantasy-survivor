"""FastAPI application factory.

``create_app`` builds a fully configured app from settings. Tests call it
with overrides; ``app`` at module level is what uvicorn and Lambda import.
"""

import logging

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.auth import build_verifier
from app.config import Settings, get_settings
from app.logging import configure_logging
from app.routers import health, leagues, me, seasons, stats
from app.services.errors import ForbiddenError, NotFoundError, RuleViolationError
from app.storage.factory import build_store

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
    app.state.store = build_store(settings)

    app.include_router(health.router)
    app.include_router(me.router)
    app.include_router(seasons.router)
    app.include_router(seasons.scoring_router)
    app.include_router(stats.router)
    app.include_router(leagues.router)

    app.add_exception_handler(NotFoundError, _not_found)
    app.add_exception_handler(ForbiddenError, _forbidden)
    app.add_exception_handler(RuleViolationError, _rule_violation)

    log.info("app configured", extra={"env": settings.app_env})
    return app


def _not_found(_: Request, exc: Exception) -> JSONResponse:
    return JSONResponse({"detail": str(exc)}, status_code=status.HTTP_404_NOT_FOUND)


def _forbidden(_: Request, exc: Exception) -> JSONResponse:
    return JSONResponse({"detail": str(exc)}, status_code=status.HTTP_403_FORBIDDEN)


def _rule_violation(_: Request, exc: Exception) -> JSONResponse:
    return JSONResponse({"detail": str(exc)}, status_code=status.HTTP_409_CONFLICT)


app = create_app()
