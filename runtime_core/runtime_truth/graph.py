from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any, Dict, List

VERSION = "v19.84.1"

STAGE_NAMES = [
    "Signal Ingestion", "Signal Normalization", "Source Validation & Weighting",
    "Context Expansion", "Signal Consolidation", "Entity Extraction",
    "Relationship Mapping", "Trend Discovery", "Cluster Formation",
    "Insight / Thesis Structuring", "Gap Detection", "Gap Qualification",
    "Discovery Generation", "Breakthrough Identification & Classification",
    "Advancement Path Selection", "Auto Invention / Solution Generation",
    "Solution Structuring", "Buildability Assessment", "Viability Assessment",
    "Manufacturability / Deployability Assessment", "Feasibility Validation",
    "Design Portal Output / Blueprints / Specs", "Market Positioning",
    "Moat & Differentiation", "Business Model & Value Capture", "Competitor Analysis",
    "Portfolio Creation / Optimization", "Acquirer Identification",
    "Acquisition Fit & Rationale", "Final Package Construction",
]

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def count_terms(text: str, terms: List[str]) -> int:
    low = text.lower()
    return sum(1 for term in terms if term in low)

def stage_rows(active: List[int]) -> Dict[str, Any]:
    active_set = set(active)
    selected = []
    skipped = []
    for index, name in enumerate(STAGE_NAMES, start=1):
        row = {"stage": index, "name": name}
        if index in active_set:
            row["status"] = "selected"
            selected.append(row)
        else:
            row["status"] = "skipped_by_route"
            row["reason"] = "not required for selected route"
            skipped.append(row)
    return {"selected": selected, "skipped_by_route": skipped}

def decide_runtime_route(raw_input: str, mode: str = "deterministic") -> Dict[str, Any]:
    text = (raw_input or "").strip()
    run_id = "truth-" + hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]

    if not text:
        rows = stage_rows([])
        return {
            "version": VERSION,
            "run_id": run_id,
            "status": "blocked",
            "mode": mode,
            "route": None,
            "terminal_state": "insufficient_data",
            "governance_state": "blocked",
            "confidence": 0.0,
            "selected_route_stages": rows["selected"],
            "skipped_by_route": rows["skipped_by_route"],
            "evidence": {"input_length": 0, "reason": "raw_input missing"},
            "created_at": utc_now(),
        }

    breakthrough = count_terms(text, [
        "breakthrough", "prototype", "patent", "novel", "invention", "blueprint",
        "manufacturability", "buildability", "feasibility", "autonomous",
        "system replacement", "design portal", "technical constraint"
    ])
    acquisition = count_terms(text, [
        "acquisition", "acquirer", "buyer", "m&a", "deal", "strategic fit",
        "moat", "value capture", "commercialization"
    ])
    portfolio = count_terms(text, [
        "portfolio", "risk", "exposure", "allocation", "optimization", "market",
        "trend", "thesis", "sector", "opportunity", "repricing"
    ])

    if breakthrough >= max(acquisition, portfolio) and breakthrough >= 2:
        route = "breakthrough_design"
        active = list(range(1, 31))
        terminal_state = "design_output_ready"
    elif acquisition >= max(breakthrough, portfolio) and acquisition >= 2:
        route = "acquisition_package"
        active = [1,2,3,4,5,6,7,8,9,10,11,12,23,24,25,26,28,29,30]
        terminal_state = "acquisition_ready"
    else:
        route = "portfolio_creation_optimization"
        active = [1,2,3,4,5,6,7,8,9,10,23,26,27]
        terminal_state = "portfolio_optimization_ready"

    rows = stage_rows(active)
    signal_total = max(1, breakthrough + acquisition + portfolio)
    confidence = round(min(0.91, 0.44 + (signal_total * 0.045)), 4)

    return {
        "version": VERSION,
        "run_id": run_id,
        "status": "success",
        "mode": mode,
        "route": route,
        "terminal_state": terminal_state,
        "governance_state": "ready",
        "confidence": confidence,
        "selected_route_stages": rows["selected"],
        "skipped_by_route": rows["skipped_by_route"],
        "evidence": {
            "input_length": len(text),
            "route_signals": {
                "breakthrough": breakthrough,
                "acquisition": acquisition,
                "portfolio": portfolio
            },
            "truthful_note": "This route decision is a runtime truth contract layer; deeper evaluation output remains owned by the existing evaluator."
        },
        "created_at": utc_now(),
    }
