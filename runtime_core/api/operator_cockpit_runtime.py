from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Request


router = APIRouter(tags=["Claire Operator Cockpit Runtime"])

ROOT = Path(__file__).resolve()
for parent in ROOT.parents:
    if (parent / "pyproject.toml").exists() or (parent / "main.py").exists():
        PROJECT_ROOT = parent
        break
else:
    PROJECT_ROOT = Path.cwd()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def path_for(*parts: str) -> Path:
    return PROJECT_ROOT.joinpath(*parts)


def read_json(path: Path, fallback: Any) -> Any:
    if not path.exists():
        return fallback
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback


def write_json(path: Path, payload: Any) -> Any:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


def ensure_action_queue() -> dict[str, Any]:
    path = path_for("data", "governed_action_queue.json")
    payload = read_json(path, None)
    if isinstance(payload, dict):
        payload.setdefault("queue_id", "governed_action_queue")
        payload.setdefault("items", payload.get("actions", []))
        payload.setdefault("actions", payload.get("items", []))
        return payload
    payload = {
        "queue_id": "governed_action_queue",
        "status": "ready",
        "source": "data/governed_action_queue.json",
        "items": [
            {
                "id": "action_runtime_start",
                "label": "Start governed runtime loop",
                "status": "pending_operator_approval",
                "risk_level": "medium",
                "endpoint": "/runtime/start",
            },
            {
                "id": "action_truth_refresh",
                "label": "Trigger manual truth-firewall refresh",
                "status": "pending_operator_approval",
                "risk_level": "medium",
                "endpoint": "/runtime/truth/refresh",
            },
            {
                "id": "action_execution_gate",
                "label": "Trigger autonomous execution gate",
                "status": "pending_operator_approval",
                "risk_level": "high",
                "endpoint": "/runtime/gate/trigger",
            },
        ],
        "actions": [],
        "updated_at": utc_now(),
    }
    payload["actions"] = payload["items"]
    return write_json(path, payload)


def review_items() -> list[dict[str, Any]]:
    stores = [
        read_json(path_for("data", "governed_review_queue.json"), {}),
        read_json(path_for("data", "continuous_runtime", "review_queue.json"), {}),
        read_json(path_for("data", "runtime_truth", "review_queue.json"), {}),
    ]
    items: list[dict[str, Any]] = []
    for store in stores:
        if not isinstance(store, dict):
            continue
        for key in ("items", "queue", "review_queue", "candidates"):
            value = store.get(key)
            if isinstance(value, list):
                items.extend([item for item in value if isinstance(item, dict)])
    return items


def pending(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        item
        for item in items
        if str(item.get("status", item.get("decision", ""))).lower()
        in {"", "pending", "pending_review", "pending_operator_review", "pending_operator_approval", "awaiting_sources", "review", "queued"}
    ]


def latest_cycle() -> dict[str, Any]:
    cycle_dir = path_for("data", "continuous_runtime", "cycles")
    if not cycle_dir.exists():
        return {}
    cycles = sorted(cycle_dir.glob("*.json"), key=lambda item: item.stat().st_mtime, reverse=True)
    return read_json(cycles[0], {}) if cycles else {}


def load_manifest() -> dict[str, Any]:
    manifest = read_json(path_for("data", "continuous_runtime", "manifest.json"), {})
    runtime_manifest = read_json(path_for("data", "runtime", "runtime_manifest.json"), {})
    active_registry = read_json(path_for("data", "runtime", "active_module_registry.json"), {})
    return {
        "status": manifest.get("status", "available") if isinstance(manifest, dict) else "available",
        "source": "data/continuous_runtime/manifest.json",
        "active_runtime_manifest": manifest if isinstance(manifest, dict) else {},
        "runtime_manifest": runtime_manifest if isinstance(runtime_manifest, dict) else {},
        "active_subsystems": _manifest_list(active_registry, "modules", "active_modules", "items"),
        "active_providers": _manifest_list(runtime_manifest, "providers", "active_providers"),
        "active_probes": _manifest_list(runtime_manifest, "probes", "active_probes"),
        "active_gates": _manifest_list(runtime_manifest, "gates", "active_gates", "guardrails"),
        "active_truth_sources": _manifest_list(runtime_manifest, "truth_sources", "sources", "artifact_paths"),
        "active_decision_paths": _manifest_list(runtime_manifest, "decision_paths", "routes"),
        "active_action_paths": _manifest_list(runtime_manifest, "action_paths", "actions"),
        "active_governance_rules": _manifest_list(runtime_manifest, "governance_rules", "guardrails", "policies"),
    }


def _manifest_list(payload: dict[str, Any], *keys: str) -> list[Any]:
    for key in keys:
        value = payload.get(key) if isinstance(payload, dict) else None
        if isinstance(value, list):
            return value
        if isinstance(value, dict):
            return [{"key": item_key, "value": item_value} for item_key, item_value in value.items()]
    return []


def runtime_status_payload() -> dict[str, Any]:
    status = read_json(path_for("data", "continuous_runtime", "status.json"), {})
    truth = read_json(path_for("data", "runtime_truth", "runtime_state.json"), {})
    truth_report = read_json(path_for("data", "runtime_truth", "runtime_truth_consumption_report.json"), {})
    action_queue = ensure_action_queue()
    reviews = review_items()
    action_items = action_queue.get("items", []) if isinstance(action_queue.get("items"), list) else []
    cycle = latest_cycle()
    loop_running = bool(status.get("loop_running"))
    mode = status.get("continuous_runtime_status") or status.get("status") or "configured_not_running"
    pending_actions = pending([item for item in action_items if isinstance(item, dict)])
    pending_reviews = pending(reviews)
    blocked_items = [
        item
        for item in [*action_items, *reviews]
        if "blocked" in str(item.get("status", item.get("decision", ""))).lower()
        or "blocked" in str(item.get("runtime_truth_write", "")).lower()
    ]
    return {
        "schema_version": "v19.57_operator_cockpit_runtime",
        "status": "ready",
        "generated_at": utc_now(),
        "runtime": {
            "mode": mode,
            "status": status.get("status", mode),
            "loop_running": loop_running,
            "operator_approval_required": bool(status.get("operator_approval_required", True)),
            "runtime_truth_mutated": bool(status.get("runtime_truth_mutated", False)),
            "promotion_required": bool(status.get("promotion_required", True)),
            "autonomous_execution_readiness": "ready_gated" if not loop_running else "running_gated",
            "runtime_state": status.get("runtime_state", truth.get("state", "unknown")),
            "last_cycle_id": status.get("last_cycle_id") or cycle.get("cycle_id"),
            "last_cycle_at": status.get("last_cycle_at") or cycle.get("created_at"),
            "next_cycle": "operator_or_scheduler_triggered",
        },
        "deltas": {
            "last_cycle": cycle,
            "pending_actions": len(pending_actions),
            "pending_decisions": len([item for item in pending_reviews if item.get("allowed_decisions") or item.get("decision") is None]),
            "pending_reviews": len(pending_reviews),
            "blocked_items": len(blocked_items),
            "risk_level": "high" if any(str(item.get("risk_level", "")).lower() == "high" for item in pending_actions) else "medium",
            "truth_firewall_status": truth_report.get("status", truth.get("governance_state", "ready")),
            "governed_decision_path": "operator_review_required_before_runtime_truth_mutation",
            "system_next": status.get("message", "Awaiting operator action."),
        },
        "queues": {
            "actions": pending_actions[:25],
            "reviews": pending_reviews[:25],
            "blocked": blocked_items[:25],
        },
        "truth": {
            "state": truth,
            "report": truth_report,
            "runtime_truth_mutation_enabled": bool(truth_report.get("runtime_truth_mutation_enabled", False)),
        },
        "manifest": load_manifest(),
        "sources": {
            "continuous_status": "data/continuous_runtime/status.json",
            "governed_review_queue": "data/governed_review_queue.json",
            "governed_action_queue": "data/governed_action_queue.json",
            "runtime_truth": "data/runtime_truth/*.json",
            "operator_review": "data/operator_review/*.json",
        },
    }


def update_status(**updates: Any) -> dict[str, Any]:
    path = path_for("data", "continuous_runtime", "status.json")
    status = read_json(path, {})
    status.update(updates)
    status["updated_at"] = utc_now()
    status.setdefault("operator_approval_required", True)
    status.setdefault("runtime_truth_mutated", False)
    return write_json(path, status)


def append_operator_record(kind: str, payload: dict[str, Any]) -> dict[str, Any]:
    path = path_for("data", "operator_review", f"{kind}.json")
    store = read_json(path, {"items": []})
    if not isinstance(store, dict):
        store = {"items": []}
    record = {
        "id": f"{kind}_{uuid4().hex[:10]}",
        "created_at": utc_now(),
        "operator": payload.get("operator", "operator"),
        "action": payload.get("action", kind),
        "target_id": payload.get("target_id"),
        "decision": payload.get("decision"),
        "note": payload.get("note", ""),
        "runtime_truth_write": "blocked",
    }
    store.setdefault("items", []).append(record)
    store["updated_at"] = record["created_at"]
    write_json(path, store)
    return record


def action_response(kind: str, record: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = runtime_status_payload()
    payload["operator_action"] = {
        "status": f"{kind}_recorded",
        "record": record or {},
        "runtime_truth_write": "blocked",
        "unsafe_authority_unlocked": False,
    }
    return payload


@router.get("/runtime/status")
async def runtime_status() -> dict[str, Any]:
    return runtime_status_payload()


@router.get("/runtime/loop")
async def runtime_loop() -> dict[str, Any]:
    return runtime_status_payload()


@router.get("/runtime/next")
async def runtime_next() -> dict[str, Any]:
    return runtime_status_payload()["deltas"]


@router.get("/runtime/truth")
async def runtime_truth() -> dict[str, Any]:
    return runtime_status_payload()["truth"]


@router.get("/runtime/gate")
async def runtime_gate() -> dict[str, Any]:
    status = runtime_status_payload()
    return {
        "status": "gated",
        "autonomous_execution_readiness": status["runtime"]["autonomous_execution_readiness"],
        "operator_approval_required": status["runtime"]["operator_approval_required"],
        "truth_firewall_status": status["deltas"]["truth_firewall_status"],
        "runtime_truth_write": "blocked",
    }


@router.get("/runtime/manifest")
async def runtime_manifest() -> dict[str, Any]:
    return load_manifest()


@router.get("/operator/status")
async def operator_status() -> dict[str, Any]:
    status = read_json(path_for("data", "continuous_runtime", "status.json"), {})
    return {
        "configured_state": status.get("configured_state")
        or status.get("continuous_runtime_status")
        or status.get("runtime_state")
        or status.get("status")
        or "configured_not_running",
        "loop_running": bool(status.get("loop_running", False)),
        "operator_approval_required": bool(status.get("operator_approval_required", True)),
        "runtime_truth_mutated": bool(status.get("runtime_truth_mutated", False)),
        "last_cycle_id": status.get("last_cycle_id"),
        "last_updated": status.get("last_updated") or status.get("updated_at"),
        "runtime": runtime_status_payload()["runtime"],
        "deltas": runtime_status_payload()["deltas"],
        "queues": runtime_status_payload()["queues"],
        "manifest": runtime_status_payload()["manifest"],
    }


@router.get("/governed/actions")
async def governed_actions() -> dict[str, Any]:
    queue = ensure_action_queue()
    queue["pending_count"] = len(pending(queue.get("items", [])))
    return queue


@router.get("/governed/decisions")
async def governed_decisions() -> dict[str, Any]:
    queue = read_json(path_for("data", "governed_review_queue.json"), {})
    decisions = queue.get("decisions", []) if isinstance(queue, dict) else []
    return {"status": "ready", "source": "data/governed_review_queue.json", "items": decisions, "pending_count": len(pending(review_items()))}


@router.get("/governed/reviews")
async def governed_reviews() -> dict[str, Any]:
    items = review_items()
    return {"status": "ready", "items": items, "pending_count": len(pending(items)), "source": "data/governed_review_queue.json"}


@router.post("/runtime/start")
async def runtime_start(request: Request) -> dict[str, Any]:
    body = await _body(request)
    update_status(status="active", continuous_runtime_status="running", loop_running=True, runtime_state="running")
    return action_response("runtime_start", append_operator_record("runtime_actions", {"action": "start", **body}))


@router.post("/runtime/stop")
async def runtime_stop(request: Request) -> dict[str, Any]:
    body = await _body(request)
    update_status(status="halted", continuous_runtime_status="halted", loop_running=False, runtime_state="halted")
    return action_response("runtime_stop", append_operator_record("runtime_actions", {"action": "stop", **body}))


def mark_queue_item(path: Path, item_id: str, status: str, reason: str = "") -> dict[str, Any]:
    store = read_json(path, {"items": []})
    if not isinstance(store, dict):
        store = {"items": []}
    keys = ["items", "actions", "queue", "reviews", "review_queue"]
    matched: dict[str, Any] | None = None
    for key in keys:
        value = store.get(key)
        if not isinstance(value, list):
            continue
        for item in value:
            if not isinstance(item, dict):
                continue
            if str(item.get("id") or item.get("review_item_id") or item.get("action_id")) == item_id:
                item["status"] = status
                item["decision"] = status
                item["decided_at"] = utc_now()
                item["reason"] = reason
                matched = item
    store["updated_at"] = utc_now()
    write_json(path, store)
    return matched or {"id": item_id, "status": "not_found", "requested_status": status}


@router.post("/runtime/approve")
async def runtime_approve(request: Request) -> dict[str, Any]:
    body = await _body(request)
    return action_response("approval", append_operator_record("runtime_decisions", {"action": "approve", "decision": "approved", **body}))


@router.post("/runtime/reject")
async def runtime_reject(request: Request) -> dict[str, Any]:
    body = await _body(request)
    return action_response("rejection", append_operator_record("runtime_decisions", {"action": "reject", "decision": "rejected", **body}))


@router.post("/runtime/truth/refresh")
async def runtime_truth_refresh(request: Request) -> dict[str, Any]:
    body = await _body(request)
    update_status(runtime_truth_mutated=False, truth_firewall_refreshed_at=utc_now())
    return action_response("truth_firewall_refresh", append_operator_record("runtime_actions", {"action": "truth_refresh", **body}))


@router.post("/runtime/gate/trigger")
async def runtime_gate_trigger(request: Request) -> dict[str, Any]:
    body = await _body(request)
    update_status(autonomous_execution_gate="triggered_review_only", operator_approval_required=True)
    return action_response("autonomous_execution_gate", append_operator_record("runtime_actions", {"action": "gate", **body}))


@router.post("/runtime/safe_mode")
async def runtime_safe_mode(request: Request) -> dict[str, Any]:
    body = await _body(request)
    update_status(status="safe_mode", continuous_runtime_status="degraded", loop_running=False, runtime_state="safe_mode")
    return action_response("safe_mode", append_operator_record("runtime_actions", {"action": "safe_mode", **body}))


@router.post("/runtime/freeze")
async def runtime_freeze(request: Request) -> dict[str, Any]:
    body = await _body(request)
    update_status(status="frozen", continuous_runtime_status="halted", loop_running=False, runtime_state="freeze_mode")
    return action_response("freeze_mode", append_operator_record("runtime_actions", {"action": "freeze", **body}))


@router.post("/runtime/reset")
async def runtime_reset(request: Request) -> dict[str, Any]:
    body = await _body(request)
    update_status(status="active", continuous_runtime_status="configured_not_running", loop_running=False, runtime_state="reset_requested")
    return action_response("runtime_reset", append_operator_record("runtime_actions", {"action": "reset", **body}))


@router.post("/runtime/replay")
async def runtime_replay(request: Request) -> dict[str, Any]:
    body = await _body(request)
    update_status(last_replay_requested_at=utc_now(), runtime_state="governed_replay_requested")
    return action_response("governed_replay", append_operator_record("runtime_actions", {"action": "replay", **body}))


async def _body(request: Request) -> dict[str, Any]:
    try:
        body = await request.json()
    except Exception:
        body = {}
    return body if isinstance(body, dict) else {}
