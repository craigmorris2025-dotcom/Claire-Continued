from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict
from uuid import uuid4

from fastapi import APIRouter


router = APIRouter(tags=["Claire Source Universes"])

ROOT = Path(__file__).resolve()
for parent in ROOT.parents:
    if (parent / "pyproject.toml").exists() or (parent / "main.py").exists():
        PROJECT_ROOT = parent
        break
else:
    PROJECT_ROOT = Path.cwd()

SOURCE_DIR = PROJECT_ROOT / "data" / "source_universes"


DEFAULT_UNIVERSES = [
    {
        "universe_id": "market_intelligence",
        "label": "Market Intelligence",
        "purpose": "Monitor markets, sectors, companies, trends, weak signals, and portfolio-relevant movements.",
        "governance": "read_only_governed_sources",
        "status": "configured",
        "allowed_source_types": ["market_data", "company_data", "sector_data", "news", "filings", "research"],
    },
    {
        "universe_id": "technology_breakthroughs",
        "label": "Technology Breakthroughs",
        "purpose": "Monitor emerging technologies, scientific breakthroughs, invention opportunities, and design-route candidates.",
        "governance": "read_only_governed_sources",
        "status": "configured",
        "allowed_source_types": ["research", "patents", "technical_docs", "papers", "standards", "engineering_signals"],
    },
    {
        "universe_id": "existing_systems",
        "label": "Existing Systems",
        "purpose": "Monitor systems that can be decomposed, improved, redesigned, or replaced by superior Claire-generated systems.",
        "governance": "operator_supplied_or_governed_ingestion",
        "status": "configured",
        "allowed_source_types": ["uploaded_docs", "system_maps", "product_docs", "architecture_docs", "process_docs"],
    },
    {
        "universe_id": "acquisition_targets",
        "label": "Acquisition Targets",
        "purpose": "Monitor acquirer fit, category creation, strategic value, marketability, and package-readiness signals.",
        "governance": "read_only_governed_sources",
        "status": "configured",
        "allowed_source_types": ["company_data", "market_data", "M&A_signals", "competitive_intelligence"],
    },
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, payload: Dict[str, Any]) -> Dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


def read_json(path: Path, fallback: Dict[str, Any]) -> Dict[str, Any]:
    if not path.exists():
        return fallback
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback


def universe_path(universe_id: str) -> Path:
    return SOURCE_DIR / f"{universe_id}.json"


def ensure_universe_index() -> Dict[str, Any]:
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    index_path = SOURCE_DIR / "universe_index.json"

    if not index_path.exists():
        universes = []
        for universe in DEFAULT_UNIVERSES:
            payload = dict(universe)
            payload["created_at"] = utc_now()
            payload["updated_at"] = payload["created_at"]
            payload["backend_owns_truth"] = True
            write_json(universe_path(payload["universe_id"]), payload)
            universes.append({
                "universe_id": payload["universe_id"],
                "label": payload["label"],
                "purpose": payload["purpose"],
                "status": payload["status"],
            })
        return write_json(index_path, {
            "status": "configured",
            "updated_at": utc_now(),
            "backend_owns_truth": True,
            "universes": universes,
        })

    index = read_json(index_path, {"universes": []})
    known = {item.get("universe_id") for item in index.get("universes", [])}
    changed = False
    for universe in DEFAULT_UNIVERSES:
        if universe["universe_id"] not in known:
            payload = dict(universe)
            payload["created_at"] = utc_now()
            payload["updated_at"] = payload["created_at"]
            payload["backend_owns_truth"] = True
            write_json(universe_path(payload["universe_id"]), payload)
            index.setdefault("universes", []).append({
                "universe_id": payload["universe_id"],
                "label": payload["label"],
                "purpose": payload["purpose"],
                "status": payload["status"],
            })
            changed = True
    if changed:
        index["updated_at"] = utc_now()
        index["backend_owns_truth"] = True
        write_json(index_path, index)
    return index


def create_probe(universe_id: str, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    ensure_universe_index()
    universe = read_json(universe_path(universe_id), {})
    if not universe:
        return {
            "status": "missing_universe",
            "universe_id": universe_id,
            "reason": "Source universe has not been configured.",
            "backend_owns_truth": True,
        }

    payload = payload or {}
    probe_id = "probe_" + datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S") + "_" + uuid4().hex[:8]
    probe = {
        "probe_id": probe_id,
        "universe_id": universe_id,
        "created_at": utc_now(),
        "status": "recorded",
        "mode": payload.get("mode", "governed_read_only_probe"),
        "query": payload.get("query"),
        "source_types": payload.get("source_types", universe.get("allowed_source_types", [])),
        "result": "probe_request_recorded_waiting_for_live_provider_or_source_adapter",
        "evidence_refs": [],
        "candidate_counts": {
            "signals": 0,
            "discoveries": 0,
            "breakthroughs": 0,
            "portfolios": 0,
            "designs": 0,
            "packages": 0,
        },
        "guardrails": [
            "read_only",
            "source_trust_required",
            "no_runtime_truth_promotion_without_review",
            "no_fake_results",
        ],
        "backend_owns_truth": True,
    }
    write_json(SOURCE_DIR / f"{universe_id}_probe.json", probe)
    write_json(SOURCE_DIR / "probes" / f"{probe_id}.json", probe)
    return probe


@router.get("/universes")
async def universes() -> Dict[str, Any]:
    return ensure_universe_index()


@router.get("/universes/{universe_id}")
async def universe(universe_id: str) -> Dict[str, Any]:
    ensure_universe_index()
    return read_json(universe_path(universe_id), {
        "status": "missing_universe",
        "universe_id": universe_id,
        "backend_owns_truth": True,
    })


@router.post("/universes/{universe_id}/probe")
async def probe_universe(universe_id: str, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    return create_probe(universe_id, payload)
