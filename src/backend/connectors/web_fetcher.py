"""
WebFetcher — Universal HTTP client for Claire-Syntalion connectors.
Provides: session management, rate limiting, caching, error recovery.
All outbound web requests route through this module.
"""
import asyncio
import hashlib
import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, Optional, Union

logger = logging.getLogger("claire.connectors.web_fetcher")

# Cache directory
CACHE_DIR = Path("data/cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Rate limiting state
_rate_limits: Dict[str, float] = {}
_MIN_INTERVAL = 1.0  # seconds between requests per domain


class WebFetcherError(Exception):
    """Raised when a web fetch fails after all retries."""
    pass


class WebFetcher:
    """
    Centralized HTTP client — every connector routes requests through here.
    Features:
      - Automatic retry with exponential backoff
      - Per-domain rate limiting
      - Response caching with TTL
      - Graceful degradation (returns None on failure, connector falls back)
    """

    def __init__(self, cache_ttl: int = 3600, max_retries: int = 3,
                 timeout: int = 30, user_agent: str = "Claire-Syntalion/4.2"):
        self.cache_ttl = cache_ttl
        self.max_retries = max_retries
        self.timeout = timeout
        self.user_agent = user_agent
        self._session = None

    def _get_cache_key(self, url: str, params: Optional[Dict] = None) -> str:
        raw = url + json.dumps(params or {}, sort_keys=True)
        return hashlib.sha256(raw.encode()).hexdigest()

    def _get_cached(self, cache_key: str) -> Optional[Dict]:
        cache_file = CACHE_DIR / f"{cache_key}.json"
        if cache_file.exists():
            try:
                data = json.loads(cache_file.read_text(encoding="utf-8"))
                if time.time() - data.get("_cached_at", 0) < self.cache_ttl:
                    logger.debug(f"Cache hit: {cache_key[:12]}...")
                    return data.get("payload")
            except (json.JSONDecodeError, KeyError):
                cache_file.unlink(missing_ok=True)
        return None

    def _set_cached(self, cache_key: str, payload: Any) -> None:
        cache_file = CACHE_DIR / f"{cache_key}.json"
        try:
            cache_file.write_text(json.dumps({
                "_cached_at": time.time(),
                "payload": payload
            }, default=str), encoding="utf-8")
        except Exception as e:
            logger.warning(f"Cache write failed: {e}")

    def _rate_limit(self, domain: str) -> None:
        now = time.time()
        last = _rate_limits.get(domain, 0)
        wait = _MIN_INTERVAL - (now - last)
        if wait > 0:
            time.sleep(wait)
        _rate_limits[domain] = time.time()

    def _extract_domain(self, url: str) -> str:
        from urllib.parse import urlparse
        return urlparse(url).netloc

    def get(self, url: str, params: Optional[Dict] = None,
            headers: Optional[Dict] = None,
            use_cache: bool = True) -> Optional[Dict[str, Any]]:
        """
        Synchronous GET request with caching and retry.
        Returns parsed JSON dict or None on failure.
        """
        import urllib.request
        import urllib.parse
        import urllib.error
        import ssl

        # Check cache first
        cache_key = self._get_cache_key(url, params)
        if use_cache:
            cached = self._get_cached(cache_key)
            if cached is not None:
                return cached

        # Rate limit
        domain = self._extract_domain(url)
        self._rate_limit(domain)

        # Build URL with params
        if params:
            query = urllib.parse.urlencode(params)
            full_url = f"{url}?{query}" if "?" not in url else f"{url}&{query}"
        else:
            full_url = url

        # Default headers
        req_headers = {
            "User-Agent": self.user_agent,
            "Accept": "application/json",
        }
        if headers:
            req_headers.update(headers)

        # SSL context (allow self-signed for dev)
        ctx = ssl.create_default_context()

        # Retry loop
        last_error = None
        for attempt in range(self.max_retries):
            try:
                req = urllib.request.Request(full_url, headers=req_headers)
                with urllib.request.urlopen(req, timeout=self.timeout, context=ctx) as resp:
                    raw = resp.read().decode("utf-8")
                    try:
                        data = json.loads(raw)
                    except json.JSONDecodeError:
                        data = {"raw_text": raw, "content_type": resp.headers.get("Content-Type")}

                    if use_cache:
                        self._set_cached(cache_key, data)

                    logger.info(f"WebFetcher GET {domain} OK (attempt {attempt+1})")
                    return data

            except urllib.error.HTTPError as e:
                last_error = e
                if e.code in (429, 503):
                    wait = (2 ** attempt) * 2
                    logger.warning(f"Rate limited ({e.code}), waiting {wait}s...")
                    time.sleep(wait)
                    continue
                elif e.code in (401, 403):
                    logger.error(f"Auth error {e.code} for {domain}")
                    return None
                else:
                    logger.warning(f"HTTP {e.code} from {domain} (attempt {attempt+1})")

            except Exception as e:
                last_error = e
                wait = (2 ** attempt)
                logger.warning(f"Request failed: {e} — retry in {wait}s")
                time.sleep(wait)

        logger.error(f"WebFetcher exhausted retries for {domain}: {last_error}")
        return None

    def post(self, url: str, payload: Optional[Dict] = None,
             headers: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """
        Synchronous POST request (no caching).
        """
        import urllib.request
        import ssl

        domain = self._extract_domain(url)
        self._rate_limit(domain)

        req_headers = {
            "User-Agent": self.user_agent,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        if headers:
            req_headers.update(headers)

        body = json.dumps(payload or {}).encode("utf-8")
        ctx = ssl.create_default_context()

        last_error = None
        for attempt in range(self.max_retries):
            try:
                req = urllib.request.Request(url, data=body, headers=req_headers, method="POST")
                with urllib.request.urlopen(req, timeout=self.timeout, context=ctx) as resp:
                    raw = resp.read().decode("utf-8")
                    try:
                        return json.loads(raw)
                    except json.JSONDecodeError:
                        return {"raw_text": raw}
            except Exception as e:
                last_error = e
                time.sleep(2 ** attempt)

        logger.error(f"WebFetcher POST exhausted retries for {domain}: {last_error}")
        return None

    def clear_cache(self, max_age: Optional[int] = None) -> int:
        """Remove cached responses. If max_age given, only remove entries older than max_age seconds."""
        removed = 0
        for f in CACHE_DIR.glob("*.json"):
            try:
                if max_age:
                    data = json.loads(f.read_text())
                    if time.time() - data.get("_cached_at", 0) < max_age:
                        continue
                f.unlink()
                removed += 1
            except Exception:
                pass
        return removed


# Module-level singleton
_fetcher: Optional[WebFetcher] = None


def get_fetcher(**kwargs) -> WebFetcher:
    """Get or create the global WebFetcher instance."""
    global _fetcher
    if _fetcher is None:
        _fetcher = WebFetcher(**kwargs)
    return _fetcher
