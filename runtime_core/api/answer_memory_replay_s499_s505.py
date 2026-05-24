from __future__ import annotations

"""
Claire Answer Memory and Replay — S499-S505

This module creates a governed, local, review-only memory/replay model for
Claire answer packages.

It builds on:
- S450-S456 Claire Intelligence Answer Contract
- S457-S463 Claire Command Response Cards
- S464-S470 Evidence-Backed Answer Model
- S471-S477 Claire Knowledge Base Registry
- S478-S484 Market / Research / Engineering Answer Routes
- S485-S491 Innovation Potential Detection and Route Escalation
- S492-S498 Useful Output Package Preview

Purpose:
- create immutable-style answer memory records
- preserve traceability for question, classification, evidence, package preview,
  innovation candidate, assumptions, verification needs, and governance
- replay prior answer/package context without mutating runtime truth
- provide audit/review status and replay comparison
- prepare the path for future lifecycle memory and recursive self-ingestion

No network requests, live crawling, browser execution, response-body reads,
runtime mutation, automatic updates, autonomous execution, package export,
or persistent database writes are performed here.
"""

from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence


VERSION = "v19.89.8-S499-S505"
PHASE = "S499-S505"
JS_ASSET = "frontend/cockpit/shell/assets/claire_answer_memory_replay.js"
CSS_ASSET = "frontend/cockpit/shell/assets/claire_answer_memory_replay.css"


BLOCKED_AUTHORITY: Dict[str, bool] = {
    "runtime_mutation_enabled": False,
    "runtime_truth_mutation_allowed": False,
    "runtime_truth_write_allowed": False,
    "automatic_updates_enabled": False,
    "autonomous_crawling_enabled": False,
    "autonomous_execution_enabled": False,
    "autonomous_agent_execution_enabled": False,
    "live_web_execution_enabled": False,
    "browser_execution_enabled": False,
    "network_request_performed": False,
    "body_read_allowed": False,
    "package_execution_enabled": False,
    "package_export_performed": False,
    "persistent_memory_write_performed": False,
    "recursive_self_ingestion_executed": False,
}


MEMORY_RECORD_FIELDS = [
    "memory_id",
    "version",
    "created_at",
    "question",
    "package_id",
    "package_type",
    "classification",
    "route_summary",
    "evidence_summary",
    "innovation_summary",
    "assumptions",
    "verification_needed",
    "readiness_score",
    "review_status",
    "governance",
    "replay_trace",
]


REPLAY_STATUS = [
    "replay_ready",
    "replay_with_verification_needed",
    "replay_blocked_missing_trace",
    "replay_reference_only",
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize(text: str | None) -> str:
    return " ".join(str(text or "").strip().lower().split())


def _safe_base(stage_version: str, status: str, **extra: Any) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "version": VERSION,
        "phase": PHASE,
        "stage_version": stage_version,
        "status": status,
        "ready": True,
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "created_at": _now(),
    }
    payload.update(BLOCKED_AUTHORITY)
    payload.update(extra)
    return payload


def _load_package_preview_module():
    from runtime_core.api import useful_output_package_preview_s492_s498 as preview

    return preview


def _stable_id(prefix: str, *parts: Any) -> str:
    joined = "|".join(str(part) for part in parts)
    return f"{prefix}_{abs(hash(joined)) % 10_000_000:07d}"


def build_s499_answer_memory_schema() -> Dict[str, Any]:
    return _safe_base(
        "S499",
        "answer_memory_schema_ready",
        memory_record_fields=MEMORY_RECORD_FIELDS,
        replay_statuses=REPLAY_STATUS,
        memory_scope="in_memory_contract_only",
        storage_rules=[
            "S499 defines the memory record shape only.",
            "This module does not write persistent memory to disk or database.",
            "Future lifecycle memory owner must validate storage, replay, and recursive self-ingestion authority.",
        ],
    )


def build_answer_memory_record(
    question: str | None,
    package_preview: Optional[Dict[str, Any]] = None,
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Build a review-only in-memory record from a package preview."""
    preview_module = _load_package_preview_module()
    preview = deepcopy(
        package_preview
        if package_preview is not None
        else preview_module.build_useful_output_package_preview(question, context=context or {})
    )

    evidence_summary = deepcopy(preview.get("evidence_summary", {}))
    route_candidate = deepcopy(preview.get("route_candidate"))
    classification = (
        preview.get("evidence_answer", {}).get("classification")
        or preview.get("classification")
        or {}
    )

    route_summary = {
        "package_type": preview.get("package_type"),
        "label": preview.get("label"),
        "review_gate": preview.get("governance", {}).get("review_gate"),
        "readiness_score": preview.get("readiness_score"),
        "review_status": preview.get("review_status"),
    }

    innovation_summary = {
        "route_candidate": route_candidate,
        "has_route_candidate": route_candidate is not None,
        "review_only": True,
        "execution_allowed": False,
    }

    replay_trace = {
        "source_package_id": preview.get("package_id"),
        "source_version": preview.get("version"),
        "sections": sorted((preview.get("sections") or {}).keys()),
        "knowledge_result_count": preview.get("knowledge_result_count", 0),
        "verification_count": len(preview.get("verification_needed", []) or []),
        "assumption_count": len(preview.get("assumptions", []) or []),
        "trace_available": True,
    }

    record = {
        "memory_id": _stable_id("answer_memory", question, preview.get("package_id"), preview.get("package_type")),
        "version": VERSION,
        "created_at": _now(),
        "question": str(question or preview.get("question") or ""),
        "package_id": preview.get("package_id"),
        "package_type": preview.get("package_type"),
        "classification": classification,
        "route_summary": route_summary,
        "evidence_summary": evidence_summary,
        "innovation_summary": innovation_summary,
        "assumptions": deepcopy(preview.get("assumptions", [])),
        "verification_needed": deepcopy(preview.get("verification_needed", [])),
        "readiness_score": preview.get("readiness_score"),
        "review_status": preview.get("review_status"),
        "governance": {
            "memory_record_only": True,
            "persistent_write_allowed": False,
            "persistent_write_performed": False,
            "replay_allowed": True,
            "recursive_self_ingestion_allowed": False,
            **BLOCKED_AUTHORITY,
        },
        "replay_trace": replay_trace,
    }
    record.update(BLOCKED_AUTHORITY)
    return record


def build_s500_memory_record_builder_contract() -> Dict[str, Any]:
    sample = build_answer_memory_record("Can Claire produce a reviewable market brief from this trend?")
    return _safe_base(
        "S500",
        "answer_memory_record_builder_ready",
        builder="build_answer_memory_record",
        sample_record={
            "memory_id": sample["memory_id"],
            "package_type": sample["package_type"],
            "review_status": sample["review_status"],
            "trace_available": sample["replay_trace"]["trace_available"],
        },
    )


def build_answer_memory_index(records: Optional[Sequence[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """Build an in-memory index over supplied records; does not persist anything."""
    active_records = list(records or [])
    by_type: Dict[str, List[str]] = {}
    by_status: Dict[str, List[str]] = {}
    verification_needed: List[str] = []

    for record in active_records:
        memory_id = str(record.get("memory_id", ""))
        package_type = str(record.get("package_type", "unknown"))
        review_status = str(record.get("review_status", "unknown"))
        by_type.setdefault(package_type, []).append(memory_id)
        by_status.setdefault(review_status, []).append(memory_id)
        if record.get("verification_needed"):
            verification_needed.append(memory_id)

    return _safe_base(
        "S501",
        "answer_memory_index_ready",
        record_count=len(active_records),
        by_package_type={key: sorted(value) for key, value in by_type.items()},
        by_review_status={key: sorted(value) for key, value in by_status.items()},
        records_with_verification_needed=sorted(verification_needed),
        index_scope="in_memory_supplied_records_only",
    )


def build_s501_memory_index_contract() -> Dict[str, Any]:
    preview_module = _load_package_preview_module()
    market = preview_module.build_useful_output_package_preview(
        "Can Claire build a market trend brief with portfolio implications?",
        preferred_package_type="market_brief",
        preferred_domain="market",
    )
    engineering = preview_module.build_useful_output_package_preview(
        "Can Claire build an engineering feasibility preview for this system architecture?",
        preferred_package_type="engineering_feasibility_preview",
        preferred_domain="engineering",
    )
    records = [
        build_answer_memory_record(market["question"], package_preview=market),
        build_answer_memory_record(engineering["question"], package_preview=engineering),
    ]
    index = build_answer_memory_index(records)
    return _safe_base(
        "S501",
        "memory_index_contract_ready",
        sample_index=index,
        index_rules=[
            "Index is built from supplied records only.",
            "No persistent storage scan is performed.",
            "Future lifecycle memory owner can replace this with durable governed storage.",
        ],
    )


def replay_answer_memory_record(record: Dict[str, Any], replay_question: str | None = None) -> Dict[str, Any]:
    """Replay a memory record as reference context without executing or mutating anything."""
    trace = record.get("replay_trace") or {}
    verification_needed = list(record.get("verification_needed") or [])
    assumptions = list(record.get("assumptions") or [])

    if not trace.get("trace_available"):
        status = "replay_blocked_missing_trace"
    elif verification_needed:
        status = "replay_with_verification_needed"
    else:
        status = "replay_ready"

    replay = {
        "replay_id": _stable_id("answer_replay", record.get("memory_id"), replay_question or record.get("question")),
        "version": VERSION,
        "created_at": _now(),
        "source_memory_id": record.get("memory_id"),
        "source_package_id": record.get("package_id"),
        "source_package_type": record.get("package_type"),
        "original_question": record.get("question"),
        "replay_question": str(replay_question or record.get("question") or ""),
        "status": status,
        "reference_summary": {
            "route_summary": deepcopy(record.get("route_summary", {})),
            "evidence_summary": deepcopy(record.get("evidence_summary", {})),
            "innovation_summary": deepcopy(record.get("innovation_summary", {})),
            "readiness_score": record.get("readiness_score"),
            "review_status": record.get("review_status"),
        },
        "assumptions": assumptions,
        "verification_needed": verification_needed,
        "allowed_use": [
            "compare_with_new_question",
            "show_prior_reasoning_context",
            "identify_unresolved_verification_needs",
            "prepare_future_lifecycle_memory_candidate",
        ],
        "blocked_use": [
            "treat_as_new_live_research",
            "mutate_runtime_truth",
            "execute_route_transition",
            "perform_recursive_self_ingestion_without_owner",
            "apply_update_or_export_package",
        ],
        "governance": {
            "reference_only": True,
            "persistent_write_allowed": False,
            "runtime_truth_write_allowed": False,
            "recursive_self_ingestion_executed": False,
            **BLOCKED_AUTHORITY,
        },
    }
    replay.update(BLOCKED_AUTHORITY)
    return replay


def build_s502_replay_contract() -> Dict[str, Any]:
    record = build_answer_memory_record("Can Claire make a breakthrough candidate preview from this market gap?")
    replay = replay_answer_memory_record(record, replay_question="Compare this with the next market gap.")
    return _safe_base(
        "S502",
        "answer_replay_contract_ready",
        replay_fields=[
            "replay_id",
            "source_memory_id",
            "source_package_id",
            "original_question",
            "replay_question",
            "status",
            "reference_summary",
            "assumptions",
            "verification_needed",
            "allowed_use",
            "blocked_use",
            "governance",
        ],
        sample_replay={
            "replay_id": replay["replay_id"],
            "status": replay["status"],
            "source_package_type": replay["source_package_type"],
        },
    )


def compare_memory_records(left: Dict[str, Any], right: Dict[str, Any]) -> Dict[str, Any]:
    """Compare two memory records for route/package continuity."""
    left_sections = set((left.get("replay_trace") or {}).get("sections") or [])
    right_sections = set((right.get("replay_trace") or {}).get("sections") or [])
    shared_sections = sorted(left_sections.intersection(right_sections))
    changed_sections = sorted(left_sections.symmetric_difference(right_sections))

    comparison = {
        "comparison_id": _stable_id("memory_comparison", left.get("memory_id"), right.get("memory_id")),
        "version": VERSION,
        "created_at": _now(),
        "left_memory_id": left.get("memory_id"),
        "right_memory_id": right.get("memory_id"),
        "same_package_type": left.get("package_type") == right.get("package_type"),
        "left_package_type": left.get("package_type"),
        "right_package_type": right.get("package_type"),
        "shared_sections": shared_sections,
        "changed_sections": changed_sections,
        "readiness_delta": round(float(right.get("readiness_score") or 0.0) - float(left.get("readiness_score") or 0.0), 3),
        "verification_delta": len(right.get("verification_needed") or []) - len(left.get("verification_needed") or []),
        "comparison_use": "operator_review_only",
    }
    comparison.update(BLOCKED_AUTHORITY)
    return comparison


def build_s503_memory_comparison_contract() -> Dict[str, Any]:
    preview_module = _load_package_preview_module()
    market_a = preview_module.build_useful_output_package_preview(
        "Can Claire build a market trend brief with portfolio implications?",
        preferred_package_type="market_brief",
        preferred_domain="market",
    )
    market_b = preview_module.build_useful_output_package_preview(
        "Can Claire build a market trend brief with stronger demand logic?",
        preferred_package_type="market_brief",
        preferred_domain="market",
    )
    left = build_answer_memory_record(market_a["question"], package_preview=market_a)
    right = build_answer_memory_record(market_b["question"], package_preview=market_b)
    comparison = compare_memory_records(left, right)
    return _safe_base(
        "S503",
        "memory_comparison_contract_ready",
        comparison_fields=[
            "comparison_id",
            "same_package_type",
            "shared_sections",
            "changed_sections",
            "readiness_delta",
            "verification_delta",
            "comparison_use",
        ],
        sample_comparison=comparison,
    )


def build_s504_cockpit_asset_manifest(project_root: str | Path | None = None) -> Dict[str, Any]:
    root = Path(project_root) if project_root is not None else Path.cwd()
    js = root / JS_ASSET
    css = root / CSS_ASSET
    return _safe_base(
        "S504",
        "cockpit_asset_manifest_ready",
        assets={
            "js": JS_ASSET,
            "css": CSS_ASSET,
            "js_exists": js.exists(),
            "css_exists": css.exists(),
        },
        cockpit_regions=[
            "answer_memory_panel",
            "memory_record_cards",
            "replay_trace_view",
            "verification_needs_badges",
            "memory_comparison_panel",
            "recursive_learning_candidate_stub",
        ],
        visual_authority="presentation_only",
    )


def build_s505_stop_gate(report_dir: str | Path | None = None, project_root: str | Path | None = None) -> Dict[str, Any]:
    preview_module = _load_package_preview_module()

    s499 = build_s499_answer_memory_schema()
    market_preview = preview_module.build_useful_output_package_preview(
        "Can Claire build a market trend brief with portfolio implications?",
        preferred_package_type="market_brief",
        preferred_domain="market",
    )
    engineering_preview = preview_module.build_useful_output_package_preview(
        "Can Claire build an engineering feasibility preview for this architecture?",
        preferred_package_type="engineering_feasibility_preview",
        preferred_domain="engineering",
    )

    market_record = build_answer_memory_record(market_preview["question"], package_preview=market_preview)
    engineering_record = build_answer_memory_record(engineering_preview["question"], package_preview=engineering_preview)
    index = build_answer_memory_index([market_record, engineering_record])
    replay = replay_answer_memory_record(market_record, "Replay this market brief for operator review.")
    comparison = compare_memory_records(market_record, engineering_record)

    s500 = build_s500_memory_record_builder_contract()
    s501 = build_s501_memory_index_contract()
    s502 = build_s502_replay_contract()
    s503 = build_s503_memory_comparison_contract()
    s504 = build_s504_cockpit_asset_manifest(project_root)

    checks = {
        "s499_schema_ready": "memory_id" in s499["memory_record_fields"],
        "s500_record_builder_ready": s500["sample_record"]["trace_available"] is True,
        "s501_index_ready": index["record_count"] == 2 and "market_brief" in index["by_package_type"],
        "s502_replay_ready": replay["status"] in REPLAY_STATUS and replay["governance"]["reference_only"] is True,
        "s503_comparison_ready": "readiness_delta" in comparison and comparison["comparison_use"] == "operator_review_only",
        "s504_assets_exist": s504["assets"]["js_exists"] is True and s504["assets"]["css_exists"] is True,
        "memory_record_safe": all(market_record.get(flag) is False for flag in BLOCKED_AUTHORITY),
        "replay_safe": all(replay.get(flag) is False for flag in BLOCKED_AUTHORITY),
        "comparison_safe": all(comparison.get(flag) is False for flag in BLOCKED_AUTHORITY),
        "no_persistent_write": market_record["governance"]["persistent_write_performed"] is False,
        "no_recursive_self_ingestion_execution": replay["governance"]["recursive_self_ingestion_executed"] is False,
    }

    ok = all(checks.values())
    result = _safe_base(
        "S505",
        "claire_answer_memory_replay_passed" if ok else "claire_answer_memory_replay_failed",
        ok=ok,
        ready=ok,
        checks=checks,
        sample_outputs={
            "market_record": market_record,
            "engineering_record": engineering_record,
            "index": index,
            "replay": replay,
            "comparison": comparison,
        },
        forward_motion_allowed=ok,
        next_phase="S506-S512 Governed update package inspector readiness",
    )

    if report_dir is not None:
        target_dir = Path(report_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        (target_dir / "s505_claire_answer_memory_replay_stop_gate.json").write_text(
            __import__("json").dumps(result, indent=2),
            encoding="utf-8",
        )

    return result


def build_answer_memory_replay_s499_s505(project_root: str | Path | None = None) -> Dict[str, Any]:
    return _safe_base(
        "S499-S505",
        "claire_answer_memory_replay_ready",
        contracts={
            "s499": build_s499_answer_memory_schema(),
            "s500": build_s500_memory_record_builder_contract(),
            "s501": build_s501_memory_index_contract(),
            "s502": build_s502_replay_contract(),
            "s503": build_s503_memory_comparison_contract(),
            "s504": build_s504_cockpit_asset_manifest(project_root),
        },
        stop_gate=build_s505_stop_gate(project_root=project_root),
    )


__all__ = [
    "VERSION",
    "PHASE",
    "BLOCKED_AUTHORITY",
    "MEMORY_RECORD_FIELDS",
    "REPLAY_STATUS",
    "build_s499_answer_memory_schema",
    "build_answer_memory_record",
    "build_s500_memory_record_builder_contract",
    "build_answer_memory_index",
    "build_s501_memory_index_contract",
    "replay_answer_memory_record",
    "build_s502_replay_contract",
    "compare_memory_records",
    "build_s503_memory_comparison_contract",
    "build_s504_cockpit_asset_manifest",
    "build_s505_stop_gate",
    "build_answer_memory_replay_s499_s505",
]
