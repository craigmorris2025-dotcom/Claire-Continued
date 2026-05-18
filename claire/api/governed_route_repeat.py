from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Mapping

from claire.api.governed_discovery_candidates import build_route_discovery_candidates
from claire.api.governed_useful_outputs import build_useful_output_candidate
from claire.api.governed_review_queue import enqueue_for_review

ROUTES = ("portfolio", "breakthrough", "design")

def build_route_repeat_payload(evidence_basket: Mapping[str, Any], extraction: Mapping[str, Any] | None = None, *, store_path: Path | None = None) -> Dict[str, Any]:
    discoveries = build_route_discovery_candidates(evidence_basket, extraction, routes=ROUTES)
    outputs = {route: build_useful_output_candidate(candidate) for route, candidate in discoveries.items()}
    review_items = {route: enqueue_for_review(output, store_path=store_path, operator="route_repeat") for route, output in outputs.items()}
    return {
        "route_repeat_version": "S89",
        "status": "route_repeat_ready",
        "routes": list(ROUTES),
        "discovery_candidates": discoveries,
        "useful_output_candidates": outputs,
        "review_items": review_items,
        "authority": {
            "runtime_truth_write": "blocked",
            "autonomous_execution": "blocked",
            "manual_review_required": True,
        },
    }
