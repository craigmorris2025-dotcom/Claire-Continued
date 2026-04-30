from fastapi import APIRouter
from .endpoints import register_endpoints
from .commands import router as commands_router

router = APIRouter()

# Standard endpoints
register_endpoints(router)

# Search bar command interface
router.include_router(commands_router, prefix="/api")

from .routes_update import router as update_router

router.include_router(update_router, prefix="/api")
