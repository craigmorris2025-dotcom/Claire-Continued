import logging

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from claire.config.logging import setup_logging

# ?? import routers at top (cleaner + safer)
from claire.api.routes_pipeline import router as pipeline_router


logger = logging.getLogger("claire.server")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup + shutdown lifecycle."""
    setup_logging()
    logger.info("Claire starting (recovery mode)")
    yield
    logger.info("Claire shutting down")


def create_app() -> FastAPI:
    """Create a minimal FastAPI app with one safe route attached."""

    app = FastAPI(
        title="Claire (Recovery Mode)",
        version="0.1",
        lifespan=lifespan,
    )

    # CORS (wide open for now)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ? Health routes
    @app.get("/")
    async def root():
        return {"status": "ok", "mode": "recovery"}

    @app.get("/health")
    async def health():
        return {"status": "healthy"}

    # ? Attach first working router
    app.include_router(pipeline_router)

    return app


# App instance for Uvicorn
app = create_app()
