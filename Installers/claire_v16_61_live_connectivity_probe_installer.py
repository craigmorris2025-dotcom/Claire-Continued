from pathlib import Path

ROOT = Path.cwd()

def write(path, content):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print(f"Wrote {path}")

write("src/claire/live/live_connectivity_probe.py", r"""
from __future__ import annotations

import socket
from datetime import datetime, timezone
from typing import Any, Dict


DEFAULT_PROBE_HOSTS = [
    ("example.com", 80),
    ("www.google.com", 80),
]


def probe_live_connectivity(timeout_seconds: float = 3.0) -> Dict[str, Any]:
    results = []

    for host, port in DEFAULT_PROBE_HOSTS:
        try:
            with socket.create_connection((host, port), timeout=timeout_seconds):
                results.append({
                    "host": host,
                    "port": port,
                    "status": "reachable",
                })
        except Exception as exc:
            results.append({
                "host": host,
                "port": port,
                "status": "unreachable",
                "error": str(exc),
            })

    reachable_count = len([r for r in results if r["status"] == "reachable"])

    return {
        "version": "16.61",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "online_available" if reachable_count else "offline_or_blocked",
        "reachable_count": reachable_count,
        "probe_count": len(results),
        "note": "Connectivity probe only. No unrestricted fetching or scoring is performed.",
        "results": results,
    }
""")

print("v16.61 live connectivity probe installed.")
