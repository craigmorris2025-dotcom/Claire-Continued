#!/usr/bin/env python3
from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()

ROUTES = {
    "portfolio": ["portfolio", "optimization", "market", "risk", "positioning"],
    "breakthrough": ["breakthrough", "gap", "classification", "path_selection"],
    "design": ["design", "architecture", "blueprint", "implementation"],
    "acquisition": ["acquisition", "acquirer", "package", "deal"],
}

def main() -> int:
    src = ROOT / "src" / "claire"
    route_hits = {route: [] for route in ROUTES}

    if src.exists():
        for path in src.rglob("*.py"):
            text = path.read_text(encoding="utf-8", errors="ignore").lower()
            rel = str(path.relative_to(ROOT)).replace("\\", "/")
            for route, terms in ROUTES.items():
                hits = [t for t in terms if t in text or t in rel.lower()]
                if hits:
                    route_hits[route].append({"path": rel, "hits": hits})

    route_scores = {
        route: min(100, len(items) * 5)
        for route, items in route_hits.items()
    }

    payload = {
        "upgrade": "portfolio_breakthrough_routing",
        "version": "v16.44",
        "created_at": datetime.now().isoformat(),
        "status": "available",
        "route_scores": route_scores,
        "route_hits": {route: items[:100] for route, items in route_hits.items()},
        "routing_policy": {
            "default_route": "portfolio",
            "breakthrough_is_conditional": True,
            "design_is_conditional": True,
            "acquisition_package_is_terminal_route": True,
        },
        "recommendations": [
            "keep portfolio route as default practical output path",
            "trigger breakthrough only with qualified gap/advancement evidence",
            "trigger design only after advancement path requires build/spec output",
            "keep acquisition package terminal and evidence-backed",
        ],
    }

    out_dir = ROOT / "data" / "intelligence"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "portfolio_breakthrough_routing.json"
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(json.dumps({"upgrade": payload["upgrade"], "route_scores": payload["route_scores"]}, indent=2))
    print(f"\nPortfolio breakthrough routing written: {out}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
