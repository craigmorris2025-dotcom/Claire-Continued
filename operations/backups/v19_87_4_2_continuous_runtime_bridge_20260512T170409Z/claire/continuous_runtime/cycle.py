from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

VERSION = "v19.84.2"

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def read_json(path: Path, fallback: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback

def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

def default_status() -> Dict[str, Any]:
    return {
        "runtime": "continuous_intelligence",
        "status": "configured_not_running",
        "mode": "governed_24_7_discovery_monitoring",
        "backend_owns_truth": True,
        "operator_approval_required": True,
        "continuous_objectives": [
            "discover emerging trends",
            "detect gaps",
            "identify breakthrough candidates",
            "identify needed solutions",
            "identify technological solution candidates",
            "identify portfolio opportunities",
            "identify acquisition/package candidates",
            "store lifecycle memory",
            "support recursive self-ingestion"
        ],
        "guardrails": [
            "no uncontrolled web mutation",
            "no automatic active-code updates",
            "no frontend-owned route truth",
            "no fake discoveries",
            "missing evidence enriches before failure",
            "operator review required before promotion"
        ],
        "last_cycle_id": None,
        "last_cycle_at": None,
        "next_cycle_policy": "operator_or_scheduler_triggered",
        "artifact_paths": {
            "status": "data/continuous_runtime/status.json",
            "review_queue": "data/continuous_runtime/review_queue.json",
            "discovery_candidates": "data/continuous_runtime/discovery_candidates.json",
            "breakthrough_candidates": "data/continuous_runtime/breakthrough_candidates.json",
            "portfolio_candidates": "data/continuous_runtime/portfolio_candidates.json",
            "design_candidates": "data/continuous_runtime/design_candidates.json"
        },
        "updated_at": utc_now()
    }

def ensure_continuous_runtime_files(root: Path) -> None:
    data_dir = root / "data" / "continuous_runtime"
    data_dir.mkdir(parents=True, exist_ok=True)
    defaults = {
        "status.json": default_status(),
        "review_queue.json": {"items": [], "policy": "operator_review_required_before_promotion", "updated_at": utc_now()},
        "discovery_candidates.json": {"items": [], "candidate_type": "discovery", "updated_at": utc_now()},
        "breakthrough_candidates.json": {"items": [], "candidate_type": "breakthrough", "updated_at": utc_now()},
        "portfolio_candidates.json": {"items": [], "candidate_type": "portfolio", "updated_at": utc_now()},
        "design_candidates.json": {"items": [], "candidate_type": "design", "updated_at": utc_now()},
        "package_candidates.json": {"items": [], "candidate_type": "package", "updated_at": utc_now()},
    }
    for name, payload in defaults.items():
        path = data_dir / name
        if not path.exists():
            write_json(path, payload)

def term_count(text: str, terms: List[str]) -> int:
    low = text.lower()
    return sum(1 for term in terms if term in low)

def classify_candidate(raw_input: str) -> Dict[str, Any]:
    text = (raw_input or "").strip()
    if not text:
        return {"valid": False, "blocked_reason": "raw_input is required", "candidate_type": None, "route": None, "confidence": 0.0, "signals": {}}
    discovery = term_count(text, ["trend", "gap", "signal", "emerging", "market", "sector", "demand", "weak signal", "opportunity", "pressure"])
    breakthrough = term_count(text, ["breakthrough", "prototype", "patent", "novel", "invention", "autonomous", "manufacturability", "buildability", "feasibility", "design", "constraint"])
    portfolio = term_count(text, ["portfolio", "risk", "exposure", "allocation", "optimization", "asset", "repricing", "credit", "liquidity", "investment"])
    design = term_count(text, ["blueprint", "design portal", "component", "architecture", "system replacement", "engineering", "deployment", "technical"])
    scores = {"discovery": discovery, "breakthrough": breakthrough, "portfolio": portfolio, "design": design}
    candidate_type = max(scores, key=scores.get)
    strongest = scores[candidate_type]
    if strongest <= 0:
        candidate_type = "discovery"
        route = "insufficient_specificity_discovery_review"
        confidence = 0.31
    elif candidate_type == "breakthrough":
        route = "breakthrough_escalation_review"
        confidence = min(0.89, 0.45 + strongest * 0.07)
    elif candidate_type == "design":
        route = "design_route_review"
        confidence = min(0.86, 0.44 + strongest * 0.07)
    elif candidate_type == "portfolio":
        route = "portfolio_intelligence_review"
        confidence = min(0.84, 0.43 + strongest * 0.06)
    else:
        route = "discovery_review"
        confidence = min(0.82, 0.42 + strongest * 0.06)
    return {"valid": True, "candidate_type": candidate_type, "route": route, "confidence": round(confidence, 4), "signals": scores}

def run_once(root: Path, raw_input: str, source: str = "operator_manual") -> Dict[str, Any]:
    ensure_continuous_runtime_files(root)
    data_dir = root / "data" / "continuous_runtime"
    classification = classify_candidate(raw_input)
    cycle_id = "cycle-" + hashlib.sha256((raw_input or "").encode("utf-8")).hexdigest()[:12]
    ts = utc_now()
    status_path = data_dir / "status.json"
    review_path = data_dir / "review_queue.json"
    status = read_json(status_path, default_status())
    review_queue = read_json(review_path, {"items": [], "policy": "operator_review_required_before_promotion"})
    if not classification["valid"]:
        status["status"] = "configured_not_running"
        status["last_cycle_id"] = cycle_id
        status["last_cycle_at"] = ts
        status["last_cycle_result"] = {"status": "blocked", "reason": classification["blocked_reason"], "no_fake_outputs": True}
        status["updated_at"] = ts
        write_json(status_path, status)
        return {"status": "blocked", "cycle_id": cycle_id, "reason": classification["blocked_reason"], "continuous_runtime_status": "configured_not_running", "backend_owns_truth": True}
    candidate_id = "cand-" + hashlib.sha256((raw_input + classification["candidate_type"]).encode("utf-8")).hexdigest()[:12]
    candidate = {
        "id": candidate_id,
        "cycle_id": cycle_id,
        "candidate_type": classification["candidate_type"],
        "route": classification["route"],
        "status": "pending_operator_review",
        "source": source,
        "raw_input_preview": raw_input[:500],
        "confidence": classification["confidence"],
        "signals": classification["signals"],
        "created_at": ts,
        "promotion_policy": "operator_approval_required",
        "truth_policy": {"backend_owns_truth": True, "fake_output": False, "generated_from_input": True, "live_web_claimed": False}
    }
    file_map = {"discovery": "discovery_candidates.json", "breakthrough": "breakthrough_candidates.json", "portfolio": "portfolio_candidates.json", "design": "design_candidates.json"}
    candidate_file = data_dir / file_map.get(candidate["candidate_type"], "discovery_candidates.json")
    candidate_set = read_json(candidate_file, {"items": [], "candidate_type": candidate["candidate_type"]})
    if candidate_id not in {item.get("id") for item in candidate_set.get("items", [])}:
        candidate_set.setdefault("items", []).append(candidate)
    candidate_set["candidate_type"] = candidate["candidate_type"]
    candidate_set["updated_at"] = ts
    write_json(candidate_file, candidate_set)
    review_item = {"id": "review-" + candidate_id, "cycle_id": cycle_id, "candidate_id": candidate_id, "candidate_type": candidate["candidate_type"], "route": candidate["route"], "status": "pending_operator_review", "confidence": candidate["confidence"], "created_at": ts, "required_action": "approve_reject_or_request_enrichment"}
    if review_item["id"] not in {item.get("id") for item in review_queue.get("items", [])}:
        review_queue.setdefault("items", []).append(review_item)
    review_queue["policy"] = "operator_review_required_before_promotion"
    review_queue["updated_at"] = ts
    write_json(review_path, review_queue)
    status["status"] = "configured_not_running"
    status["last_cycle_id"] = cycle_id
    status["last_cycle_at"] = ts
    status["last_cycle_result"] = {"status": "candidate_created", "candidate_id": candidate_id, "candidate_type": candidate["candidate_type"], "route": candidate["route"], "operator_review_required": True, "continuous_runtime_running": False, "no_fake_outputs": True}
    status["updated_at"] = ts
    write_json(status_path, status)
    return {"status": "success", "cycle_id": cycle_id, "candidate": candidate, "review_item": review_item, "continuous_runtime_status": "configured_not_running", "backend_owns_truth": True, "operator_approval_required": True, "note": "One governed cycle executed from operator input. Continuous loop remains not running."}
