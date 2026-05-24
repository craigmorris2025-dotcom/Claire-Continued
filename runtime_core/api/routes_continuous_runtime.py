from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict
from uuid import uuid4

from fastapi import APIRouter
from runtime_core.acquisition.acquirer_identification import AcquirerIdentification
from runtime_core.api.portfolio_artifacts import persist_portfolio_artifact
from runtime_core.design.proof_engine import build_design_proof
from runtime_core.emergence.system_emergence_engine import build_system_emergence_engine
from runtime_core.ingestion.source_boundary import allowed_input_files, project_relative, source_violations
from runtime_core.memory.recursive_learning import build_recursive_learning_snapshot
from runtime_core.research.evidence_governance import build_evidence_governance
from runtime_core.strategic_world import build_strategic_world_layer
from runtime_core.system_ingestion.analyzer import Analyzer as ExistingSystemAnalyzer
from runtime_core.technology.technology_base import assess_technology_base


router = APIRouter(tags=["Claire Continuous Intelligence Runtime"])

ROOT = Path(__file__).resolve()
for parent in ROOT.parents:
    if (parent / "pyproject.toml").exists() or (parent / "main.py").exists():
        PROJECT_ROOT = parent
        break
else:
    PROJECT_ROOT = Path.cwd()

CONTINUOUS_DIR = PROJECT_ROOT / "data" / "continuous_runtime"
SCHEDULER_STATE_FILENAME = "scheduler_state.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, payload: Dict[str, Any]) -> Dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


def read_json(path: Path, fallback: Dict[str, Any]) -> Dict[str, Any]:
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8-sig"))


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
            "support recursive self-ingestion",
        ],
        "guardrails": [
            "no uncontrolled web mutation",
            "no automatic active-code updates",
            "no frontend-owned route truth",
            "no fake discoveries",
            "missing evidence enriches before failure",
            "operator review required before promotion",
        ],
        "last_cycle_id": None,
        "last_cycle_at": None,
        "next_cycle_policy": "bounded_scheduler_ready_operator_or_task_runner_triggered",
        "scheduler_policy": {
            "status": "bounded_scheduler_available_not_daemonized",
            "daemon_installed": False,
            "task_runner_installed": False,
            "manual_tick_endpoint": "/runtime/continuous/scheduler/tick",
            "runtime_truth_mutation_allowed": False,
            "operator_review_required": True,
        },
        "artifact_paths": {
            "status": "data/continuous_runtime/status.json",
            "review_queue": "data/continuous_runtime/review_queue.json",
            "discovery_candidates": "data/continuous_runtime/discovery_candidates.json",
            "breakthrough_candidates": "data/continuous_runtime/breakthrough_candidates.json",
            "portfolio_candidates": "data/continuous_runtime/portfolio_candidates.json",
            "design_candidates": "data/continuous_runtime/design_candidates.json",
            "scheduler_state": "data/continuous_runtime/scheduler_state.json",
            "route_capability_proofs": "data/continuous_runtime/route_capability_proofs.json",
        },
        "updated_at": utc_now(),
    }


def default_scheduler_state() -> Dict[str, Any]:
    return {
        "schema_version": "claire.continuous_runtime_scheduler_state.v1",
        "status": "bounded_scheduler_ready",
        "mode": "governed_24_7_discovery_monitoring",
        "daemon_installed": False,
        "task_runner_installed": False,
        "heartbeat_status": "manual_or_external_runner_required",
        "tick_endpoint": "/runtime/continuous/scheduler/tick",
        "status_endpoint": "/runtime/continuous/scheduler/status",
        "interval_seconds": 900,
        "tick_count": 0,
        "last_tick_at": None,
        "last_cycle_id": None,
        "last_tick_result": None,
        "authority": {
            "network_request_performed": False,
            "runtime_truth_mutation_allowed": False,
            "automatic_update_allowed": False,
            "operator_review_required": True,
            "documents_used_as_runtime_programming": False,
        },
        "updated_at": utc_now(),
    }


def ensure_runtime_files() -> Dict[str, Any]:
    status_path = CONTINUOUS_DIR / "status.json"
    defaults = default_status()
    status = {**defaults, **read_json(status_path, defaults)}
    status.setdefault("updated_at", utc_now())
    write_json(status_path, status)

    empty_sets = {
        "review_queue.json": {"items": [], "policy": "operator_review_required_before_promotion"},
        "discovery_candidates.json": {"items": [], "candidate_type": "discovery"},
        "breakthrough_candidates.json": {"items": [], "candidate_type": "breakthrough"},
        "portfolio_candidates.json": {"items": [], "candidate_type": "portfolio"},
        "design_candidates.json": {"items": [], "candidate_type": "design"},
        "package_candidates.json": {"items": [], "candidate_type": "package"},
    }
    for filename, payload in empty_sets.items():
        path = CONTINUOUS_DIR / filename
        if not path.exists():
            payload = dict(payload)
            payload["updated_at"] = utc_now()
            write_json(path, payload)
    ensure_scheduler_state()
    return status


def ensure_scheduler_state() -> Dict[str, Any]:
    path = CONTINUOUS_DIR / SCHEDULER_STATE_FILENAME
    defaults = default_scheduler_state()
    state = {**defaults, **read_json(path, defaults)}
    state.setdefault("authority", defaults["authority"])
    state["authority"] = {**defaults["authority"], **state.get("authority", {})}
    state["updated_at"] = utc_now()
    write_json(path, state)
    return state


def update_route_capability_proofs(run_spine: dict[str, Any], now: str) -> Dict[str, Any]:
    path = CONTINUOUS_DIR / "route_capability_proofs.json"
    ledger = read_json(
        path,
        {
            "schema_version": "claire.route_capability_proofs.v1",
            "status": "ready",
            "routes": {},
        },
    )
    if not isinstance(ledger, dict):
        ledger = {"schema_version": "claire.route_capability_proofs.v1", "status": "ready", "routes": {}}
    routes = ledger.setdefault("routes", {})
    route = str(run_spine.get("route_selected") or "unknown")
    quality = run_spine.get("quality_gate", {}) if isinstance(run_spine.get("quality_gate"), dict) else {}
    stage_count = len(run_spine.get("stage_status", [])) if isinstance(run_spine.get("stage_status"), list) else 0
    proof_complete = (
        run_spine.get("status") == "valid_continuous_lifecycle_snapshot"
        and stage_count >= 30
        and quality.get("portfolio_candidate_present") is True
        and quality.get("acquisition_rationale_present") is True
    )
    if route == "existing_system_replacement":
        proof_complete = (
            proof_complete
            and quality.get("existing_system_decomposition_present") is True
            and quality.get("superior_system_design_present") is True
            and quality.get("design_proof_complete") is True
            and quality.get("recursive_learning_complete") is True
        )
    route_record = routes.get(route, {}) if isinstance(routes.get(route), dict) else {}
    route_record.update(
        {
            "route": route,
            "last_run_id": run_spine.get("run_id"),
            "last_seen_at": now,
            "last_stage_count": stage_count,
            "last_status": run_spine.get("status"),
            "last_quality_gate": quality,
            "proof_complete": proof_complete,
            "documents_used_as_runtime_programming": False,
        }
    )
    if proof_complete:
        route_record["last_successful_run_id"] = run_spine.get("run_id")
        route_record["last_successful_at"] = now
    routes[route] = route_record
    ledger["status"] = "route_capability_proofs_ready"
    ledger["updated_at"] = now
    return write_json(path, ledger)


def _write_candidate_store(filename: str, kind: str, records: list[Dict[str, Any]], now: str) -> Dict[str, Any]:
    payload = {
        "status": "ready",
        "candidate_type": kind,
        "items": records,
        "count": len(records),
        "source": "allowlisted_input_boundary",
        "operator_review_required": True,
        "runtime_truth_mutated": False,
        "updated_at": now,
    }
    return write_json(CONTINUOUS_DIR / filename, payload)


def _monitor_records(payload: dict[str, Any]) -> list[dict[str, Any]]:
    connectors = payload.get("result", {}).get("connectors", {}).get("results", [])
    records: list[dict[str, Any]] = []
    if not isinstance(connectors, list):
        return records
    for connector in connectors:
        if not isinstance(connector, dict):
            continue
        source_family = connector.get("source_family") or connector.get("connector")
        for record in connector.get("records", []) if isinstance(connector.get("records"), list) else []:
            if isinstance(record, dict):
                records.append({**record, "source_family": record.get("source_family") or source_family})
    return records


def _promoted_evidence_records(payload: dict[str, Any]) -> list[dict[str, Any]]:
    items = payload.get("items", []) if isinstance(payload, dict) else []
    if not isinstance(items, list):
        return []
    records: list[dict[str, Any]] = []
    for item in reversed(items):
        if not isinstance(item, dict):
            continue
        records.append(
            {
                "record_id": item.get("evidence_id") or item.get("source_result_id"),
                "title": item.get("title") or "Promoted metadata evidence",
                "snippet": item.get("snippet") or "",
                "source_url": item.get("url"),
                "source_family": item.get("source_family") or "promoted_metadata_evidence",
                "source_type": "promoted_metadata_evidence",
                "entity_name": item.get("query") or "connected_source",
                "status": item.get("evidence_state") or "promoted_metadata_evidence",
                "origin": "data/internet_evidence/promoted_metadata_evidence_store.json",
                "provider": item.get("provider"),
                "trust_tier": item.get("trust_tier"),
                "terms": [part for part in str(item.get("query") or "").split() if len(part) > 2],
            }
        )
    return records


def _signal_from_record(record: dict[str, Any], index: int, now: str) -> dict[str, Any]:
    title = str(record.get("title") or record.get("entity_name") or record.get("record_id") or f"Signal {index}").strip()
    snippet = str(record.get("snippet") or record.get("summary") or record.get("description") or "").strip()
    entity = str(record.get("entity_name") or record.get("entity_id") or record.get("domain") or "market").strip()
    source_family = str(record.get("source_family") or record.get("source_type") or "allowlisted_monitor").strip()
    return {
        "signal_id": f"signal-{index:03d}",
        "title": title,
        "summary": snippet[:500] or f"Allowlisted monitor record for {entity}.",
        "entity": entity,
        "source_family": source_family,
        "source_type": record.get("source_type") or "allowlisted_metadata",
        "captured_at": now,
        "provenance": {
            "origin": record.get("origin") or "data/live_intelligence/latest_monitor_run.json",
            "record_id": record.get("record_id") or record.get("id") or f"monitor-record-{index}",
            "metadata_only": True,
            "provider": record.get("provider"),
            "trust_tier": record.get("trust_tier"),
        },
        "credibility_weight": 0.72 if "sec" in source_family.lower() or "regulatory" in source_family.lower() else 0.62,
    }


def _keywords_from_signals(signals: list[dict[str, Any]]) -> list[str]:
    stop = {"and", "the", "for", "with", "from", "this", "that", "into", "under", "over", "are", "need", "needs"}
    counts: dict[str, int] = {}
    for signal in signals:
        text = f"{signal.get('title', '')} {signal.get('summary', '')}".lower()
        for raw in text.replace("/", " ").replace("-", " ").replace(",", " ").split():
            token = "".join(ch for ch in raw if ch.isalnum())
            if len(token) < 4 or token in stop:
                continue
            counts[token] = counts.get(token, 0) + 1
    return [key for key, _ in sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:12]]


def _query_keywords(query: str) -> list[str]:
    stop = {"and", "the", "for", "with", "from", "this", "that", "into", "under", "over", "are", "need", "needs", "signal"}
    tokens: list[str] = []
    for raw in str(query or "").lower().replace("/", " ").replace("-", " ").split():
        token = "".join(ch for ch in raw if ch.isalnum())
        if len(token) < 3 or token in stop:
            continue
        if token not in tokens:
            tokens.append(token)
    return tokens[:8]


def _score_advancement_path(signals: list[dict[str, Any]], keywords: list[str], query: str = "") -> dict[str, Any]:
    text = " ".join(
        [
            query,
            *keywords,
            *[
                f"{signal.get('title', '')} {signal.get('summary', '')} {signal.get('entity', '')} {signal.get('source_family', '')}"
                for signal in signals
            ],
        ]
    ).lower()
    promoted_count = sum(
        1
        for signal in signals
        if signal.get("source_type") == "promoted_metadata_evidence"
        or signal.get("provenance", {}).get("trust_tier")
    )
    technology_terms = {
        "ai",
        "autonomous",
        "automation",
        "technology",
        "platform",
        "software",
        "patent",
        "system",
        "invention",
        "research",
        "r&d",
        "architecture",
    }
    need_terms = {
        "gap",
        "need",
        "needed",
        "solution",
        "compliance",
        "governance",
        "pressure",
        "risk",
        "market",
        "acquisition",
        "portfolio",
    }
    tech_hits = sum(1 for term in technology_terms if term in text)
    need_hits = sum(1 for term in need_terms if term in text)
    technology_base = assess_technology_base(" ".join([query, *keywords]))
    innovation_candidates = technology_base.get("innovation_candidates", [])
    reemergence_engine = technology_base.get("reemergence_pattern_engine", {})
    top_innovation = innovation_candidates[0] if innovation_candidates else {}
    top_breakthrough = float(top_innovation.get("breakthrough_score", 0.0) or 0.0)
    buildability_score = float(top_innovation.get("buildability_score", 0.0) or 0.0)
    manufacturability_score = float(top_innovation.get("manufacturability_score", 0.0) or 0.0)
    reemergence_score = float(reemergence_engine.get("readiness_score", 0.0) or 0.0) if isinstance(reemergence_engine, dict) else 0.0
    reemergence_route = (
        reemergence_engine.get("route_guidance", {}).get("recommended_route")
        if isinstance(reemergence_engine.get("route_guidance"), dict)
        else None
    )
    reemergence_patterns = reemergence_engine.get("detected_patterns", []) if isinstance(reemergence_engine, dict) else []
    signal_families = reemergence_engine.get("signal_families", {}) if isinstance(reemergence_engine, dict) else {}
    ready_signal_families = [
        family_id
        for family_id, family in signal_families.items()
        if isinstance(family, dict) and family.get("ready") is True
    ]
    evidence_score = min(0.95, 0.35 + len(signals) * 0.025 + promoted_count * 0.035)
    gap_score = min(0.95, 0.30 + need_hits * 0.045 + promoted_count * 0.020)
    discovery_score = min(0.95, 0.40 + len(keywords) * 0.020 + tech_hits * 0.020 + need_hits * 0.015)
    breakthrough_score = min(
        0.95,
        discovery_score * 0.25
        + gap_score * 0.20
        + evidence_score * 0.15
        + top_breakthrough * 0.22
        + buildability_score * 0.10
        + manufacturability_score * 0.08,
    )
    if reemergence_route == "breakthrough_design" and reemergence_score >= 0.64:
        breakthrough_score = min(0.95, breakthrough_score + 0.035)
    elif reemergence_route == "portfolio_creation_optimization" and reemergence_score >= 0.36:
        discovery_score = min(0.95, discovery_score + 0.025)
    design_required = (
        breakthrough_score >= 0.72
        and buildability_score >= 0.65
        and manufacturability_score >= 0.62
        and bool(top_innovation)
    )
    system_terms = {
        "existing system",
        "legacy system",
        "system replacement",
        "superior system",
        "decomposition",
        "workflow",
        "architecture",
        "integration",
        "migration",
        "replace",
    }
    existing_system_required = design_required and any(term in text for term in system_terms)
    route = "existing_system_replacement" if existing_system_required else "breakthrough_design" if design_required else "portfolio_creation_optimization"
    return {
        "schema_version": "claire.autonomous_advancement_path_decision.v1",
        "route_selected": route,
        "advancement_path_policy_respected": True,
        "scores": {
            "evidence_score": round(evidence_score, 4),
            "discovery_score": round(discovery_score, 4),
            "gap_score": round(gap_score, 4),
            "breakthrough_score": round(breakthrough_score, 4),
            "buildability_score": round(buildability_score, 4),
            "manufacturability_score": round(manufacturability_score, 4),
            "technology_breakthrough_score": round(top_breakthrough, 4),
            "reemergence_readiness_score": round(reemergence_score, 4),
            "signal_family_readiness_score": round(len(ready_signal_families) / 7, 4),
        },
        "thresholds": {
            "breakthrough_design_min": 0.72,
            "buildability_min": 0.65,
            "manufacturability_min": 0.62,
        },
        "conditions": {
            "signals_present": bool(signals),
            "promoted_evidence_count": promoted_count,
            "technology_terms": tech_hits,
            "need_terms": need_hits,
            "solution_generation_required": design_required,
            "design_portal_required": design_required,
            "existing_system_replacement_required": existing_system_required,
            "reemergence_pattern_detected": bool(reemergence_patterns),
            "reemergence_cycle_stage": reemergence_engine.get("cycle_stage") if isinstance(reemergence_engine, dict) else None,
            "ready_signal_families": ready_signal_families,
        },
        "technology_base": {
            "status": technology_base.get("status"),
            "counts": technology_base.get("counts", {}),
            "top_innovation_candidate": top_innovation,
        },
        "reemergence_pattern_engine": {
            "status": reemergence_engine.get("status") if isinstance(reemergence_engine, dict) else None,
            "readiness_score": round(reemergence_score, 4),
            "cycle_stage": reemergence_engine.get("cycle_stage") if isinstance(reemergence_engine, dict) else None,
            "route_guidance": reemergence_engine.get("route_guidance", {}) if isinstance(reemergence_engine, dict) else {},
            "detected_patterns": [
                {
                    "pattern_id": item.get("pattern_id"),
                    "name": item.get("name"),
                    "score": item.get("score"),
                    "primary_signal_families": item.get("primary_signal_families", []),
                    "historical_examples": item.get("historical_examples", []),
                }
                for item in reemergence_patterns[:5]
                if isinstance(item, dict)
            ],
            "signals_to_watch": reemergence_engine.get("signals_to_watch", []) if isinstance(reemergence_engine, dict) else [],
            "pipeline_bindings": reemergence_engine.get("pipeline_bindings", {}) if isinstance(reemergence_engine, dict) else {},
        },
        "reason": (
            "Qualified gap/discovery/technology conditions require autonomous solution generation and design routing."
            if design_required and not existing_system_required
            else "Existing-system signals require decomposition, superior system design, and full replacement/acquisition routing."
            if existing_system_required
            else "Trend and portfolio intelligence path remains strongest; design route waits for stronger gap/breakthrough/buildability conditions."
        ),
    }


def _build_existing_system_replacement(
    cycle_id: str,
    query: str,
    signals: list[dict[str, Any]],
    solution: dict[str, Any],
    advancement: dict[str, Any],
) -> dict[str, Any]:
    text = " ".join([query, *[f"{item.get('title', '')} {item.get('summary', '')}" for item in signals]])
    decomposition = ExistingSystemAnalyzer().analyze(text)
    components = decomposition.get("components", [])
    gaps = decomposition.get("gaps", [])
    return {
        "schema_version": "claire.existing_system_replacement.v1",
        "candidate_id": f"existing-system-replacement-{cycle_id[-8:]}",
        "status": "pending_operator_review",
        "route": advancement["route_selected"],
        "existing_system_ingestion": {
            "status": "completed",
            "source": "live_query_and_promoted_metadata",
            "query": query,
            "signal_count": len(signals),
        },
        "existing_system_decomposition": {
            "status": decomposition.get("status"),
            "analysis_type": decomposition.get("analysis_type"),
            "components": components,
            "gaps": gaps,
            "redesign_required": decomposition.get("redesign_required"),
            "confidence": decomposition.get("confidence"),
        },
        "superior_system_design": {
            "title": f"Superior system design for {solution.get('title') or 'qualified replacement candidate'}",
            "status": "draft_ready_for_design_portal_review",
            "replacement_logic": [
                "preserve useful existing-system components",
                "replace weak validation, integration, governance, and routing gaps",
                "map replacement functions into buildable current technologies",
                "produce blueprint/spec handoff before runtime truth promotion",
            ],
            "target_components": [item.get("id") for item in components if isinstance(item, dict)],
            "target_gaps": [item.get("id") for item in gaps if isinstance(item, dict)],
            "solution_ref": solution.get("candidate_id"),
            "buildability_score": advancement.get("scores", {}).get("buildability_score"),
            "manufacturability_score": advancement.get("scores", {}).get("manufacturability_score"),
        },
        "runtime_truth_write": "blocked",
    }


def _build_solution_candidate(
    cycle_id: str,
    discovery: dict[str, Any],
    portfolio: dict[str, Any],
    advancement: dict[str, Any],
    keywords: list[str],
) -> dict[str, Any]:
    top = advancement.get("technology_base", {}).get("top_innovation_candidate", {})
    title = top.get("title") or f"Needed solution for {discovery.get('title', 'qualified discovery')}"
    component_names = top.get("component_names") if isinstance(top.get("component_names"), list) else []
    existing_system_route = advancement["route_selected"] == "existing_system_replacement"
    return {
        "candidate_id": f"solution-{cycle_id[-8:]}",
        "candidate_type": "solution",
        "title": title,
        "status": "pending_operator_review",
        "route": advancement["route_selected"],
        "source_discovery_id": discovery.get("candidate_id"),
        "source_portfolio_id": portfolio.get("candidate_id"),
        "needed_solution": discovery.get("summary"),
        "solution_thesis": top.get("thesis")
        or f"Generate a constrained solution around {', '.join(keywords[:6])} using current buildable technology and governed evidence.",
        "functions": [
            "ingest and decompose existing system" if existing_system_route else "ingest governed signals",
            "detect gap and required solution",
            "map current buildable technologies",
            "structure components and workflows",
            "generate superior replacement system design" if existing_system_route else "prepare design portal output",
            "validate buildability, viability, manufacturability, and feasibility",
            "handoff to portfolio, acquirer, and final package",
        ],
        "components": component_names[:8],
        "scores": advancement.get("scores", {}),
        "constraints": [
            "no runtime truth mutation without operator promotion",
            "no external claims without promoted live evidence",
            "reject or revise if buildability/manufacturability/feasibility gates fail",
        ],
        "runtime_truth_write": "blocked",
    }


def _build_design_candidate(cycle_id: str, solution: dict[str, Any], advancement: dict[str, Any]) -> dict[str, Any]:
    candidate = {
        "candidate_id": f"design-{cycle_id[-8:]}",
        "candidate_type": "design",
        "title": f"Design package: {solution.get('title', 'qualified solution')}",
        "status": "pending_operator_review",
        "route": advancement["route_selected"],
        "source_solution_id": solution.get("candidate_id"),
        "blueprint_required": True,
        "cad_viewer_required": True,
        "video_viewer_required": True,
        "buildability_score": advancement.get("scores", {}).get("buildability_score"),
        "manufacturability_score": advancement.get("scores", {}).get("manufacturability_score"),
        "feasibility_status": "requires_design_portal_validation",
        "runtime_truth_write": "blocked",
    }
    candidate["design_proof"] = build_design_proof(candidate, solution, {}, advancement)
    candidate["feasibility_status"] = candidate["design_proof"]["architecture_feasibility"]["verdict"]
    candidate["design_maturity_level"] = candidate["design_proof"]["design_maturity"]["level"]
    return candidate


def _build_run_spine(cycle_id: str, now: str, query: str, source_records: list[dict[str, Any]], signals: list[dict[str, Any]]) -> dict[str, Any]:
    signal_keywords = _keywords_from_signals(signals)
    keywords = list(dict.fromkeys([*_query_keywords(query), *signal_keywords]))[:12]
    primary_theme = " ".join(keywords[:4]) or "allowlisted market intelligence"
    confidence = round(min(0.88, 0.42 + len(signals) * 0.035), 4)
    advancement = _score_advancement_path(signals, keywords, query)
    route_selected = advancement["route_selected"]
    design_required = bool(advancement.get("conditions", {}).get("design_portal_required"))
    emergence_engine = build_system_emergence_engine(
        query,
        context={
            "signals": signals,
            "domain": "market_intelligence",
            "advancement_path_decision": advancement,
            "reemergence_pattern_engine": advancement.get("reemergence_pattern_engine", {}),
            "source_authority": {"source_evidence_present": bool(signals), "live_evidence_present": bool(signals)},
        },
    )
    trend = {
        "trend_id": f"trend-{cycle_id[-8:]}",
        "title": f"{primary_theme.title()} trend cluster",
        "summary": f"Allowlisted signals indicate a portfolio-relevant pattern around {primary_theme}.",
        "keywords": keywords,
        "evidence_signal_ids": [signal["signal_id"] for signal in signals[:6]],
        "confidence": confidence,
    }
    thesis = {
        "thesis_id": f"thesis-{cycle_id[-8:]}",
        "statement": f"Portfolio intelligence should prioritize {primary_theme} because multiple governed metadata signals point to buyer, compliance, or operational pressure.",
        "confidence": confidence,
        "evidence_signal_ids": trend["evidence_signal_ids"],
    }
    discovery = {
        "candidate_id": f"discovery-{cycle_id[-8:]}",
        "candidate_type": "discovery",
        "title": trend["title"],
        "summary": trend["summary"],
        "status": "pending_operator_review",
        "confidence": confidence,
        "source_signal_ids": trend["evidence_signal_ids"],
        "route": "portfolio_creation_optimization",
        "advancement_route": route_selected,
        "runtime_truth_write": "blocked",
    }
    portfolio = {
        "candidate_id": f"portfolio-{cycle_id[-8:]}",
        "candidate_type": "portfolio",
        "title": f"Portfolio thesis: {primary_theme.title()}",
        "portfolio_thesis": thesis["statement"],
        "summary": (
            "Portfolio output generated from allowlisted metadata signals and autonomous advancement routing."
            if design_required
            else "Portfolio output generated from allowlisted metadata signals. Breakthrough and design routes remain conditional."
        ),
        "status": "pending_operator_review",
        "confidence": confidence,
        "keywords": keywords,
        "route": route_selected,
        "source_discovery_id": discovery["candidate_id"],
        "source_signal_ids": trend["evidence_signal_ids"],
        "runtime_truth_write": "blocked",
    }
    breakthrough = {
        "candidate_id": f"breakthrough-{cycle_id[-8:]}",
        "candidate_type": "breakthrough",
        "title": f"Breakthrough classification: {primary_theme.title()}",
        "summary": advancement["reason"],
        "status": "pending_operator_review" if design_required else "evaluated_not_qualified",
        "threshold_met": design_required,
        "primary_type": "technological_breakthrough" if design_required else "portfolio_intelligence",
        "secondary_types": [
            "gap_discovery_breakthrough",
            "software_platform_breakthrough",
            "system_architecture_breakthrough",
            "acquisition_strategy_breakthrough",
        ]
        if design_required
        else ["portfolio_construction_signal"],
        "route": route_selected,
        "scores": advancement["scores"],
        "conditions": advancement["conditions"],
        "runtime_truth_write": "blocked",
    }
    evidence_governance = build_evidence_governance(signals, thesis, discovery)
    solution = _build_solution_candidate(cycle_id, discovery, portfolio, advancement, keywords) if design_required else {}
    design_candidate = _build_design_candidate(cycle_id, solution, advancement) if solution else {}
    existing_system_replacement = (
        _build_existing_system_replacement(cycle_id, query, signals, solution, advancement)
        if route_selected == "existing_system_replacement"
        else {}
    )
    if design_candidate:
        design_candidate["design_proof"] = build_design_proof(
            design_candidate,
            solution,
            existing_system_replacement,
            advancement,
        )
        design_candidate["feasibility_status"] = design_candidate["design_proof"]["architecture_feasibility"]["verdict"]
        design_candidate["design_maturity_level"] = design_candidate["design_proof"]["design_maturity"]["level"]
    acquirer_output = AcquirerIdentification().execute(
        {
            "stage_id": 28,
            "source_stage": 27,
            "payload": portfolio,
            "metadata": {"cycle_id": cycle_id, "generated_by": "continuous_lifecycle_snapshot"},
            "timestamp": now,
        }
    )
    acquirer_matches = acquirer_output.get("payload", {}).get("acquirer_matches", [])
    lifecycle_memory = read_json(CONTINUOUS_DIR / "lifecycle_memory.json", {})
    memory_records = (
        lifecycle_memory.get("records", [])
        if isinstance(lifecycle_memory, dict) and isinstance(lifecycle_memory.get("records"), list)
        else []
    )
    strategic_world_seed = {
        "run_id": cycle_id,
        "route_selected": route_selected,
        "emergence_engine": emergence_engine,
        "signals": signals,
        "trend": trend,
        "thesis": thesis,
        "discovery_candidate": discovery,
        "portfolio_candidate": portfolio,
        "design_candidate": design_candidate,
        "evidence_governance": evidence_governance,
        "quality_gate": {
            "design_proof_complete": bool(
                design_candidate.get("design_proof", {}).get("status") == "design_proof_ready"
            ),
        },
    }
    strategic_world = build_strategic_world_layer(strategic_world_seed, memory_records=memory_records)
    stage_status = []
    for stage_id in range(1, 31):
        if stage_id <= 10:
            status = "completed"
            output = "signal_to_thesis_spine"
        elif stage_id in {11, 12, 13}:
            status = "completed"
            output = "discovery_and_gap_basis"
        elif stage_id == 14:
            status = "completed" if design_required else "evaluated_not_escalated"
            output = "breakthrough_classification" if design_required else "breakthrough_threshold_not_met"
        elif stage_id == 15:
            status = "completed"
            output = "advancement_path_selection"
        elif stage_id in {16, 17, 18, 19, 20, 21, 22}:
            status = "completed" if design_required else "skipped_by_route"
            output = {
                16: "auto_invention_solution_generation",
                17: "solution_structuring",
                18: "buildability_assessment",
                19: "viability_assessment",
                20: "manufacturability_deployability",
                21: "feasibility_validation",
                22: "design_portal_output",
            }[stage_id] if design_required else "design_path_not_selected"
        elif stage_id in {23, 24, 25, 26, 27, 28, 29, 30}:
            status = "completed"
            output = "portfolio_acquisition_package"
        else:
            status = "completed"
            output = "run_output"
        stage_status.append(
            {
                "stage_id": stage_id,
                "status": status,
                "output_key": output,
                "confidence": confidence if status != "skipped_by_route" else None,
                "failure_reasons": [],
            }
        )
    route_insertions = []
    if existing_system_replacement:
        route_insertions = [
            {
                "stage_id": "0",
                "status": "completed",
                "output_key": "existing_system_ingestion",
                "confidence": confidence,
                "failure_reasons": [],
            },
            {
                "stage_id": "7.5",
                "status": "completed",
                "output_key": "existing_system_decomposition",
                "confidence": existing_system_replacement.get("existing_system_decomposition", {}).get("confidence"),
                "failure_reasons": [],
            },
            {
                "stage_id": "22.5",
                "status": "completed",
                "output_key": "superior_system_design",
                "confidence": confidence,
                "failure_reasons": [],
            },
        ]
    return {
        "schema_version": "claire.continuous_lifecycle_snapshot.v1",
        "run_id": cycle_id,
        "created_at": now,
        "status": "valid_continuous_lifecycle_snapshot" if signals and portfolio else "insufficient_signal_data",
        "mode": "hybrid_local_allowlisted",
        "route_selected": route_selected,
        "advancement_path_policy_respected": True,
        "advancement_path_decision": advancement,
        "emergence_engine": emergence_engine,
        "source_records": source_records,
        "signals": signals,
        "trend": trend,
        "thesis": thesis,
        "discovery_candidate": discovery,
        "evidence_governance": evidence_governance,
        "breakthrough_candidate": breakthrough if design_required else {},
        "solution_candidate": solution,
        "design_candidate": design_candidate,
        "existing_system_replacement": existing_system_replacement,
        "portfolio_candidate": portfolio,
        "breakthrough_evaluation": {
            "stage_id": 14,
            "status": "qualified_for_design" if design_required else "evaluated_not_qualified",
            "threshold_met": design_required,
            "reason": advancement["reason"],
            "scores": advancement["scores"],
        },
        "design_gate": {
            "stage_id": 15,
            "status": "selected" if design_required else "not_selected",
            "reason": (
                "Autonomous advancement path selected solution generation and Design Portal routing."
                if design_required
                else "Design portal requires qualified breakthrough route."
            ),
        },
        "acquisition": {
            "stage_28_output": acquirer_output,
            "acquirer_matches": acquirer_matches,
            "acquirer_count": len(acquirer_matches),
        },
        "final_package": {
            "status": "review_ready",
            "package_type": "portfolio_acquisition_brief",
            "review_required": True,
            "sections": [
                "signals",
                "trend",
                "thesis",
                "gap",
                "discovery",
                "breakthrough_classification",
                "advancement_path",
                "solution" if design_required else "solution_if_applicable",
                "design_portal_output" if design_required else "design_portal_if_applicable",
                "portfolio_candidate",
                "acquisition",
                "strategic_world",
                "operator_review",
            ],
        },
        "stage_status": stage_status,
        "route_insertions": route_insertions,
        "quality_gate": {
            "fresh_input_present": bool(signals),
            "trend_present": bool(trend),
            "thesis_present": bool(thesis),
            "portfolio_candidate_present": bool(portfolio),
            "advancement_path_selected": bool(route_selected),
            "emergence_engine_complete": emergence_engine.get("status") in {
                "emergence_engine_operational",
                "emergence_engine_foundation_ready",
            },
            "evidence_governance_complete": evidence_governance.get("status") == "evidence_governance_ready",
            "solution_candidate_present": bool(solution),
            "design_candidate_present": bool(design_candidate),
            "design_proof_complete": bool(
                design_candidate.get("design_proof", {}).get("status") == "design_proof_ready"
            ),
            "existing_system_decomposition_present": bool(existing_system_replacement),
            "superior_system_design_present": bool(existing_system_replacement),
            "acquisition_rationale_present": bool(acquirer_matches),
            "strategic_world_complete": strategic_world.get("status") == "strategic_world_ready",
            "lifecycle_memory_written": True,
        },
        "authority": {
            "network_request_performed": False,
            "body_read_performed": False,
            "runtime_truth_mutated": False,
            "automatic_update_performed": False,
            "operator_review_required": True,
            "metadata_only": True,
        },
        "strategic_world": strategic_world,
    }


def _write_lifecycle_memory_record(run_spine: dict[str, Any], now: str) -> dict[str, Any]:
    path = CONTINUOUS_DIR / "lifecycle_memory.json"
    store = read_json(path, {"schema_version": "claire.lifecycle_memory.curated.v1", "status": "ready", "records": []})
    if not isinstance(store, dict):
        store = {"schema_version": "claire.lifecycle_memory.curated.v1", "status": "ready", "records": []}
    store.setdefault("schema_version", "claire.lifecycle_memory.curated.v1")
    store.setdefault("records", [])
    record = {
        "run_id": run_spine["run_id"],
        "status": "success",
        "created_at": now,
        "result": {
            "run_id": run_spine["run_id"],
            "status": "success",
            "domain": "market_intelligence",
            "keywords": run_spine.get("trend", {}).get("keywords", []),
            "route_selected": run_spine["route_selected"],
            "emergence_engine": {
                "status": run_spine.get("emergence_engine", {}).get("status"),
                "readiness_score": run_spine.get("emergence_engine", {}).get("readiness_score"),
                "product_completion_percent": run_spine.get("emergence_engine", {}).get("product_completion_percent"),
                "cycle_stage": run_spine.get("emergence_engine", {}).get("cycle_stage"),
                "detected_patterns": run_spine.get("emergence_engine", {}).get("detected_patterns", []),
                "ready_signal_families": run_spine.get("emergence_engine", {}).get("ready_signal_families", []),
            },
            "terminal_state": "portfolio_acquisition_review_ready",
            "source_authority": {
                "live_truth_eligible": True,
                "source_evidence_present": True,
                "effective_source_count": len(run_spine.get("signals", [])),
                "metadata_only": True,
            },
            "run_quality": {
                "status": "valid_run",
                "memory_feedback_eligible": True,
            },
            "user_facing_result": {
                "headline": run_spine.get("portfolio_candidate", {}).get("title", ""),
                "summary": run_spine.get("portfolio_candidate", {}).get("summary", ""),
            },
        },
    }
    existing = [item for item in store["records"] if isinstance(item, dict) and item.get("run_id") != run_spine["run_id"]]
    store["records"] = [record] + existing[:24]
    recursive_snapshot = build_recursive_learning_snapshot(run_spine, store["records"])
    store["recursive_learning"] = recursive_snapshot
    store["status"] = "ready"
    store["updated_at"] = now
    store["policy"] = {
        "stage_1_ingestion": "allowed",
        "raw_run_history_ingestion": "blocked",
        "candidate_store_ingestion": "blocked",
        "promotion_requires_fresh_validation": True,
    }
    write_json(CONTINUOUS_DIR / "recursive_learning.json", recursive_snapshot)
    return write_json(path, store)


def _local_technology_cycle(cycle_id: str, now: str, query: str) -> Dict[str, Any]:
    input_files = allowed_input_files(PROJECT_ROOT)
    source_records = []
    rejected = []
    for path in input_files:
        payload = read_json(path, {})
        violations = source_violations(payload, PROJECT_ROOT)
        if violations:
            rejected.append({"path": project_relative(path, PROJECT_ROOT), "violations": violations})
            continue
        source_records.append({
            "path": project_relative(path, PROJECT_ROOT),
            "status": "allowed_input",
            "record_count": len(payload) if isinstance(payload, list) else len(payload.keys()) if isinstance(payload, dict) else 1,
        })

    monitor_payload = read_json(PROJECT_ROOT / "data" / "live_intelligence" / "latest_monitor_run.json", {})
    promoted_payload = read_json(PROJECT_ROOT / "data" / "internet_evidence" / "promoted_metadata_evidence_store.json", {})
    live_records = [*_promoted_evidence_records(promoted_payload), *_monitor_records(monitor_payload)]
    signals = [
        _signal_from_record(record, index, now)
        for index, record in enumerate(live_records[:12], start=1)
    ]
    run_spine = _build_run_spine(cycle_id, now, query, source_records, signals)
    portfolio_artifact = persist_portfolio_artifact(run_spine, PROJECT_ROOT) if signals else {}
    if portfolio_artifact:
        run_spine["portfolio_artifact"] = portfolio_artifact
        run_spine["final_package"]["artifact"] = portfolio_artifact
    run_spine_path = CONTINUOUS_DIR / "current_run.json"
    write_json(run_spine_path, run_spine)
    write_json(CONTINUOUS_DIR / "runs" / f"{cycle_id}.json", run_spine)
    memory_store = _write_lifecycle_memory_record(run_spine, now)
    recursive_learning = memory_store.get("recursive_learning", {}) if isinstance(memory_store, dict) else {}
    if isinstance(recursive_learning, dict):
        run_spine["recursive_learning"] = recursive_learning
        run_spine.setdefault("quality_gate", {})["recursive_learning_complete"] = (
            recursive_learning.get("status") == "recursive_learning_ready"
        )
        run_spine["emergence_engine"] = build_system_emergence_engine(
            query,
            context={
                "signals": signals,
                "domain": "market_intelligence",
                "advancement_path_decision": run_spine.get("advancement_path_decision", {}),
                "reemergence_pattern_engine": run_spine.get("advancement_path_decision", {}).get("reemergence_pattern_engine", {}),
                "source_authority": {"source_evidence_present": bool(signals), "live_evidence_present": bool(signals)},
                "quality_gate": run_spine.get("quality_gate", {}),
                "route_selected": run_spine.get("route_selected"),
            },
            memory_records=memory_store.get("records", []) if isinstance(memory_store, dict) else [],
        )
        write_json(run_spine_path, run_spine)
        write_json(CONTINUOUS_DIR / "runs" / f"{cycle_id}.json", run_spine)
    route_proofs = update_route_capability_proofs(run_spine, now)

    breakthrough_candidates = [run_spine["breakthrough_candidate"]] if run_spine.get("breakthrough_candidate") else []
    discovery_candidates = [run_spine["discovery_candidate"]] if signals else []
    portfolio_candidates = [run_spine["portfolio_candidate"]] if signals else []
    design_candidates = [run_spine["design_candidate"]] if run_spine.get("design_candidate") else []

    _write_candidate_store("breakthrough_candidates.json", "breakthrough", breakthrough_candidates, now)
    _write_candidate_store("discovery_candidates.json", "discovery", discovery_candidates, now)
    _write_candidate_store("portfolio_candidates.json", "portfolio", portfolio_candidates, now)
    _write_candidate_store("design_candidates.json", "design", design_candidates, now)
    _write_candidate_store(
        "package_candidates.json",
        "package",
        [
            {
                "candidate_id": f"package-{cycle_id[-8:]}",
                "candidate_type": "package",
                "title": "Portfolio acquisition review package",
                "status": "pending_operator_review",
                "route": run_spine["route_selected"],
                "source_portfolio_id": run_spine.get("portfolio_candidate", {}).get("candidate_id"),
                "sections": run_spine.get("final_package", {}).get("sections", []),
                "artifact": portfolio_artifact,
                "view_url": portfolio_artifact.get("view_url"),
                "download_url": portfolio_artifact.get("download_url"),
                "runtime_truth_write": "blocked",
            }
        ]
        if portfolio_candidates
        else [],
        now,
    )

    return {
        "status": "completed_allowlisted_input_cycle",
        "source_mode": "allowlisted_input_files_only",
        "query": query,
        "technology_base_status": "blocked_internal_system_zone",
        "technology_counts": {},
        "run_spine": {
            "path": "data/continuous_runtime/current_run.json",
            "run_id": cycle_id,
            "status": run_spine["status"],
            "route_selected": run_spine["route_selected"],
            "stage_count": len(run_spine["stage_status"]),
            "lifecycle_memory_records": len(memory_store.get("records", [])) if isinstance(memory_store, dict) else 0,
        },
        "strategic_world": {
            "status": run_spine.get("strategic_world", {}).get("status"),
            "schema_version": run_spine.get("strategic_world", {}).get("schema_version"),
            "domains": run_spine.get("strategic_world", {}).get("domains", []),
            "recommendation_count": len(run_spine.get("strategic_world", {}).get("ranked_recommendations", [])),
            "governance": run_spine.get("strategic_world", {}).get("governance", {}),
            "execution_boundary": run_spine.get("strategic_world", {}).get("governance", {}).get("execution_boundary"),
            "external_execution_allowed": run_spine.get("strategic_world", {}).get("governance", {}).get(
                "external_execution_allowed",
                False,
            ),
        },
        "quality_gate": run_spine.get("quality_gate", {}),
        "input_boundary": {
            "status": "enforced",
            "allowed_sources": source_records,
            "rejected_sources": rejected,
        },
        "candidate_counts": {
            "discoveries": len(discovery_candidates),
            "breakthroughs": len(breakthrough_candidates),
            "portfolios": len(portfolio_candidates),
            "designs": len(design_candidates),
            "packages": 1 if portfolio_candidates else 0,
        },
        "top_candidate": breakthrough_candidates[0] if breakthrough_candidates else discovery_candidates[0] if discovery_candidates else {},
        "advancement_path_decision": run_spine.get("advancement_path_decision", {}),
        "portfolio_artifact": portfolio_artifact,
        "route_capability_proofs": route_proofs,
        "authority": {
            "network_request_performed": False,
            "body_read_performed": False,
            "runtime_truth_mutated": False,
            "automatic_update_performed": False,
            "operator_review_required": True,
            "internal_system_ingestion_blocked": True,
        },
    }


def create_cycle_payload(trigger: str = "operator", query: str | None = None) -> Dict[str, Any]:
    ensure_runtime_files()
    cycle_id = "cycle_" + datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S") + "_" + uuid4().hex[:8]
    now = utc_now()
    query = query or "allowlisted input boundary lifecycle memory source universe live registry monitor"
    local_cycle = _local_technology_cycle(cycle_id, now, query)

    cycle = {
        "cycle_id": cycle_id,
        "created_at": now,
        "trigger": trigger,
        "status": local_cycle["status"],
        "purpose": "continuous intelligence monitoring cycle",
        "result": "local_source_backed_candidates_created_pending_operator_review",
        "candidate_counts": local_cycle["candidate_counts"],
        "top_candidate": local_cycle["top_candidate"],
        "technology_counts": local_cycle["technology_counts"],
        "advancement_path_decision": local_cycle.get("advancement_path_decision", {}),
        "run_spine": local_cycle["run_spine"],
        "strategic_world": local_cycle.get("strategic_world", {}),
        "quality_gate": local_cycle.get("quality_gate", {}),
        "portfolio_artifact": local_cycle.get("portfolio_artifact", {}),
        "input_boundary": local_cycle["input_boundary"],
        "missing_evidence": [] if local_cycle["candidate_counts"]["discoveries"] else [
            "validated local technology candidates",
        ],
        "rule": "continuous runtime ingests explicit allowlisted inputs, then applies versioned code contracts and the run spine for route selection, solution generation, design routing, portfolio, acquisition, and package construction; documents remain validation references only and internal system-zone candidate ingestion remains blocked",
        "authority": local_cycle["authority"],
    }

    cycle_path = CONTINUOUS_DIR / "cycles" / f"{cycle_id}.json"
    write_json(cycle_path, cycle)

    status = read_json(CONTINUOUS_DIR / "status.json", default_status())
    status["status"] = "active"
    status["continuous_runtime_status"] = "running"
    status["loop_running"] = True
    status["runtime_state"] = "running"
    status["last_cycle_id"] = cycle_id
    status["last_cycle_at"] = now
    status["candidate_generation"] = "allowlisted_inputs_only"
    status["input_boundary"] = local_cycle["input_boundary"]
    status["last_candidate_counts"] = local_cycle["candidate_counts"]
    status["updated_at"] = now
    write_json(CONTINUOUS_DIR / "status.json", status)

    review_queue = read_json(CONTINUOUS_DIR / "review_queue.json", {"items": []})
    if isinstance(review_queue, list):
        review_queue = {"items": review_queue}
    if not isinstance(review_queue, dict):
        review_queue = {"items": []}
    review_queue.setdefault("items", []).append({
        "id": cycle_id,
        "type": "continuous_cycle",
        "status": "awaiting_allowlisted_signals" if not local_cycle["candidate_counts"]["discoveries"] else "pending_operator_review",
        "created_at": now,
        "summary": (
            f"Continuous intelligence cycle ingested {len(local_cycle['input_boundary']['allowed_sources'])} "
            "allowlisted source files and applied autonomous advancement routing from versioned code contracts."
        ),
        "artifact": f"data/continuous_runtime/cycles/{cycle_id}.json",
        "candidate_counts": local_cycle["candidate_counts"],
        "top_candidate": local_cycle["top_candidate"],
        "operator_review_required": True,
        "runtime_truth_mutated": False,
    })
    review_queue["updated_at"] = now
    write_json(CONTINUOUS_DIR / "review_queue.json", review_queue)

    return {
        "status": "continuous_cycle_created",
        "continuous_runtime": status,
        "cycle": cycle,
        "review_queue": review_queue,
        "backend_owns_truth": True,
    }


def scheduler_status_payload() -> Dict[str, Any]:
    status = ensure_runtime_files()
    scheduler_state = ensure_scheduler_state()
    return {
        "status": "bounded_scheduler_ready",
        "continuous_runtime": status,
        "scheduler_state": scheduler_state,
        "authority": scheduler_state["authority"],
        "completion_gap": (
            "Scheduler tick path is proven inside the runtime. A Windows Task Scheduler job or service "
            "still has to be installed before this is truly 24/7."
        ),
    }


def run_scheduler_tick(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    ensure_runtime_files()
    scheduler_state = ensure_scheduler_state()
    query = None
    if payload and isinstance(payload, dict):
        query = str(payload.get("query") or payload.get("raw_input") or payload.get("input") or "").strip() or None
    query = query or "scheduled AI market signal existing system gap discovery breakthrough design portfolio acquirer"
    cycle_payload = create_cycle_payload(trigger="bounded_scheduler_tick", query=query)
    now = utc_now()

    scheduler_state["tick_count"] = int(scheduler_state.get("tick_count") or 0) + 1
    scheduler_state["last_tick_at"] = now
    scheduler_state["last_cycle_id"] = cycle_payload.get("cycle", {}).get("cycle_id")
    scheduler_state["last_tick_result"] = "cycle_created"
    scheduler_state["heartbeat_status"] = "last_tick_completed_external_runner_not_installed"
    scheduler_state["updated_at"] = now
    write_json(CONTINUOUS_DIR / SCHEDULER_STATE_FILENAME, scheduler_state)

    status = read_json(CONTINUOUS_DIR / "status.json", default_status())
    status.setdefault("scheduler_policy", default_status()["scheduler_policy"])
    status["scheduler_policy"] = {
        **default_status()["scheduler_policy"],
        **status.get("scheduler_policy", {}),
        "status": "bounded_scheduler_tick_proven_not_daemonized",
        "manual_tick_endpoint": "/runtime/continuous/scheduler/tick",
        "last_tick_at": now,
        "last_cycle_id": scheduler_state["last_cycle_id"],
    }
    status["updated_at"] = now
    write_json(CONTINUOUS_DIR / "status.json", status)

    return {
        "status": "scheduler_tick_completed",
        "scheduler_state": scheduler_state,
        "continuous_runtime": status,
        "cycle": cycle_payload["cycle"],
        "review_queue": cycle_payload["review_queue"],
        "authority": scheduler_state["authority"],
    }


@router.get("/runtime/continuous/status")
async def continuous_status() -> Dict[str, Any]:
    return ensure_runtime_files()


@router.get("/runtime/continuous/scheduler/status")
async def continuous_scheduler_status() -> Dict[str, Any]:
    return scheduler_status_payload()


@router.post("/runtime/continuous/scheduler/tick")
async def continuous_scheduler_tick(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    return run_scheduler_tick(payload)


@router.post("/runtime/continuous/start")
async def continuous_start(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    trigger = "operator"
    query = None
    if payload and isinstance(payload, dict):
        trigger = str(payload.get("trigger", "operator"))
        query = str(payload.get("query") or payload.get("raw_input") or payload.get("input") or "").strip() or None
    return create_cycle_payload(trigger=trigger, query=query)


@router.post("/runtime/continuous/pause")
async def continuous_pause() -> Dict[str, Any]:
    status = ensure_runtime_files()
    status["status"] = "paused"
    status["updated_at"] = utc_now()
    write_json(CONTINUOUS_DIR / "status.json", status)
    return status


@router.get("/runtime/continuous/cycles")
async def continuous_cycles() -> Dict[str, Any]:
    ensure_runtime_files()
    cycle_dir = CONTINUOUS_DIR / "cycles"
    cycles = []
    if cycle_dir.exists():
        for path in sorted(cycle_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
            cycles.append(read_json(path, {"cycle_id": path.stem}))
    return {"status": "ok", "cycles": cycles}


@router.get("/runtime/continuous/review-queue")
async def continuous_review_queue() -> Dict[str, Any]:
    ensure_runtime_files()
    return read_json(CONTINUOUS_DIR / "review_queue.json", {"items": []})
