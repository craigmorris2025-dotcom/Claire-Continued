from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping

from claire.api.governed_s92_s98_cockpit_contracts import (
    build_canonical_s85_s91_panel,
    build_review_queue_status,
    build_export_manifest,
    build_cockpit_evidence_output_card,
    build_end_to_end_cockpit_demo_proof,
)

LOCKS = {
    "backend_owns_truth": True,
    "cockpit_presentation_only": True,
    "runtime_truth_mutation_blocked": True,
    "runtime_truth_write_blocked": True,
    "automatic_updates_blocked": True,
    "autonomous_execution_blocked": True,
    "live_web_execution_blocked_unless_explicitly_gated": True,
    "manual_promotion_mandatory": True,
    "quarantine_mandatory": True,
    "continuous_crawling_blocked": True,
}

SPINE_STAGES = [
    "governed_intake",
    "quarantine",
    "evidence_basket",
    "extraction",
    "discovery_candidate",
    "useful_output_candidate",
    "review_queue",
    "operator_decision",
    "export_manifest",
    "route_state",
    "cockpit_read_model",
    "system_proof",
]

ROUTES = ["portfolio", "breakthrough", "design"]

def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _stable_id(prefix: str, payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
    return f"{prefix}_{hashlib.sha256(encoded).hexdigest()[:16]}"

def default_spine_evidence() -> Dict[str, Any]:
    return {
        "basket_id": "s106_spine_basket",
        "trust_score": 0.84,
        "evidence_items": [
            {"evidence_id": "s106_ev_001", "title": "Canonical runtime spine readiness signal", "trust_score": 0.84},
        ],
    }

def default_spine_extraction() -> Dict[str, Any]:
    return {
        "extraction_id": "s106_spine_extraction",
        "signals": [
            {"label": "runtime unification signal", "type": "portfolio", "confidence": 0.82},
            {"label": "cockpit convergence signal", "type": "design", "confidence": 0.77},
        ],
    }

def build_canonical_runtime_spine(
    evidence_basket: Mapping[str, Any] | None = None,
    extraction: Mapping[str, Any] | None = None,
    *,
    store_path: Path | None = None,
    export_dir: Path | None = None,
) -> Dict[str, Any]:
    evidence_basket = evidence_basket or default_spine_evidence()
    extraction = extraction or default_spine_extraction()

    panel = build_canonical_s85_s91_panel(evidence_basket, extraction, store_path=store_path, export_dir=export_dir)
    queue = build_review_queue_status(store_path=store_path)
    manifest = build_export_manifest(export_dir=export_dir)
    card = build_cockpit_evidence_output_card(evidence_basket, extraction, store_path=store_path, export_dir=export_dir)
    proof = build_end_to_end_cockpit_demo_proof(evidence_basket, extraction, store_path=store_path, export_dir=export_dir)

    stage_state = {}
    for stage in SPINE_STAGES:
        stage_state[stage] = {
            "stage": stage,
            "status": "available",
            "authority": "backend_owned_read_model",
            "runtime_truth_write": "blocked",
        }

    route_state = {
        route: {
            "route": route,
            "status": "available",
            "operator_review_required": True,
            "runtime_truth_write": "blocked",
        }
        for route in ROUTES
    }

    spine_payload = {
        "created_at": _utc_now(),
        "stage_count": len(SPINE_STAGES),
        "routes": ROUTES,
        "panel_status": panel.get("status"),
        "proof_status": proof.get("status"),
        "review_total": queue.get("total_items", 0),
        "export_count": manifest.get("export_count", 0),
    }

    return {
        "spine_version": "S106",
        "spine_id": _stable_id("spine", spine_payload),
        "status": "runtime_spine_ready" if proof.get("status") == "ready" else "runtime_spine_incomplete",
        "created_at": spine_payload["created_at"],
        "authority_model": {
            "single_runtime_state_authority": True,
            "single_evidence_authority": True,
            "single_route_state_authority": True,
            "cockpit_reads_only": True,
            "backend_owns_truth": True,
        },
        "stage_state": stage_state,
        "route_state": route_state,
        "sources": {
            "proof_panel": panel,
            "review_queue": queue,
            "export_manifest": manifest,
            "cockpit_card": card,
            "end_to_end_proof": proof,
        },
        "locks": dict(LOCKS),
    }

def build_lifecycle_authority_map(spine: Mapping[str, Any] | None = None) -> Dict[str, Any]:
    spine = spine or build_canonical_runtime_spine()
    return {
        "authority_map_version": "S107",
        "status": "authority_map_ready",
        "owners": {
            "runtime_state": "backend",
            "evidence_state": "backend",
            "route_state": "backend",
            "review_decisions": "operator_action_contract",
            "exports": "derived_artifact_writer",
            "cockpit": "presentation_only",
        },
        "blocked_authorities": {
            "runtime_truth_write": True,
            "runtime_truth_mutation": True,
            "automatic_updates": True,
            "autonomous_execution": True,
            "continuous_crawling": True,
        },
        "spine_id": spine.get("spine_id"),
        "locks": dict(LOCKS),
    }

def build_evidence_to_lifecycle_bridge(spine: Mapping[str, Any] | None = None) -> Dict[str, Any]:
    spine = spine or build_canonical_runtime_spine()
    mapping = [
        {"evidence_slice": "quarantined_result", "lifecycle_stage": "Signal Ingestion", "authority": "read_only"},
        {"evidence_slice": "evidence_basket", "lifecycle_stage": "Source Validation & Weighting", "authority": "read_only"},
        {"evidence_slice": "extraction", "lifecycle_stage": "Entity Extraction", "authority": "read_only"},
        {"evidence_slice": "discovery_candidate", "lifecycle_stage": "Discovery Generation", "authority": "review_required"},
        {"evidence_slice": "useful_output_candidate", "lifecycle_stage": "Advancement Path Selection", "authority": "review_required"},
        {"evidence_slice": "reviewed_export", "lifecycle_stage": "Final Package Construction", "authority": "derived_artifact_only"},
    ]
    return {
        "bridge_version": "S108",
        "status": "evidence_lifecycle_bridge_ready",
        "spine_id": spine.get("spine_id"),
        "mapping": mapping,
        "runtime_truth_write": "blocked",
        "locks": dict(LOCKS),
    }

def build_cockpit_operations_fetch_map(spine: Mapping[str, Any] | None = None) -> Dict[str, Any]:
    spine = spine or build_canonical_runtime_spine()
    return {
        "fetch_map_version": "S109",
        "status": "cockpit_operations_fetch_map_ready",
        "read_only": True,
        "spine_id": spine.get("spine_id"),
        "fetch_map": {
            "runtime_spine": "/api/governed/runtime-spine",
            "authority_map": "/api/governed/runtime-spine/authority-map",
            "evidence_lifecycle_bridge": "/api/governed/runtime-spine/evidence-bridge",
            "operations_fetch_map": "/api/governed/runtime-spine/fetch-map",
            "operator_review_queue": "/api/governed/operator/review-queue",
            "operator_export_manifest": "/api/governed/operator/export-manifest",
            "operator_api_demo_proof": "/api/governed/operator/api-demo-proof",
        },
        "locks": dict(LOCKS),
    }

def build_operator_control_read_model(spine: Mapping[str, Any] | None = None) -> Dict[str, Any]:
    spine = spine or build_canonical_runtime_spine()
    sources = spine.get("sources", {}) if isinstance(spine.get("sources"), Mapping) else {}
    queue = sources.get("review_queue", {}) if isinstance(sources.get("review_queue"), Mapping) else {}
    manifest = sources.get("export_manifest", {}) if isinstance(sources.get("export_manifest"), Mapping) else {}
    return {
        "control_model_version": "S110",
        "status": "operator_control_read_model_ready",
        "review_queue_total": queue.get("total_items", 0),
        "export_count": manifest.get("export_count", 0),
        "available_operator_actions": ["approve", "reject", "archive", "export_only"],
        "action_authority": "manual_operator_only",
        "runtime_truth_write": "blocked",
        "locks": dict(LOCKS),
    }

def build_governed_search_control_read_model(spine: Mapping[str, Any] | None = None) -> Dict[str, Any]:
    spine = spine or build_canonical_runtime_spine()
    return {
        "search_control_model_version": "S111",
        "status": "governed_search_control_read_model_ready",
        "manual_probe_required": True,
        "quarantine_required": True,
        "manual_promotion_required": True,
        "continuous_crawling": "blocked",
        "automatic_updates": "blocked",
        "runtime_truth_write": "blocked",
        "spine_id": spine.get("spine_id"),
        "locks": dict(LOCKS),
    }

def build_dashboard_managed_demo(spine: Mapping[str, Any] | None = None) -> Dict[str, Any]:
    spine = spine or build_canonical_runtime_spine()
    authority = build_lifecycle_authority_map(spine)
    bridge = build_evidence_to_lifecycle_bridge(spine)
    fetch_map = build_cockpit_operations_fetch_map(spine)
    control = build_operator_control_read_model(spine)
    search = build_governed_search_control_read_model(spine)

    ready = (
        spine.get("status") == "runtime_spine_ready"
        and authority.get("status") == "authority_map_ready"
        and bridge.get("status") == "evidence_lifecycle_bridge_ready"
        and fetch_map.get("status") == "cockpit_operations_fetch_map_ready"
        and control.get("status") == "operator_control_read_model_ready"
        and search.get("status") == "governed_search_control_read_model_ready"
    )

    return {
        "dashboard_demo_version": "S112",
        "status": "dashboard_managed_demo_ready" if ready else "dashboard_managed_demo_incomplete",
        "spine": spine,
        "authority_map": authority,
        "evidence_bridge": bridge,
        "fetch_map": fetch_map,
        "operator_control": control,
        "governed_search_control": search,
        "locks": dict(LOCKS),
    }
