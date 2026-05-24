
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

VERSION = "v17.75.2"
CONTRACT_NAME = "Workspace Dashboard + Web Search + Agent Command Bar Preparation"

SEARCH_LOG_PATH = Path("data/operator/search_command/search_log.json")
COMMAND_LOG_PATH = Path("data/operator/search_command/command_log.json")
CAPABILITIES_PATH = Path("data/operator/search_command/search_command_capabilities.json")
DASHBOARD_PAYLOAD_PATH = Path("data/dashboard/search_command_bar_payload.json")

SEARCHABLE_ROOTS = [
    Path("data/continuous_runtime"),
    Path("data/source_universes"),
    Path("data/live"),
    Path("data/live_intelligence"),
    Path("data/internet_evidence"),
    Path("data/design_portal"),
    Path("data/internet_readiness"),
    Path("data/update_governance"),
]

WORKSPACES = [
    "mission",
    "routes",
    "discovery",
    "autodesign",
    "design_portal",
    "portfolio",
    "acquisition",
    "internet",
    "updates",
    "proof",
    "diagnostics",
]

COMMANDS = {
    "show proof pack": {"action": "open_workspace", "workspace": "proof", "endpoint": "/proof/e2e"},
    "open proof": {"action": "open_workspace", "workspace": "proof", "endpoint": "/proof/e2e"},
    "show stop go": {"action": "open_workspace", "workspace": "proof", "endpoint": "/system/stop-go"},
    "show stop/go": {"action": "open_workspace", "workspace": "proof", "endpoint": "/system/stop-go"},
    "open autodesign": {"action": "open_workspace", "workspace": "autodesign", "endpoint": "/autodesign/handoff"},
    "open auto design": {"action": "open_workspace", "workspace": "autodesign", "endpoint": "/autodesign/handoff"},
    "open design portal": {"action": "open_workspace", "workspace": "design_portal", "endpoint": "/design-portal/output"},
    "show route audit": {"action": "open_workspace", "workspace": "routes", "endpoint": "/routes/audit"},
    "open routes": {"action": "open_workspace", "workspace": "routes", "endpoint": "/routes/audit"},
    "show internet readiness": {"action": "open_workspace", "workspace": "internet", "endpoint": "/internet/readiness"},
    "open internet": {"action": "open_workspace", "workspace": "internet", "endpoint": "/internet/readiness"},
    "show updates": {"action": "open_workspace", "workspace": "updates", "endpoint": "/updates/regression-lock"},
    "open updates": {"action": "open_workspace", "workspace": "updates", "endpoint": "/updates/regression-lock"},
    "rebuild runtime truth": {"action": "api_call_prepared", "method": "POST", "endpoint": "/runtime/truth/rebuild", "requires_operator_confirmation": True},
    "refresh dashboard": {"action": "api_call_prepared", "method": "POST", "endpoint": "/operator/dashboard/refresh", "requires_operator_confirmation": False},
}

WEB_SEARCH_MODES = {
    "normal_web_search": {
        "label": "Normal Web Search",
        "prepared": True,
        "enabled": False,
        "reason": "Prepared as a normal search-engine mode, but live search remains gated until governed provider and internet readiness are verified.",
    },
    "governed_research_search": {
        "label": "Governed Research Search",
        "prepared": True,
        "enabled": False,
        "reason": "Requires source trust, allowlist/quarantine, evidence capture, rate limits, and operator-visible results.",
    },
    "runtime_system_search": {
        "label": "Claire Runtime/System Search",
        "prepared": True,
        "enabled": True,
        "reason": "Searches local runtime truth, proof, route, AutoDesign, Design Portal, validation, internet readiness, and update governance outputs.",
    },
    "agent_command_mode": {
        "label": "AI Agent Command Mode",
        "prepared": True,
        "enabled": False,
        "reason": "Command parsing is prepared. Autonomous execution remains disabled until later governed agent runtime builds.",
    },
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    if not path.exists():
        return {}, {"path": str(path).replace("\\", "/"), "status": "missing"}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            return {}, {"path": str(path).replace("\\", "/"), "status": "invalid", "error": "JSON root is not object"}
        return payload, {"path": str(path).replace("\\", "/"), "status": "loaded"}
    except Exception as exc:
        return {}, {"path": str(path).replace("\\", "/"), "status": "invalid", "error": str(exc)}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def append_json_log(path: Path, record: Dict[str, Any], max_records: int = 250) -> None:
    existing, _ = read_json(path)
    records = existing.get("records") if isinstance(existing.get("records"), list) else []
    records.append(record)
    write_json(path, {
        "version": VERSION,
        "updated_at": now(),
        "records": records[-max_records:],
    })


def rel(root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve())).replace("\\", "/")
    except Exception:
        return str(path).replace("\\", "/")


def summarize(value: Any, limit: int = 900) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        text = value
    else:
        try:
            text = json.dumps(value, ensure_ascii=False)
        except Exception:
            text = str(value)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:limit] + ("..." if len(text) > limit else "")


def load_internet_readiness(root: Path) -> Dict[str, Any]:
    payload, _ = read_json(root / "data/internet_readiness/internet_readiness_verification.json")
    return payload


def capabilities(project_root: Optional[Path | str] = None) -> Dict[str, Any]:
    root = Path(project_root or Path.cwd()).resolve()
    internet = load_internet_readiness(root)
    readiness = internet.get("readiness") if isinstance(internet.get("readiness"), dict) else {}

    caps = {
        "version": VERSION,
        "contract_name": CONTRACT_NAME,
        "generated_at": now(),
        "search_bar": {
            "permanent": True,
            "role": "normal web search + governed research + runtime search + future AI-agent command surface",
            "placeholder": "Search web, ask Claire, run command, or find system output...",
            "must_not_be_removed": True,
        },
        "modes": WEB_SEARCH_MODES,
        "live_web_conditions": {
            "provider_key_required": True,
            "source_trust_required": True,
            "allowlist_or_quarantine_required": True,
            "rate_limits_required": True,
            "evidence_capture_required": True,
            "operator_visible_results_required": True,
            "current_live_web_enabled": bool(readiness.get("live_internet_enabled", False)),
            "current_automatic_updates_enabled": bool(readiness.get("automatic_updates_enabled", False)),
        },
        "workspace_targets": WORKSPACES,
        "prepared_commands": COMMANDS,
        "unsafe_actions_disabled": {
            "uncontrolled_internet_search": True,
            "hidden_background_browsing": True,
            "automatic_update_execution": True,
            "uncontrolled_self_modification": True,
            "fake_search_results": True,
            "autonomous_agent_execution": True,
        },
    }
    write_json(root / CAPABILITIES_PATH, caps)
    write_json(root / DASHBOARD_PAYLOAD_PATH, {
        "version": VERSION,
        "generated_at": caps["generated_at"],
        "search_bar": caps["search_bar"],
        "modes": caps["modes"],
        "workspace_targets": caps["workspace_targets"],
        "live_web_conditions": caps["live_web_conditions"],
    })
    return caps


def infer_mode(query: str, requested_mode: Optional[str]) -> str:
    if requested_mode and requested_mode in {"web", "research", "runtime", "system", "command", "agent"}:
        return requested_mode
    q = query.strip().lower()
    if q.startswith("/") or q.startswith("open ") or q.startswith("show ") or q.startswith("rebuild ") or q.startswith("refresh ") or q.startswith("run "):
        return "command"
    if q.startswith("web:") or q.startswith("search web") or q.startswith("google ") or q.startswith("internet "):
        return "web"
    if q.startswith("research:") or q.startswith("governed research"):
        return "research"
    return "runtime"


def searchable_files(root: Path) -> List[Path]:
    files: List[Path] = []
    for base in SEARCHABLE_ROOTS:
        absolute = root / base
        if not absolute.exists():
            continue
        for path in absolute.rglob("*"):
            if path.is_file() and path.suffix.lower() in {".json", ".md", ".txt"}:
                files.append(path)
    return files[:2500]


def local_runtime_search(root: Path, query: str, limit: int = 12) -> List[Dict[str, Any]]:
    q = query.lower().strip()
    if not q:
        return []
    tokens = [t for t in re.split(r"[^a-zA-Z0-9_./-]+", q) if t]
    results: List[Dict[str, Any]] = []

    for path in searchable_files(root):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        lower = text.lower()
        score = 0
        for token in tokens:
            if token in lower:
                score += lower.count(token)
        if q in lower:
            score += 10
        if score <= 0:
            continue

        idx = min([lower.find(token) for token in tokens if token in lower] or [0])
        snippet = text[max(0, idx - 160): idx + 520]
        results.append({
            "type": "runtime_system_result",
            "path": rel(root, path),
            "score": score,
            "snippet": summarize(snippet, 520),
        })

    results.sort(key=lambda item: item["score"], reverse=True)
    return results[:limit]


def parse_command(query: str) -> Dict[str, Any]:
    q = query.strip().lower().replace("/", "")
    exact = COMMANDS.get(q)
    if exact:
        return {
            "recognized": True,
            "query": query,
            "intent": q,
            "plan": exact,
            "execution_enabled": False,
            "automatic_execution_enabled": False,
            "requires_user_click": True,
        }

    for workspace in WORKSPACES:
        if workspace.replace("_", " ") in q or workspace in q:
            return {
                "recognized": True,
                "query": query,
                "intent": f"open {workspace}",
                "plan": {"action": "open_workspace", "workspace": workspace},
                "execution_enabled": False,
                "automatic_execution_enabled": False,
                "requires_user_click": True,
            }

    if q.startswith("run ") or q.startswith("research ") or q.startswith("design ") or q.startswith("build "):
        return {
            "recognized": True,
            "query": query,
            "intent": "future_agent_command",
            "plan": {
                "action": "agent_command_prepared",
                "status": "not_enabled",
                "reason": "Claire agent command execution is an endgame capability and remains disabled until governed agent runtime is installed.",
            },
            "execution_enabled": False,
            "automatic_execution_enabled": False,
            "requires_user_click": True,
        }

    return {
        "recognized": False,
        "query": query,
        "intent": "unknown",
        "plan": {
            "action": "search_instead",
            "status": "available",
            "recommended_mode": "runtime",
        },
        "execution_enabled": False,
        "automatic_execution_enabled": False,
        "requires_user_click": False,
    }


def web_search_status(project_root: Optional[Path | str] = None) -> Dict[str, Any]:
    root = Path(project_root or Path.cwd()).resolve()
    internet = load_internet_readiness(root)
    readiness = internet.get("readiness") if isinstance(internet.get("readiness"), dict) else {}
    return {
        "version": VERSION,
        "generated_at": now(),
        "normal_web_search_prepared": True,
        "normal_web_search_enabled": False,
        "governed_research_enabled": False,
        "live_internet_enabled": bool(readiness.get("live_internet_enabled", False)),
        "safe_to_attempt_live_probe_after_operator_review": bool(readiness.get("safe_to_attempt_live_probe_after_operator_review", False)),
        "automatic_updates_enabled": False,
        "reason": "Normal web search mode is prepared, but live web calls remain disabled until governed provider, source trust, quarantine, rate limits, and operator review are active.",
    }


def web_search_request(project_root: Optional[Path | str] = None, query: str = "", mode: str = "web") -> Dict[str, Any]:
    root = Path(project_root or Path.cwd()).resolve()
    status = web_search_status(root)
    record = {
        "version": VERSION,
        "generated_at": now(),
        "query": query,
        "mode": mode,
        "type": "web_search_request",
        "executed": False,
        "results": [],
        "status": "prepared_not_executed",
        "reason": status["reason"],
        "governance": {
            "source_trust_required": True,
            "allowlist_or_quarantine_required": True,
            "evidence_capture_required": True,
            "rate_limits_required": True,
            "operator_visible_results_required": True,
            "no_hidden_background_browsing": True,
        },
    }
    append_json_log(root / SEARCH_LOG_PATH, record)
    return record


def search_query(project_root: Optional[Path | str] = None, query: str = "", mode: Optional[str] = None, limit: int = 12) -> Dict[str, Any]:
    root = Path(project_root or Path.cwd()).resolve()
    query = str(query or "").strip()
    resolved_mode = infer_mode(query, mode)

    if resolved_mode == "command" or resolved_mode == "agent":
        parsed = parse_command(query)
        append_json_log(root / COMMAND_LOG_PATH, {
            "generated_at": now(),
            "query": query,
            "mode": resolved_mode,
            "parsed": parsed,
        })
        return {
            "version": VERSION,
            "generated_at": now(),
            "query": query,
            "mode": resolved_mode,
            "status": "command_parsed",
            "results": [parsed],
            "execution_enabled": False,
            "automatic_execution_enabled": False,
        }

    if resolved_mode in {"web", "research"}:
        return web_search_request(root, query=query, mode=resolved_mode)

    results = local_runtime_search(root, query, limit=limit)
    response = {
        "version": VERSION,
        "generated_at": now(),
        "query": query,
        "mode": "runtime",
        "status": "completed",
        "result_count": len(results),
        "results": results,
        "web_search_available": False,
        "web_search_prepared": True,
        "agent_command_prepared": True,
    }
    append_json_log(root / SEARCH_LOG_PATH, response)
    return response


def parse_operator_command(project_root: Optional[Path | str] = None, query: str = "") -> Dict[str, Any]:
    root = Path(project_root or Path.cwd()).resolve()
    parsed = parse_command(query)
    append_json_log(root / COMMAND_LOG_PATH, {
        "generated_at": now(),
        "query": query,
        "parsed": parsed,
    })
    return {
        "version": VERSION,
        "generated_at": now(),
        "command": parsed,
        "execution_enabled": False,
        "automatic_execution_enabled": False,
        "background_execution_enabled": False,
    }


def build_search_command_layer(project_root: Optional[Path | str] = None) -> Dict[str, Any]:
    caps = capabilities(project_root)
    return {
        "version": VERSION,
        "contract_name": CONTRACT_NAME,
        "generated_at": now(),
        "capabilities": caps,
        "web_search_status": web_search_status(project_root),
        "governance": {
            "search_bar_permanent": True,
            "normal_web_search_prepared": True,
            "runtime_search_enabled": True,
            "agent_command_surface_prepared": True,
            "live_web_disabled_until_governed": True,
            "no_fake_search_results": True,
            "no_hidden_background_browsing": True,
            "no_automatic_update_execution": True,
        },
    }
