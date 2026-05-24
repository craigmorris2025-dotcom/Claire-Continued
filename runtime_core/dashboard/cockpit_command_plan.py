from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from runtime_core.governance.governed_search_plan import build_search_plan
from runtime_core.operator.search_command_layer import search_query
from runtime_core.technology.technology_base import search_technology_base

from .cockpit_dashboard_state import (
    configured_provider_state,
    live_source_state,
    monitor_signal_items,
    normalize_signal,
    read_json,
    source_universe_items,
)


SCHEMA_VERSION = "v19.89.8_cockpit_command_plan"
HISTORY_SCHEMA_VERSION = "v19.89.8_cockpit_command_history"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def terms(query: str) -> set[str]:
    text = "".join(ch.lower() if ch.isalnum() else " " for ch in (query or ""))
    return {part for part in text.split() if len(part) > 2}


def text_matches(query_terms: set[str], *values: Any) -> bool:
    if not query_terms:
        return False
    haystack = " ".join(str(value or "").lower() for value in values)
    return any(term in haystack for term in query_terms)


def evidence_preview(root: Path, query: str, limit: int = 8) -> list[dict[str, Any]]:
    query_terms = terms(query)
    signals = [normalize_signal(item) for item in monitor_signal_items(root)]
    approved = [normalize_signal(item) for item in read_json(root / "data" / "live" / "approved_live_ingestion_records.json", []) if isinstance(item, dict)]
    candidates: list[dict[str, Any]] = []
    for item in signals + approved:
        if text_matches(query_terms, item.get("title"), item.get("summary"), item.get("domain"), item.get("source")):
            candidates.append(
                {
                    "evidence_id": item.get("id") or item.get("source"),
                    "title": item.get("title"),
                    "source": item.get("source"),
                    "status": item.get("status"),
                    "mode": item.get("mode"),
                    "promotion_state": "review_required",
                    "runtime_truth_write": "blocked",
                }
            )
    return candidates[:limit]


def source_universe_matches(root: Path, query: str) -> list[dict[str, Any]]:
    query_terms = terms(query)
    universes = source_universe_items(root)
    matches = [
        item for item in universes
        if text_matches(query_terms, item.get("title"), item.get("summary"), item.get("id"))
    ]
    return matches or universes


def inferred_knowledge_domains(query: str) -> list[str]:
    query_terms = terms(query)
    domains: list[str] = []
    domain_terms = {
        "technology_intelligence": {"technology", "tech", "stack", "compatibility", "maturity", "component", "autonomous", "invention", "engine"},
        "engineering": {"build", "buildable", "feasible", "feasibility", "manufacturable", "deployable", "prototype", "architecture"},
        "design_portal": {"design", "blueprint", "spec", "component", "system"},
        "breakthrough": {"breakthrough", "innovation", "novel", "invention"},
        "portfolio": {"portfolio", "market", "commercial", "acquisition"},
        "governance": {"governance", "safety", "compliance", "redline", "approval"},
        "recursive_learning": {"recursive", "learning", "feedback", "memory"},
    }
    for domain, hints in domain_terms.items():
        if query_terms.intersection(hints):
            domains.append(domain)
    return domains


def local_knowledge_matches(query: str, limit: int = 6) -> dict[str, Any]:
    from runtime_core.api.knowledge_base_registry_s471_s477 import search_knowledge_registry

    domains = inferred_knowledge_domains(query)
    payload = search_knowledge_registry(query, domains=domains, limit=limit)
    results = payload.get("results", []) if isinstance(payload, dict) else []
    return {
        "schema_version": "v19.89.8_local_knowledge_search",
        "status": "ready" if results else "empty",
        "source": "runtime_core.api.knowledge_base_registry_s471_s477",
        "query": query,
        "inferred_domains": domains,
        "result_count": len(results) if isinstance(results, list) else 0,
        "results": results if isinstance(results, list) else [],
        "authority": {
            "network_request_performed": False,
            "provider_execution_performed": False,
            "body_read_performed": False,
            "runtime_truth_mutation": False,
        },
    }


def system_search_matches(root: Path, query: str, limit: int = 8) -> dict[str, Any]:
    payload = search_query(project_root=root, query=query, mode="runtime", limit=limit)
    results = payload.get("results", []) if isinstance(payload, dict) else []
    return {
        "schema_version": "v19.89.8_runtime_system_search",
        "status": "ready" if results else "empty",
        "source": "claire.operator.search_command_layer",
        "query": query,
        "result_count": len(results) if isinstance(results, list) else 0,
        "results": results if isinstance(results, list) else [],
        "authority": {
            "network_request_performed": False,
            "provider_execution_performed": False,
            "body_read_performed": False,
            "runtime_truth_mutation": False,
        },
    }


def technology_matches(query: str, limit: int = 6) -> dict[str, Any]:
    payload = search_technology_base(query, limit=limit)
    results = payload.get("results", []) if isinstance(payload, dict) else []
    return {
        "schema_version": "v19.89.8_command_technology_search",
        "status": "ready" if results else "empty",
        "source": "claire.technology.technology_base",
        "query": query,
        "result_count": len(results) if isinstance(results, list) else 0,
        "results": results if isinstance(results, list) else [],
        "innovation_candidates": payload.get("innovation_candidates", []) if isinstance(payload, dict) else [],
        "evidence_sources": payload.get("evidence_sources", []) if isinstance(payload, dict) else [],
        "current_buildable_count": payload.get("current_buildable_count") if isinstance(payload, dict) else None,
        "speculative_or_future_count": payload.get("speculative_or_future_count") if isinstance(payload, dict) else None,
        "authority": payload.get("authority", {}) if isinstance(payload, dict) else {},
    }


def local_source_pack_matches(root: Path, query: str, limit: int = 8) -> dict[str, Any]:
    query_terms = terms(query)
    manifest = read_json(root / "data" / "source_packs" / "local_upload_source_packs.json", {})
    packs = manifest.get("packs", []) if isinstance(manifest, dict) else []
    matches: list[dict[str, Any]] = []
    for pack in packs if isinstance(packs, list) else []:
        if not isinstance(pack, dict):
            continue
        if pack.get("active_guidance") is False:
            continue
        root_path = Path(str(pack.get("root_path") or ""))
        files = pack.get("files", [])
        for filename in files if isinstance(files, list) else []:
            path = resolve_source_pack_file(root_path, str(filename))
            title = path.stem
            role_text = " ".join(str(item) for item in pack.get("route_roles", []) if item)
            searchable = " ".join([pack.get("label", ""), title, role_text, pack.get("source_universe", "")])
            snippet = ""
            if path.exists() and path.suffix.lower() in {".txt", ".md", ".html"}:
                try:
                    snippet = path.read_text(encoding="utf-8", errors="replace")[:900]
                except Exception:
                    snippet = ""
            if not text_matches(query_terms, searchable, snippet):
                continue
            score = 0.35
            lower_blob = f"{searchable} {snippet}".lower()
            score += min(0.45, 0.08 * sum(1 for term in query_terms if term in lower_blob))
            if pack.get("trust_tier"):
                score += 0.10
            if path.exists():
                score += 0.10
            matches.append(
                {
                    "pack_id": pack.get("pack_id"),
                    "pack_label": pack.get("label"),
                    "title": title,
                    "path": str(path).replace("\\", "/"),
                    "exists": path.exists(),
                    "source_universe": pack.get("source_universe"),
                    "trust_tier": pack.get("trust_tier"),
                    "route_roles": pack.get("route_roles", []),
                    "score": round(min(1.0, score), 3),
                    "snippet": " ".join(snippet.split())[:420] if snippet else "Configured local source-pack document.",
                }
            )
    matches.sort(key=lambda item: (item["score"], item["exists"]), reverse=True)
    return {
        "schema_version": "v19.90_local_source_pack_search",
        "status": "ready" if matches else "empty",
        "source": "data/source_packs/local_upload_source_packs.json",
        "query": query,
        "result_count": len(matches[:limit]),
        "results": matches[:limit],
        "authority": {
            "network_request_performed": False,
            "provider_execution_performed": False,
            "body_read_performed": False,
            "runtime_truth_mutation": False,
            "manual_promotion_required": True,
        },
    }


def resolve_source_pack_file(root_path: Path, filename: str) -> Path:
    exact = root_path / filename
    if exact.exists():
        return exact
    numbered = sorted(root_path.glob(f"*. {filename}"))
    if numbered:
        return numbered[0]
    if "Operator Instruction Manual" in filename:
        manual = sorted(root_path.glob("*Operator Instruction Manual.pdf"))
        if manual:
            return manual[0]
    return exact


def plan_next_actions(provider: dict[str, Any], evidence_count: int) -> list[dict[str, Any]]:
    if provider.get("live_search_enabled"):
        first = {
            "action_id": "operator.review_metadata_probe",
            "label": "Review one-shot metadata probe",
            "status": "ready_for_operator_review",
            "enabled": True,
            "endpoint": "/api/governed/live-probe/head",
        }
    elif provider.get("provider_key_present"):
        first = {
            "action_id": "operator.enable_governed_provider_gate",
            "label": "Enable governed provider gate",
            "status": "requires_operator_gate",
            "enabled": False,
            "endpoint": "/api/search/provider/manual-probe/preflight",
        }
    else:
        first = {
            "action_id": "operator.configure_provider",
            "label": "Configure search provider",
            "status": "provider_key_required",
            "enabled": False,
            "endpoint": "/api/search/providers/configuration/payload",
        }
    return [
        first,
        {
            "action_id": "operator.review_evidence_preview",
            "label": "Review evidence preview",
            "status": "ready" if evidence_count else "awaiting_query_match_or_live_probe",
            "enabled": evidence_count > 0,
            "endpoint": "/api/dashboard/state",
        },
        {
            "action_id": "operator.promote_after_review",
            "label": "Promote evidence after review",
            "status": "manual_review_required",
            "enabled": False,
            "endpoint": "/operator/evidence/review",
        },
    ]


def build_cockpit_command_plan(query: str, project_root: Path | str | None = None) -> dict[str, Any]:
    root = Path(project_root or Path.cwd()).resolve()
    normalized_query = " ".join((query or "").strip().split())
    plan = build_search_plan(normalized_query)
    from runtime_core.api.intelligence_answer_routes import build_intelligence_routed_answer

    intelligence_answer = build_intelligence_routed_answer(
        normalized_query,
        context={"entrypoint": "cockpit_command_plan"},
    )
    provider = configured_provider_state(root)
    live_sources = live_source_state(root)
    evidence = evidence_preview(root, normalized_query)
    universes = source_universe_matches(root, normalized_query)
    knowledge = local_knowledge_matches(normalized_query)
    system_search = system_search_matches(root, normalized_query)
    technology = technology_matches(normalized_query)
    source_packs = local_source_pack_matches(root, normalized_query)
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "planned" if normalized_query else "blocked_empty_query",
        "generated_at": now(),
        "query": normalized_query,
        "search_plan": plan,
        "intelligence_answer": intelligence_answer,
        "local_knowledge_matches": knowledge,
        "system_search_matches": system_search,
        "technology_matches": technology,
        "local_source_pack_matches": source_packs,
        "source_universe_matches": universes,
        "evidence_preview": evidence,
        "live_sources": live_sources,
        "provider": provider,
        "authority": {
            "network_request_performed": False,
            "provider_execution_performed": False,
            "body_read_performed": False,
            "runtime_truth_mutation": False,
            "automatic_update_performed": False,
            "evidence_promotion": "manual_review_required",
        },
        "next_actions": plan_next_actions(provider, len(evidence)),
    }


def persist_latest_command_plan(payload: dict[str, Any], project_root: Path | str | None = None) -> None:
    root = Path(project_root or Path.cwd()).resolve()
    out_dir = root / "data" / "operator" / "search_command"
    out_dir.mkdir(parents=True, exist_ok=True)
    latest = out_dir / "latest_command_plan.json"
    log = out_dir / "command_log.json"
    latest.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    records = read_json(log, [])
    if not isinstance(records, list):
        records = []
    records.append(payload)
    log.write_text(json.dumps(records[-100:], indent=2, sort_keys=True), encoding="utf-8")


def command_history(project_root: Path | str | None = None, limit: int = 12) -> dict[str, Any]:
    root = Path(project_root or Path.cwd()).resolve()
    log = root / "data" / "operator" / "search_command" / "command_log.json"
    records = read_json(log, [])
    if not isinstance(records, list):
        records = []
    clean_limit = max(1, min(int(limit or 12), 50))
    items: list[dict[str, Any]] = []
    for item in reversed([record for record in records if isinstance(record, dict)]):
        evidence = item.get("evidence_preview", [])
        universes = item.get("source_universe_matches", [])
        knowledge = item.get("local_knowledge_matches", {})
        knowledge_results = knowledge.get("results", []) if isinstance(knowledge, dict) else []
        system_search = item.get("system_search_matches", {})
        system_results = system_search.get("results", []) if isinstance(system_search, dict) else []
        technology = item.get("technology_matches", {})
        technology_results = technology.get("results", []) if isinstance(technology, dict) else []
        source_packs = item.get("local_source_pack_matches", {})
        source_pack_results = source_packs.get("results", []) if isinstance(source_packs, dict) else []
        actions = item.get("next_actions", [])
        connected = item.get("connected_search", {}) if isinstance(item.get("connected_search"), dict) else {}
        provider = item.get("provider", {}) if isinstance(item.get("provider"), dict) else {}
        connected_provider = connected.get("provider", {}) if isinstance(connected.get("provider"), dict) else {}
        items.append(
            {
                "query": item.get("query", ""),
                "status": item.get("status", "unknown"),
                "generated_at": item.get("generated_at"),
                "intent": item.get("search_plan", {}).get("intent_label") if isinstance(item.get("search_plan"), dict) else None,
                "provider_status": provider.get("status") or connected_provider.get("status"),
                "connected_search_status": connected.get("status"),
                "evidence_count": len(evidence) if isinstance(evidence, list) else 0,
                "local_knowledge_count": len(knowledge_results) if isinstance(knowledge_results, list) else 0,
                "system_result_count": len(system_results) if isinstance(system_results, list) else 0,
                "technology_count": len(technology_results) if isinstance(technology_results, list) else 0,
                "local_source_pack_count": len(source_pack_results) if isinstance(source_pack_results, list) else 0,
                "source_universe_count": len(universes) if isinstance(universes, list) else 0,
                "next_action_count": len(actions) if isinstance(actions, list) else 0,
                "authority": item.get("authority", {}),
            }
        )
        if len(items) >= clean_limit:
            break
    return {
        "schema_version": HISTORY_SCHEMA_VERSION,
        "status": "ready" if items else "empty",
        "source": "data/operator/search_command/command_log.json",
        "count": len(items),
        "total_count": len([record for record in records if isinstance(record, dict)]),
        "items": items,
    }
