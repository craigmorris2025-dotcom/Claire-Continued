"""
FastAPI Application Factory   Claire Syntalion v4.2
"""

import os
import pathlib
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# FIXED IMPORTS   remove "src."
from backend.config.settings import get_settings
from backend.config.logging import setup_logging
from backend.platform.update_manager import check_for_updates

logger = logging.getLogger("claire.server")

# Frontend directory
FRONTEND_DIR = pathlib.Path(__file__).parent.parent / "frontend"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup + shutdown lifecycle."""
    setup_logging()
    settings = get_settings()

    # Ensure required directories exist
    os.makedirs(settings.output_dir, exist_ok=True)
    os.makedirs(settings.log_dir, exist_ok=True)
    os.makedirs(settings.data_dir, exist_ok=True)
    os.makedirs("data/cache", exist_ok=True)
    os.makedirs("data/backups", exist_ok=True)

    logger.info(f"Claire Syntalion v4.2.1 starting   env={settings.env}")
    yield
    logger.info("Claire Syntalion shutting down")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="Claire Syntalion   Sovereign R&D Platform",
        description="24-engine autonomous evaluation pipeline   v4.2",
        version="4.2.1",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Auto-update on startup
    @app.on_event("startup")
    async def auto_update():
        await check_for_updates()

    # Routers   all imports corrected to match your folder tree
    from backend.api.routes_pipeline import router as pipeline_router
    from backend.api.routes_history import router as history_router
    from backend.api.routes_acquirers import router as acquirers_router
    from backend.api.routes_system import router as system_router
    from backend.api.routes_connectors import router as connectors_router
    from backend.api.routes_update import router as update_router
    from backend.api.routes_proxy import router as proxy_router
    from backend.api.routes_platform import router as platform_router
    from backend.api.routes_dashboard import router as dashboard_router

    app.include_router(pipeline_router, prefix="", tags=["Pipeline"])
    app.include_router(history_router, prefix="", tags=["History"])
    app.include_router(acquirers_router, prefix="", tags=["Acquirers"])
    app.include_router(system_router, prefix="", tags=["System"])
    app.include_router(connectors_router, prefix="", tags=["Connectors"])
    app.include_router(update_router, prefix="", tags=["Update"])
    app.include_router(proxy_router, prefix="", tags=["Proxy"])
    app.include_router(platform_router, prefix="", tags=["Platform"])
    app.include_router(dashboard_router, prefix="/api", tags=["Dashboard"])

    # Static frontend mounting
    css_dir = FRONTEND_DIR / "css"
    js_dir = FRONTEND_DIR / "js"
    assets_dir = FRONTEND_DIR / "assets"

    if css_dir.exists():
        app.mount("/css", StaticFiles(directory=str(css_dir)), name="css")

    if js_dir.exists():
        app.mount("/js", StaticFiles(directory=str(js_dir)), name="js")

    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    # Root endpoint
    @app.get("/", include_in_schema=False)
    async def root():
        return {
            "name": "Claire Syntalion",
            "version": "4.2.1",
            "status": "online"
        }

    return app


# App instance for Uvicorn
app = create_app()
