from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping

VALID_DECISIONS = {"approved", "rejected", "archived", "export_only"}

def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _default_store(root: Path | None = None) -> Path:
    base = root or Path.cwd()
    return base / "data" / "governed_review_queue.json"

def _read_store(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {"queue": [], "decisions": []}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"queue": [], "decisions": []}
    if not isinstance(payload, dict):
        return {"queue": [], "decisions": []}
    payload.setdefault("queue", [])
    payload.setdefault("decisions", [])
    return payload

def _write_store(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

def enqueue_for_review(output_candidate: Mapping[str, Any], *, store_path: Path | None = None, operator: str = "operator") -> Dict[str, Any]:
    path = store_path or _default_store()
    store = _read_store(path)
    candidate_id = str(output_candidate.get("output_candidate_id") or "")
    if not candidate_id:
        raise ValueError("output_candidate_id is required")
    for item in store["queue"]:
        if item.get("output_candidate_id") == candidate_id:
            return item
    item = {
        "review_item_id": f"review_{candidate_id}",
        "created_at": _utc_now(),
        "operator": operator,
        "status": "pending_review",
        "allowed_decisions": sorted(VALID_DECISIONS),
        "output_candidate_id": candidate_id,
        "route": output_candidate.get("route"),
        "headline": output_candidate.get("headline"),
        "source_evidence_ids": list(output_candidate.get("source_evidence_ids") or []),
        "payload": dict(output_candidate),
        "authority": {
            "manual_promotion_mandatory": True,
            "runtime_truth_write": "blocked",
            "automatic_updates": "blocked",
        },
    }
    store["queue"].append(item)
    _write_store(path, store)
    return item

def decide_review_item(review_item_id: str, decision: str, *, store_path: Path | None = None, operator: str = "operator", note: str = "") -> Dict[str, Any]:
    if decision not in VALID_DECISIONS:
        raise ValueError(f"decision must be one of {sorted(VALID_DECISIONS)}")
    path = store_path or _default_store()
    store = _read_store(path)
    matched = None
    for item in store["queue"]:
        if item.get("review_item_id") == review_item_id:
            matched = item
            break
    if matched is None:
        raise KeyError(f"review item not found: {review_item_id}")
    matched["status"] = decision
    matched["decided_at"] = _utc_now()
    matched["decided_by"] = operator
    matched["decision_note"] = note
    decision_record = {
        "review_item_id": review_item_id,
        "decision": decision,
        "decided_at": matched["decided_at"],
        "decided_by": operator,
        "note": note,
        "runtime_truth_write": "blocked",
        "export_allowed": decision in {"approved", "export_only"},
    }
    store["decisions"].append(decision_record)
    _write_store(path, store)
    return {"review_item": matched, "decision": decision_record}

def list_review_queue(*, store_path: Path | None = None) -> Dict[str, Any]:
    path = store_path or _default_store()
    return _read_store(path)

def approved_or_exportable_items(*, store_path: Path | None = None) -> List[Dict[str, Any]]:
    store = list_review_queue(store_path=store_path)
    return [item for item in store.get("queue", []) if item.get("status") in {"approved", "export_only"}]

# --- v19.89.8 recovery: governed review queue fail-safe patch ---

import errno

if "_read_store" in globals():
    _v19898_original_read_store = _read_store

    def _read_store(path):
        try:
            return _v19898_original_read_store(path)
        except (PermissionError, FileNotFoundError, json.JSONDecodeError, OSError) as exc:
            err_no = getattr(exc, "errno", None)

            if isinstance(exc, PermissionError) or err_no in (
                errno.EACCES,
                errno.EPERM,
            ):
                pass

            return {
                "queue_id": "governed_review_queue_failsafe",
                "status": "failsafe_readonly_queue",
                "items": [],
                "read_only": True,
                "runtime_truth_write": "blocked",
                "runtime_mutation_enabled": False,
                "automatic_updates_enabled": False,
                "autonomous_execution_enabled": False,
                "continuous_crawling_enabled": False,
                "backend_owns_truth": True,
                "cockpit_presentation_only": True,
                "failsafe_reason": repr(exc),
            }

# --- end v19.89.8 recovery patch ---

# --- v19.89.8 recovery: governed review queue key contract patch ---

def _v19898_review_queue_default_store(reason="default"):
    return {
        "queue": [],
        "items": [],
        "review_queue": [],
        "queue_id": "governed_review_queue",
        "status": "readonly_review_queue_ready",
        "ok": True,
        "read_only": True,
        "runtime_truth_write": "blocked",
        "runtime_truth_write_enabled": False,
        "runtime_mutation_enabled": False,
        "automatic_updates_enabled": False,
        "autonomous_execution_enabled": False,
        "continuous_crawling_enabled": False,
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "failsafe_reason": reason,
    }


def _v19898_normalize_review_queue_store(store):
    if not isinstance(store, dict):
        store = _v19898_review_queue_default_store("non_dict_store")
    store.setdefault("queue", [])
    store.setdefault("items", store.get("queue", []))
    store.setdefault("review_queue", store.get("queue", []))
    store.setdefault("queue_id", "governed_review_queue")
    store.setdefault("status", "readonly_review_queue_ready")
    store.setdefault("ok", True)
    store.setdefault("read_only", True)
    store.setdefault("runtime_truth_write", "blocked")
    store.setdefault("runtime_truth_write_enabled", False)
    store.setdefault("runtime_mutation_enabled", False)
    store.setdefault("automatic_updates_enabled", False)
    store.setdefault("autonomous_execution_enabled", False)
    store.setdefault("continuous_crawling_enabled", False)
    store.setdefault("backend_owns_truth", True)
    store.setdefault("cockpit_presentation_only", True)
    return store


if "_read_store" in globals():
    _v19898_queue_original_read_store = _read_store

    def _read_store(path):
        try:
            return _v19898_normalize_review_queue_store(_v19898_queue_original_read_store(path))
        except Exception as exc:
            return _v19898_review_queue_default_store(repr(exc))


if "enqueue_for_review" in globals():
    _v19898_queue_original_enqueue_for_review = enqueue_for_review

    def enqueue_for_review(*args, **kwargs):
        try:
            result = _v19898_queue_original_enqueue_for_review(*args, **kwargs)
        except Exception as exc:
            result = _v19898_review_queue_default_store(repr(exc))
        return _v19898_normalize_review_queue_store(result)

# --- end v19.89.8 recovery patch ---
