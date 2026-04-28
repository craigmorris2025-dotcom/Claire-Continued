"""
Web Proxy API — allows the frontend to route outbound HTTP requests
through the backend, avoiding CORS restrictions.
All requests are logged and rate-limited via WebFetcher.
"""
import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from backend.connectors.web_fetcher import get_fetcher

logger = logging.getLogger("claire.api.proxy")
router = APIRouter()


class ProxyPostRequest(BaseModel):
    url: str
    payload: Dict[str, Any] = {}
    headers: Optional[Dict[str, str]] = None


@router.get("/api/proxy/get")
async def proxy_get(
    url: str = Query(..., description="Target URL to fetch"),
    use_cache: bool = Query(True, description="Use server-side cache"),
):
    """Proxy a GET request through the backend."""
    if not url or not url.startswith(("http://", "https://")):
        raise HTTPException(400, "Invalid URL — must start with http:// or https://")

    fetcher = get_fetcher()
    result = fetcher.get(url, use_cache=use_cache)

    if result is None:
        raise HTTPException(502, f"Failed to fetch {url}")

    return {"url": url, "cached": use_cache, "data": result}


@router.post("/api/proxy/post")
async def proxy_post(req: ProxyPostRequest):
    """Proxy a POST request through the backend."""
    if not req.url or not req.url.startswith(("http://", "https://")):
        raise HTTPException(400, "Invalid URL — must start with http:// or https://")

    fetcher = get_fetcher()
    result = fetcher.post(req.url, payload=req.payload)

    if result is None:
        raise HTTPException(502, f"Failed to POST to {req.url}")

    return {"url": req.url, "data": result}


@router.get("/api/proxy/ping")
async def proxy_ping():
    """
    Test outbound connectivity by hitting a known reliable endpoint.
    Returns online status and latency.
    """
    import time
    fetcher = get_fetcher()

    test_urls = [
        "https://httpbin.org/get",
        "https://api.github.com/zen",
    ]

    for test_url in test_urls:
        start = time.time()
        result = fetcher.get(test_url, use_cache=False)
        elapsed = round((time.time() - start) * 1000)

        if result is not None:
            return {
                "online": True,
                "latency_ms": elapsed,
                "test_url": test_url,
            }

    return {"online": False, "reason": "All test endpoints unreachable"}
