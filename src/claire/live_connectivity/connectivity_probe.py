from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Dict
from urllib.request import Request, urlopen

class ConnectivityProbe:
    def probe(self, url: str = "https://example.com", timeout: int = 8) -> Dict[str, Any]:
        started = datetime.now(timezone.utc).isoformat()
        try:
            req = Request(url, headers={"User-Agent": "ClaireConnectivityProbe/16.0"})
            with urlopen(req, timeout=timeout) as response:
                return {
                    "record_type": "connectivity_probe",
                    "url": url,
                    "status": "success",
                    "http_status": getattr(response, "status", None),
                    "started_at_utc": started,
                    "completed_at_utc": datetime.now(timezone.utc).isoformat(),
                }
        except Exception as exc:
            return {
                "record_type": "connectivity_probe",
                "url": url,
                "status": "failed",
                "error": str(exc),
                "started_at_utc": started,
                "completed_at_utc": datetime.now(timezone.utc).isoformat(),
            }
