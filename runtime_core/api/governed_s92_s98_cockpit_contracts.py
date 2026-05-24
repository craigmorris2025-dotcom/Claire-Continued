from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Mapping

from runtime_core.api.governed_s85_s91_payload import build_s85_s91_payload
from runtime_core.api.governed_review_queue import decide_review_item, enqueue_for_review, list_review_queue
from runtime_core.api.governed_reviewed_exports import export_reviewed_output
from runtime_core.api.governed_demo_run import build_demo_contract
from runtime_core.api.governed_route_repeat import ROUTES

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

def _default_export_dir(root: Path | None = None) -> Path:
    base = root or Path.cwd()
    return base / "exports" / "governed_outputs"

def _safe_json(path: Path) -> Dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return payload if isinstance(payload, dict) else None

def build_canonical_s85_s91_panel(
    evidence_basket: Mapping[str, Any] | None = None,
    extraction: Mapping[str, Any] | None = None,
    *,
    store_path: Path | None = None,
    export_dir: Path | None = None,
) -> Dict[str, Any]:
    proof_payload = build_s85_s91_payload(evidence_basket, extraction, store_path=store_path, export_dir=export_dir)
    proof = proof_payload.get("proof", {})
    demo = proof.get("demo", {}) if isinstance(proof, Mapping) else {}
    useful = demo.get("useful_output_candidate") if isinstance(demo, Mapping) else {}
    if not isinstance(useful, Mapping):
        useful = {}
    return {
        "panel_version": "S92",
        "panel_id": "governed_evidence_to_output",
        "title": "Governed Evidence To Output Proof",
        "status": proof_payload.get("status"),
        "read_only": True,
        "presentation_only": True,
        "proof_status": proof_payload.get("status"),
        "headline": useful.get("headline"),
        "route": useful.get("route"),
        "export": demo.get("export") if isinstance(demo, Mapping) else None,
        "proof_chain": proof.get("proof_chain") if isinstance(proof, Mapping) else None,
        "locks": dict(LOCKS),
    }

def build_review_queue_status(*, store_path: Path | None = None) -> Dict[str, Any]:
    store = list_review_queue(store_path=store_path)
    queue = store.get("queue", []) if isinstance(store, Mapping) else []
    decisions = store.get("decisions", []) if isinstance(store, Mapping) else []
    counts = {"pending_review": 0, "approved": 0, "rejected": 0, "archived": 0, "export_only": 0}
    for item in queue:
        if isinstance(item, Mapping):
            status = str(item.get("status") or "pending_review")
            counts[status] = counts.get(status, 0) + 1
    return {
        "endpoint_contract_version": "S93",
        "status": "review_queue_available",
        "read_only": True,
        "counts": counts,
        "total_items": len(queue),
        "total_decisions": len(decisions),
        "items": queue,
        "locks": dict(LOCKS),
    }

def build_export_manifest(*, export_dir: Path | None = None) -> Dict[str, Any]:
    directory = export_dir or _default_export_dir()
    items = []
    if directory.exists():
        for path in sorted(directory.glob("*.json")):
            payload = _safe_json(path)
            if payload is None:
                continue
            audit = payload.get("audit") if isinstance(payload.get("audit"), Mapping) else {}
            items.append({
                "filename": path.name,
                "path": str(path),
                "review_item_id": payload.get("review_item_id"),
                "route": payload.get("route"),
                "headline": payload.get("headline"),
                "decision_status": payload.get("decision_status"),
                "export_version": payload.get("export_version"),
                "runtime_truth_write": audit.get("runtime_truth_write"),
            })
    return {
        "endpoint_contract_version": "S94",
        "status": "export_manifest_available",
        "read_only": True,
        "export_count": len(items),
        "exports": items,
        "locks": dict(LOCKS),
    }

def build_cockpit_evidence_output_card(
    evidence_basket: Mapping[str, Any] | None = None,
    extraction: Mapping[str, Any] | None = None,
    *,
    store_path: Path | None = None,
    export_dir: Path | None = None,
) -> Dict[str, Any]:
    panel = build_canonical_s85_s91_panel(evidence_basket, extraction, store_path=store_path, export_dir=export_dir)
    export = panel.get("export") if isinstance(panel.get("export"), Mapping) else {}
    return {
        "card_version": "S95",
        "card_id": "governed-output-proof-card",
        "status": "ready" if panel.get("proof_status") == "ready" else "not_ready",
        "title": "Governed Output Proof",
        "headline": panel.get("headline") or "No reviewed output available",
        "route": panel.get("route"),
        "export_status": export.get("status"),
        "export_path": export.get("path"),
        "proof_chain": panel.get("proof_chain"),
        "read_only": True,
        "presentation_only": True,
        "locks": dict(LOCKS),
    }

def perform_operator_review_action(
    review_item_id: str,
    action: str,
    *,
    store_path: Path | None = None,
    export_dir: Path | None = None,
    operator: str = "operator",
    note: str = "",
) -> Dict[str, Any]:
    normalized = action.strip().lower()
    if normalized == "approve":
        decision = "approved"
    elif normalized == "reject":
        decision = "rejected"
    elif normalized == "archive":
        decision = "archived"
    elif normalized in {"export_only", "export-only"}:
        decision = "export_only"
    else:
        raise ValueError("action must be approve, reject, archive, or export_only")
    decision_payload = decide_review_item(review_item_id, decision, store_path=store_path, operator=operator, note=note)
    exported = None
    if decision in {"approved", "export_only"}:
        exported = export_reviewed_output(decision_payload["review_item"], export_dir=export_dir, export_format="json")
    return {
        "action_contract_version": "S96",
        "status": "action_complete",
        "action": normalized,
        "decision": decision_payload["decision"],
        "review_item": decision_payload["review_item"],
        "export": exported,
        "locks": dict(LOCKS),
    }

def build_route_demo_selector(
    route: str,
    evidence_basket: Mapping[str, Any],
    extraction: Mapping[str, Any] | None = None,
    *,
    store_path: Path | None = None,
    export_dir: Path | None = None,
    approve: bool = False,
) -> Dict[str, Any]:
    normalized = route.strip().lower()
    if normalized not in set(ROUTES):
        raise ValueError(f"route must be one of {sorted(ROUTES)}")
    demo = build_demo_contract(evidence_basket, extraction, route=normalized, store_path=store_path, export_dir=export_dir, approve=approve)
    return {
        "selector_contract_version": "S97",
        "status": "route_demo_selected",
        "selected_route": normalized,
        "approved_for_export": bool(approve),
        "demo": demo,
        "locks": dict(LOCKS),
    }

def build_end_to_end_cockpit_demo_proof(
    evidence_basket: Mapping[str, Any],
    extraction: Mapping[str, Any] | None = None,
    *,
    store_path: Path | None = None,
    export_dir: Path | None = None,
) -> Dict[str, Any]:
    selected = build_route_demo_selector("portfolio", evidence_basket, extraction, store_path=store_path, export_dir=export_dir, approve=True)
    panel = build_canonical_s85_s91_panel(evidence_basket, extraction, store_path=store_path, export_dir=export_dir)
    queue = build_review_queue_status(store_path=store_path)
    manifest = build_export_manifest(export_dir=export_dir)
    card = build_cockpit_evidence_output_card(evidence_basket, extraction, store_path=store_path, export_dir=export_dir)
    selected_demo = selected.get("demo", {}) if isinstance(selected.get("demo"), Mapping) else {}
    selected_export = selected_demo.get("export", {}) if isinstance(selected_demo.get("export"), Mapping) else {}
    proof_ready = (
        selected_export.get("status") == "exported"
        and panel.get("proof_status") == "ready"
        and manifest.get("export_count", 0) >= 1
        and card.get("status") == "ready"
    )
    return {
        "cockpit_demo_proof_version": "S98",
        "status": "ready" if proof_ready else "not_ready",
        "selected_demo": selected,
        "canonical_panel": panel,
        "review_queue_status": queue,
        "export_manifest": manifest,
        "cockpit_card": card,
        "locks": dict(LOCKS),
    }
