from __future__ import annotations

"""
Claire Governed Update Evidence Capture and Operator Review Queue — S527-S533

Full replacement repair for S533 stop-gate boolean contract.

Fix:
- blocked_packet_visible now returns a strict boolean, not the blockers list.
- blocked queue and rejection checks remain unchanged.
- No execution, install, download, promotion, mutation, queue persistence, live web,
  or operator decision execution is enabled.
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence


VERSION = "v19.89.8-S527-S533"
PHASE = "S527-S533"
JS_ASSET = "frontend/cockpit/shell/assets/claire_update_evidence_review_queue.js"
CSS_ASSET = "frontend/cockpit/shell/assets/claire_update_evidence_review_queue.css"


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
    "queue_persistent_write_performed": False,
    "operator_decision_execution_performed": False,
}


EVIDENCE_TYPES = [
    "inspection_metadata",
    "zero_trust_check",
    "validation_plan",
    "sandbox_profile",
    "file_impact_map",
    "command_manifest",
    "preflight_decision",
    "rollback_checklist",
    "execution_gate",
    "operator_note",
]


REVIEW_STATUSES = [
    "queued_for_review",
    "needs_more_evidence",
    "blocked",
    "ready_for_operator_decision",
    "operator_reviewed_reference_only",
]


RECOMMENDED_ACTIONS = [
    "hold",
    "request_more_evidence",
    "reject_candidate",
    "prepare_future_manual_validation",
    "escalate_to_operator_decision_packet",
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


def _load_update_inspector_module():
    from claire.api import claire_governed_update_inspector_s506_s512 as update_inspector

    return update_inspector


def _load_validation_plan_module():
    from claire.api import claire_controlled_update_validation_plan_s520_s526 as validation_plan

    return validation_plan


def _stable_id(prefix: str, *parts: Any) -> str:
    joined = "|".join(str(part) for part in parts)
    return f"{prefix}_{abs(hash(joined)) % 10_000_000:07d}"


def build_s527_update_evidence_item_schema() -> Dict[str, Any]:
    return _safe_base(
        "S527",
        "update_evidence_item_schema_ready",
        evidence_types=EVIDENCE_TYPES,
        evidence_item_fields=[
            "evidence_id",
            "evidence_type",
            "title",
            "summary",
            "source_stage",
            "source_id",
            "quality",
            "blockers",
            "supports",
            "limitations",
            "captured_at",
        ],
        evidence_rules=[
            "Evidence is captured from supplied/internal payloads only.",
            "No live source is fetched.",
            "No response body is read.",
            "Evidence does not mutate runtime truth.",
        ],
    )


def make_update_evidence_item(
    evidence_type: str,
    title: str,
    summary: str,
    source_stage: str,
    source_id: str,
    quality: str = "usable",
    blockers: Optional[Sequence[str]] = None,
    supports: Optional[Sequence[str]] = None,
    limitations: Optional[Sequence[str]] = None,
) -> Dict[str, Any]:
    item = {
        "evidence_id": _stable_id("update_evidence", evidence_type, title, source_id),
        "version": VERSION,
        "evidence_type": evidence_type,
        "title": title,
        "summary": summary,
        "source_stage": source_stage,
        "source_id": source_id,
        "quality": quality,
        "blockers": list(blockers or []),
        "supports": list(supports or []),
        "limitations": list(limitations or []),
        "captured_at": _now(),
        "capture_scope": "in_memory_payload_only",
    }
    item.update(BLOCKED_AUTHORITY)
    return item


def capture_update_evidence_bundle(
    inspection: Optional[Dict[str, Any]] = None,
    execution_plan: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    inspector = _load_update_inspector_module()
    validation = _load_validation_plan_module()

    active_inspection = dict(inspection or inspector.inspect_update_package_candidate())
    active_plan = dict(execution_plan or validation.build_controlled_validation_execution_plan(active_inspection))

    candidate = active_inspection.get("candidate", {})
    blockers: List[str] = []
    if active_inspection.get("risk_level") == "blocked":
        blockers.append("inspection_blocked")
    if active_plan.get("gate_state") == "blocked":
        blockers.extend(active_plan.get("blockers", []))

    items: List[Dict[str, Any]] = [
        make_update_evidence_item(
            "inspection_metadata",
            "Update candidate metadata",
            f"Candidate {candidate.get('package_id')} inspected as metadata-only payload.",
            "S506-S512",
            str(active_inspection.get("inspection_id")),
            quality="usable" if active_inspection.get("risk_level") != "blocked" else "blocked",
            blockers=active_inspection.get("missing_fields", []),
            supports=["candidate_identity", "declared_purpose", "target_paths"],
            limitations=["metadata_only", "no_download", "no_body_read"],
        ),
        make_update_evidence_item(
            "zero_trust_check",
            "Zero-trust inspection summary",
            f"Risk level: {active_inspection.get('risk_level')}; readiness score: {active_inspection.get('readiness_score')}.",
            "S507",
            str(active_inspection.get("inspection_id")),
            quality="usable" if active_inspection.get("risk_level") in {"review_ready", "moderate"} else "blocked",
            blockers=blockers,
            supports=["risk_level", "forbidden_authority_check", "protected_path_check"],
            limitations=["checks_declared_not_executed"],
        ),
        make_update_evidence_item(
            "validation_plan",
            "Controlled validation plan",
            f"Plan gate state: {active_plan.get('gate_state')}; execution remains blocked.",
            "S520-S526",
            str(active_plan.get("execution_plan_id")),
            quality="usable",
            blockers=active_plan.get("blockers", []),
            supports=["phase_plan", "command_manifest", "preflight_context"],
            limitations=["no_command_execution", "no_test_execution"],
        ),
        make_update_evidence_item(
            "command_manifest",
            "Validation command manifest",
            f"{active_plan.get('command_manifest', {}).get('command_count', 0)} commands declared; none executed.",
            "S521",
            str(active_plan.get("command_manifest", {}).get("command_manifest_id")),
            quality="usable",
            blockers=[],
            supports=["declared_commands", "future_manual_validation_plan"],
            limitations=["declarative_only", "operator_execution_owner_required"],
        ),
        make_update_evidence_item(
            "rollback_checklist",
            "Rollback proof checklist",
            "Rollback proof checklist exists but rollback has not been proven.",
            "S524",
            "rollback_checklist_reference",
            quality="limited",
            blockers=["rollback_not_proven"],
            supports=["rollback_requirements"],
            limitations=["no_backup_created", "no_restore_validated"],
        ),
        make_update_evidence_item(
            "execution_gate",
            "Operator controlled execution gate",
            "Execution gate remains blocked pending rollback proof, validation evidence, and operator approval.",
            "S525",
            "operator_controlled_execution_gate_reference",
            quality="usable",
            blockers=["operator_approval_required", "validation_not_executed"],
            supports=["blocked_execution_authority", "manual_owner_required"],
            limitations=["no_execution_performed"],
        ),
    ]

    blocked_count = sum(1 for item in items if item["quality"] == "blocked" or bool(item["blockers"]))
    usable_count = sum(1 for item in items if item["quality"] in {"usable", "strong"})
    quality_state = "blocked" if active_inspection.get("risk_level") == "blocked" else "needs_more_evidence" if blocked_count else "review_ready"

    bundle = {
        "evidence_bundle_id": _stable_id("update_evidence_bundle", active_inspection.get("inspection_id"), active_plan.get("execution_plan_id")),
        "version": VERSION,
        "created_at": _now(),
        "inspection_id": active_inspection.get("inspection_id"),
        "execution_plan_id": active_plan.get("execution_plan_id"),
        "candidate_package_id": candidate.get("package_id"),
        "items": items,
        "item_count": len(items),
        "usable_count": usable_count,
        "blocked_or_limited_count": blocked_count,
        "quality_state": quality_state,
        "capture_scope": "in_memory_payload_only",
    }
    bundle.update(BLOCKED_AUTHORITY)
    return bundle


def build_s528_evidence_capture_contract() -> Dict[str, Any]:
    bundle = capture_update_evidence_bundle()
    return _safe_base(
        "S528",
        "update_evidence_capture_contract_ready",
        sample_bundle={
            "item_count": bundle["item_count"],
            "usable_count": bundle["usable_count"],
            "quality_state": bundle["quality_state"],
        },
        capture_rules=[
            "Capture evidence from existing payloads only.",
            "Do not fetch, download, install, execute, or mutate.",
            "Mark missing proof as blockers instead of hiding it.",
        ],
    )


def build_operator_review_packet(
    evidence_bundle: Optional[Dict[str, Any]] = None,
    operator_note: str | None = None,
) -> Dict[str, Any]:
    bundle = dict(evidence_bundle or capture_update_evidence_bundle())
    blockers = sorted({blocker for item in bundle.get("items", []) for blocker in item.get("blockers", [])})
    verification_needed = sorted(
        set(blockers + ["operator_review_required", "rollback_proof_required", "validation_evidence_required"])
    )

    if bundle.get("quality_state") == "blocked":
        review_status = "blocked"
        recommended_action = "reject_candidate"
    elif blockers:
        review_status = "needs_more_evidence"
        recommended_action = "request_more_evidence"
    else:
        review_status = "ready_for_operator_decision"
        recommended_action = "prepare_future_manual_validation"

    packet = {
        "review_packet_id": _stable_id("operator_review_packet", bundle.get("evidence_bundle_id"), operator_note or ""),
        "version": VERSION,
        "created_at": _now(),
        "evidence_bundle_id": bundle.get("evidence_bundle_id"),
        "candidate_package_id": bundle.get("candidate_package_id"),
        "review_status": review_status,
        "recommended_action": recommended_action,
        "evidence_item_count": bundle.get("item_count", 0),
        "blockers": blockers,
        "verification_needed": verification_needed,
        "operator_note": str(operator_note or ""),
        "summary": (
            "Update candidate is ready for operator decision review."
            if review_status == "ready_for_operator_decision"
            else "Update candidate requires more evidence or rejection before any future validation."
        ),
        "decision_execution_allowed": False,
        "queue_persistent_write_allowed": False,
        "review_only": True,
    }
    packet.update(BLOCKED_AUTHORITY)
    return packet


def build_s529_operator_review_packet_contract() -> Dict[str, Any]:
    packet = build_operator_review_packet(operator_note="S529 sample review packet.")
    return _safe_base(
        "S529",
        "operator_review_packet_contract_ready",
        review_statuses=REVIEW_STATUSES,
        recommended_actions=RECOMMENDED_ACTIONS,
        packet_fields=[
            "review_packet_id",
            "evidence_bundle_id",
            "candidate_package_id",
            "review_status",
            "recommended_action",
            "evidence_item_count",
            "blockers",
            "verification_needed",
            "operator_note",
            "summary",
            "review_only",
        ],
        sample_packet={
            "review_status": packet["review_status"],
            "recommended_action": packet["recommended_action"],
            "evidence_item_count": packet["evidence_item_count"],
        },
    )


def build_operator_review_queue(packets: Optional[Sequence[Dict[str, Any]]] = None) -> Dict[str, Any]:
    active_packets = list(packets or [build_operator_review_packet()])
    by_status: Dict[str, List[str]] = {}
    by_action: Dict[str, List[str]] = {}
    blocked_packets: List[str] = []

    for packet in active_packets:
        packet_id = str(packet.get("review_packet_id", ""))
        status = str(packet.get("review_status", "queued_for_review"))
        action = str(packet.get("recommended_action", "hold"))
        by_status.setdefault(status, []).append(packet_id)
        by_action.setdefault(action, []).append(packet_id)
        if status == "blocked" or bool(packet.get("blockers")):
            blocked_packets.append(packet_id)

    queue = {
        "review_queue_id": _stable_id("operator_review_queue", len(active_packets), sorted(packet.get("review_packet_id", "") for packet in active_packets)),
        "version": VERSION,
        "created_at": _now(),
        "queue_scope": "supplied_packets_in_memory_only",
        "packet_count": len(active_packets),
        "packets": active_packets,
        "by_status": {key: sorted(value) for key, value in by_status.items()},
        "by_recommended_action": {key: sorted(value) for key, value in by_action.items()},
        "blocked_packets": sorted(blocked_packets),
        "queue_persistent_write_allowed": False,
        "queue_persistent_write_performed": False,
        "operator_review_required": True,
    }
    queue.update(BLOCKED_AUTHORITY)
    return queue


def build_s530_operator_review_queue_contract() -> Dict[str, Any]:
    inspector = _load_update_inspector_module()
    blocked_inspection = inspector.inspect_update_package_candidate(
        inspector.build_sample_update_candidate(
            package_id="blocked_review_queue_demo",
            expected_hash="",
            signature_present=False,
            rollback_plan_present=False,
            apply_allowed=True,
        )
    )
    blocked_bundle = capture_update_evidence_bundle(inspection=blocked_inspection)
    packets = [
        build_operator_review_packet(operator_note="Normal sample packet."),
        build_operator_review_packet(blocked_bundle, operator_note="Blocked sample packet."),
    ]
    queue = build_operator_review_queue(packets)
    return _safe_base(
        "S530",
        "operator_review_queue_contract_ready",
        sample_queue={
            "packet_count": queue["packet_count"],
            "status_keys": sorted(queue["by_status"].keys()),
            "blocked_count": len(queue["blocked_packets"]),
        },
        queue_rules=[
            "Queue is built from supplied packets only.",
            "No persistent queue storage occurs.",
            "Queue does not execute operator decisions.",
            "Blocked packets must remain visible.",
        ],
    )


def build_review_decision_recommendation(packet: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    active_packet = dict(packet or build_operator_review_packet())
    status = active_packet.get("review_status", "queued_for_review")
    blockers = list(active_packet.get("blockers", []))
    verification_needed = list(active_packet.get("verification_needed", []))

    if status == "blocked":
        recommendation = "reject_candidate"
    elif blockers or verification_needed:
        recommendation = "request_more_evidence"
    elif status == "ready_for_operator_decision":
        recommendation = "prepare_future_manual_validation"
    else:
        recommendation = "hold"

    decision = {
        "decision_recommendation_id": _stable_id("review_decision", active_packet.get("review_packet_id"), recommendation),
        "version": VERSION,
        "created_at": _now(),
        "review_packet_id": active_packet.get("review_packet_id"),
        "recommendation": recommendation,
        "reasoning": {
            "review_status": status,
            "blockers": blockers,
            "verification_needed": verification_needed,
        },
        "allowed_result": "operator_review_recommendation_only",
        "decision_execution_allowed": False,
        "operator_decision_execution_performed": False,
        "can_promote_update": False,
        "can_apply_update": False,
    }
    decision.update(BLOCKED_AUTHORITY)
    return decision


def build_s531_review_decision_recommendation_contract() -> Dict[str, Any]:
    packet = build_operator_review_packet()
    decision = build_review_decision_recommendation(packet)
    return _safe_base(
        "S531",
        "review_decision_recommendation_contract_ready",
        sample_decision=decision,
        decision_rules=[
            "Recommendation is not execution.",
            "Operator review is still required.",
            "Promotion and update application remain impossible here.",
            "Missing validation or rollback evidence forces more-evidence or rejection recommendation.",
        ],
    )


def build_s532_cockpit_asset_manifest(project_root: str | Path | None = None) -> Dict[str, Any]:
    root = Path(project_root) if project_root is not None else Path.cwd()
    js = root / JS_ASSET
    css = root / CSS_ASSET
    return _safe_base(
        "S532",
        "cockpit_asset_manifest_ready",
        assets={
            "js": JS_ASSET,
            "css": CSS_ASSET,
            "js_exists": js.exists(),
            "css_exists": css.exists(),
        },
        cockpit_regions=[
            "update_evidence_review_queue_panel",
            "evidence_bundle_card",
            "operator_review_packet_card",
            "review_queue_table",
            "review_decision_recommendation_card",
        ],
        visual_authority="presentation_only",
    )


def build_s533_stop_gate(report_dir: str | Path | None = None, project_root: str | Path | None = None) -> Dict[str, Any]:
    inspector = _load_update_inspector_module()

    s527 = build_s527_update_evidence_item_schema()
    normal_bundle = capture_update_evidence_bundle()
    normal_packet = build_operator_review_packet(normal_bundle)
    normal_queue = build_operator_review_queue([normal_packet])
    normal_decision = build_review_decision_recommendation(normal_packet)

    blocked_inspection = inspector.inspect_update_package_candidate(
        inspector.build_sample_update_candidate(
            package_id="blocked_s533_demo",
            expected_hash="",
            signature_present=False,
            rollback_plan_present=False,
            download_allowed=True,
            apply_allowed=True,
        )
    )
    blocked_bundle = capture_update_evidence_bundle(inspection=blocked_inspection)
    blocked_packet = build_operator_review_packet(blocked_bundle)
    blocked_queue = build_operator_review_queue([normal_packet, blocked_packet])
    blocked_decision = build_review_decision_recommendation(blocked_packet)

    s528 = build_s528_evidence_capture_contract()
    s529 = build_s529_operator_review_packet_contract()
    s530 = build_s530_operator_review_queue_contract()
    s531 = build_s531_review_decision_recommendation_contract()
    s532 = build_s532_cockpit_asset_manifest(project_root)

    checks = {
        "s527_schema_ready": "inspection_metadata" in s527["evidence_types"],
        "s528_capture_ready": normal_bundle["item_count"] >= 5 and normal_bundle["network_request_performed"] is False,
        "s529_packet_ready": normal_packet["review_only"] is True and normal_packet["decision_execution_allowed"] is False,
        "s530_queue_ready": normal_queue["packet_count"] == 1 and normal_queue["queue_persistent_write_performed"] is False,
        "s531_decision_ready": normal_decision["decision_execution_allowed"] is False and normal_decision["can_apply_update"] is False,
        "s532_assets_exist": s532["assets"]["js_exists"] is True and s532["assets"]["css_exists"] is True,
        "blocked_packet_visible": blocked_packet["review_status"] == "blocked" and bool(blocked_packet["blockers"]),
        "blocked_queue_tracks_blocked": blocked_packet["review_packet_id"] in blocked_queue["blocked_packets"],
        "blocked_decision_rejects": blocked_decision["recommendation"] == "reject_candidate",
        "no_queue_persistence": blocked_queue["queue_persistent_write_performed"] is False,
        "all_authority_blocked": all(normal_packet.get(flag) is False for flag in BLOCKED_AUTHORITY),
    }

    ok = all(checks.values())
    result = _safe_base(
        "S533",
        "claire_update_evidence_review_queue_passed" if ok else "claire_update_evidence_review_queue_failed",
        ok=ok,
        ready=ok,
        checks=checks,
        sample_outputs={
            "normal_bundle": normal_bundle,
            "normal_packet": normal_packet,
            "normal_queue": normal_queue,
            "normal_decision": normal_decision,
            "blocked_bundle": blocked_bundle,
            "blocked_packet": blocked_packet,
            "blocked_queue": blocked_queue,
            "blocked_decision": blocked_decision,
        },
        forward_motion_allowed=ok,
        stop_point="STOP POINT A - update review queue exists; evidence packets can be reviewed, still no execution.",
        next_phase="S534-S540 Controlled validation result intake contract",
    )

    if report_dir is not None:
        target_dir = Path(report_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        (target_dir / "s533_claire_update_evidence_review_queue_stop_gate.json").write_text(
            __import__("json").dumps(result, indent=2),
            encoding="utf-8",
        )

    return result


def build_claire_update_evidence_review_queue_s527_s533(project_root: str | Path | None = None) -> Dict[str, Any]:
    return _safe_base(
        "S527-S533",
        "claire_update_evidence_review_queue_ready",
        contracts={
            "s527": build_s527_update_evidence_item_schema(),
            "s528": build_s528_evidence_capture_contract(),
            "s529": build_s529_operator_review_packet_contract(),
            "s530": build_s530_operator_review_queue_contract(),
            "s531": build_s531_review_decision_recommendation_contract(),
            "s532": build_s532_cockpit_asset_manifest(project_root),
        },
        stop_gate=build_s533_stop_gate(project_root=project_root),
    )


__all__ = [
    "VERSION",
    "PHASE",
    "BLOCKED_AUTHORITY",
    "EVIDENCE_TYPES",
    "REVIEW_STATUSES",
    "RECOMMENDED_ACTIONS",
    "build_s527_update_evidence_item_schema",
    "make_update_evidence_item",
    "capture_update_evidence_bundle",
    "build_s528_evidence_capture_contract",
    "build_operator_review_packet",
    "build_s529_operator_review_packet_contract",
    "build_operator_review_queue",
    "build_s530_operator_review_queue_contract",
    "build_review_decision_recommendation",
    "build_s531_review_decision_recommendation_contract",
    "build_s532_cockpit_asset_manifest",
    "build_s533_stop_gate",
    "build_claire_update_evidence_review_queue_s527_s533",
]
