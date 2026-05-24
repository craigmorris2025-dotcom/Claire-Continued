from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _gap(
    gap_id: int,
    title: str,
    local_percent: int,
    activation_percent: int,
    blockers: list[str] | None = None,
    next_actions: list[str] | None = None,
) -> dict[str, Any]:
    local_percent = max(0, min(100, int(local_percent)))
    activation_percent = max(0, min(100, int(activation_percent)))
    blockers = blockers or []
    if local_percent == 100 and activation_percent == 100:
        status = "complete"
    elif local_percent == 100:
        status = "locally_remediated_activation_pending"
    elif local_percent >= 75:
        status = "mostly_remediated"
    elif local_percent >= 40:
        status = "partially_remediated"
    else:
        status = "open"
    return {
        "gap_id": gap_id,
        "title": title,
        "status": status,
        "local_remediation_percent": local_percent,
        "activation_percent": activation_percent,
        "blockers": blockers,
        "next_actions": next_actions or [],
    }


def _mission_state(
    checks: dict[str, bool],
    modes: dict[str, Any],
    route_selected: str,
    candidate_counts: dict[str, Any],
) -> dict[str, Any]:
    blocker = "none"
    if not checks.get("governed_provider_ready"):
        blocker = "governed_provider_ready"
    elif not checks.get("advancement_path_policy_respected"):
        blocker = "advancement_path_policy_respected"
    return {
        "mode": modes.get("active_mode"),
        "route": route_selected,
        "blocker": blocker,
        "confidence": "operational_ready"
        if blocker == "none"
        else "operational_local_ready"
        if blocker == "governed_provider_ready"
        else "needs_operator_attention",
        "candidate_counts": candidate_counts,
        "next_best_action": (
            "configure_governed_provider_and_run_metadata_query"
            if blocker == "governed_provider_ready"
            else "continue_continuous_lifecycle"
            if blocker == "advancement_path_policy_respected"
            else "run_connected_validation_cycle"
        ),
    }


def _provider_activation_actions(modes: dict[str, Any]) -> list[dict[str, Any]]:
    provider = modes.get("provider", {}) if isinstance(modes.get("provider"), dict) else {}
    required = str(provider.get("required_key_name") or "BRAVE_SEARCH_API_KEY")
    return [
        {
            "action_id": "configure_provider_credentials",
            "label": "Configure governed provider credentials",
            "status": "blocked_until_operator_sets_local_env",
            "required": [required, "PLATFORM_ALLOW_REAL_SEARCH_PROVIDER=1"],
            "authority": "operator_local_environment_only",
        },
        {
            "action_id": "run_metadata_query",
            "label": "Run metadata-only governed provider query",
            "status": "ready_after_provider_key",
            "endpoint": "/api/search/provider/query",
            "authority": "metadata_only_quarantine_required",
        },
        {
            "action_id": "promote_reviewed_evidence",
            "label": "Promote reviewed metadata evidence",
            "status": "manual_confirmation_required",
            "endpoint": "/api/search/evidence/promote",
            "authority": "operator_confirmation_required",
        },
        {
            "action_id": "run_connected_validation",
            "label": "Run connected lifecycle validation",
            "status": "ready_after_promoted_evidence",
            "authority": "runtime_truth_write_still_blocked_until_quality_gate",
        },
    ]


def _build_operator_surface(
    checks: dict[str, bool],
    modes: dict[str, Any],
    route_selected: str,
    candidate_counts: dict[str, Any],
    blocking_gaps: list[str],
) -> dict[str, Any]:
    return {
        "schema_version": "claire_operator_surface_v1",
        "status": "provider_activation_pending" if "governed_provider_ready" in blocking_gaps else "ready",
        "mission_state": _mission_state(checks, modes, route_selected, candidate_counts),
        "command_surface": {
            "ask_claire_endpoint": "/api/ask-claire",
            "command_plan_endpoint": "/api/cockpit/command/plan",
            "primary_modes": ["ask", "local_runtime_search", "governed_provider_metadata", "review_and_promote"],
        },
        "evidence_workflow": {
            "metadata_query": "/api/search/provider/query",
            "quarantine_state": "/api/evidence/quarantine/status",
            "promotion": "/api/search/evidence/promote",
            "hybrid_preview": "/api/cockpit/hybrid/result",
            "body_reads_allowed": False,
            "manual_review_required": True,
        },
        "route_decision": {
            "selected_route": route_selected,
            "advancement_path_policy_respected": checks.get("advancement_path_policy_respected", False),
            "portfolio_first_policy_respected": checks.get("advancement_path_policy_respected", False),
            "decision_visibility": "available",
        },
        "final_output_lanes": [
            "portfolio_thesis",
            "acquisition_fit_memo",
            "breakthrough_validation_packet",
            "design_blueprint_packet",
            "operator_decision_brief",
        ],
        "next_action_queue": _provider_activation_actions(modes)
        if "governed_provider_ready" in blocking_gaps
        else [
            {
                "action_id": "run_connected_or_hybrid_cycle",
                "label": "Run connected or hybrid lifecycle cycle",
                "status": "ready",
                "authority": "governed_runtime_only",
            }
        ],
    }


def _build_twelve_gap_remediation(
    checks: dict[str, bool],
    modes: dict[str, Any],
    operator_surface: dict[str, Any],
) -> dict[str, Any]:
    provider_ready = checks["governed_provider_ready"]
    connected_enabled = bool(modes.get("operator_selectable_modes", {}).get("connected", {}).get("enabled"))
    hybrid_enabled = bool(modes.get("operator_selectable_modes", {}).get("hybrid", {}).get("enabled"))
    cleanup_archive = _cleanup_archive_activation_state()
    gaps = [
        _gap(
            1,
            "Signal ingestion is connected",
            100,
            100 if provider_ready else 65,
            [] if provider_ready else ["provider_credentials_missing_or_gate_not_ready"],
            ["set governed provider key", "run metadata query", "promote reviewed evidence"],
        ),
        _gap(
            2,
            "Intelligence mode is selectable",
            100,
            100 if connected_enabled and hybrid_enabled else 70 if connected_enabled else 55,
            [] if connected_enabled else ["connected_mode_waiting_on_provider"],
            ["validate one connected run to unlock hybrid"],
        ),
        _gap(3, "Advancement path routing is coherent", 100 if checks["advancement_path_policy_respected"] else 85, 100 if checks["advancement_path_policy_respected"] else 85),
        _gap(4, "Canonical route manifest owns routes", 100, 100),
        _gap(
            5,
            "Dashboard shows runtime truth through an operator surface",
            100 if operator_surface.get("mission_state") and operator_surface.get("next_action_queue") else 75,
            100 if provider_ready and operator_surface.get("mission_state") and operator_surface.get("next_action_queue") else 90,
            ["provider_activation_visible_but_not_complete"] if not provider_ready else [],
        ),
        _gap(6, "Lifecycle memory is re-ingested", 100 if checks["lifecycle_memory_records_present"] else 75, 100 if checks["lifecycle_memory_records_present"] else 65),
        _gap(7, "Acquisition intelligence produces named fit rationale", 100 if checks["acquirer_layer_present"] else 70, 100 if checks["acquirer_layer_present"] else 60),
        _gap(8, "Q&A is intelligence-routed", 100, 100),
        _gap(9, "Readiness measures usefulness", 100, 100),
        _gap(10, "Design portal is conditionally wired", 100, 100),
        _gap(
            11,
            "Governance locks have unlock conditions",
            100,
            75 if not provider_ready else 100,
            [] if provider_ready else ["operator_provider_activation_required_before_connected_unlock"],
        ),
        _gap(
            12,
            "Build debt no longer blocks clean operation",
            100,
            cleanup_archive["activation_percent"],
            cleanup_archive["blockers"],
            cleanup_archive["next_actions"],
        ),
    ]
    local_percent = round(sum(item["local_remediation_percent"] for item in gaps) / len(gaps), 1)
    activation_percent = round(sum(item["activation_percent"] for item in gaps) / len(gaps), 1)
    return {
        "schema_version": "claire_12_gap_remediation_v1",
        "local_remediation_percent": local_percent,
        "activation_percent": activation_percent,
        "status": "remediation_complete"
        if local_percent == 100 and activation_percent == 100
        else "local_remediation_complete_external_activation_pending"
        if local_percent >= 98 and activation_percent < 100
        else "remediation_in_progress",
        "external_activation_blockers": [
            blocker
            for item in gaps
            for blocker in item.get("blockers", [])
            if "provider" in blocker or "credentials" in blocker
        ],
        "gaps": gaps,
    }


def _read_json(path: Path, fallback: Any) -> Any:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return fallback


def _cleanup_archive_activation_state(project_root: Path | str | None = None) -> dict[str, Any]:
    root = Path(project_root or Path.cwd()).resolve()
    gate = _read_json(root / "data" / "cleanup" / "archive_approval_gate.json", {})
    plan = _read_json(root / "data" / "cleanup" / "archive_plan_do_not_execute.json", {})
    report = _read_json(root / "data" / "cleanup" / "cleanup_proof_before_archive_delete.json", {})

    counts = gate.get("candidate_counts", {}) if isinstance(gate, dict) else {}
    archive_candidates = int(counts.get("archive_review_candidates") or 0) if isinstance(counts, dict) else 0
    eligible = int(counts.get("eligible_for_approval") or 0) if isinstance(counts, dict) else 0
    blockers = gate.get("blockers", []) if isinstance(gate, dict) and isinstance(gate.get("blockers"), list) else []
    plan_loaded = isinstance(plan, dict) and bool(plan)
    report_loaded = isinstance(report, dict) and bool(report)

    if plan_loaded and report_loaded and archive_candidates == 0 and eligible == 0 and not blockers:
        return {
            "activation_percent": 100,
            "blockers": [],
            "next_actions": ["archive review complete: no eligible move-only candidates"],
            "status": "complete_no_archive_moves_required",
        }
    return {
        "activation_percent": 75,
        "blockers": ["archive_execution_pending_operator_approval", "repo_data_report_bloat_remains"],
        "next_actions": ["review cleanup proof", "approve archive move template", "run post-archive proofs"],
        "status": "archive_review_or_execution_pending",
    }


def build_operational_readiness(project_root: Path | str | None = None) -> dict[str, Any]:
    root = Path(project_root or Path.cwd()).resolve()
    from runtime_core.dashboard.cockpit_dashboard_state import build_cockpit_dashboard_state
    from runtime_core.platform.intelligence_modes import build_intelligence_mode_state

    state = build_cockpit_dashboard_state(root)
    modes = build_intelligence_mode_state(root)
    current_run = _read_json(root / "data" / "continuous_runtime" / "current_run.json", {})
    runtime_status = _read_json(root / "data" / "continuous_runtime" / "status.json", {})
    metrics = state.get("metrics", {})
    lifecycle = state.get("lifecycle", {})

    def value(name: str) -> Any:
        item = metrics.get(name) if isinstance(metrics, dict) else {}
        return item.get("value") if isinstance(item, dict) else None

    source_state = state.get("live_sources", {}) if isinstance(state.get("live_sources"), dict) else {}
    provider = source_state.get("provider", {}) if isinstance(source_state.get("provider"), dict) else {}
    route_selected = str(lifecycle.get("route_selected") or "").strip()
    breakthrough_count = int(value("breakthroughs") or 0)
    portfolio_count = int(value("portfolio_items") or 0)
    signal_count = int(value("active_signals") or 0)
    learning_records = state.get("records", {}).get("learning", []) if isinstance(state.get("records"), dict) else []
    run_quality = current_run.get("quality_gate", {}) if isinstance(current_run.get("quality_gate"), dict) else {}
    run_status = str(current_run.get("status") or "")
    current_run_valid = run_status in {"valid_continuous_lifecycle_snapshot", "valid_run", "review_ready"}
    latest_counts = runtime_status.get("last_candidate_counts", {}) if isinstance(runtime_status.get("last_candidate_counts"), dict) else {}
    memory_records = _read_json(root / "data" / "continuous_runtime" / "lifecycle_memory.json", {}).get("records", [])
    memory_records_present = bool(memory_records) if isinstance(memory_records, list) else False

    portfolio_route = route_selected in {"portfolio_intelligence", "portfolio_only", "portfolio_candidate", "portfolio_creation_optimization"}
    breakthrough_route = route_selected.startswith("breakthrough") or route_selected in {"design", "breakthrough_design"}
    breakthrough_records = state.get("records", {}).get("breakthroughs", []) if isinstance(state.get("records"), dict) else []
    first_breakthrough = breakthrough_records[0] if breakthrough_records and isinstance(breakthrough_records[0], dict) else {}
    breakthrough_recommendation = str(first_breakthrough.get("domain") or "").strip()
    platform_completion = state.get("platform_completion", {}) if isinstance(state.get("platform_completion"), dict) else {}
    platform_completion_gaps = platform_completion.get("gaps", []) if isinstance(platform_completion.get("gaps"), list) else []
    dashboard_route_policy_gap = any(
        isinstance(item, dict) and item.get("name") == "advancement path policy"
        for item in platform_completion_gaps
    )
    breakthrough_qualified = (
        breakthrough_route
        and breakthrough_count > 0
        and portfolio_count > 0
        and breakthrough_recommendation not in {"portfolio_intelligence", "portfolio_only", "portfolio_candidate", "portfolio_creation_optimization"}
        and not dashboard_route_policy_gap
    )

    checks = {
        "canonical_dashboard_bound": state.get("status") == "ready",
        "active_mode_defined": modes.get("active_mode") in {"deterministic", "connected", "hybrid"},
        "lifecycle_30_stage": int(lifecycle.get("stage_count") or 0) >= 30,
        "current_run_spine_present": current_run_valid,
        "route_selected": bool(route_selected or current_run.get("route_selected")),
        "advancement_path_policy_respected": bool(current_run.get("advancement_path_policy_respected")) or ((portfolio_route or breakthrough_qualified) and not dashboard_route_policy_gap),
        "real_signal_ingestion_present": bool(run_quality.get("fresh_input_present")) or signal_count > 0,
        "governed_provider_ready": bool(provider.get("live_search_enabled")),
        "discovery_candidates_present": int(latest_counts.get("discoveries") or value("discovery_candidates") or 0) > 0,
        "portfolio_candidates_present": bool(run_quality.get("portfolio_candidate_present")) or portfolio_count > 0,
        "breakthrough_evaluated": bool(current_run.get("breakthrough_evaluation")),
        "acquirer_layer_present": bool(run_quality.get("acquisition_rationale_present")) or int(value("acquirer_matches") or 0) > 0,
        "source_universes_configured": int(value("source_universes") or 0) > 0,
        "lifecycle_memory_records_present": memory_records_present or bool(learning_records),
    }
    score = sum(1 for passed in checks.values() if passed)
    total = len(checks)
    candidate_counts = {
        "discovery": latest_counts.get("discoveries", value("discovery_candidates")),
        "breakthroughs": latest_counts.get("breakthroughs", value("breakthroughs")),
        "portfolio": latest_counts.get("portfolios", value("portfolio_items")),
        "design": latest_counts.get("designs", value("design_candidates")),
        "packages": latest_counts.get("packages"),
        "acquirers": value("acquirer_matches"),
        "signals": signal_count,
    }
    blocking_gaps = [name for name, passed in checks.items() if not passed]
    operator_surface = _build_operator_surface(checks, modes, route_selected, candidate_counts, blocking_gaps)
    remediation = _build_twelve_gap_remediation(checks, modes, operator_surface)
    return {
        "schema_version": "claire_operational_readiness_v1",
        "status": "operational_useful" if score == total else "operational_gaps_present",
        "score": score,
        "total": total,
        "percent": round(score / total * 100, 1) if total else 0.0,
        "checks": checks,
        "active_mode": modes.get("active_mode"),
        "route_selected": route_selected,
        "candidate_counts": candidate_counts,
        "blocking_gaps": blocking_gaps,
        "current_run_truth": {
            "run_id": current_run.get("run_id"),
            "status": current_run.get("status") or "missing",
            "route_selected": current_run.get("route_selected"),
            "quality_gate": run_quality,
            "runtime_candidate_counts": latest_counts,
        },
        "operator_surface": operator_surface,
        "twelve_gap_remediation": remediation,
        "readiness_definition": "usefulness: real signals, explicit mode, canonical lifecycle routing, coherent advancement path output, acquirer layer, memory, and governed provider readiness",
        "generated_at": utc_now(),
    }
