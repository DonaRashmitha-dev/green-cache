"""Green Cache: FastAPI application entry point."""

import structlog
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router
from config import settings

logger = structlog.get_logger(__name__)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Green Cache",
        description="Multilingual semantic cache for LLMs with environmental impact tracking",
        version="0.1.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router, prefix="/api/v1")

    @app.on_event("startup")
    async def startup_event() -> None:
        logger.info(
            "green_cache_startup",
            host=settings.host,
            port=settings.port,
            backend=settings.cache_backend,
            embedding_model=settings.embedding_model,
        )

    @app.on_event("shutdown")
    async def shutdown_event() -> None:
        logger.info("green_cache_shutdown")

    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower(),
        reload=not settings.is_production,
    )
