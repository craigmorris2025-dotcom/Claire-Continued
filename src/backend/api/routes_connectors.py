"""
Connector API routes — expose connector data through REST.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
from backend.connectors.manager import ConnectorManager

router = APIRouter(prefix="/connectors", tags=["connectors"])

_manager = ConnectorManager()


class ConnectorQuery(BaseModel):
    connector: Optional[str] = None
    domain: str = "technology"
    sector: Optional[str] = None
    keywords: List[str] = []
    mode: str = "deterministic"


@router.get("/status")
async def connector_status():
    """List all registered connectors and their status."""
    return {
        "connectors": _manager.status(),
        "available": _manager.available,
        "count": len(_manager.available),
    }


@router.post("/fetch")
async def connector_fetch(query: ConnectorQuery):
    """Fetch data from one or all connectors."""
    q = {
        "domain": query.domain,
        "sector": query.sector or query.domain,
        "keywords": query.keywords,
    }
    if query.connector:
        result = _manager.fetch_one(query.connector, q, mode=query.mode)
        if "error" in result and not result.get("data"):
            raise HTTPException(status_code=404, detail=result["error"])
        return result
    return _manager.fetch_all(q, mode=query.mode)
