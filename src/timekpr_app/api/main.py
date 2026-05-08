"""FastAPI application and server startup."""

from __future__ import annotations

import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from timekpr_app import __version__
from timekpr_app.api import auth, config, health, stats
from timekpr_app.config import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore
    """Application startup and shutdown."""
    logger.info(f"timekpr-app v{__version__} starting (env: {settings.app_env})")
    yield
    logger.info("timekpr-app shutting down")


# Create FastAPI app
app = FastAPI(
    title=settings.app_title,
    version=__version__,
    description="Web API for timekpr screen time management",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with /api prefix
app.include_router(health.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(stats.router, prefix="/api")
app.include_router(config.router, prefix="/api")


@app.get("/", tags=["info"])
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {
        "name": settings.app_title,
        "version": __version__,
        "docs": "/docs",
    }


def cli() -> None:
    """CLI entry point for uvicorn server."""
    import uvicorn

    logger.info(f"Starting server on {settings.host}:{settings.port}")
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level=logging.getLevelName(logging.getLogger().level).lower(),
    )


if __name__ == "__main__":
    cli()
