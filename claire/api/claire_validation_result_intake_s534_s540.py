from __future__ import annotations

"""
Claire Controlled Validation Result Intake Contract — S534-S540

This module defines how Claire may receive and evaluate manually supplied
controlled-validation results after a future operator-controlled validation run.

It builds on:
- S520-S526 Controlled Update Validation Execution Plan
- S527-S533 Governed Update Evidence Capture and Operator Review Queue

Purpose:
- define validation result record shape
- ingest supplied validation results without executing commands
- map results to evidence and blockers
- assess validation result readiness
- build result review packets
- preserve the path toward a later promotion decision packet

No validation command is run, no test is executed, no result is fetched from
external systems, no package is downloaded, no update is installed, no promotion
occurs, no persistent result store is written, and no runtime truth is mutated.
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence


VERSION = "v19.89.8-S534-S540"
PHASE = "S534-S540"
JS_ASSET = "frontend/cockpit/shell/assets/claire_validation_result_intake.js"
CSS_ASSET = "frontend/cockpit/shell/assets/claire_validation_result_intake.css"


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
    "package_download_performed": False,
    "package_install_performed": False,
    "package_execution_enabled": False,
    "package_export_performed": False,
    "sandbox_file_write_performed": False,
    "sandbox_created": False,
    "test_execution_performed": False,
    "validation_execution_performed": False,
    "promotion_performed": False,
    "result_persistent_write_performed": False,
    "result_fetch_performed": False,
}


VALIDATION_RESULT_STATUSES = [
    "not_provided",
    "passed",
    "failed",
    "inconclusive",
    "blocked",
]


RESULT_READINESS_STATES = [
    "awaiting_results",
    "blocked",
    "failed_validation",
    "inconclusive",
    "results_supplied_for_review",
    "all_passed_supplied",
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


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


def _stable_id(prefix: str, *parts: Any) -> str:
    joined = "|".join(str(part) for part in parts)
    return f"{prefix}_{abs(hash(joined)) % 10_000_000:07d}"


def _load_validation_plan_module():
    from claire.api import claire_controlled_update_validation_plan_s520_s526 as validation_plan

    return validation_plan


def _load_review_queue_module():
    from claire.api import claire_update_evidence_review_queue_s527_s533 as review_queue

    return review_queue


def build_s534_validation_result_schema() -> Dict[str, Any]:
    return _safe_base(
        "S534",
        "validation_result_schema_ready",
        result_statuses=VALIDATION_RESULT_STATUSES,
        result_record_fields=[
            "result_id",
            "command_id",
            "label",
            "status",
            "summary",
            "evidence_refs",
            "blockers",
            "operator_supplied",
            "captured_at",
            "execution_performed_by_claire",
        ],
        result_rules=[
            "Results are supplied to Claire; Claire does not run commands here.",
            "Missing results remain visible as not_provided.",
            "Failed or blocked results block promotion readiness.",
            "All supplied results remain review-only until a later promotion packet.",
        ],
    )


def build_validation_result_record(
    command_id: str,
    label: str | None = None,
    status: str = "not_provided",
    summary: str | None = None,
    evidence_refs: Optional[Sequence[str]] = None,
    blockers: Optional[Sequence[str]] = None,
    operator_supplied: bool = False,
) -> Dict[str, Any]:
    normalized_status = status if status in VALIDATION_RESULT_STATUSES else "inconclusive"
    active_blockers = list(blockers or [])
    if normalized_status == "failed" and not active_blockers:
        active_blockers.append("validation_failed")
    if normalized_status == "blocked" and not active_blockers:
        active_blockers.append("validation_blocked")
    if normalized_status == "not_provided" and not active_blockers:
        active_blockers.append("result_not_provided")

    record = {
        "result_id": _stable_id("validation_result", command_id, normalized_status, summary or ""),
        "version": VERSION,
        "command_id": str(command_id),
        "label": str(label or command_id),
        "status": normalized_status,
        "summary": str(summary or "No validation result supplied."),
        "evidence_refs": list(evidence_refs or []),
        "blockers": active_blockers,
        "operator_supplied": bool(operator_supplied),
        "captured_at": _now(),
        "execution_performed_by_claire": False,
        "result_fetch_performed": False,
    }
    record.update(BLOCKED_AUTHORITY)
    return record


def intake_validation_results(
    execution_plan: Optional[Dict[str, Any]] = None,
    supplied_results: Optional[Sequence[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    validation_plan = _load_validation_plan_module()
    active_plan = dict(execution_plan or validation_plan.build_controlled_validation_execution_plan())
    commands = list(active_plan.get("command_manifest", {}).get("commands", []))
    supplied_by_command = {
        str(result.get("command_id")): dict(result)
        for result in list(supplied_results or [])
        if result.get("command_id") is not None
    }

    records: List[Dict[str, Any]] = []
    for command in commands:
        command_id = str(command.get("command_id"))
        supplied = supplied_by_command.get(command_id)
        if supplied:
            records.append(
                build_validation_result_record(
                    command_id=command_id,
                    label=str(command.get("label") or supplied.get("label") or command_id),
                    status=str(supplied.get("status", "inconclusive")),
                    summary=str(supplied.get("summary", "")),
                    evidence_refs=list(supplied.get("evidence_refs", [])),
                    blockers=list(supplied.get("blockers", [])),
                    operator_supplied=True,
                )
            )
        else:
            records.append(
                build_validation_result_record(
                    command_id=command_id,
                    label=str(command.get("label") or command_id),
                    status="not_provided",
                    summary="Awaiting operator-supplied validation result.",
                    operator_supplied=False,
                )
            )

    status_counts: Dict[str, int] = {status: 0 for status in VALIDATION_RESULT_STATUSES}
    for record in records:
        status_counts[record["status"]] = status_counts.get(record["status"], 0) + 1

    if status_counts.get("blocked", 0):
        state = "blocked"
    elif status_counts.get("failed", 0):
        state = "failed_validation"
    elif status_counts.get("inconclusive", 0):
        state = "inconclusive"
    elif status_counts.get("not_provided", 0) == len(records):
        state = "awaiting_results"
    elif status_counts.get("not_provided", 0):
        state = "results_supplied_for_review"
    elif records and all(record["status"] == "passed" for record in records):
        state = "all_passed_supplied"
    else:
        state = "results_supplied_for_review"

    intake = {
        "result_intake_id": _stable_id("validation_result_intake", active_plan.get("execution_plan_id"), status_counts),
        "version": VERSION,
        "created_at": _now(),
        "execution_plan_id": active_plan.get("execution_plan_id"),
        "record_count": len(records),
        "records": records,
        "status_counts": status_counts,
        "result_readiness_state": state,
        "operator_supplied_count": sum(1 for record in records if record["operator_supplied"]),
        "execution_performed_by_claire": False,
        "validation_execution_performed": False,
        "test_execution_performed": False,
        "result_persistent_write_allowed": False,
        "result_persistent_write_performed": False,
    }
    intake.update(BLOCKED_AUTHORITY)
    return intake


def build_s535_result_intake_contract() -> Dict[str, Any]:
    intake = intake_validation_results()
    return _safe_base(
        "S535",
        "validation_result_intake_contract_ready",
        sample_intake={
            "record_count": intake["record_count"],
            "result_readiness_state": intake["result_readiness_state"],
            "operator_supplied_count": intake["operator_supplied_count"],
        },
        intake_rules=[
            "Default intake creates not_provided placeholders.",
            "Supplied results are accepted as operator-provided evidence.",
            "No command execution or result fetching occurs.",
        ],
    )


def build_result_evidence_map(intake: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    active_intake = dict(intake or intake_validation_results())
    evidence_items: List[Dict[str, Any]] = []
    blockers: List[str] = []

    for record in active_intake.get("records", []):
        record_blockers = list(record.get("blockers", []))
        blockers.extend(record_blockers)
        evidence_items.append(
            {
                "evidence_id": _stable_id("validation_result_evidence", record.get("result_id")),
                "result_id": record.get("result_id"),
                "command_id": record.get("command_id"),
                "status": record.get("status"),
                "summary": record.get("summary"),
                "evidence_refs": list(record.get("evidence_refs", [])),
                "blockers": record_blockers,
                "quality": "usable" if record.get("status") == "passed" else "limited" if record.get("status") in {"inconclusive", "not_provided"} else "blocked",
                "execution_performed_by_claire": False,
            }
        )

    evidence_map = {
        "result_evidence_map_id": _stable_id("validation_result_evidence_map", active_intake.get("result_intake_id")),
        "version": VERSION,
        "created_at": _now(),
        "result_intake_id": active_intake.get("result_intake_id"),
        "evidence_items": evidence_items,
        "evidence_count": len(evidence_items),
        "blockers": sorted(set(blockers)),
        "all_results_have_evidence_refs": all(bool(item["evidence_refs"]) for item in evidence_items) if evidence_items else False,
        "evidence_scope": "operator_supplied_or_placeholder_results_only",
    }
    evidence_map.update(BLOCKED_AUTHORITY)
    return evidence_map


def build_s536_result_evidence_contract() -> Dict[str, Any]:
    evidence_map = build_result_evidence_map()
    return _safe_base(
        "S536",
        "validation_result_evidence_contract_ready",
        sample_evidence_map={
            "evidence_count": evidence_map["evidence_count"],
            "blocker_count": len(evidence_map["blockers"]),
            "all_results_have_evidence_refs": evidence_map["all_results_have_evidence_refs"],
        },
        evidence_rules=[
            "Result evidence maps supplied results to command IDs.",
            "Missing evidence references are allowed but reduce readiness.",
            "Failed, blocked, and missing results become blockers.",
        ],
    )


def assess_validation_result_readiness(
    intake: Optional[Dict[str, Any]] = None,
    evidence_map: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    active_intake = dict(intake or intake_validation_results())
    active_map = dict(evidence_map or build_result_evidence_map(active_intake))
    state = active_intake.get("result_readiness_state", "awaiting_results")

    blockers = list(active_map.get("blockers", []))
    if not active_map.get("all_results_have_evidence_refs"):
        blockers.append("missing_result_evidence_refs")
    if active_intake.get("operator_supplied_count", 0) == 0:
        blockers.append("no_operator_supplied_results")

    if state == "all_passed_supplied" and not blockers:
        readiness = "ready_for_promotion_decision_packet"
    elif state in {"blocked", "failed_validation"}:
        readiness = "blocked_from_promotion_decision"
    elif state == "inconclusive":
        readiness = "needs_clearer_results"
    else:
        readiness = "awaiting_more_validation_evidence"

    assessment = {
        "readiness_assessment_id": _stable_id("validation_result_readiness", active_intake.get("result_intake_id"), readiness),
        "version": VERSION,
        "created_at": _now(),
        "result_intake_id": active_intake.get("result_intake_id"),
        "result_evidence_map_id": active_map.get("result_evidence_map_id"),
        "result_readiness_state": state,
        "promotion_decision_packet_ready": readiness == "ready_for_promotion_decision_packet",
        "readiness": readiness,
        "blockers": sorted(set(blockers)),
        "can_promote_update": False,
        "can_apply_update": False,
        "operator_review_required": True,
    }
    assessment.update(BLOCKED_AUTHORITY)
    return assessment


def build_s537_result_readiness_contract() -> Dict[str, Any]:
    assessment = assess_validation_result_readiness()
    return _safe_base(
        "S537",
        "validation_result_readiness_contract_ready",
        sample_assessment={
            "readiness": assessment["readiness"],
            "promotion_decision_packet_ready": assessment["promotion_decision_packet_ready"],
            "blocker_count": len(assessment["blockers"]),
        },
        readiness_rules=[
            "Readiness assessment cannot promote or apply updates.",
            "All-passed supplied results may only become input to a later promotion decision packet.",
            "Missing evidence references keep the packet from promotion-decision readiness.",
        ],
    )


def build_result_review_packet(
    intake: Optional[Dict[str, Any]] = None,
    evidence_map: Optional[Dict[str, Any]] = None,
    assessment: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    active_intake = dict(intake or intake_validation_results())
    active_map = dict(evidence_map or build_result_evidence_map(active_intake))
    active_assessment = dict(assessment or assess_validation_result_readiness(active_intake, active_map))

    if active_assessment["promotion_decision_packet_ready"]:
        review_status = "ready_for_promotion_packet_builder"
        recommended_action = "build_later_promotion_decision_packet"
    elif active_assessment["readiness"] == "blocked_from_promotion_decision":
        review_status = "blocked"
        recommended_action = "reject_or_rework_update_candidate"
    else:
        review_status = "needs_more_validation_evidence"
        recommended_action = "collect_missing_validation_results"

    packet = {
        "result_review_packet_id": _stable_id("validation_result_review", active_intake.get("result_intake_id"), review_status),
        "version": VERSION,
        "created_at": _now(),
        "result_intake_id": active_intake.get("result_intake_id"),
        "result_evidence_map_id": active_map.get("result_evidence_map_id"),
        "readiness_assessment_id": active_assessment.get("readiness_assessment_id"),
        "review_status": review_status,
        "recommended_action": recommended_action,
        "status_counts": active_intake.get("status_counts", {}),
        "blockers": active_assessment.get("blockers", []),
        "summary": "Validation results are captured for operator review only.",
        "promotion_decision_packet_ready": active_assessment["promotion_decision_packet_ready"],
        "decision_execution_allowed": False,
        "review_only": True,
    }
    packet.update(BLOCKED_AUTHORITY)
    return packet


def build_s538_result_review_packet_contract() -> Dict[str, Any]:
    packet = build_result_review_packet()
    return _safe_base(
        "S538",
        "validation_result_review_packet_contract_ready",
        packet_fields=[
            "result_review_packet_id",
            "result_intake_id",
            "result_evidence_map_id",
            "readiness_assessment_id",
            "review_status",
            "recommended_action",
            "status_counts",
            "blockers",
            "promotion_decision_packet_ready",
            "review_only",
        ],
        sample_packet={
            "review_status": packet["review_status"],
            "recommended_action": packet["recommended_action"],
            "promotion_decision_packet_ready": packet["promotion_decision_packet_ready"],
        },
    )


def build_s539_cockpit_asset_manifest(project_root: str | Path | None = None) -> Dict[str, Any]:
    root = Path(project_root) if project_root is not None else Path.cwd()
    js = root / JS_ASSET
    css = root / CSS_ASSET
    return _safe_base(
        "S539",
        "cockpit_asset_manifest_ready",
        assets={
            "js": JS_ASSET,
            "css": CSS_ASSET,
            "js_exists": js.exists(),
            "css_exists": css.exists(),
        },
        cockpit_regions=[
            "validation_result_intake_panel",
            "validation_result_record_cards",
            "result_evidence_map",
            "readiness_assessment_card",
            "result_review_packet_card",
        ],
        visual_authority="presentation_only",
    )


def _passed_supplied_results_for_plan(plan: Dict[str, Any]) -> List[Dict[str, Any]]:
    commands = list(plan.get("command_manifest", {}).get("commands", []))
    return [
        {
            "command_id": command.get("command_id"),
            "status": "passed",
            "summary": f"Operator supplied pass result for {command.get('command_id')}.",
            "evidence_refs": [f"operator_evidence_{command.get('command_id')}"],
            "blockers": [],
        }
        for command in commands
    ]


def build_s540_stop_gate(report_dir: str | Path | None = None, project_root: str | Path | None = None) -> Dict[str, Any]:
    validation_plan = _load_validation_plan_module()
    plan = validation_plan.build_controlled_validation_execution_plan()

    s534 = build_s534_validation_result_schema()
    empty_intake = intake_validation_results(plan)
    empty_map = build_result_evidence_map(empty_intake)
    empty_assessment = assess_validation_result_readiness(empty_intake, empty_map)
    empty_packet = build_result_review_packet(empty_intake, empty_map, empty_assessment)

    passed_results = _passed_supplied_results_for_plan(plan)
    passed_intake = intake_validation_results(plan, passed_results)
    passed_map = build_result_evidence_map(passed_intake)
    passed_assessment = assess_validation_result_readiness(passed_intake, passed_map)
    passed_packet = build_result_review_packet(passed_intake, passed_map, passed_assessment)

    failed_results = list(passed_results)
    if failed_results:
        failed_results[0] = {
            "command_id": failed_results[0]["command_id"],
            "status": "failed",
            "summary": "Operator supplied failure result.",
            "evidence_refs": ["operator_failure_log"],
            "blockers": ["targeted_validation_failed"],
        }
    failed_intake = intake_validation_results(plan, failed_results)
    failed_map = build_result_evidence_map(failed_intake)
    failed_assessment = assess_validation_result_readiness(failed_intake, failed_map)
    failed_packet = build_result_review_packet(failed_intake, failed_map, failed_assessment)

    s535 = build_s535_result_intake_contract()
    s536 = build_s536_result_evidence_contract()
    s537 = build_s537_result_readiness_contract()
    s538 = build_s538_result_review_packet_contract()
    s539 = build_s539_cockpit_asset_manifest(project_root)

    checks = {
        "s534_schema_ready": "passed" in s534["result_statuses"],
        "s535_intake_ready": empty_intake["record_count"] >= 1 and empty_intake["validation_execution_performed"] is False,
        "s536_evidence_ready": empty_map["evidence_count"] == empty_intake["record_count"],
        "s537_readiness_ready": empty_assessment["can_promote_update"] is False and empty_assessment["can_apply_update"] is False,
        "s538_review_packet_ready": empty_packet["review_only"] is True and empty_packet["decision_execution_allowed"] is False,
        "s539_assets_exist": s539["assets"]["js_exists"] is True and s539["assets"]["css_exists"] is True,
        "empty_results_wait": empty_intake["result_readiness_state"] == "awaiting_results",
        "passed_results_packet_ready": passed_packet["promotion_decision_packet_ready"] is True,
        "failed_results_block": failed_packet["review_status"] == "blocked",
        "no_execution_or_persistence": all(
            value is False
            for value in [
                empty_intake["validation_execution_performed"],
                empty_intake["test_execution_performed"],
                empty_intake["result_persistent_write_performed"],
                passed_intake["validation_execution_performed"],
                failed_intake["validation_execution_performed"],
            ]
        ),
        "all_authority_blocked": all(passed_packet.get(flag) is False for flag in BLOCKED_AUTHORITY),
    }

    ok = all(checks.values())
    result = _safe_base(
        "S540",
        "claire_validation_result_intake_passed" if ok else "claire_validation_result_intake_failed",
        ok=ok,
        ready=ok,
        checks=checks,
        sample_outputs={
            "empty_intake": empty_intake,
            "empty_packet": empty_packet,
            "passed_intake": passed_intake,
            "passed_packet": passed_packet,
            "failed_intake": failed_intake,
            "failed_packet": failed_packet,
        },
        forward_motion_allowed=ok,
        stop_point="STOP POINT B foundation - validation results can be ingested for review; promotion packet comes next, still no application.",
        next_phase="S541-S547 Update promotion decision packet",
    )

    if report_dir is not None:
        target_dir = Path(report_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        (target_dir / "s540_claire_validation_result_intake_stop_gate.json").write_text(
            __import__("json").dumps(result, indent=2),
            encoding="utf-8",
        )

    return result


def build_claire_validation_result_intake_s534_s540(project_root: str | Path | None = None) -> Dict[str, Any]:
    return _safe_base(
        "S534-S540",
        "claire_validation_result_intake_ready",
        contracts={
            "s534": build_s534_validation_result_schema(),
            "s535": build_s535_result_intake_contract(),
            "s536": build_s536_result_evidence_contract(),
            "s537": build_s537_result_readiness_contract(),
            "s538": build_s538_result_review_packet_contract(),
            "s539": build_s539_cockpit_asset_manifest(project_root),
        },
        stop_gate=build_s540_stop_gate(project_root=project_root),
    )


__all__ = [
    "VERSION",
    "PHASE",
    "BLOCKED_AUTHORITY",
    "VALIDATION_RESULT_STATUSES",
    "RESULT_READINESS_STATES",
    "build_s534_validation_result_schema",
    "build_validation_result_record",
    "intake_validation_results",
    "build_s535_result_intake_contract",
    "build_result_evidence_map",
    "build_s536_result_evidence_contract",
    "assess_validation_result_readiness",
    "build_s537_result_readiness_contract",
    "build_result_review_packet",
    "build_s538_result_review_packet_contract",
    "build_s539_cockpit_asset_manifest",
    "build_s540_stop_gate",
    "build_claire_validation_result_intake_s534_s540",
]
