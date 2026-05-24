from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPORT_JSON = ROOT / "reports" / "SYSTEM_COMPLETION_READINESS.json"
REPORT_MD = ROOT / "reports" / "SYSTEM_COMPLETION_READINESS.md"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_json(path: Path, fallback: Any) -> Any:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback
    return fallback


def clamp(value: float) -> float:
    return max(0.0, min(100.0, round(value, 1)))


def _all_verified(claims: Any) -> bool:
    return isinstance(claims, list) and bool(claims) and all(
        isinstance(item, dict)
        and item.get("verdict") == "verified"
        and bool(item.get("supporting_refs"))
        for item in claims
    )


def evidence_depth_complete(current: dict[str, Any], quality: dict[str, Any]) -> bool:
    evidence = current.get("evidence_governance", {}) if isinstance(current.get("evidence_governance"), dict) else {}
    evidence_quality = evidence.get("quality", {}) if isinstance(evidence.get("quality"), dict) else {}
    conflicts = evidence.get("conflict_resolution", {}) if isinstance(evidence.get("conflict_resolution"), dict) else {}
    return (
        quality.get("evidence_governance_complete") is True
        and evidence.get("status") == "evidence_governance_ready"
        and int(evidence.get("evidence_count") or 0) >= 5
        and float(evidence_quality.get("aggregate_score") or 0.0) >= 0.80
        and evidence_quality.get("methodology_rigor") == "metadata_lineage_verified"
        and _all_verified(evidence.get("claim_verification"))
        and isinstance(evidence.get("citation_lineage"), list)
        and len(evidence.get("citation_lineage")) >= 4
        and conflicts.get("status") in {"no_conflicts_detected", "resolved_conflicts_present"}
    )


def recursive_learning_depth_complete(current: dict[str, Any], quality: dict[str, Any]) -> bool:
    recursive = current.get("recursive_learning", {}) if isinstance(current.get("recursive_learning"), dict) else {}
    signal_extraction = recursive.get("learning_signal_extraction", {}) if isinstance(recursive.get("learning_signal_extraction"), dict) else {}
    pattern_mining = recursive.get("run_pattern_mining", {}) if isinstance(recursive.get("run_pattern_mining"), dict) else {}
    gap_detection = recursive.get("recurring_gap_detection", {}) if isinstance(recursive.get("recurring_gap_detection"), dict) else {}
    thesis_evolution = recursive.get("thesis_evolution", {}) if isinstance(recursive.get("thesis_evolution"), dict) else {}
    recursive_quality = recursive.get("recursive_quality", {}) if isinstance(recursive.get("recursive_quality"), dict) else {}
    strategy_memory = recursive.get("strategy_memory", {}) if isinstance(recursive.get("strategy_memory"), dict) else {}
    return (
        quality.get("recursive_learning_complete") is True
        and recursive.get("status") == "recursive_learning_ready"
        and int(recursive.get("run_count") or 0) >= 3
        and int(signal_extraction.get("signal_count") or 0) >= 3
        and bool(signal_extraction.get("recurring_keywords"))
        and bool(pattern_mining.get("route_counts"))
        and "gap_closure_rate" in gap_detection
        and bool(thesis_evolution.get("latest_thesis"))
        and float(recursive_quality.get("score") or 0.0) >= 0.85
        and recursive_quality.get("memory_feedback_eligible") is True
        and strategy_memory.get("status") == "updated"
        and bool(strategy_memory.get("focus_keywords"))
    )


def design_proof_depth_complete(current: dict[str, Any], quality: dict[str, Any]) -> bool:
    design = current.get("design_candidate", {}) if isinstance(current.get("design_candidate"), dict) else {}
    proof = design.get("design_proof", {}) if isinstance(design.get("design_proof"), dict) else {}
    architecture = proof.get("architecture_feasibility", {}) if isinstance(proof.get("architecture_feasibility"), dict) else {}
    sequence = proof.get("build_sequence", {}) if isinstance(proof.get("build_sequence"), dict) else {}
    dependency = proof.get("dependency_risk", {}) if isinstance(proof.get("dependency_risk"), dict) else {}
    deployment = proof.get("deployment_model", {}) if isinstance(proof.get("deployment_model"), dict) else {}
    cost = proof.get("implementation_cost", {}) if isinstance(proof.get("implementation_cost"), dict) else {}
    maturity = proof.get("design_maturity", {}) if isinstance(proof.get("design_maturity"), dict) else {}
    return (
        quality.get("design_proof_complete") is True
        and proof.get("status") == "design_proof_ready"
        and architecture.get("verdict") in {"feasible", "conditionally_feasible"}
        and float(architecture.get("score") or 0.0) >= 0.68
        and sequence.get("status") == "valid_order"
        and isinstance(sequence.get("steps"), list)
        and len(sequence.get("steps")) >= 5
        and dependency.get("level") in {"low", "medium", "high"}
        and "score" in dependency
        and deployment.get("status") == "valid_bounded_deployment_model"
        and int(cost.get("effort_hours") or 0) > 0
        and int(cost.get("estimated_total_usd") or 0) > 0
        and maturity.get("level") in {"managed", "defined"}
        and float(maturity.get("score") or 0.0) >= 0.78
        and float(proof.get("overall_score") or 0.0) >= 0.72
    )


def score_item(name: str, weight: float, passed: bool, score: float | None = None, evidence: str = "", gap: str = "") -> dict[str, Any]:
    raw = 100.0 if passed else 0.0
    if score is not None:
        raw = clamp(score)
    return {
        "name": name,
        "weight": weight,
        "score": raw,
        "weighted_points": round(weight * raw / 100.0, 2),
        "passed": raw >= 85.0,
        "evidence": evidence,
        "gap": gap,
    }


def run() -> dict[str, Any]:
    status = read_json(ROOT / "data" / "continuous_runtime" / "status.json", {})
    scheduler_state = read_json(ROOT / "data" / "continuous_runtime" / "scheduler_state.json", {})
    route_proofs = read_json(ROOT / "data" / "continuous_runtime" / "route_capability_proofs.json", {})
    current = read_json(ROOT / "data" / "continuous_runtime" / "current_run.json", {})
    route_audit = read_json(ROOT / "reports" / "ROUTE_CONTRACT_CONFLICT_AUDIT.json", {})
    cleanup_audit = read_json(ROOT / "reports" / "SOURCE_AUTHORITY_AND_CLEANUP_AUDIT.json", {})
    source_packs = read_json(ROOT / "data" / "source_packs" / "local_upload_source_packs.json", {})
    latest_ptr = read_json(ROOT / "data" / "continuous_runtime" / "artifacts" / "portfolio" / "latest.json", {})
    portfolio_payload = {}
    run_id = latest_ptr.get("run_id")
    if run_id:
        portfolio_payload = read_json(ROOT / "data" / "continuous_runtime" / "artifacts" / "portfolio" / str(run_id) / "portfolio_brief.json", {})

    quality = current.get("quality_gate", {}) if isinstance(current.get("quality_gate"), dict) else {}
    evidence_complete = evidence_depth_complete(current, quality)
    recursive_complete = recursive_learning_depth_complete(current, quality)
    design_complete = design_proof_depth_complete(current, quality)
    counts = status.get("last_candidate_counts", {}) if isinstance(status.get("last_candidate_counts"), dict) else {}
    scheduler = status.get("scheduler_policy", {}) if isinstance(status.get("scheduler_policy"), dict) else {}
    proof_routes = route_proofs.get("routes", {}) if isinstance(route_proofs.get("routes"), dict) else {}
    existing_replacement_proof = proof_routes.get("existing_system_replacement", {}) if isinstance(proof_routes.get("existing_system_replacement"), dict) else {}
    bp = portfolio_payload.get("business_portfolio", {}) if isinstance(portfolio_payload.get("business_portfolio"), dict) else {}
    alignment = bp.get("pipeline_alignment", {}) if isinstance(bp.get("pipeline_alignment"), dict) else {}
    packs = source_packs.get("packs", []) if isinstance(source_packs, dict) else []
    active_doc_packs = [
        pack for pack in packs
        if isinstance(pack, dict)
        and pack.get("active_guidance") is not False
        and pack.get("runtime_ingestion_allowed") is not False
        and ("doc" in str(pack.get("pack_id", "")).lower() or "pipeline" in str(pack.get("pack_id", "")).lower())
    ]
    generated_zone = cleanup_audit.get("generated_zone_audit", {}) if isinstance(cleanup_audit.get("generated_zone_audit"), dict) else {}
    cleanup_files = int(
        generated_zone.get("unisolated_files_in_generated_legacy_zones")
        if "unisolated_files_in_generated_legacy_zones" in generated_zone
        else cleanup_audit.get("generated_legacy_files")
        or generated_zone.get("total_files_in_generated_legacy_zones")
        or 0
    )
    cleanup_score = 100.0 if cleanup_files == 0 else 70.0 if cleanup_files < 250 else 45.0 if cleanup_files < 750 else 25.0
    scheduler_tick_proven = (
        scheduler_state.get("last_tick_result") == "cycle_created"
        and int(scheduler_state.get("tick_count") or 0) > 0
    )
    scheduler_score = (
        100.0
        if scheduler.get("daemon_installed") is True or scheduler.get("task_runner_installed") is True
        else 68.0
        if scheduler_tick_proven
        else 45.0
        if scheduler.get("status")
        else 20.0
    )

    items = [
        score_item(
            "End-to-end 30-stage route execution",
            14,
            current.get("status") == "valid_continuous_lifecycle_snapshot" and len(current.get("stage_status", [])) >= 30,
            evidence=f"status={current.get('status')}, stages={len(current.get('stage_status', []))}",
            gap="Needs valid continuous lifecycle snapshot with all 30 stages.",
        ),
        score_item(
            "Correct advancement path and existing-system replacement route",
            10,
            existing_replacement_proof.get("proof_complete") is True,
            evidence=(
                f"current_route={current.get('route_selected')}, "
                f"existing_system_replacement_proof={existing_replacement_proof.get('last_successful_run_id')}"
            ),
            gap="Replacement route must decompose the current system and produce superior system design.",
        ),
        score_item(
            "Output package and dashboard handoff",
            10,
            bool(latest_ptr.get("run_id")) and quality.get("portfolio_candidate_present") is True and quality.get("acquisition_rationale_present") is True,
            evidence=f"latest_portfolio={latest_ptr.get('run_id')}",
            gap="Portfolio/final package, acquirer rationale, and dashboard handoff must all exist.",
        ),
        score_item(
            "Documents excluded from runtime programming",
            8,
            not active_doc_packs and alignment.get("docs_used_as_runtime_source") is False,
            evidence=f"active_doc_packs={len(active_doc_packs)}, portfolio_flag={alignment.get('docs_used_as_runtime_source')}",
            gap="Docs must remain validation references only.",
        ),
        score_item(
            "Stage-1 source boundary",
            8,
            status.get("input_boundary", {}).get("status") == "enforced" and not status.get("input_boundary", {}).get("rejected_sources"),
            evidence="allowlisted runtime state/evidence files only",
            gap="Runtime ingestion must stay restricted to governed state/evidence files.",
        ),
        score_item(
            "Governed live evidence and internet readiness",
            10,
            evidence_complete,
            score=100 if evidence_complete else 88 if quality.get("evidence_governance_complete") is True else 72 if bool(status.get("loop_running")) and counts.get("discoveries", 0) >= 1 else 35,
            evidence=f"loop_running={status.get('loop_running')}, candidate_counts={counts}, evidence_governance_complete={quality.get('evidence_governance_complete')}, depth_complete={evidence_complete}",
            gap="Needs repeatable live provider evidence quality, citation lineage, conflict resolution, and market validation.",
        ),
        score_item(
            "24/7 scheduler/service",
            12,
            scheduler.get("daemon_installed") is True or scheduler.get("task_runner_installed") is True,
            score=scheduler_score,
            evidence=f"scheduler={scheduler}, scheduler_state={scheduler_state}",
            gap="Needs installed daemon or OS task runner with heartbeat, recovery, and due-cycle execution.",
        ),
        score_item(
            "Recursive learning loop",
            8,
            recursive_complete,
            score=100 if recursive_complete else 84 if quality.get("recursive_learning_complete") is True else 68 if quality.get("lifecycle_memory_written") is True else 25,
            evidence=f"lifecycle_memory_written={quality.get('lifecycle_memory_written')}, recursive_learning_complete={quality.get('recursive_learning_complete')}, depth_complete={recursive_complete}",
            gap="Needs normalized recovered recursive_longitudinal modules and feedback quality scoring.",
        ),
        score_item(
            "Design proof depth",
            8,
            design_complete,
            score=100 if design_complete else 84 if quality.get("design_proof_complete") is True else 62 if quality.get("design_candidate_present") is True else 20,
            evidence=f"design_candidate_present={quality.get('design_candidate_present')}, design_proof_complete={quality.get('design_proof_complete')}, depth_complete={design_complete}",
            gap="Needs normalized design_proof modules: build sequence, dependency risk, deployment model, implementation cost, maturity.",
        ),
        score_item(
            "Cleanup and cross-wire isolation",
            12,
            cleanup_files == 0,
            score=cleanup_score,
            evidence=f"unisolated_generated_legacy_files={cleanup_files}, active_route_blockers={route_audit.get('active_blocker_count')}",
            gap="Generated/legacy files still dominate repo context and need archive/quarantine after approval.",
        ),
    ]

    total = round(sum(item["weighted_points"] for item in items), 1)
    status_label = "not_ready" if total < 60 else "prototype_ready_needs_hardening" if total < 78 else "near_ready" if total < 90 else "ready"
    payload = {
        "schema_version": "claire.system_completion_readiness.v1",
        "generated_at": utc_now(),
        "completion_percent": total,
        "status": status_label,
        "interpretation": "Percent is readiness-to-finished-system, not proof that the current route can produce an output.",
        "items": items,
        "top_blockers": [item for item in items if item["score"] < 70],
        "next_order": [
            "Install/prove continuous scheduler or OS task runner heartbeat.",
            "Normalize recovered research_live modules into evidence quality, claim verification, lineage, and conflict checks.",
            "Normalize recovered design_proof modules into design portal scoring.",
            "Archive/quarantine generated legacy zones after operator approval.",
            "Run repeated live cycles and compare recursive learning quality over time.",
        ],
    }
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT_MD.write_text(render_markdown(payload), encoding="utf-8")
    return payload


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# System Completion Readiness",
        "",
        f"Generated: {payload['generated_at']}",
        f"Completion: `{payload['completion_percent']}%`",
        f"Status: `{payload['status']}`",
        "",
        payload["interpretation"],
        "",
        "## Scored Areas",
    ]
    for item in payload["items"]:
        lines.append(f"- `{item['score']}%` {item['name']} ({item['weight']} pts): {item['evidence']}")
    lines.extend(["", "## Top Blockers"])
    for item in payload["top_blockers"]:
        lines.append(f"- {item['name']}: {item['gap']}")
    lines.extend(["", "## Next Order"])
    lines.extend(f"- {item}" for item in payload["next_order"])
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    result = run()
    print(json.dumps({
        "completion_percent": result["completion_percent"],
        "status": result["status"],
        "top_blockers": [item["name"] for item in result["top_blockers"]],
        "reports": {"json": str(REPORT_JSON), "markdown": str(REPORT_MD)},
    }, indent=2, sort_keys=True))
