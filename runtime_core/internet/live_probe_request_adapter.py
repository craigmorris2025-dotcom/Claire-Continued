
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

VERSION = "v17.84.1"
CONTRACT_NAME = "Live Probe Body Compatibility Repair"

CONFIRM_TEXT = "RUN GOVERNED WEB PROBE"


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def normalize_live_probe_payload(payload: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    body = payload or {}
    query = (
        body.get("query")
        or body.get("raw_input")
        or body.get("q")
        or body.get("search")
        or body.get("prompt")
        or ""
    )
    confirm_text = (
        body.get("confirm_text")
        or body.get("confirmation")
        or body.get("operator_confirm_text")
        or ""
    )
    return {
        "version": VERSION,
        "normalized_at": now(),
        "query": str(query or "").strip(),
        "confirm_text": str(confirm_text or "").strip(),
        "accepted_query_fields": ["query", "raw_input", "q", "search", "prompt"],
        "accepted_confirm_fields": ["confirm_text", "confirmation", "operator_confirm_text"],
        "original_keys": sorted(list(body.keys())),
    }


def run_adapter_payload(payload: Optional[Dict[str, Any]] = None, project_root: Optional[Path | str] = None) -> Dict[str, Any]:
    normalized = normalize_live_probe_payload(payload)

    try:
        from runtime_core.internet.governed_live_probe import run_governed_live_probe
    except Exception as exc:
        return {
            "version": VERSION,
            "contract_name": CONTRACT_NAME,
            "status": "blocked",
            "executed": False,
            "reason": "governed_live_probe_module_unavailable",
            "error": str(exc),
            "normalized_request": normalized,
        }

    result = run_governed_live_probe(
        project_root=project_root,
        query=normalized["query"],
        confirm_text=normalized["confirm_text"],
    )

    if isinstance(result, dict):
        result["request_adapter"] = {
            "version": VERSION,
            "accepted_query_fields": normalized["accepted_query_fields"],
            "accepted_confirm_fields": normalized["accepted_confirm_fields"],
            "normalized_query_present": bool(normalized["query"]),
            "original_keys": normalized["original_keys"],
            "use_this_swagger_endpoint": "POST /internet/live-probe/run-confirmed",
        }
    return result


def adapter_status(project_root: Optional[Path | str] = None) -> Dict[str, Any]:
    try:
        from runtime_core.internet.governed_live_probe import build_probe_contract, live_probe_summary
        contract = build_probe_contract(project_root)
        summary = live_probe_summary(project_root)
    except Exception as exc:
        contract = {"status": "unavailable", "error": str(exc)}
        summary = {"status": "unavailable", "error": str(exc)}

    return {
        "version": VERSION,
        "contract_name": CONTRACT_NAME,
        "status": "ready",
        "reason": "Use /internet/live-probe/run-confirmed for the governed probe body. It accepts query or raw_input.",
        "accepted_body_examples": [
            {"query": "OpenAI latest research", "confirm_text": CONFIRM_TEXT},
            {"raw_input": "OpenAI latest research", "confirm_text": CONFIRM_TEXT},
        ],
        "required_confirm_text": CONFIRM_TEXT,
        "safe_defaults": {
            "does_not_run_on_install": True,
            "requires_operator_confirm_text": True,
            "single_query_only": True,
            "no_runtime_truth_auto_ingestion": True,
            "automatic_updates_disabled": True,
        },
        "probe_contract_status": contract.get("status"),
        "probe_summary": summary,
    }
