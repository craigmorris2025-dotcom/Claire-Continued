
from __future__ import annotations

import json
import os
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from runtime_core.config.env import getenv

VERSION = "v17.84"
CONTRACT_NAME = "Governed Single-Query Live Search Probe"

PROBE_CONTRACT_PATH = Path("data/internet_live_probe/governed_live_probe_contract.json")
PROBE_STATUS_PATH = Path("data/internet_live_probe/live_probe_status.json")
LAST_RESULT_PATH = Path("data/internet_live_probe/last_live_probe_result.json")
EVIDENCE_LOG_PATH = Path("data/internet_live_probe/live_probe_evidence_log.json")
QUARANTINE_LOG_PATH = Path("data/internet_live_probe/live_probe_quarantine_log.json")
DASHBOARD_PAYLOAD_PATH = Path("data/dashboard/governed_live_probe_payload.json")
STOP_GO_PATH = Path("data/internet_live_probe/v17_84_governed_live_probe_stop_go.json")
STOP_GO_MD_PATH = Path("data/internet_live_probe/v17_84_governed_live_probe_stop_go.md")

PROVIDER_GATE_PATH = Path("data/internet_provider/provider_configuration_gate.json")
ALLOWLIST_PATH = Path("data/internet_provider/source_allowlist_template.json")
QUARANTINE_POLICY_PATH = Path("data/internet_provider/quarantine_policy.json")

CONFIRM_TEXT = "RUN GOVERNED WEB PROBE"

LIMITS = {
    "max_results": 5,
    "request_timeout_seconds": 12,
    "max_query_chars": 240,
    "max_response_bytes": 750000,
    "single_query_only": True,
}

SUPPORTED_PROVIDERS = {
    "brave": {"key": "BRAVE_SEARCH_API_KEY"},
    "bing": {"key": "BING_SEARCH_API_KEY"},
    "serpapi": {"key": "SERPAPI_API_KEY"},
    "tavily": {"key": "TAVILY_API_KEY"},
}

GOVERNANCE = {
    "single_query_probe_only": True,
    "operator_confirm_text_required": True,
    "source_trust_required": True,
    "allowlist_or_quarantine_required": True,
    "evidence_capture_required": True,
    "rate_limits_required": True,
    "operator_visible_results_required": True,
    "no_hidden_background_browsing": True,
    "no_automatic_update_execution": True,
    "no_autonomous_agent_execution": True,
    "no_runtime_truth_auto_ingestion": True,
    "unknown_domains_quarantined": True,
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


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


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def redact(value: str) -> str:
    if not value:
        return ""
    if len(value) <= 6:
        return "***"
    return value[:2] + "***" + value[-2:]


def selected_provider() -> Dict[str, Any]:
    provider = getenv("PLATFORM_SEARCH_PROVIDER", "none").strip().lower() or "none"
    known = provider in SUPPORTED_PROVIDERS
    key_name = SUPPORTED_PROVIDERS.get(provider, {}).get("key", "")
    key_value = os.getenv(key_name, "") if key_name else ""
    return {
        "provider": provider,
        "known": known,
        "key_name": key_name,
        "key_present": bool(key_value),
        "key_redacted": redact(key_value),
    }


def load_allowlist(root: Path) -> Dict[str, Any]:
    payload, source = read_json(root / ALLOWLIST_PATH)
    trusted: List[str] = []
    raw = payload.get("trusted_domains")
    if isinstance(raw, list):
        for item in raw:
            if isinstance(item, dict) and item.get("domain") and item.get("enabled", True):
                trusted.append(str(item["domain"]).lower().strip())
            elif isinstance(item, str):
                trusted.append(item.lower().strip())
    return {
        "source": source,
        "allowlist_enabled": bool(payload.get("allowlist_enabled", False)),
        "quarantine_unknown_domains": payload.get("quarantine_unknown_domains", True) is not False,
        "trusted_domains": sorted(set(trusted)),
    }


def domain_from_url(url: str) -> str:
    try:
        parsed = urllib.parse.urlparse(url)
        host = (parsed.netloc or "").lower()
        if host.startswith("www."):
            host = host[4:]
        return host
    except Exception:
        return ""


def trust_status(url: str, allowlist: Dict[str, Any]) -> Dict[str, Any]:
    domain = domain_from_url(url)
    trusted = False
    for trusted_domain in allowlist.get("trusted_domains", []):
        if domain == trusted_domain or domain.endswith("." + trusted_domain):
            trusted = True
            break
    if trusted:
        return {"domain": domain, "trust_status": "trusted_allowlist", "quarantined": False}
    if allowlist.get("quarantine_unknown_domains", True):
        return {"domain": domain, "trust_status": "unknown_quarantined", "quarantined": True}
    return {"domain": domain, "trust_status": "unknown_visible", "quarantined": False}


def append_log(path: Path, record: Dict[str, Any], max_records: int = 100) -> None:
    payload, _ = read_json(path)
    records = payload.get("records") if isinstance(payload.get("records"), list) else []
    records.append(record)
    write_json(path, {
        "version": VERSION,
        "updated_at": now(),
        "records": records[-max_records:],
    })


def provider_gate_status(root: Path) -> Dict[str, Any]:
    gate, source = read_json(root / PROVIDER_GATE_PATH)
    return {
        "source": source,
        "status": gate.get("status", "missing"),
        "stop_go": gate.get("stop_go", {}),
        "governance": gate.get("governance", {}),
        "environment": gate.get("environment", {}),
    }


def build_probe_contract(project_root: Optional[Path | str] = None) -> Dict[str, Any]:
    root = Path(project_root or Path.cwd()).resolve()
    provider = selected_provider()
    gate = provider_gate_status(root)
    allowlist = load_allowlist(root)
    quarantine, quarantine_source = read_json(root / QUARANTINE_POLICY_PATH)

    blockers: List[str] = []
    warnings: List[str] = []

    if provider["provider"] == "none":
        blockers.append("no_provider_selected")
    elif not provider["known"]:
        blockers.append("unsupported_provider")
    elif not provider["key_present"]:
        blockers.append(f"missing_provider_key:{provider['key_name']}")

    if gate["source"].get("status") != "loaded":
        blockers.append("missing_v17_83_provider_gate")
    if allowlist["source"].get("status") != "loaded":
        warnings.append("allowlist_template_missing")
    if quarantine_source.get("status") != "loaded":
        warnings.append("quarantine_policy_missing")

    status = "READY_FOR_OPERATOR_CONFIRMED_SINGLE_QUERY_PROBE"
    recommendation = "Live probe is prepared. Run only one operator-confirmed query. Results are evidence-captured and unknown domains are quarantined."
    if blockers:
        status = "BLOCKED_PROVIDER_NOT_READY"
        recommendation = "Configure PLATFORM_SEARCH_PROVIDER and its API key locally, then rerun v17.83/v17.84 gates."

    contract = {
        "version": VERSION,
        "contract_name": CONTRACT_NAME,
        "generated_at": now(),
        "status": status,
        "recommendation": recommendation,
        "blockers": sorted(set(blockers)),
        "warnings": sorted(set(warnings)),
        "provider": provider,
        "provider_gate": gate,
        "allowlist": allowlist,
        "quarantine_policy_source": quarantine_source,
        "limits": LIMITS,
        "required_confirm_text": CONFIRM_TEXT,
        "governance": GOVERNANCE,
        "execution_defaults": {
            "live_probe_runs_on_install": False,
            "automatic_execution_enabled": False,
            "background_execution_enabled": False,
            "runtime_truth_auto_ingestion_enabled": False,
            "updates_auto_execution_enabled": False,
        },
        "next": [
            "Use Swagger POST /internet/live-probe/run with confirm_text if provider is configured",
            "Review evidence and quarantine logs",
            "Do not feed results into runtime truth until a later reviewed evidence-promotion build",
        ],
    }

    write_json(root / PROBE_CONTRACT_PATH, contract)
    write_json(root / PROBE_STATUS_PATH, {
        "version": VERSION,
        "generated_at": contract["generated_at"],
        "status": status,
        "recommendation": recommendation,
        "provider": provider,
        "live_probe_enabled_for_confirmed_request": not blockers,
        "automatic_execution_enabled": False,
        "background_execution_enabled": False,
    })
    write_json(root / DASHBOARD_PAYLOAD_PATH, {
        "version": VERSION,
        "generated_at": contract["generated_at"],
        "status": status,
        "recommendation": recommendation,
        "provider": provider,
        "live_probe_runs_on_install": False,
        "single_query_only": True,
        "confirm_text_required": True,
        "automatic_execution_enabled": False,
    })
    write_json(root / STOP_GO_PATH, {
        "version": VERSION,
        "generated_at": contract["generated_at"],
        "status": status,
        "blockers": sorted(set(blockers)),
        "warnings": sorted(set(warnings)),
        "recommendation": recommendation,
    })
    write_stop_go_markdown(root, contract)
    return contract


def write_stop_go_markdown(root: Path, contract: Dict[str, Any]) -> None:
    lines = [
        "# Claire v17.84 Governed Single-Query Live Search Probe",
        "",
        f"Generated: {contract['generated_at']}",
        "",
        f"Status: **{contract['status']}**",
        "",
        f"Recommendation: {contract['recommendation']}",
        "",
        "## Hard Rules",
        "",
        "- This installer does not run a web search.",
        "- A live probe requires explicit operator confirmation.",
        "- Only one query is allowed per request.",
        "- Unknown domains are quarantined.",
        "- Results do not automatically feed runtime truth.",
        "- Automatic updates and agent execution remain disabled.",
        "",
        "## Required confirm text",
        "",
        f"`{CONFIRM_TEXT}`",
        "",
        "## Provider",
        "",
        f"- Provider: `{contract['provider']['provider']}`",
        f"- Known: `{contract['provider']['known']}`",
        f"- Key present: `{contract['provider']['key_present']}`",
        "",
    ]
    if contract.get("blockers"):
        lines.append("## Blockers")
        lines.append("")
        for item in contract["blockers"]:
            lines.append(f"- {item}")
        lines.append("")
    if contract.get("warnings"):
        lines.append("## Warnings")
        lines.append("")
        for item in contract["warnings"]:
            lines.append(f"- {item}")
        lines.append("")
    lines.extend([
        "## Swagger test body",
        "",
        "POST `/internet/live-probe/run`",
        "",
        "```json",
        json.dumps({"query": "OpenAI latest research", "confirm_text": CONFIRM_TEXT}, indent=2),
        "```",
    ])
    write_text(root / STOP_GO_MD_PATH, "\n".join(lines))


def http_get_json(url: str, headers: Optional[Dict[str, str]] = None, timeout: int = 12, max_bytes: int = 750000) -> Dict[str, Any]:
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        data = response.read(max_bytes)
        text = data.decode("utf-8", errors="replace")
        try:
            return json.loads(text)
        except Exception:
            return {"raw_text": text}


def http_post_json(url: str, payload: Dict[str, Any], headers: Optional[Dict[str, str]] = None, timeout: int = 12, max_bytes: int = 750000) -> Dict[str, Any]:
    body = json.dumps(payload).encode("utf-8")
    req_headers = {"Content-Type": "application/json"}
    req_headers.update(headers or {})
    req = urllib.request.Request(url, data=body, headers=req_headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as response:
        data = response.read(max_bytes)
        text = data.decode("utf-8", errors="replace")
        try:
            return json.loads(text)
        except Exception:
            return {"raw_text": text}


def provider_query(provider: str, key: str, query: str) -> Dict[str, Any]:
    timeout = int(LIMITS["request_timeout_seconds"])
    max_bytes = int(LIMITS["max_response_bytes"])
    q = urllib.parse.quote(query)

    if provider == "brave":
        url = f"https://api.search.brave.com/res/v1/web/search?q={q}&count={LIMITS['max_results']}"
        return http_get_json(url, headers={"X-Subscription-Token": key, "Accept": "application/json"}, timeout=timeout, max_bytes=max_bytes)

    if provider == "bing":
        url = f"https://api.bing.microsoft.com/v7.0/search?q={q}&count={LIMITS['max_results']}"
        return http_get_json(url, headers={"Ocp-Apim-Subscription-Key": key}, timeout=timeout, max_bytes=max_bytes)

    if provider == "serpapi":
        url = f"https://serpapi.com/search.json?engine=google&q={q}&num={LIMITS['max_results']}&api_key={urllib.parse.quote(key)}"
        return http_get_json(url, timeout=timeout, max_bytes=max_bytes)

    if provider == "tavily":
        url = "https://api.tavily.com/search"
        return http_post_json(url, {
            "api_key": key,
            "query": query,
            "max_results": LIMITS["max_results"],
            "include_answer": False,
            "include_raw_content": False,
        }, timeout=timeout, max_bytes=max_bytes)

    raise ValueError(f"Unsupported provider: {provider}")


def normalize_results(provider: str, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []

    if provider == "brave":
        web = payload.get("web") if isinstance(payload.get("web"), dict) else {}
        raw = web.get("results") if isinstance(web.get("results"), list) else []
        for item in raw[:LIMITS["max_results"]]:
            if isinstance(item, dict):
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "snippet": item.get("description", ""),
                })

    elif provider == "bing":
        web = payload.get("webPages") if isinstance(payload.get("webPages"), dict) else {}
        raw = web.get("value") if isinstance(web.get("value"), list) else []
        for item in raw[:LIMITS["max_results"]]:
            if isinstance(item, dict):
                results.append({
                    "title": item.get("name", ""),
                    "url": item.get("url", ""),
                    "snippet": item.get("snippet", ""),
                })

    elif provider == "serpapi":
        raw = payload.get("organic_results") if isinstance(payload.get("organic_results"), list) else []
        for item in raw[:LIMITS["max_results"]]:
            if isinstance(item, dict):
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("link", ""),
                    "snippet": item.get("snippet", ""),
                })

    elif provider == "tavily":
        raw = payload.get("results") if isinstance(payload.get("results"), list) else []
        for item in raw[:LIMITS["max_results"]]:
            if isinstance(item, dict):
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "snippet": item.get("content", ""),
                })

    return results


def run_governed_live_probe(project_root: Optional[Path | str] = None, query: str = "", confirm_text: str = "") -> Dict[str, Any]:
    root = Path(project_root or Path.cwd()).resolve()
    contract = build_probe_contract(root)

    if confirm_text != CONFIRM_TEXT:
        result = {
            "version": VERSION,
            "generated_at": now(),
            "status": "blocked",
            "executed": False,
            "reason": "confirm_text_missing_or_wrong",
            "required_confirm_text": CONFIRM_TEXT,
            "query": query,
        }
        write_json(root / LAST_RESULT_PATH, result)
        return result

    if contract.get("blockers"):
        result = {
            "version": VERSION,
            "generated_at": now(),
            "status": "blocked",
            "executed": False,
            "reason": "probe_contract_has_blockers",
            "blockers": contract.get("blockers", []),
            "query": query,
        }
        write_json(root / LAST_RESULT_PATH, result)
        return result

    query = str(query or "").strip()
    if not query:
        result = {
            "version": VERSION,
            "generated_at": now(),
            "status": "blocked",
            "executed": False,
            "reason": "empty_query",
            "query": query,
        }
        write_json(root / LAST_RESULT_PATH, result)
        return result

    if len(query) > LIMITS["max_query_chars"]:
        result = {
            "version": VERSION,
            "generated_at": now(),
            "status": "blocked",
            "executed": False,
            "reason": "query_too_long",
            "max_query_chars": LIMITS["max_query_chars"],
        }
        write_json(root / LAST_RESULT_PATH, result)
        return result

    provider_state = selected_provider()
    provider = provider_state["provider"]
    key_name = provider_state["key_name"]
    key = os.getenv(key_name, "")
    allowlist = load_allowlist(root)

    started = time.time()
    try:
        raw = provider_query(provider, key, query)
        normalized = normalize_results(provider, raw)
        governed_results = []
        quarantine_records = []

        for item in normalized:
            trust = trust_status(item.get("url", ""), allowlist)
            governed = {
                **item,
                "source_domain": trust["domain"],
                "trust_status": trust["trust_status"],
                "quarantined": trust["quarantined"],
                "retrieved_at": now(),
                "provider": provider,
                "may_feed_runtime_truth": False,
                "operator_review_required": True,
            }
            governed_results.append(governed)
            if trust["quarantined"]:
                quarantine_records.append(governed)

        result = {
            "version": VERSION,
            "generated_at": now(),
            "status": "completed",
            "executed": True,
            "query": query,
            "provider": provider,
            "elapsed_seconds": round(time.time() - started, 3),
            "result_count": len(governed_results),
            "quarantined_count": len(quarantine_records),
            "results": governed_results,
            "governance": {
                **GOVERNANCE,
                "runtime_truth_auto_ingestion_enabled": False,
                "operator_review_required_before_promotion": True,
            },
            "raw_payload_saved": False,
        }

        append_log(root / EVIDENCE_LOG_PATH, {
            "generated_at": result["generated_at"],
            "query": query,
            "provider": provider,
            "result_count": len(governed_results),
            "results": governed_results,
        })
        if quarantine_records:
            append_log(root / QUARANTINE_LOG_PATH, {
                "generated_at": result["generated_at"],
                "query": query,
                "provider": provider,
                "quarantined_count": len(quarantine_records),
                "records": quarantine_records,
            })

    except Exception as exc:
        result = {
            "version": VERSION,
            "generated_at": now(),
            "status": "failed",
            "executed": False,
            "query": query,
            "provider": provider,
            "elapsed_seconds": round(time.time() - started, 3),
            "error": str(exc),
            "governance": GOVERNANCE,
        }

    write_json(root / LAST_RESULT_PATH, result)
    return result


def live_probe_summary(project_root: Optional[Path | str] = None) -> Dict[str, Any]:
    root = Path(project_root or Path.cwd()).resolve()
    contract = build_probe_contract(root)
    last, last_source = read_json(root / LAST_RESULT_PATH)
    return {
        "version": VERSION,
        "generated_at": now(),
        "contract_status": contract.get("status"),
        "recommendation": contract.get("recommendation"),
        "provider": contract.get("provider"),
        "last_result_source": last_source,
        "last_result_status": last.get("status", "none"),
        "last_executed": last.get("executed", False),
        "confirm_text_required": CONFIRM_TEXT,
        "automatic_execution_enabled": False,
        "background_execution_enabled": False,
    }
