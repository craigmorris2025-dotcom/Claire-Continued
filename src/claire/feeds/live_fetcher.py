"""
Safe Public Metadata Fetcher.

v5.46:
- Controlled fetcher for public metadata only.
- Disabled by default unless CLAIRE_ENABLE_LIVE_FEEDS=1.
- No authentication, no private-network targets, limited bytes, limited timeout.
"""

from __future__ import annotations

from typing import Any, Dict
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import html
import ipaddress
import os
import re
import socket


class SafePublicMetadataFetcher:
    """Fetch title/meta-description only from public HTTP(S) pages when explicitly enabled."""

    MAX_BYTES = 200_000
    TIMEOUT_SECONDS = 8

    def live_enabled(self) -> bool:
        return os.environ.get("CLAIRE_ENABLE_LIVE_FEEDS", "").strip() == "1"

    def status(self) -> Dict[str, Any]:
        return {
            "status": "success",
            "fetcher": "safe_public_metadata_fetcher",
            "live_enabled": self.live_enabled(),
            "enable_variable": "CLAIRE_ENABLE_LIVE_FEEDS=1",
            "limits": {
                "max_bytes": self.MAX_BYTES,
                "timeout_seconds": self.TIMEOUT_SECONDS,
                "allowed_schemes": ["http", "https"],
                "private_network_blocked": True,
                "auth_required": False,
            },
        }

    def fetch_metadata(self, url: str) -> Dict[str, Any]:
        if not self.live_enabled():
            return {
                "status": "disabled",
                "url": url,
                "title": "",
                "snippet": "",
                "warning": "Live feeds are disabled. Set CLAIRE_ENABLE_LIVE_FEEDS=1 to enable controlled public metadata fetches.",
            }

        validation = self._validate_url(url)
        if not validation["allowed"]:
            return {
                "status": "blocked",
                "url": url,
                "title": "",
                "snippet": "",
                "warning": validation["reason"],
            }

        try:
            request = Request(
                url,
                headers={
                    "User-Agent": "ClaireLocalResearchBot/0.1 (+local-user-controlled; metadata-only)",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.1",
                },
            )
            with urlopen(request, timeout=self.TIMEOUT_SECONDS) as response:
                content_type = response.headers.get("Content-Type", "")
                raw = response.read(self.MAX_BYTES)
            text = raw.decode("utf-8", errors="ignore")
            return {
                "status": "success",
                "url": url,
                "title": self._extract_title(text),
                "snippet": self._extract_description(text),
                "content_type": content_type,
                "bytes_read": len(raw),
            }
        except HTTPError as exc:
            return {"status": "error", "url": url, "title": "", "snippet": "", "warning": f"HTTP error: {exc.code}"}
        except URLError as exc:
            return {"status": "error", "url": url, "title": "", "snippet": "", "warning": f"URL error: {exc.reason}"}
        except Exception as exc:
            return {"status": "error", "url": url, "title": "", "snippet": "", "warning": str(exc)}

    def _validate_url(self, url: str) -> Dict[str, Any]:
        parsed = urlparse((url or "").strip())
        if parsed.scheme not in {"http", "https"}:
            return {"allowed": False, "reason": "Only http/https public URLs are allowed."}
        if not parsed.hostname:
            return {"allowed": False, "reason": "URL hostname is missing."}
        host = parsed.hostname.lower()
        if host in {"localhost", "127.0.0.1", "0.0.0.0"}:
            return {"allowed": False, "reason": "Local/private hostnames are blocked."}

        try:
            addresses = socket.getaddrinfo(host, None)
            for item in addresses:
                ip = ipaddress.ip_address(item[4][0])
                if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_reserved:
                    return {"allowed": False, "reason": "Private, local, reserved, or multicast network targets are blocked."}
        except Exception:
            return {"allowed": False, "reason": "Could not validate hostname safely."}

        return {"allowed": True, "reason": "allowed"}

    def _extract_title(self, text: str) -> str:
        match = re.search(r"<title[^>]*>(.*?)</title>", text, flags=re.IGNORECASE | re.DOTALL)
        if not match:
            return ""
        return self._clean(match.group(1))[:240]

    def _extract_description(self, text: str) -> str:
        patterns = [
            r'<meta[^>]+name=["\']description["\'][^>]+content=["\'](.*?)["\']',
            r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\'](.*?)["\']',
            r'<meta[^>]+content=["\'](.*?)["\'][^>]+name=["\']description["\']',
            r'<meta[^>]+content=["\'](.*?)["\'][^>]+property=["\']og:description["\']',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
            if match:
                return self._clean(match.group(1))[:500]
        return ""

    def _clean(self, value: str) -> str:
        value = html.unescape(value or "")
        value = re.sub(r"\s+", " ", value).strip()
        return value
