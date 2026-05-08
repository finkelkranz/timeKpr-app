"""FastAPI application and server startup."""

from __future__ import annotations

import asyncio
import logging
import sys
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from timekpr_app import __version__
from timekpr_app.api import auth, config, health, stats, stats_history
from timekpr_app.config import get_settings
from timekpr_app.timekpr_db import init_db, save_all_users_stats
from timekpr_app.timekpr_file import get_all_users_data

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
settings = get_settings()

# Global variable for background task
_polling_task: asyncio.Task | None = None


async def poll_timekpr_stats(interval_seconds: int = 300) -> None:
    """Background task to poll timekpr statistics and save to database.
    
    Args:
        interval_seconds: How often to poll (default: 300 = 5 minutes)
    """
    logger.info(f"Starting timekpr polling task (interval: {interval_seconds}s)")
    
    # Initialize database on first run
    try:
        init_db()
        logger.info("Statistics database initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        return
    
    while True:
        try:
            # Poll all users and save to database
            start_time = datetime.now()
            count = save_all_users_stats()
            elapsed = (datetime.now() - start_time).total_seconds()
            logger.info(f"Polled {count} users in {elapsed:.2f}s")
        except FileNotFoundError as e:
            logger.warning(f"File access error (running without root?): {e}")
        except PermissionError as e:
            logger.warning(f"Permission error (running without root?): {e}")
        except Exception as e:
            logger.error(f"Error polling timekpr stats: {e}")
        
        # Wait for next interval
        await asyncio.sleep(interval_seconds)


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore
    """Application startup and shutdown."""
    global _polling_task
    
    logger.info(f"timekpr-app v{__version__} starting (env: {settings.app_env})")
    
    # Start background polling task
    _polling_task = asyncio.create_task(poll_timekpr_stats())
    
    yield
    
    # Shutdown: cancel polling task
    logger.info("timekpr-app shutting down")
    if _polling_task:
        _polling_task.cancel()
        try:
            await _polling_task
        except asyncio.CancelledError:
            logger.info("Polling task cancelled")


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
app.include_router(stats_history.router, prefix="/api")


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
