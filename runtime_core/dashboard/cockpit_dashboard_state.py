from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from runtime_core.api.operator_cockpit_runtime import runtime_status_payload
from runtime_core.api.industry_standard_endpoint_package import build_endpoint_standard_settings
from runtime_core.api.endpoint_reconciliation_report import build_endpoint_reconciliation_report
from runtime_core.api.dependency_chain_proof import PROOF_PATH as DEPENDENCY_CHAIN_PROOF_PATH
from runtime_core.api.dashboard_active_control_map import build_dashboard_active_control_map
from runtime_core.design.artifact_package import build_design_artifact_package
from runtime_core.dashboard.system_wiring_map import build_system_wiring_map
from runtime_core.design.live_design_portal import build_live_design_portal_workbench
from runtime_core.validation.run_quality_gate import evaluate_run_quality
from runtime_core.config.env import getenv


SCHEMA_VERSION = "v19.89.8_cockpit_dashboard_state"
SEARCH_PROVIDER_KEYS = {
    "bing": "BING_SEARCH_API_KEY",
    "brave": "BRAVE_SEARCH_API_KEY",
    "duckduckgo": "",
    "searchgov": "SEARCHGOV_ACCESS_KEY",
    "serpapi": "SERPAPI_API_KEY",
    "tavily": "TAVILY_API_KEY",
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path, fallback: Any) -> Any:
    if not path.exists():
        return fallback
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback


def list_items(payload: Any, *keys: str) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if not isinstance(payload, dict):
        return []
    for key in keys or ("items", "candidates", "queue", "results", "records"):
        value = payload.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
    return []


def latest_json(directory: Path, pattern: str = "*.json") -> dict[str, Any]:
    if not directory.exists():
        return {}
    files = sorted(directory.glob(pattern), key=lambda item: item.stat().st_mtime, reverse=True)
    return read_json(files[0], {}) if files else {}


def latest_lifecycle(root: Path) -> dict[str, Any]:
    run_dirs = root.joinpath("data", "runs")
    candidates: list[Path] = []
    if run_dirs.exists():
        candidates.extend(run_dirs.glob("*/lifecycle_state.json"))
    if not candidates:
        return {}
    latest = max(candidates, key=lambda item: item.stat().st_mtime)
    return read_json(latest, {})


def latest_core_output(root: Path) -> dict[str, Any]:
    run_dirs = root.joinpath("data", "runs")
    candidates: list[Path] = []
    if run_dirs.exists():
        candidates.extend(run_dirs.glob("*/core_output.json"))
    if not candidates:
        return {}
    latest = max(candidates, key=lambda item: item.stat().st_mtime)
    payload = read_json(latest, {})
    if isinstance(payload, dict):
        payload["_source_path"] = str(latest.relative_to(root)).replace("\\", "/")
    return payload


def count_items(root: Path, *parts: str) -> int:
    return len(list_items(read_json(root.joinpath(*parts), {})))


def candidate_items(root: Path, *parts: str) -> list[dict[str, Any]]:
    return list_items(read_json(root.joinpath(*parts), {}))


def count_mapping(payload: Any, key: str) -> int:
    if not isinstance(payload, dict):
        return 0
    value = payload.get(key)
    return len(value) if isinstance(value, dict) else 0


def source_universe_items(root: Path) -> list[dict[str, Any]]:
    payload = read_json(root / "data" / "source_universes" / "universe_index.json", {})
    universes = list_items(payload, "universes")
    return [
        {
            "id": item.get("universe_id"),
            "title": item.get("label") or item.get("universe_id") or "Source universe",
            "domain": "source_universe",
            "status": item.get("status") or "configured",
            "score": None,
            "mode": "governed",
            "summary": item.get("purpose") or "",
            "source": "data/source_universes/universe_index.json",
        }
        for item in universes
    ]


def monitor_signal_items(root: Path) -> list[dict[str, Any]]:
    payload = read_json(root / "data" / "live_intelligence" / "latest_monitor_run.json", {})
    results = payload.get("result", {}).get("connectors", {}).get("results", []) if isinstance(payload, dict) else []
    signals: list[dict[str, Any]] = []
    if isinstance(results, list):
        for result in results:
            if not isinstance(result, dict):
                continue
            for record in result.get("records", []) if isinstance(result.get("records"), list) else []:
                if isinstance(record, dict):
                    signals.append(record)
    return signals


def promoted_metadata_signal_items(root: Path) -> list[dict[str, Any]]:
    payload = read_json(root / "data" / "internet_evidence" / "promoted_metadata_evidence_store.json", {})
    items = list_items(payload, "items")
    signals: list[dict[str, Any]] = []
    for item in items:
        signals.append(
            {
                "record_id": item.get("evidence_id") or item.get("source_result_id"),
                "title": item.get("title") or "Promoted metadata evidence",
                "entity_name": item.get("query") or item.get("provider") or "connected evidence",
                "source_family": item.get("source_family") or "promoted_metadata_evidence",
                "source_type": "promoted_metadata_evidence",
                "source_url": item.get("url"),
                "snippet": item.get("snippet") or "",
                "status": item.get("evidence_state") or "promoted_metadata_evidence",
                "metadata": {
                    "provider": item.get("provider"),
                    "trust_tier": item.get("trust_tier"),
                    "origin": "data/internet_evidence/promoted_metadata_evidence_store.json",
                },
            }
        )
    return signals


def approved_ingestion_items(root: Path) -> list[dict[str, Any]]:
    return list_items(read_json(root / "data" / "live" / "approved_live_ingestion_records.json", []))


def normalize_signal(item: dict[str, Any], fallback_title: str = "Live source signal") -> dict[str, Any]:
    evaluation = item.get("source_evaluation") if isinstance(item.get("source_evaluation"), dict) else {}
    metadata = item.get("metadata") if isinstance(item.get("metadata"), dict) else {}
    source_type = item.get("source_type") or item.get("source_family") or metadata.get("connector") or "live_source"
    if "regulatory" in str(source_type).lower() or "filing" in str(source_type).lower():
        signal_type = "regulatory"
    elif "market" in str(item.get("market_universe", "")).lower():
        signal_type = "market"
    else:
        signal_type = "tech"
    return {
        "id": item.get("record_id") or item.get("id") or item.get("source_url"),
        "title": item.get("title") or fallback_title,
        "domain": item.get("entity_name") or item.get("domain") or evaluation.get("domain") or item.get("source_family") or "live source",
        "status": item.get("status") or item.get("scoring_status") or "metadata_only",
        "score": item.get("score") or ("eligible" if evaluation.get("may_score") else None),
        "mode": "governed_live",
        "summary": item.get("snippet") or item.get("payload", {}).get("summary", "") if isinstance(item.get("payload"), dict) else item.get("snippet", ""),
        "source": item.get("source_url") or "data/live_intelligence/latest_monitor_run.json",
        "type": signal_type,
    }


def configured_provider_state(root: Path) -> dict[str, Any]:
    root = Path(root).resolve()
    provider_root = None
    try:
        from runtime_core.api.governed_connected_search import project_root as connected_project_root
        from runtime_core.api.governed_connected_search import provider_state
        provider_root = connected_project_root().resolve()
        state = provider_state() if root == provider_root else {}
    except Exception:
        state = {}
    gate = read_json(root / "data" / "internet_provider" / "provider_configuration_gate.json", {})
    status = gate.get("status") if isinstance(gate, dict) else None
    environment = gate.get("environment", {}) if isinstance(gate, dict) and isinstance(gate.get("environment"), dict) else {}
    configured_provider = str(state.get("provider") or environment.get("selected_provider") or "").strip().lower()
    if not configured_provider and provider_root is not None and root == provider_root:
        configured_provider = getenv("PLATFORM_SEARCH_PROVIDER").strip().lower()
    if configured_provider == "provider_stack":
        configured_provider = ""
    required_key = str(state.get("required_key_name") or SEARCH_PROVIDER_KEYS.get(configured_provider, ""))
    configured_keys = environment.get("configured_keys", {}) if isinstance(environment.get("configured_keys"), dict) else {}
    configured_key_state = configured_keys.get(required_key, {}) if required_key else {}
    key_present = bool(state.get("required_key_present") or configured_key_state.get("present"))
    stack_execution_allowed = bool(state.get("execution_allowed") or any(
        item.get("execution_allowed") for item in state.get("provider_stack_states", [])
    ))
    live_search_enabled = stack_execution_allowed
    if live_search_enabled:
        activation_status = "provider_ready_for_governed_metadata_search"
    elif configured_provider and key_present:
        activation_status = "provider_configured_requires_governed_gate"
    elif configured_provider:
        activation_status = "provider_selected_missing_key"
    else:
        activation_status = status or "provider_not_configured"
    return {
        "status": activation_status,
        "selected_provider": configured_provider or gate.get("environment", {}).get("selected_provider", "none") if isinstance(gate, dict) else "none",
        "provider_key_present": key_present,
        "required_key_name": required_key,
        "live_search_enabled": live_search_enabled,
        "provider_stack": state.get("provider_stack", []),
        "provider_stack_states": state.get("provider_stack_states", []),
        "recommended_stack": state.get("recommended_stack", []),
        "source": "data/internet_provider/provider_configuration_gate.json",
    }


def live_source_state(root: Path) -> dict[str, Any]:
    universe_index = read_json(root / "data" / "source_universes" / "universe_index.json", {})
    source_registry = read_json(root / "data" / "live" / "source_registry.json", {})
    source_health = read_json(root / "data" / "live_sources" / "source_health_snapshot.json", {})
    probe_status = read_json(root / "data" / "internet_live_probe" / "live_probe_status.json", {})
    connectivity = read_json(root / "data" / "real_governed_live_connectivity" / "real_live_connectivity_manifest.json", {})
    approved = approved_ingestion_items(root)
    monitor = read_json(root / "data" / "live_intelligence" / "latest_monitor_run.json", {})
    promoted = read_json(root / "data" / "internet_evidence" / "promoted_metadata_evidence_store.json", {})
    promoted_count = len(list_items(promoted, "items"))
    return {
        "status": "configured_provider_gated",
        "universes_configured": len(list_items(universe_index, "universes")),
        "allowed_domains": count_mapping(source_registry, "allowed_domains"),
        "blocked_domains": count_mapping(source_registry, "blocked_domains"),
        "pending_review_domains": count_mapping(source_registry, "pending_review_domains"),
        "catalog_sources": int(source_health.get("source_count", 0) or 0) if isinstance(source_health, dict) else 0,
        "healthy_catalog_sources": int(source_health.get("healthy_count", 0) or 0) if isinstance(source_health, dict) else 0,
        "live_fetch_performed": bool(source_health.get("live_fetch_performed")) if isinstance(source_health, dict) else False,
        "approved_ingestion_records": len(approved),
        "latest_monitor_signals": int(monitor.get("summary", {}).get("signals", 0) or 0) if isinstance(monitor, dict) else 0,
        "promoted_metadata_evidence": promoted_count,
        "latest_monitor_clusters": int(monitor.get("summary", {}).get("clusters", 0) or 0) if isinstance(monitor, dict) else 0,
        "latest_monitor_gaps": int(monitor.get("summary", {}).get("gaps", 0) or 0) if isinstance(monitor, dict) else 0,
        "latest_monitor_ready": bool(monitor.get("summary", {}).get("live_opportunities_ready")) if isinstance(monitor, dict) else False,
        "probe_status": probe_status.get("status") if isinstance(probe_status, dict) else "unknown",
        "connectivity_layer": connectivity.get("status") if isinstance(connectivity, dict) else "unknown",
        "connectivity_capabilities": connectivity.get("capabilities", []) if isinstance(connectivity, dict) else [],
        "provider": configured_provider_state(root),
        "sources": {
            "universe_index": "data/source_universes/universe_index.json",
            "source_registry": "data/live/source_registry.json",
            "source_health": "data/live_sources/source_health_snapshot.json",
            "probe_status": "data/internet_live_probe/live_probe_status.json",
            "connectivity_manifest": "data/real_governed_live_connectivity/real_live_connectivity_manifest.json",
            "latest_monitor": "data/live_intelligence/latest_monitor_run.json",
            "promoted_metadata": "data/internet_evidence/promoted_metadata_evidence_store.json",
        },
    }


def normalize_candidate(item: dict[str, Any], fallback_title: str) -> dict[str, Any]:
    artifact = item.get("artifact") if isinstance(item.get("artifact"), dict) else {}
    return {
        "id": item.get("id") or item.get("candidate_id") or item.get("review_item_id"),
        "title": item.get("title") or item.get("label") or item.get("headline") or fallback_title,
        "domain": item.get("domain") or item.get("type") or item.get("candidate_type") or "Backend record",
        "status": item.get("status") or item.get("decision") or "backend_record",
        "score": item.get("score") or item.get("composite_score"),
        "mode": item.get("mode") or item.get("route") or "backend",
        "summary": item.get("summary") or item.get("reason") or item.get("description") or "",
        "source": item.get("source") or item.get("path") or "backend_state",
        "artifact": artifact,
        "view_url": item.get("view_url") or artifact.get("view_url"),
        "download_url": item.get("download_url") or artifact.get("download_url"),
    }


def latest_run_records(core_output: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    if not isinstance(core_output, dict) or not core_output:
        return {"portfolio": [], "design": [], "deals": [], "breakthroughs": [], "discovery": []}
    run_quality = evaluate_run_quality(core_output)
    truth_eligible = bool(run_quality.get("dashboard_truth_eligible"))
    source = core_output.get("_source_path") or "data/runs/*/core_output.json"
    user = core_output.get("user_facing_result") if isinstance(core_output.get("user_facing_result"), dict) else {}
    portfolio = core_output.get("portfolio") if isinstance(core_output.get("portfolio"), dict) else {}
    solution = core_output.get("solution") if isinstance(core_output.get("solution"), dict) else {}
    autodesign = core_output.get("autodesign") if isinstance(core_output.get("autodesign"), dict) else {}
    acquisition = core_output.get("acquisition") if isinstance(core_output.get("acquisition"), dict) else {}
    final_package = core_output.get("final_package") if isinstance(core_output.get("final_package"), dict) else {}
    technology = core_output.get("technology_intelligence") if isinstance(core_output.get("technology_intelligence"), dict) else {}
    breakthrough = core_output.get("breakthrough") if isinstance(core_output.get("breakthrough"), dict) else {}
    discovery = core_output.get("discovery") if isinstance(core_output.get("discovery"), dict) else {}
    opportunity = discovery.get("opportunity_discovery") if isinstance(discovery.get("opportunity_discovery"), dict) else discovery
    trend = core_output.get("trend_discovery") if isinstance(core_output.get("trend_discovery"), dict) else {}

    headline = user.get("headline") or core_output.get("route_selected") or "Latest Claire run"
    run_id = core_output.get("run_id") or "latest"
    opportunity_score = opportunity.get("opportunity_score", {}) if isinstance(opportunity.get("opportunity_score"), dict) else {}
    evidence_signals = opportunity.get("evidence_signals", {}) if isinstance(opportunity.get("evidence_signals"), dict) else {}
    opportunity_map = opportunity.get("opportunity_map", {}) if isinstance(opportunity.get("opportunity_map"), dict) else {}
    trend_score = trend.get("discovery_score", {}) if isinstance(trend.get("discovery_score"), dict) else {}
    cluster = trend.get("cluster_formation", {}) if isinstance(trend.get("cluster_formation"), dict) else {}
    portfolio_item = {
        "id": run_id,
        "title": headline,
        "domain": core_output.get("route_selected") or "portfolio",
        "status": core_output.get("status") or "backend_run",
        "score": portfolio.get("score") or portfolio.get("portfolio_score") or core_output.get("confidence", {}).get("overall") if isinstance(core_output.get("confidence"), dict) else None,
        "mode": "latest_core_output",
        "summary": user.get("summary") or portfolio.get("summary") or "",
        "source": source,
        "run_quality": run_quality,
    }
    breakthrough_item = {
        "id": f"{run_id}_breakthrough",
        "title": breakthrough.get("classification") or breakthrough.get("primary_type") or "Breakthrough classification",
        "domain": breakthrough.get("route_recommendation") or breakthrough.get("primary_type") or "breakthrough",
        "status": "breakthrough" if breakthrough.get("is_breakthrough") else breakthrough.get("classification") or "classified",
        "score": breakthrough.get("score"),
        "mode": "latest_core_output",
        "summary": breakthrough.get("classification_rationale") or "Breakthrough record is sourced from latest core output.",
        "source": source,
        "novelty": opportunity.get("novelty_score"),
        "feasibility": technology.get("confidence"),
        "market_alignment": opportunity_score.get("score"),
        "acquirer_fit": acquisition.get("score"),
        "risk_inverse": 1 - float(evidence_signals.get("risk_score", 0) or 0),
        "run_quality": run_quality,
    }
    discovery_item = {
        "id": f"{run_id}_discovery",
        "title": opportunity_map.get("solution_class") or "Discovery candidate",
        "domain": opportunity.get("sector") or trend.get("sector") or "discovery",
        "status": opportunity.get("status") or trend.get("status") or "backend_run",
        "score": opportunity_score.get("score") or trend_score.get("score"),
        "mode": "latest_core_output",
        "summary": opportunity.get("opportunity_thesis") or cluster.get("cluster") or "Discovery record is sourced from latest core output.",
        "source": source,
        "run_quality": run_quality,
    }
    design_item = {
        "id": f"{core_output.get('run_id', 'latest')}_design",
        "title": solution.get("title") or autodesign.get("title") or "Design / solution output",
        "domain": technology.get("status") or "technology_intelligence",
        "status": solution.get("status") or autodesign.get("status") or "backend_run",
        "score": technology.get("confidence") or solution.get("confidence"),
        "mode": "latest_core_output",
        "summary": solution.get("summary") or autodesign.get("summary") or "Design records are sourced from the latest core output.",
        "source": source,
        "run_quality": run_quality,
    }
    deal_item = {
        "id": f"{core_output.get('run_id', 'latest')}_package",
        "title": final_package.get("title") or acquisition.get("headline") or "Final package",
        "domain": acquisition.get("status") or "acquisition",
        "status": final_package.get("status") or "package_ready",
        "score": final_package.get("score") or acquisition.get("score"),
        "mode": "latest_core_output",
        "summary": final_package.get("summary") or acquisition.get("summary") or "Final package record is sourced from the latest core output.",
        "source": source,
        "run_quality": run_quality,
    }
    if not truth_eligible:
        degraded_item = {
            "id": f"{run_id}_quality_blocked",
            "title": "Latest run blocked from dashboard truth",
            "domain": core_output.get("route_selected") or "run_quality",
            "status": run_quality.get("status"),
            "score": run_quality.get("score"),
            "mode": "run_quality_gate",
            "summary": run_quality.get("reason"),
            "source": source,
            "run_quality": run_quality,
        }
        return {
            "portfolio": [degraded_item],
            "design": [],
            "deals": [],
            "breakthroughs": [],
            "discovery": [],
        }
    return {
        "portfolio": [portfolio_item],
        "design": [design_item],
        "deals": [deal_item],
        "breakthroughs": [breakthrough_item] if breakthrough else [],
        "discovery": [discovery_item] if discovery or trend else [],
    }


def acquirer_match_items(query: str = "", limit: int = 12) -> list[dict[str, Any]]:
    try:
        from runtime_core.engines.acquirer_matching import AcquirerMatchingEngine
        from runtime_core.technology.technology_base import assess_technology_base
    except Exception:
        return []

    technology_base = assess_technology_base(query)
    records = technology_base.get("technology_search", {}).get("results", [])
    keywords: list[str] = []
    categories: list[str] = []
    for record in records if isinstance(records, list) else []:
        if not isinstance(record, dict):
            continue
        keywords.extend(str(value) for value in record.get("domains", []) if value)
        keywords.extend(str(value) for value in record.get("capabilities", []) if value)
        categories.extend(str(value) for value in record.get("acquirer_fit", []) if value)

    market_gap = {
        "sector": "general_intelligence",
        "acquirer_categories": categories,
        "buyer_segments": categories,
        "strategic_pressure": {"score": 0.62},
    }
    matches = AcquirerMatchingEngine().match(
        keywords=keywords or ["enterprise", "AI", "data", "workflow"],
        domain="technology",
        market_gap=market_gap,
    )
    deduped: dict[str, dict[str, Any]] = {}
    for item in matches:
        key = str(item.get("name") or item.get("ticker") or "").lower()
        if not key:
            continue
        current = deduped.get(key)
        if current is None or float(item.get("match_score", 0) or 0) > float(current.get("match_score", 0) or 0):
            deduped[key] = item

    return [
        {
            "id": item.get("ticker") or item.get("name"),
            "name": item.get("name"),
            "title": item.get("name"),
            "domain": item.get("sector"),
            "status": "backend_matched",
            "score": item.get("match_score"),
            "fit": round(float(item.get("match_score", 0) or 0) * 100, 1),
            "mode": "internal_acquirer_matching",
            "summary": "; ".join(item.get("rationale", [])),
            "source": "claire.engines.acquirer_matching",
            "focus": ", ".join(item.get("focus", [])[:4]),
            "items": len(item.get("matched_signals", [])),
            "fit_dimensions": item.get("fit_dimensions", {}),
        }
        for item in list(deduped.values())[:limit]
    ]


def governance_event_items(root: Path, runtime: dict[str, Any], limit: int = 25) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    queues = runtime.get("queues", {}) if isinstance(runtime, dict) else {}
    for group in ("actions", "reviews", "blocked"):
        for item in queues.get(group, []) if isinstance(queues.get(group), list) else []:
            if isinstance(item, dict):
                rows.append(
                    {
                        "id": item.get("id") or item.get("review_item_id") or item.get("action_id"),
                        "title": item.get("label") or item.get("action") or item.get("title") or f"{group.title()} item",
                        "domain": group,
                        "status": item.get("status") or item.get("decision") or "pending_review",
                        "score": item.get("risk_level"),
                        "mode": "operator_governance",
                        "summary": item.get("reason") or item.get("note") or item.get("endpoint") or "",
                        "source": "operator runtime queues",
                        "created_at": item.get("created_at") or item.get("updated_at"),
                    }
                )
    review_dir = root / "data" / "operator_review"
    if review_dir.exists():
        for path in sorted(review_dir.glob("*.json"), key=lambda item: item.stat().st_mtime, reverse=True):
            payload = read_json(path, {})
            for item in list_items(payload):
                rows.append(
                    {
                        "id": item.get("id"),
                        "title": item.get("action") or path.stem,
                        "domain": path.stem,
                        "status": item.get("decision") or item.get("status") or "recorded",
                        "score": item.get("runtime_truth_write"),
                        "mode": "operator_review_record",
                        "summary": item.get("note") or item.get("target_id") or "",
                        "source": str(path.relative_to(root)).replace("\\", "/"),
                        "created_at": item.get("created_at"),
                    }
                )
    return rows[:limit]


def learning_cycle_items(root: Path, limit: int = 25) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    history = read_json(root / "data" / "memory" / "run_history.json", [])
    for item in history if isinstance(history, list) else []:
        if isinstance(item, dict):
            rows.append(
                {
                    "id": item.get("run_id"),
                    "title": item.get("run_id") or "Memory run",
                    "domain": item.get("domain") or item.get("mode") or "memory",
                    "status": item.get("status") or "stored",
                    "score": item.get("decision_classification") or item.get("breakthrough_classification"),
                    "mode": "verified_memory",
                    "summary": item.get("memory_path") or "",
                    "source": "data/memory/run_history.json",
                    "created_at": item.get("created_at"),
                }
            )
    command_log = read_json(root / "data" / "operator" / "search_command" / "command_log.json", {})
    command_items = command_log.get("items", []) if isinstance(command_log, dict) else []
    for item in command_items if isinstance(command_items, list) else []:
        if isinstance(item, dict):
            rows.append(
                {
                    "id": item.get("generated_at") or item.get("query"),
                    "title": item.get("query") or "Command plan",
                    "domain": item.get("intent") or "governed_research",
                    "status": item.get("status") or "planned",
                    "score": item.get("local_knowledge_count"),
                    "mode": "command_learning",
                    "summary": f"evidence={item.get('evidence_count', 0)} local={item.get('local_knowledge_count', 0)} universes={item.get('source_universe_count', 0)}",
                    "source": "data/operator/search_command/command_log.json",
                    "created_at": item.get("generated_at"),
                }
            )
    return rows[:limit]


def metric(value: Any, source: str, label: str = "") -> dict[str, Any]:
    return {
        "value": value,
        "source": source,
        "label": label,
        "simulated": False,
    }


def project_file_binding(root: Path, key: str, label: str, relative_path: str, surface: str) -> dict[str, Any]:
    path = root / relative_path
    payload = read_json(path, None)
    exists = path.exists()
    optional_waiting = "*" in relative_path and not exists
    record_count = len(list_items(payload)) if exists else 0
    if isinstance(payload, dict):
        if not record_count:
            for candidate_key in ("items", "records", "candidates", "queue", "results", "universes", "stages"):
                value = payload.get(candidate_key)
                if isinstance(value, list):
                    record_count = len(value)
                    break
        if not record_count and payload:
            record_count = 1
    return {
        "key": key,
        "label": label,
        "surface": surface,
        "path": relative_path.replace("\\", "/"),
        "absolute_path": str(path),
        "exists": exists,
        "status": "bound" if exists else "awaiting_run" if optional_waiting else "missing",
        "record_count": record_count,
        "size_bytes": path.stat().st_size if exists and path.is_file() else 0,
        "modified_at": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat() if exists else None,
    }


def project_file_bindings(root: Path, lifecycle: dict[str, Any], core_output: dict[str, Any]) -> list[dict[str, Any]]:
    core_path = str(core_output.get("_source_path") or "data/runs/*/core_output.json")
    lifecycle_path = "data/runs/*/lifecycle_state.json"
    if isinstance(core_path, str) and core_path.startswith("data/runs/"):
        lifecycle_path = str(Path(core_path).with_name("lifecycle_state.json")).replace("\\", "/")
    return [
        project_file_binding(root, "runtime_status", "Runtime Status", "data/continuous_runtime/status.json", "runtime"),
        project_file_binding(root, "runtime_review_queue", "Runtime Review Queue", "data/continuous_runtime/review_queue.json", "runtime"),
        project_file_binding(root, "discovery_candidates", "Discovery Candidates", "data/continuous_runtime/discovery_candidates.json", "discovery"),
        project_file_binding(root, "breakthrough_candidates", "Breakthrough Candidates", "data/continuous_runtime/breakthrough_candidates.json", "breakthrough"),
        project_file_binding(root, "portfolio_candidates", "Portfolio Candidates", "data/continuous_runtime/portfolio_candidates.json", "portfolio"),
        project_file_binding(root, "design_candidates", "Design Candidates", "data/continuous_runtime/design_candidates.json", "design"),
        project_file_binding(root, "latest_lifecycle", "Latest Lifecycle State", lifecycle_path, "lifecycle"),
        project_file_binding(root, "latest_core_output", "Latest Core Output", core_path, "run_output"),
        project_file_binding(root, "source_universes", "Source Universes", "data/source_universes/universe_index.json", "sources"),
        project_file_binding(root, "source_registry", "Source Registry", "data/live/source_registry.json", "sources"),
        project_file_binding(root, "live_source_health", "Live Source Health", "data/live_sources/source_health_snapshot.json", "sources"),
        project_file_binding(root, "live_monitor", "Live Monitor Output", "data/live_intelligence/latest_monitor_run.json", "signals"),
        project_file_binding(root, "provider_gate", "Provider Gate", "data/internet_provider/provider_configuration_gate.json", "governance"),
        project_file_binding(root, "command_plan", "Latest Command Plan", "data/operator/search_command/latest_command_plan.json", "command"),
        project_file_binding(root, "command_log", "Command Log", "data/operator/search_command/command_log.json", "learning"),
        project_file_binding(root, "run_memory", "Run Memory", "data/memory/run_history.json", "memory"),
    ]


def normalize_stage(stage: dict[str, Any]) -> dict[str, Any]:
    status = str(stage.get("status", "not_started")).lower()
    if status in {"done", "complete", "completed", "initialized", "success"}:
        visual_status = "done"
    elif status in {"active", "running", "in_progress"}:
        visual_status = "active"
    else:
        visual_status = "pending"
    return {
        "number": stage.get("stage_number") or stage.get("number"),
        "label": stage.get("stage_name") or stage.get("label") or stage.get("name") or stage.get("id") or "Lifecycle stage",
        "status": status,
        "visual_status": visual_status,
        "reason": stage.get("reason") or stage.get("message") or "",
        "group": stage.get("group") or stage.get("phase") or "Lifecycle",
    }


def completion_item(name: str, passed: bool, weight: int, source: str, status: str | None = None) -> dict[str, Any]:
    return {
        "name": name,
        "passed": bool(passed),
        "weight": weight,
        "score": weight if passed else 0,
        "status": status or ("complete" if passed else "gap"),
        "source": source,
    }


def partial_completion_item(name: str, score: int, weight: int, source: str, status: str) -> dict[str, Any]:
    clamped = max(0, min(int(score), int(weight)))
    return {
        "name": name,
        "passed": clamped >= weight,
        "weight": weight,
        "score": clamped,
        "status": status,
        "source": source,
    }


def current_run_design_core_output(current_run: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(current_run, dict) or not current_run:
        return {}
    trend = current_run.get("trend", {}) if isinstance(current_run.get("trend"), dict) else {}
    thesis = current_run.get("thesis", {}) if isinstance(current_run.get("thesis"), dict) else {}
    discovery = current_run.get("discovery_candidate", {}) if isinstance(current_run.get("discovery_candidate"), dict) else {}
    portfolio = current_run.get("portfolio_candidate", {}) if isinstance(current_run.get("portfolio_candidate"), dict) else {}
    breakthrough = current_run.get("breakthrough_evaluation", {}) if isinstance(current_run.get("breakthrough_evaluation"), dict) else {}
    design_gate = current_run.get("design_gate", {}) if isinstance(current_run.get("design_gate"), dict) else {}
    confidence = trend.get("confidence") or thesis.get("confidence") or discovery.get("confidence") or portfolio.get("confidence") or 0.0
    keywords = trend.get("keywords") if isinstance(trend.get("keywords"), list) else []
    headline = portfolio.get("title") or discovery.get("title") or trend.get("title") or current_run.get("route_selected") or "Current runtime candidate"
    summary = portfolio.get("summary") or discovery.get("summary") or trend.get("summary") or ""
    source_authority = {
        "live_evidence_present": any(
            signal.get("source_type") == "promoted_metadata_evidence"
            for signal in current_run.get("signals", [])
            if isinstance(signal, dict)
        ),
        "live_truth_eligible": False,
        "runtime_truth_mutated": current_run.get("authority", {}).get("runtime_truth_mutated") if isinstance(current_run.get("authority"), dict) else False,
    }
    return {
        "run_id": current_run.get("run_id"),
        "status": current_run.get("status"),
        "route_selected": current_run.get("route_selected"),
        "source_authority": source_authority,
        "user_facing_result": {
            "headline": headline,
            "summary": summary,
            "trend": {
                "domain": "technology",
                "sector": "regulated enterprise technology",
                "confidence": confidence,
                "discovery_score": {"score": confidence},
                "keywords": keywords,
            },
            "thesis": {
                "statement": thesis.get("statement") or portfolio.get("portfolio_thesis"),
                "thesis_score": {"score": confidence},
            },
            "discovery": {
                "opportunity_discovery": {
                    "status": discovery.get("status"),
                    "sector": "regulated enterprise technology",
                    "opportunity_score": {"score": confidence},
                    "buildability_score": {"score": confidence},
                    "opportunity_map": {
                        "solution_class": portfolio.get("title") or discovery.get("title") or "portfolio intelligence system",
                        "unmet_need": discovery.get("summary") or trend.get("summary"),
                        "target_gap": discovery.get("summary") or trend.get("summary"),
                        "proof_to_unlock": "promoted live market evidence and operator review",
                    },
                    "opportunity_thesis": thesis.get("statement") or portfolio.get("portfolio_thesis"),
                }
            },
        },
        "breakthrough": {
            "classification": breakthrough.get("status"),
            "is_breakthrough": bool(breakthrough.get("threshold_met")),
            "score": confidence,
            "route_recommendation": "breakthrough_design" if breakthrough.get("threshold_met") else current_run.get("route_selected"),
            "classification_rationale": breakthrough.get("reason"),
        },
        "design": {
            "status": design_gate.get("status"),
            "reason": design_gate.get("reason"),
        },
    }


def current_run_design_lifecycle(current_run: dict[str, Any], lifecycle: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(current_run, dict) or not current_run:
        return lifecycle
    stages = [normalize_stage(stage) for stage in list_items(current_run, "stage_status")]
    return {
        "run_id": current_run.get("run_id"),
        "route_selected": current_run.get("route_selected"),
        "stage_count": len(stages),
        "stages": stages,
    }


def build_post_run_handoff(
    *,
    current_run: dict[str, Any],
    portfolio_items: list[dict[str, Any]],
    package_items: list[dict[str, Any]],
    design_portal_workbench: dict[str, Any],
    design_artifact_package: dict[str, Any],
    source_state: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(current_run, dict) or not current_run:
        return {
            "status": "waiting_for_run",
            "operator_message": "Run the lifecycle to create a portfolio, package, and review handoff.",
            "next_actions": ["start a governed runtime cycle"],
        }
    portfolio_artifact = current_run.get("portfolio_artifact", {}) if isinstance(current_run.get("portfolio_artifact"), dict) else {}
    breakthrough = current_run.get("breakthrough_evaluation", {}) if isinstance(current_run.get("breakthrough_evaluation"), dict) else {}
    design_gate = current_run.get("design_gate", {}) if isinstance(current_run.get("design_gate"), dict) else {}
    final_package = current_run.get("final_package", {}) if isinstance(current_run.get("final_package"), dict) else {}
    acquisition = current_run.get("acquisition", {}) if isinstance(current_run.get("acquisition"), dict) else {}
    provider = source_state.get("provider", {}) if isinstance(source_state.get("provider"), dict) else {}
    market_value_status = "requires_live_market_validation"
    next_actions = [
        "open portfolio view",
        "review signal, trend, thesis, and acquirer-fit chain",
        "promote or reject candidate through operator review",
    ]
    if not provider.get("live_search_enabled"):
        next_actions.append("fix governed internet provider before external market-value claims")
    if design_gate.get("status") != "selected":
        next_actions.append("keep design portal in preview until breakthrough/design threshold is met")
    else:
        next_actions.append("open design package and validate blueprint/materials/CAD-video slots")
    return {
        "schema_version": "claire.post_run_handoff.v1",
        "status": "review_ready" if portfolio_artifact else "run_completed_missing_portfolio_package",
        "run_id": current_run.get("run_id"),
        "route_selected": current_run.get("route_selected"),
        "advancement_path_policy_respected": bool(current_run.get("advancement_path_policy_respected")),
        "operator_review_required": bool(current_run.get("authority", {}).get("operator_review_required", True)) if isinstance(current_run.get("authority"), dict) else True,
        "runtime_truth_mutated": bool(current_run.get("authority", {}).get("runtime_truth_mutated")) if isinstance(current_run.get("authority"), dict) else False,
        "what_happened": {
            "signals": len(current_run.get("signals", [])) if isinstance(current_run.get("signals"), list) else 0,
            "discovery": bool(current_run.get("discovery_candidate")),
            "portfolio": bool(current_run.get("portfolio_candidate")),
            "acquirer_matches": len(acquisition.get("acquirer_matches", [])) if isinstance(acquisition.get("acquirer_matches"), list) else 0,
            "final_package": final_package.get("status") or "missing",
        },
        "output_locations": {
            "portfolio_view_url": portfolio_artifact.get("view_url"),
            "portfolio_download_url": portfolio_artifact.get("download_url"),
            "portfolio_latest_view_url": portfolio_artifact.get("latest_view_url"),
            "portfolio_json_path": portfolio_artifact.get("artifact_path"),
            "portfolio_html_path": portfolio_artifact.get("html_path"),
            "package_candidate_store": "data/continuous_runtime/package_candidates.json" if package_items else None,
            "portfolio_candidate_store": "data/continuous_runtime/portfolio_candidates.json" if portfolio_items else None,
            "review_queue": "data/continuous_runtime/review_queue.json",
            "design_package_dir": design_artifact_package.get("package_dir"),
            "design_manifest_path": design_artifact_package.get("manifest_path"),
        },
        "route_gates": {
            "breakthrough": {
                "status": breakthrough.get("status") or "not_evaluated",
                "threshold_met": bool(breakthrough.get("threshold_met")),
                "reason": breakthrough.get("reason"),
            },
            "design": {
                "status": design_gate.get("status") or "not_evaluated",
                "reason": design_gate.get("reason"),
                "design_route_activated": bool(design_portal_workbench.get("runtime_stage", {}).get("design_route_activated")) if isinstance(design_portal_workbench.get("runtime_stage"), dict) else False,
                "package_status": design_artifact_package.get("status"),
            },
            "market_value": {
                "status": market_value_status,
                "reason": "external market value requires promoted live market sources",
            },
            "internet": {
                "status": provider.get("status") or "unknown",
                "live_search_enabled": bool(provider.get("live_search_enabled")),
            },
        },
        "if_technology_scores": {
            "expected_route": "breakthrough_design_or_solution_design",
            "condition": "breakthrough/design threshold plus buildability, feasibility, manufacturability, need-now, and evidence gates must pass",
            "current_run_result": "not_selected" if design_gate.get("status") != "selected" else "selected",
            "dashboard_surface": "Design Portal",
            "downstream_after_design": [
                "blueprint/material/component package",
                "portfolio construction",
                "acquirer matching",
                "final business/acquisition package",
                "operator promotion review",
            ],
        },
        "next_actions": next_actions,
    }


def build_internet_provider_diagnostics(
    source_state: dict[str, Any],
    search_lanes: dict[str, Any],
) -> dict[str, Any]:
    provider = source_state.get("provider", {}) if isinstance(source_state.get("provider"), dict) else {}
    lane_provider = search_lanes.get("provider", {}) if isinstance(search_lanes.get("provider"), dict) else {}
    stack_states = provider.get("provider_stack_states") or lane_provider.get("provider_stack_states") or []
    stack_states = [item for item in stack_states if isinstance(item, dict)]
    selected = provider.get("selected_provider") or lane_provider.get("provider") or "none"
    live_enabled = bool(provider.get("live_search_enabled") or lane_provider.get("execution_allowed"))
    fallback_ready = any(
        item.get("provider") == "duckduckgo" and item.get("execution_allowed") for item in stack_states
    )
    research_grade_ready = any(
        item.get("execution_allowed") and not item.get("fallback_only") for item in stack_states
    )
    blockers: list[str] = []
    warnings: list[str] = []
    if not live_enabled:
        blockers.append("provider_execution_not_enabled")
    if not research_grade_ready:
        warnings.append("research_grade_provider_key_missing")
    if not fallback_ready:
        warnings.append("fallback_metadata_provider_not_enabled")
    if not source_state.get("universes_configured"):
        blockers.append("source_universe_missing")
    if not source_state.get("promoted_metadata_evidence") and not source_state.get("latest_monitor_signals"):
        warnings.append("no_promoted_or_monitor_metadata_yet")

    lanes = search_lanes.get("lanes", {}) if isinstance(search_lanes.get("lanes"), dict) else {}
    research_lane = lanes.get("research_intake", {}) if isinstance(lanes.get("research_intake"), dict) else {}
    rate_limits = {
        "max_queries_per_minute": 6,
        "max_queries_per_session": 30,
        "max_results_per_query": 8,
        "request_timeout_seconds": 12,
        "operator_visible_results_required": True,
        "quarantine_required": True,
    }
    return {
        "schema_version": "claire.internet_provider_diagnostics.v1",
        "status": "provider_metadata_ready" if live_enabled else "provider_gated",
        "readiness_percent": 100 if live_enabled and not blockers else 75 if live_enabled else 0,
        "selected_provider": selected,
        "live_search_enabled": live_enabled,
        "metadata_only": True,
        "body_reads_allowed": False,
        "fetch_enabled": live_enabled,
        "fetch_mode": "metadata_only_quarantine_first" if live_enabled else "provider_gated",
        "rate_limits": rate_limits,
        "research_grade_provider_ready": research_grade_ready,
        "fallback_metadata_provider_ready": fallback_ready,
        "provider_stack_states": stack_states,
        "blockers": blockers,
        "warnings": warnings,
        "lanes": {
            "research_intake": research_lane.get("provider_execution_allowed", False),
            "platform_open": bool(lanes.get("platform_open")),
        },
        "evidence_state": {
            "source_universes": source_state.get("universes_configured", 0),
            "allowed_domains": source_state.get("allowed_domains", 0),
            "latest_monitor_signals": source_state.get("latest_monitor_signals", 0),
            "promoted_metadata_evidence": source_state.get("promoted_metadata_evidence", 0),
        },
        "next_actions": [
            "Use DuckDuckGo fallback for metadata-only first run validation"
            if fallback_ready and not research_grade_ready
            else "Run governed provider metadata probe",
            "Add BRAVE_SEARCH_API_KEY for preferred research-grade public web metadata"
            if not research_grade_ready
            else "Keep research-grade provider quarantine and manual promotion",
            "Promote metadata manually before treating it as runtime evidence",
        ],
    }


def build_update_logic_status(update_governance_panel: dict[str, Any]) -> dict[str, Any]:
    updates = update_governance_panel.get("available_updates", [])
    updates = [item for item in updates if isinstance(item, dict)] if isinstance(updates, list) else []
    security = update_governance_panel.get("security_posture", {}) if isinstance(update_governance_panel.get("security_posture"), dict) else {}
    approval = update_governance_panel.get("approval_workflow", {}) if isinstance(update_governance_panel.get("approval_workflow"), dict) else {}
    install = update_governance_panel.get("install_workflow", {}) if isinstance(update_governance_panel.get("install_workflow"), dict) else {}
    install_readiness = install.get("install_readiness", []) if isinstance(install.get("install_readiness"), list) else []
    blocked_or_review = [
        {
            "update_id": item.get("update_id"),
            "status": item.get("status"),
            "blockers": item.get("blockers", []),
            "trusted": item.get("provider_gate", {}).get("trusted", False) if isinstance(item.get("provider_gate"), dict) else False,
            "signature_verified": item.get("signature_verification", {}).get("verified", False) if isinstance(item.get("signature_verification"), dict) else False,
            "install": next(
                (
                    install_item
                    for install_item in install_readiness
                    if isinstance(install_item, dict) and install_item.get("update_id") == item.get("update_id")
                ),
                {},
            ),
        }
        for item in updates
    ]
    return {
        "schema_version": "claire.update_logic_status.v1",
        "status": "proposal_review_ready",
        "available_update_count": len(updates),
        "automatic_updates_enabled": bool(security.get("automatic_updates_enabled")),
        "package_install_performed": bool(security.get("package_install_performed")),
        "runtime_truth_firewall": security.get("runtime_truth_firewall", "enabled"),
        "approval_required": bool(approval.get("approval_required", True)),
        "approval_phrase": approval.get("approval_phrase"),
        "manual_owner_approval_only": bool(approval.get("manual_owner_approval_only", True)),
        "mutation_endpoints_exposed": bool(security.get("mutation_endpoints_exposed")),
        "mutation_endpoints_operator_gated": bool(security.get("mutation_endpoints_operator_gated", True)),
        "privileged_surfaces_exposed": bool(security.get("privileged_surfaces_exposed")),
        "install_endpoints_exposed": bool(install.get("install_endpoints_exposed")),
        "stage_endpoint": install.get("stage_endpoint"),
        "apply_endpoint": install.get("apply_endpoint"),
        "status_endpoint": install.get("status_endpoint"),
        "install_readiness": install_readiness,
        "updates": blocked_or_review,
        "next_actions": [
            "Review update proposals from the dashboard",
            "Use Stage Install to verify approval, package payload, rollback, and target safety",
            "Use Apply Governed Update only after owner approval and rollback snapshot readiness",
            "Keep automatic update execution disabled",
            "Require signature, rollback plan, and explicit owner approval before any apply phase",
        ],
    }


def build_first_run_readiness(
    *,
    current_run: dict[str, Any],
    stage_count: int,
    route_selected: str,
    signal_count: int,
    portfolio_count: int,
    package_count: int,
    acquirer_count: int,
    strategic_world: dict[str, Any],
    source_state: dict[str, Any],
    update_logic: dict[str, Any],
    post_run_handoff: dict[str, Any],
) -> dict[str, Any]:
    provider = source_state.get("provider", {}) if isinstance(source_state.get("provider"), dict) else {}
    checks = [
        completion_item("30-stage run spine", stage_count >= 30, 10, "data/continuous_runtime/current_run.json"),
        completion_item("route selected", bool(route_selected), 10, "current_run.route_selected"),
        completion_item("signals available", signal_count > 0, 10, "live monitor/promoted metadata"),
        completion_item("portfolio candidate", portfolio_count > 0, 10, "data/continuous_runtime/portfolio_candidates.json"),
        completion_item("package candidate", package_count > 0, 10, "data/continuous_runtime/package_candidates.json"),
        completion_item("acquirer rationale", acquirer_count > 0, 10, "current_run.acquisition"),
        completion_item("strategic world recommendations", bool(strategic_world.get("ranked_recommendations")), 10, "strategic_world_layer"),
        completion_item("dashboard handoff", post_run_handoff.get("status") == "review_ready", 10, "post_run_handoff"),
        completion_item("provider metadata path", bool(provider.get("live_search_enabled")), 8, "provider gate"),
        completion_item("update governance locked", update_logic.get("automatic_updates_enabled") is False, 12, "update governance"),
    ]
    score = sum(item["score"] for item in checks)
    total = sum(item["weight"] for item in checks)
    gaps = [item for item in checks if item["score"] < item["weight"]]
    first_run_ready = not any(item["name"] in {
        "30-stage run spine",
        "route selected",
        "portfolio candidate",
        "package candidate",
        "strategic world recommendations",
        "dashboard handoff",
        "update governance locked",
    } for item in gaps)
    return {
        "schema_version": "claire.first_run_readiness.v1",
        "status": "ready_for_operator_first_run_review" if first_run_ready else "first_run_gaps_present",
        "percent": round((score / total) * 100, 1) if total else 0.0,
        "score": score,
        "total": total,
        "checks": checks,
        "gaps": gaps,
        "run_id": current_run.get("run_id") if isinstance(current_run, dict) else None,
        "route_selected": route_selected,
        "operator_review_required": True,
        "runtime_truth_mutated": False,
        "next_actions": [
            item["name"] for item in gaps
        ] or ["review current run package", "validate provider metadata quality", "approve or reject candidate"],
    }


def build_cockpit_dashboard_state(project_root: Path | str | None = None) -> dict[str, Any]:
    root = Path(project_root or Path.cwd()).resolve()
    runtime = runtime_status_payload()
    lifecycle = latest_lifecycle(root)
    current_run = read_json(root / "data" / "continuous_runtime" / "current_run.json", {})
    stages = [normalize_stage(stage) for stage in list_items(lifecycle, "stages")]
    if not stages and isinstance(current_run, dict):
        stages = [normalize_stage(stage) for stage in list_items(current_run, "stage_status")]
    action_count = int(runtime.get("deltas", {}).get("pending_actions", 0) or 0)
    review_count = int(runtime.get("deltas", {}).get("pending_reviews", 0) or 0)
    blocked_count = int(runtime.get("deltas", {}).get("blocked_items", 0) or 0)

    portfolio_items = candidate_items(root, "data", "continuous_runtime", "portfolio_candidates.json")
    portfolio_artifact = current_run.get("portfolio_artifact", {}) if isinstance(current_run.get("portfolio_artifact"), dict) else {}
    if portfolio_artifact:
        for item in portfolio_items:
            if isinstance(item, dict):
                item.setdefault("artifact", portfolio_artifact)
                item.setdefault("view_url", portfolio_artifact.get("view_url"))
                item.setdefault("download_url", portfolio_artifact.get("download_url"))
    breakthrough_items = candidate_items(root, "data", "continuous_runtime", "breakthrough_candidates.json")
    discovery_items = candidate_items(root, "data", "continuous_runtime", "discovery_candidates.json")
    design_items = candidate_items(root, "data", "continuous_runtime", "design_candidates.json")
    package_items = candidate_items(root, "data", "continuous_runtime", "package_candidates.json")
    source_universes = source_universe_items(root)
    approved_signals = [normalize_signal(item) for item in approved_ingestion_items(root)]
    monitor_signals = [normalize_signal(item) for item in monitor_signal_items(root)]
    promoted_signals = [normalize_signal(item) for item in promoted_metadata_signal_items(root)]
    signal_items = approved_signals + monitor_signals + promoted_signals
    source_state = live_source_state(root)
    operational_conditions = read_json(root / "data" / "platform" / "operational_conditions.json", {})
    if not isinstance(operational_conditions, dict) or not operational_conditions:
        operational_conditions = {
            "schema_version": "claire.operational_conditions.v1",
            "status": "configured_for_governed_first_run",
            "internet_provider": {
                "mode": "metadata_only_quarantine_first",
                "body_reads_allowed": False,
                "operator_review_required": True,
            },
            "runtime_truth_mutation_allowed": False,
            "automatic_updates_enabled": False,
        }
    latest_command_plan = read_json(root / "data" / "operator" / "search_command" / "latest_command_plan.json", {})
    core_output = latest_core_output(root)
    run_records = latest_run_records(core_output)
    file_bindings = project_file_bindings(root, lifecycle, core_output)
    system_wiring = build_system_wiring_map(root, lifecycle=lifecycle, core_output=core_output)
    from runtime_core.platform.update_governance.open_web_update_governance import build_dashboard_update_panel

    update_governance_panel = build_dashboard_update_panel(root)
    from runtime_core.platform.intelligence_modes import build_intelligence_mode_state

    intelligence_modes = build_intelligence_mode_state(root)
    from runtime_core.dashboard.cockpit_command_plan import command_history

    command_history_payload = command_history(root)
    latest_hybrid_result = read_json(root / "data" / "continuous_runtime" / "results" / "latest_result.json", {})
    from runtime_core.api.governed_connected_search import search_lane_config

    search_lanes = search_lane_config()
    from runtime_core.technology.technology_base import assess_technology_base

    technology_base = assess_technology_base("")
    emergence_overview = (
        current_run.get("emergence_engine", {})
        if isinstance(current_run, dict) and isinstance(current_run.get("emergence_engine"), dict)
        else technology_base.get("reemergence_pattern_engine", {})
    )
    strategic_world = (
        current_run.get("strategic_world", {})
        if isinstance(current_run, dict) and isinstance(current_run.get("strategic_world"), dict)
        else {}
    )
    design_core_output = current_run_design_core_output(current_run) or core_output
    design_lifecycle = current_run_design_lifecycle(current_run, lifecycle)
    design_portal_workbench = build_live_design_portal_workbench(
        core_output=design_core_output,
        lifecycle=design_lifecycle,
        technology_base=technology_base,
    )
    design_artifact_package = build_design_artifact_package(design_portal_workbench, root)
    design_portal_workbench["artifact_package"] = design_artifact_package
    post_run_handoff = build_post_run_handoff(
        current_run=current_run,
        portfolio_items=portfolio_items,
        package_items=package_items,
        design_portal_workbench=design_portal_workbench,
        design_artifact_package=design_artifact_package,
        source_state=source_state,
    )
    from runtime_core.pipeline.activation_registry import build_pipeline_activation_registry

    pipeline_activation = build_pipeline_activation_registry()
    portfolio_count = len(portfolio_items)
    breakthrough_count = len(breakthrough_items)
    discovery_count = len(discovery_items)
    design_count = len(design_items)
    package_count = len(package_items)
    signal_count = len(signal_items)
    current_run_acquirers = (
        current_run.get("acquisition", {}).get("acquirer_matches", [])
        if isinstance(current_run.get("acquisition"), dict)
        else []
    )
    acquirer_items = [
        normalize_candidate(
            {
                "id": item.get("name"),
                "title": item.get("name"),
                "domain": item.get("acquirer_category"),
                "status": item.get("review_state"),
                "score": item.get("fit") or item.get("match_score"),
                "summary": item.get("strategic_fit_rationale"),
                "source": item.get("source"),
            },
            "Acquirer match",
        )
        for item in current_run_acquirers
        if isinstance(item, dict)
    ] or acquirer_match_items("")
    acquirer_count = len(acquirer_items)
    governance_records = governance_event_items(root, runtime)
    lifecycle_memory = read_json(root / "data" / "continuous_runtime" / "lifecycle_memory.json", {})
    lifecycle_memory_records = list_items(lifecycle_memory, "records")
    learning_records = [
        normalize_candidate(
            {
                "id": item.get("run_id"),
                "title": item.get("result", {}).get("user_facing_result", {}).get("headline") if isinstance(item.get("result"), dict) else item.get("run_id"),
                "domain": item.get("result", {}).get("domain") if isinstance(item.get("result"), dict) else "lifecycle_memory",
                "status": item.get("status"),
                "summary": item.get("result", {}).get("user_facing_result", {}).get("summary") if isinstance(item.get("result"), dict) else "",
                "source": "data/continuous_runtime/lifecycle_memory.json",
            },
            "Lifecycle memory record",
        )
        for item in lifecycle_memory_records
    ] or learning_cycle_items(root)
    portfolio_records = [
        normalize_candidate(item, "Portfolio candidate")
        for item in portfolio_items
    ] or run_records["portfolio"]
    breakthrough_records = [
        normalize_candidate(item, "Breakthrough candidate")
        for item in breakthrough_items
    ] or run_records["breakthroughs"]
    discovery_records = [
        normalize_candidate(item, "Discovery candidate")
        for item in discovery_items
    ] or run_records["discovery"]
    design_records = [
        normalize_candidate(item, "Design candidate")
        for item in design_items
    ] or run_records["design"]
    deal_records = [
        normalize_candidate(item, "Package candidate")
        for item in package_items
    ] or run_records["deals"]
    portfolio_count = len(portfolio_records)
    breakthrough_count = len(breakthrough_records)
    discovery_count = len(discovery_records)
    design_count = len(design_records)
    package_count = len(deal_records)
    bound_file_count = len([item for item in file_bindings if item["exists"]])
    missing_file_bindings = [item for item in file_bindings if item.get("status") == "missing"]

    lifecycle_score = read_json(root / "data" / "intelligence" / "lifecycle_quality_score.json", {})
    portfolio_routing = read_json(root / "data" / "intelligence" / "portfolio_breakthrough_routing.json", {})
    route_scores = portfolio_routing.get("route_scores", {}) if isinstance(portfolio_routing, dict) else {}
    frontend_files_ready = all(
        (root / "frontend" / "command_center" / "modern" / name).exists()
        for name in ("platform_dashboard.html", "platform_dashboard.css", "platform_dashboard.js")
    )
    backend_dashboard_files_ready = all(
        (root / path).exists()
        for path in (
            "runtime_core/dashboard/cockpit_dashboard_state.py",
            "runtime_core/dashboard/cockpit_command_plan.py",
            "runtime_core/api/routes_pipeline.py",
            "runtime_core/app.py",
        )
    )
    operator_button_files_ready = (root / "runtime_core/api/operator_cockpit_runtime.py").exists()
    search_bar_files_ready = all(
        (root / path).exists()
        for path in (
            "runtime_core/api/governed_connected_search.py",
            "runtime_core/dashboard/cockpit_command_plan.py",
        )
    ) and search_lanes.get("status") == "ready"
    stage_count = int(lifecycle.get("stage_count") or len(stages) or len(current_run.get("stage_status", [])) or 0)
    pipeline_gap_count = int(pipeline_activation["placeholder_count"] + pipeline_activation["failed_count"])
    weak_pipeline_count = int(pipeline_activation.get("unbound_count", 0) or 0)
    records_bound = portfolio_count > 0 and package_count > 0 and acquirer_count > 0
    source_records_bound = signal_count > 0 and source_state["universes_configured"] > 0
    breakthrough_discovery_bound = bool(current_run.get("breakthrough_evaluation")) and discovery_count > 0
    governance_learning_bound = bool(learning_records)
    completion_items = [
        completion_item("frontend dashboard files", frontend_files_ready, 8, "frontend/command_center/modern"),
        completion_item("dashboard backend state files", backend_dashboard_files_ready, 8, "runtime_core/dashboard + runtime_core/app.py"),
        completion_item("topbar action endpoints", operator_button_files_ready, 8, "runtime_core/api/operator_cockpit_runtime.py"),
        completion_item("search bar and command planner", search_bar_files_ready, 10, "governed_connected_search + cockpit_command_plan"),
        completion_item("30-stage lifecycle order", stage_count >= 30, 12, "data/runs/*/lifecycle_state.json"),
        completion_item(
            "pipeline activation registry",
            pipeline_activation["activated_count"] >= 14 and pipeline_gap_count == 0 and weak_pipeline_count == 0,
            12,
            "runtime_core/pipeline/activation_registry.py",
        ),
        completion_item("technology database binding", technology_base["counts"]["records"] > 0, 8, "runtime_core/technology/technology_base.py"),
        completion_item("portfolio/deal/acquirer records", records_bound, 12, "continuous runtime + acquirer matching engine"),
        completion_item("signals and source universes", source_records_bound, 8, "data/live_intelligence + data/source_universes"),
        completion_item("breakthrough and discovery records", breakthrough_discovery_bound, 6, "continuous_runtime candidate stores"),
        completion_item("governance and learning records", governance_learning_bound, 6, "operator runtime + verified memory + command history"),
        completion_item("live provider execution gate", bool(source_state.get("provider", {}).get("live_search_enabled")), 2, "data/internet_provider/provider_configuration_gate.json"),
    ]
    completion_score = sum(item["score"] for item in completion_items)
    completion_total = sum(item["weight"] for item in completion_items)
    completion_percent = round((completion_score / completion_total) * 100, 1) if completion_total else 0.0
    completion_gaps = [item for item in completion_items if item["score"] < item["weight"]]
    route_selected = str(lifecycle.get("route_selected") or current_run.get("route_selected") or core_output.get("route_selected") or "").strip()
    portfolio_route = route_selected in {"portfolio_intelligence", "portfolio_only", "portfolio_candidate", "portfolio_creation_optimization"}
    breakthrough_route = route_selected.startswith("breakthrough") or route_selected in {"design", "breakthrough_design"}
    breakthrough_recommendation = (
        str((core_output.get("breakthrough") or {}).get("route_recommendation") or "").strip()
        if isinstance(core_output.get("breakthrough"), dict)
        else ""
    )
    breakthrough_qualified = (
        breakthrough_route
        and breakthrough_count > 0
        and portfolio_count > 0
        and breakthrough_recommendation not in {"portfolio_intelligence", "portfolio_only", "portfolio_candidate", "portfolio_creation_optimization"}
    )
    operational_items = [
        completion_item("explicit intelligence mode", intelligence_modes.get("active_mode") in {"deterministic", "connected", "hybrid"}, 8, "/api/intelligence/modes"),
        completion_item("30-stage lifecycle run", stage_count >= 30, 10, "data/continuous_runtime/current_run.json"),
        completion_item("route selected by lifecycle", bool(route_selected), 10, "current run/lifecycle output"),
        completion_item("advancement path policy", portfolio_route or breakthrough_qualified, 12, "stage 14-15 route decision"),
        completion_item("real signal ingestion", signal_count > 0, 14, "approved live ingestion or monitor signals"),
        completion_item("governed provider ready", bool(source_state.get("provider", {}).get("live_search_enabled")), 12, "data/internet_provider/provider_configuration_gate.json"),
        completion_item("portfolio candidates produced", portfolio_count > 0, 10, "continuous runtime or latest core output"),
        completion_item("breakthrough evaluated conditionally", bool(current_run.get("breakthrough_evaluation")) or breakthrough_count > 0, 8, "stage 14 breakthrough classification"),
        completion_item("acquirer layer producing", acquirer_count > 0, 8, "claire.engines.acquirer_matching"),
        completion_item("lifecycle memory records", bool(learning_records), 8, "data/continuous_runtime/lifecycle_memory.json"),
    ]
    operational_score = sum(item["score"] for item in operational_items)
    operational_total = sum(item["weight"] for item in operational_items)
    operational_percent = round((operational_score / operational_total) * 100, 1) if operational_total else 0.0
    operational_gaps = [item for item in operational_items if item["score"] < item["weight"]]
    internet_provider_diagnostics = build_internet_provider_diagnostics(source_state, search_lanes)
    update_logic_status = build_update_logic_status(update_governance_panel)
    endpoint_standard_settings = build_endpoint_standard_settings()
    endpoint_reconciliation = build_endpoint_reconciliation_report(project_root=root)
    dependency_chain_proof = read_json(root / DEPENDENCY_CHAIN_PROOF_PATH, {})
    active_control_map = build_dashboard_active_control_map()
    first_run_readiness = build_first_run_readiness(
        current_run=current_run,
        stage_count=stage_count,
        route_selected=route_selected,
        signal_count=signal_count,
        portfolio_count=portfolio_count,
        package_count=package_count,
        acquirer_count=acquirer_count,
        strategic_world=strategic_world,
        source_state=source_state,
        update_logic=update_logic_status,
        post_run_handoff=post_run_handoff,
    )

    return {
        "schema_version": SCHEMA_VERSION,
        "status": "ready",
        "generated_at": now(),
        "simulated_values_present": False,
        "sources": {
            "runtime": "/operator/status",
            "lifecycle": "data/continuous_runtime/current_run.json",
            "portfolio": "data/continuous_runtime/portfolio_candidates.json",
            "breakthrough": "data/continuous_runtime/breakthrough_candidates.json",
            "discovery": "data/continuous_runtime/discovery_candidates.json",
            "design": "data/continuous_runtime/design_candidates.json",
            "package": "data/continuous_runtime/package_candidates.json",
            "source_universes": "data/source_universes/universe_index.json",
            "live_sources": "data/live_sources/source_health_snapshot.json",
            "live_intelligence": "data/live_intelligence/latest_monitor_run.json",
            "update_governance": "data/update_governance/update_requests",
            "intelligence_modes": "/api/intelligence/modes",
        },
        "metrics": {
            "breakthroughs": metric(breakthrough_count, "data/continuous_runtime/breakthrough_candidates.json"),
            "portfolio_items": metric(portfolio_count, "data/continuous_runtime/portfolio_candidates.json"),
            "active_signals": metric(signal_count, "data/live_intelligence/latest_monitor_run.json"),
            "acquirer_matches": metric(acquirer_count, "claire.engines.acquirer_matching"),
            "source_universes": metric(source_state["universes_configured"], "data/source_universes/universe_index.json"),
            "allowed_sources": metric(source_state["allowed_domains"], "data/live/source_registry.json"),
            "catalog_sources": metric(source_state["catalog_sources"], "data/live_sources/source_health_snapshot.json"),
            "healthy_catalog_sources": metric(source_state["healthy_catalog_sources"], "data/live_sources/source_health_snapshot.json"),
            "latest_monitor_signals": metric(source_state["latest_monitor_signals"], "data/live_intelligence/latest_monitor_run.json"),
            "promoted_metadata_evidence": metric(source_state["promoted_metadata_evidence"], "data/internet_evidence/promoted_metadata_evidence_store.json"),
            "latest_monitor_clusters": metric(source_state["latest_monitor_clusters"], "data/live_intelligence/latest_monitor_run.json"),
            "latest_monitor_gaps": metric(source_state["latest_monitor_gaps"], "data/live_intelligence/latest_monitor_run.json"),
            "safety_events": metric(blocked_count + review_count, "/operator/status"),
            "pipeline_score": metric(lifecycle_score.get("score"), "data/intelligence/lifecycle_quality_score.json"),
            "pending_actions": metric(action_count, "/operator/status"),
            "pending_reviews": metric(review_count, "/operator/status"),
            "blocked_items": metric(blocked_count, "/operator/status"),
            "discovery_candidates": metric(discovery_count, "data/continuous_runtime/discovery_candidates.json"),
            "design_candidates": metric(design_count, "data/continuous_runtime/design_candidates.json"),
            "design_artifacts": metric(design_artifact_package.get("artifact_count", 0), "data/design_portal/packages"),
            "package_candidates": metric(package_count, "data/continuous_runtime/package_candidates.json"),
            "portfolio_route_score": metric(route_scores.get("portfolio"), "data/intelligence/portfolio_breakthrough_routing.json"),
            "breakthrough_route_score": metric(route_scores.get("breakthrough"), "data/intelligence/portfolio_breakthrough_routing.json"),
            "design_route_score": metric(route_scores.get("design"), "data/intelligence/portfolio_breakthrough_routing.json"),
            "acquisition_route_score": metric(route_scores.get("acquisition"), "data/intelligence/portfolio_breakthrough_routing.json"),
            "technology_records": metric(technology_base["counts"]["records"], "internal_technology_base"),
            "technology_readiness": metric(technology_base["readiness"]["average_readiness_level"], "internal_technology_base"),
            "manufacturable_matches": metric(technology_base["counts"]["manufacturable_matches"], "internal_technology_base"),
            "technology_innovation_candidates": metric(technology_base["counts"].get("innovation_candidates", 0), "internal_technology_base"),
            "technology_breakthrough_ready": metric(technology_base["counts"].get("breakthrough_ready_candidates", 0), "internal_technology_base"),
            "emergence_completion": metric(emergence_overview.get("product_completion_percent", emergence_overview.get("readiness_score", 0)), "system_emergence_engine"),
            "emergence_patterns": metric(len(emergence_overview.get("detected_patterns", [])), "system_emergence_engine"),
            "emergence_ready_signal_families": metric(len(emergence_overview.get("ready_signal_families", [])), "system_emergence_engine"),
            "strategic_world_options": metric(len(strategic_world.get("options", [])), "strategic_world_layer"),
            "strategic_world_recommendations": metric(len(strategic_world.get("ranked_recommendations", [])), "strategic_world_layer"),
            "active_pipelines": metric(pipeline_activation["activated_count"], "pipeline_activation_registry"),
            "pipeline_gaps": metric(pipeline_activation["placeholder_count"] + pipeline_activation["failed_count"], "pipeline_activation_registry"),
            "weak_pipelines": metric(pipeline_activation.get("unbound_count", 0), "pipeline_activation_registry"),
            "platform_completion": metric(operational_percent, "operational_readiness_proof"),
            "surface_completion": metric(completion_percent, "dashboard_surface_binding"),
            "available_updates": metric(update_governance_panel.get("available_update_count", 0), "open_web_update_governance"),
            "first_run_readiness": metric(first_run_readiness["percent"], "first_run_readiness"),
            "provider_stack_ready": metric(
                len([item for item in internet_provider_diagnostics.get("provider_stack_states", []) if item.get("execution_allowed")]),
                "internet_provider_diagnostics",
            ),
            "provider_blockers": metric(len(internet_provider_diagnostics.get("blockers", [])), "internet_provider_diagnostics"),
            "update_blockers": metric(
                len([item for item in update_logic_status.get("updates", []) if item.get("blockers")]),
                "update_logic_status",
            ),
            "project_files_bound": metric(bound_file_count, "dashboard_project_file_bindings"),
            "project_files_missing": metric(len(missing_file_bindings), "dashboard_project_file_bindings"),
            "system_wiring_routes": metric(len(system_wiring.get("routes", [])), "dashboard_system_wiring_map"),
            "system_wiring_missing": metric(len(system_wiring.get("missing", [])), "dashboard_system_wiring_map"),
        },
        "records": {
            "breakthroughs": [
                normalize_candidate(item, "Breakthrough candidate")
                for item in breakthrough_items
            ] or breakthrough_records,
            "signals": signal_items,
            "source_universes": source_universes,
            "portfolio": portfolio_records,
            "deals": deal_records,
            "acquirers": acquirer_items,
            "discovery": discovery_records,
            "design": design_records,
            "technology": [
                normalize_candidate(
                    {
                        "id": item.get("id"),
                        "title": item.get("name"),
                        "domain": ", ".join(item.get("domains", [])),
                        "status": item.get("maturity"),
                        "score": item.get("readiness_level"),
                        "mode": item.get("manufacturability"),
                        "summary": ", ".join(item.get("capabilities", [])),
                        "source": "internal_technology_base",
                    },
                    "Technology record",
                )
                for item in technology_base["technology_search"]["results"]
            ],
            "technology_innovation_candidates": [
                normalize_candidate(
                    {
                        "id": item.get("candidate_id"),
                        "title": item.get("title"),
                        "domain": item.get("innovation_type"),
                        "status": item.get("status"),
                        "score": item.get("breakthrough_score"),
                        "mode": item.get("route_recommendation"),
                        "summary": item.get("thesis"),
                        "source": "generated_local_technology_database",
                    },
                    "Technology innovation candidate",
                )
                for item in technology_base.get("innovation_candidates", [])
            ],
            "emergence_patterns": [
                normalize_candidate(
                    {
                        "id": item.get("pattern_id"),
                        "title": item.get("name"),
                        "domain": ", ".join(item.get("primary_signal_families", [])),
                        "status": emergence_overview.get("cycle_stage"),
                        "score": item.get("score"),
                        "mode": emergence_overview.get("route_selected")
                        or emergence_overview.get("route_guidance", {}).get("recommended_route"),
                        "summary": "Detected ACS2 re-emergence pattern bound to system routing.",
                        "source": "system_emergence_engine",
                    },
                    "Emergence pattern",
                )
                for item in emergence_overview.get("detected_patterns", [])
                if isinstance(item, dict)
            ],
            "strategic_world": [
                normalize_candidate(
                    {
                        "id": item.get("option_id"),
                        "title": item.get("option_id"),
                        "domain": ", ".join(strategic_world.get("domains", [])),
                        "status": strategic_world.get("governance", {}).get("execution_boundary"),
                        "score": item.get("score"),
                        "mode": "recommendation_only",
                        "summary": "Stakeholder-scored strategic-world recommendation. External execution is blocked.",
                        "source": "strategic_world_layer",
                    },
                    "Strategic world recommendation",
                )
                for item in strategic_world.get("ranked_recommendations", [])
                if isinstance(item, dict)
            ],
            "governance": governance_records,
            "learning": learning_records,
            "project_files": file_bindings,
            "update_governance": update_governance_panel.get("available_updates", []),
            "internet_provider_diagnostics": [
                normalize_candidate(
                    {
                        "id": item.get("provider"),
                        "title": item.get("provider"),
                        "domain": item.get("required_key_name") or "no_key_required",
                        "status": "execution_allowed" if item.get("execution_allowed") else "gated",
                        "score": None,
                        "mode": "fallback" if item.get("fallback_only") else "research_grade",
                        "summary": "Provider metadata lane is ready." if item.get("execution_allowed") else "Provider requires credentials or explicit fallback enablement.",
                        "source": "provider_stack",
                    },
                    "Provider lane",
                )
                for item in internet_provider_diagnostics.get("provider_stack_states", [])
                if isinstance(item, dict)
            ],
            "first_run_readiness": [
                normalize_candidate(
                    {
                        "id": item.get("name"),
                        "title": item.get("name"),
                        "domain": item.get("source"),
                        "status": "passed" if item.get("score") == item.get("weight") else "gap",
                        "score": item.get("score"),
                        "mode": f"{item.get('score')}/{item.get('weight')}",
                        "summary": item.get("source"),
                        "source": "first_run_readiness",
                    },
                    "First-run check",
                )
                for item in first_run_readiness.get("checks", [])
            ],
        },
        "project_file_bindings": {
            "status": "bound" if not missing_file_bindings else "missing_files",
            "root": str(root),
            "bound_count": bound_file_count,
            "missing_count": len(missing_file_bindings),
            "bindings": file_bindings,
            "missing": missing_file_bindings,
        },
        "system_wiring": system_wiring,
        "runtime": runtime.get("runtime", {}),
        "deltas": runtime.get("deltas", {}),
        "queues": runtime.get("queues", {}),
        "truth": runtime.get("truth", {}),
        "manifest": runtime.get("manifest", {}),
        "live_sources": source_state,
        "operational_conditions": operational_conditions if isinstance(operational_conditions, dict) else {},
        "internet_provider_diagnostics": internet_provider_diagnostics,
        "search_lanes": search_lanes,
        "technology_base": technology_base,
        "emergence_engine": emergence_overview,
        "strategic_world": strategic_world,
        "design_portal_workbench": design_portal_workbench,
        "design_artifact_package": design_artifact_package,
        "post_run_handoff": post_run_handoff,
        "pipeline_activation": pipeline_activation,
        "command_plan": latest_command_plan if isinstance(latest_command_plan, dict) else {},
        "command_history": command_history_payload,
        "latest_hybrid_result": latest_hybrid_result if isinstance(latest_hybrid_result, dict) else {},
        "current_run_truth": {
            "run_id": current_run.get("run_id") if isinstance(current_run, dict) else None,
            "status": current_run.get("status") if isinstance(current_run, dict) else "missing",
            "route_selected": current_run.get("route_selected") if isinstance(current_run, dict) else None,
            "advancement_path_policy_respected": bool(current_run.get("advancement_path_policy_respected")) if isinstance(current_run, dict) else False,
            "quality_gate": current_run.get("quality_gate", {}) if isinstance(current_run, dict) else {},
            "breakthrough_evaluation": current_run.get("breakthrough_evaluation", {}) if isinstance(current_run, dict) else {},
            "design_gate": current_run.get("design_gate", {}) if isinstance(current_run, dict) else {},
            "emergence_engine": current_run.get("emergence_engine", {}) if isinstance(current_run, dict) else {},
            "strategic_world": current_run.get("strategic_world", {}) if isinstance(current_run, dict) else {},
        },
        "update_governance_panel": update_governance_panel,
        "update_logic_status": update_logic_status,
        "endpoint_standard_settings": endpoint_standard_settings,
        "endpoint_reconciliation": endpoint_reconciliation,
        "dependency_chain_proof": dependency_chain_proof,
        "active_control_map": active_control_map,
        "first_run_readiness": first_run_readiness,
        "intelligence_modes": intelligence_modes,
        "active_intelligence_mode": intelligence_modes.get("active_mode", "deterministic"),
        "platform_completion": {
            "percent": operational_percent,
            "score": operational_score,
            "total": operational_total,
            "pass_name": "operational_readiness_proof",
            "items": operational_items,
            "gaps": operational_gaps,
            "next_activation_targets": [
                item["name"] for item in operational_gaps
            ],
        },
        "surface_completion": {
            "percent": completion_percent,
            "score": completion_score,
            "total": completion_total,
            "pass_name": "dashboard_surface_binding",
            "items": completion_items,
            "gaps": completion_gaps,
            "note": "Surface completion measures mounted files, panels, and records. It is not operational readiness.",
        },
        "lifecycle": {
            "run_id": lifecycle.get("run_id"),
            "stage_count": lifecycle.get("stage_count") or len(stages),
            "route_selected": lifecycle.get("route_selected") or current_run.get("route_selected") or core_output.get("route_selected"),
            "summary": lifecycle.get("summary", {}),
            "route_scores": route_scores,
            "decision_context": {
                "selected_route": lifecycle.get("route_selected") or current_run.get("route_selected") or core_output.get("route_selected"),
                "breakthrough_score": (core_output.get("breakthrough") or {}).get("score") if isinstance(core_output.get("breakthrough"), dict) else None,
                "discovery_score": (core_output.get("trend_discovery") or {}).get("discovery_score", {}).get("score") if isinstance(core_output.get("trend_discovery"), dict) and isinstance(core_output.get("trend_discovery", {}).get("discovery_score"), dict) else None,
                "opportunity_score": (
                    (core_output.get("discovery") or {}).get("opportunity_discovery", {}).get("opportunity_score", {}).get("score")
                    if isinstance(core_output.get("discovery"), dict)
                    and isinstance(core_output.get("discovery", {}).get("opportunity_discovery"), dict)
                    and isinstance(core_output.get("discovery", {}).get("opportunity_discovery", {}).get("opportunity_score"), dict)
                    else None
                ),
                "route_rule": "Stages 1-15 establish signal, trend, thesis, discovery, and breakthrough classification; selected-route conditions determine design, portfolio, acquisition, and package stages.",
            },
            "stages": stages,
        },
        "sections": {
            "overview": {"status": "backend_bound"},
            "lifecycle": {"status": "backend_bound" if stages else "awaiting_run"},
            "signals": {"status": "backend_bound" if signal_items else "configured_awaiting_live_records"},
            "breakthroughs": {"status": "backend_bound"},
            "portfolio": {"status": "backend_bound"},
            "deals": {"status": "backend_bound"},
            "acquirers": {"status": "backend_bound" if acquirer_items else "source_unbound"},
            "modes": {"status": "runtime_bound"},
            "governance": {"status": "runtime_bound"},
            "learning": {"status": "partial_backend_bound"},
            "strategic_world": {"status": strategic_world.get("status", "waiting_for_run")},
            "subsystems": {"status": "manifest_bound"},
            "source_universes": {"status": "backend_bound" if source_universes else "missing"},
            "live_connectivity": {"status": source_state["status"]},
            "internet_provider": {"status": internet_provider_diagnostics["status"]},
            "update_governance": {"status": update_governance_panel["status"]},
            "endpoint_standards": {"status": endpoint_standard_settings["status"]},
            "endpoint_reconciliation": {"status": endpoint_reconciliation["status"]},
            "dependency_chain_proof": {"status": dependency_chain_proof.get("status", "not_run")},
            "first_run": {"status": first_run_readiness["status"]},
            "intelligence_modes": {"status": intelligence_modes["status"]},
        },
    }
