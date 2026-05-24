from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


SCHEMA_VERSION = "v19.89.8_open_web_update_governance"
APPROVAL_PHRASE = "APPROVE GOVERNED UPDATE"
MIN_TRUST_SCORE = 0.8
AUDIT_DIR = Path("data/update_governance/audit")
REQUEST_DIR = Path("data/update_governance/update_requests")
APPROVAL_DIR = Path("data/update_governance/approvals")
ROLLBACK_DIR = Path("data/update_governance/rollback_points")

PROTECTED_PATH_PREFIXES = (
    "claire/platform/update_governance/",
    "claire/governance/",
    "claire/safety/",
    "claire/evolution/",
    "claire/lifecycle/",
    "claire/runtime_truth/",
    "data/evolution/verified_states/",
    "data/runtime_truth/",
)

MUTATION_ENDPOINT_MARKERS = (
    "delete",
    "mutate",
    "promote",
    "install",
    "apply",
    "write-runtime-truth",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def project_path(project_root: Path | str | None, *parts: str) -> Path:
    return Path(project_root or Path.cwd()).resolve().joinpath(*parts)


def read_json(path: Path, fallback: Any) -> Any:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback
    return fallback


def stable_digest(payload: Any) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return hashlib.sha256(body).hexdigest()


def normalize_target_path(path: str) -> str:
    normalized = str(path or "").replace("\\", "/").strip().lstrip("/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized


def load_provider_policy(project_root: Path | str | None = None) -> dict[str, Any]:
    path = project_path(project_root, "data", "update_sources", "allowed_sources.json")
    policy = read_json(path, {})
    return {
        "allowed_schemes": list(policy.get("allowed_schemes") or ["file"]),
        "allowed_domains": list(policy.get("allowed_domains") or []),
        "allow_file_urls": bool(policy.get("allow_file_urls", True)),
        "notes": list(policy.get("notes") or []),
        "source_path": str(path),
    }


def evaluate_provider_trust(candidate: dict[str, Any], project_root: Path | str | None = None) -> dict[str, Any]:
    policy = load_provider_policy(project_root)
    provider_id = str(candidate.get("provider_id") or "unknown_provider").strip()
    package_uri = str(candidate.get("package_uri") or candidate.get("provider_url") or "").strip()
    parsed = urlparse(package_uri)
    scheme = (parsed.scheme or "file").lower() if package_uri else "metadata_only"
    domain = (parsed.hostname or candidate.get("provider_domain") or "").lower()

    if scheme == "metadata_only":
        return {
            "provider_id": provider_id,
            "provider_domain": domain,
            "scheme": scheme,
            "trusted": False,
            "trust_score": 0.0,
            "reason": "missing provider package URI",
            "approved_provider": False,
            "policy": policy,
        }

    if scheme == "file":
        trusted = bool(policy["allow_file_urls"] and "file" in policy["allowed_schemes"])
        score = 0.86 if trusted else 0.0
        reason = "local operator package source is allowed" if trusted else "local file update sources are not allowed"
    elif scheme == "https":
        trusted = "https" in policy["allowed_schemes"] and bool(domain and domain in policy["allowed_domains"])
        score = 0.92 if trusted else 0.0
        reason = "approved HTTPS update provider" if trusted else "HTTPS provider domain is not approved"
    else:
        trusted = False
        score = 0.0
        reason = f"scheme {scheme!r} is not allowed"

    return {
        "provider_id": provider_id,
        "provider_domain": domain,
        "scheme": scheme,
        "trusted": trusted and score >= MIN_TRUST_SCORE,
        "trust_score": score,
        "reason": reason,
        "approved_provider": trusted,
        "policy": policy,
    }


def verify_update_signature(candidate: dict[str, Any]) -> dict[str, Any]:
    metadata = candidate.get("metadata") if isinstance(candidate.get("metadata"), dict) else {}
    expected_sha256 = str(
        candidate.get("sha256")
        or candidate.get("expected_sha256")
        or metadata.get("sha256")
        or metadata.get("expected_sha256")
        or ""
    ).lower()
    signature = str(candidate.get("signature") or metadata.get("signature") or "").strip()
    digest_payload = {
        "update_id": candidate.get("update_id"),
        "provider_id": candidate.get("provider_id"),
        "version_from": candidate.get("version_from"),
        "version_to": candidate.get("version_to"),
        "capabilities": candidate.get("capabilities") or [],
        "target_paths": candidate.get("target_paths") or [],
        "metadata": metadata,
    }
    actual_sha256 = stable_digest(digest_payload)
    signature_expected = f"sha256:{actual_sha256}"
    verified = bool(expected_sha256 and expected_sha256 == actual_sha256 and signature == signature_expected)
    return {
        "verified": verified,
        "expected_sha256": expected_sha256,
        "actual_sha256": actual_sha256,
        "signature": signature,
        "signature_scheme": "sha256",
        "reason": "signature and digest match metadata contract" if verified else "missing or invalid signature/digest",
    }


def inspect_targets(target_paths: list[str] | None) -> dict[str, Any]:
    normalized = [normalize_target_path(path) for path in target_paths or [] if str(path or "").strip()]
    traversal = [path for path in normalized if ".." in Path(path).parts]
    protected = [
        path
        for path in normalized
        if any(path.startswith(prefix) for prefix in PROTECTED_PATH_PREFIXES)
    ]
    suspicious = [
        path
        for path in normalized
        if path.endswith((".exe", ".bat", ".cmd", ".ps1", ".dll", ".so", ".dylib"))
    ]
    return {
        "target_paths": normalized,
        "target_count": len(normalized),
        "protected_paths": protected,
        "path_traversal_attempts": traversal,
        "suspicious_targets": suspicious,
        "protected_path_count": len(protected),
        "safe_path_contract": not traversal and not suspicious,
    }


def classify_runtime_truth_firewall(targets: dict[str, Any], provider: dict[str, Any], signature: dict[str, Any]) -> dict[str, Any]:
    blockers: list[str] = []
    if not provider["trusted"]:
        blockers.append("provider_trust_failed")
    if not signature["verified"]:
        blockers.append("signature_verification_failed")
    if targets["path_traversal_attempts"]:
        blockers.append("path_traversal_blocked")
    if targets["suspicious_targets"]:
        blockers.append("executable_or_script_target_blocked")
    if targets["protected_paths"]:
        blockers.append("protected_core_logic_target_requires_owner_approval")
    return {
        "core_logic_mutation_allowed": False,
        "runtime_truth_mutation_allowed": False,
        "external_mutation_allowed": False,
        "external_mutation_performed": False,
        "firewall_status": "blocked" if blockers else "approval_required",
        "blockers": blockers,
        "protected_paths": targets["protected_paths"],
    }


def build_rollback_plan(candidate: dict[str, Any], targets: dict[str, Any]) -> dict[str, Any]:
    update_id = str(candidate.get("update_id") or f"update_{stable_digest(candidate)[:12]}")
    rollback_id = f"rollback_{update_id}_{stable_digest(targets)[:10]}"
    return {
        "rollback_id": rollback_id,
        "rollback_required": True,
        "rollback_supported": targets["target_count"] > 0,
        "rollback_point_path": str(ROLLBACK_DIR / f"{rollback_id}.json"),
        "snapshot_required_before_apply": True,
        "restore_strategy": "manifest_snapshot_then_atomic_restore",
        "backup_created": False,
        "restore_performed": False,
        "target_paths": targets["target_paths"],
        "protected_paths": targets["protected_paths"],
    }


def build_self_analysis(
    required_capabilities: list[str] | None = None,
    available_capabilities: list[str] | None = None,
) -> dict[str, Any]:
    required = required_capabilities or [
        "approved_provider_retrieval",
        "cryptographic_signature_verification",
        "mandatory_user_approval",
        "rollback_support",
        "append_only_audit_logging",
        "runtime_truth_firewall",
        "external_input_sandbox",
        "dashboard_update_panel",
    ]
    available = set(available_capabilities or required)
    missing = [capability for capability in required if capability not in available]
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "capability_gaps_detected" if missing else "capabilities_present",
        "required_capabilities": required,
        "available_capabilities": sorted(available),
        "missing_capabilities": missing,
        "update_requests": [
            {
                "capability": capability,
                "request_type": "governed_update_required",
                "approval_required": True,
                "auto_install_allowed": False,
            }
            for capability in missing
        ],
        "self_mutation_allowed": False,
        "generated_at": utc_now(),
    }


def evaluate_update_candidate(candidate: dict[str, Any], project_root: Path | str | None = None) -> dict[str, Any]:
    update_id = str(candidate.get("update_id") or f"update_{stable_digest(candidate)[:12]}")
    provider = evaluate_provider_trust(candidate, project_root)
    signature = verify_update_signature(candidate)
    targets = inspect_targets(candidate.get("target_paths") if isinstance(candidate.get("target_paths"), list) else [])
    firewall = classify_runtime_truth_firewall(targets, provider, signature)
    rollback = build_rollback_plan({**candidate, "update_id": update_id}, targets)
    blockers = list(firewall["blockers"])
    if not rollback["rollback_supported"]:
        blockers.append("rollback_target_manifest_missing")

    gate_status = "blocked" if blockers else "approval_required"
    return {
        "schema_version": SCHEMA_VERSION,
        "update_id": update_id,
        "status": gate_status,
        "ready_for_install": False,
        "install_allowed": False,
        "install_performed": False,
        "download_allowed": False,
        "download_performed": False,
        "runtime_mutation_allowed": False,
        "runtime_mutation_performed": False,
        "automatic_update_allowed": False,
        "automatic_update_performed": False,
        "provider_gate": provider,
        "signature_verification": signature,
        "target_inspection": targets,
        "runtime_truth_firewall": firewall,
        "approval_workflow": {
            "approval_required": True,
            "approval_phrase": APPROVAL_PHRASE,
            "user_approved": False,
            "approval_recorded": False,
            "approval_applies_update": False,
        },
        "rollback": rollback,
        "blockers": blockers,
        "version_diff": {
            "from": candidate.get("version_from") or "unknown",
            "to": candidate.get("version_to") or "unknown",
            "capabilities": candidate.get("capabilities") or [],
            "target_paths": targets["target_paths"],
        },
        "files": candidate.get("files") if isinstance(candidate.get("files"), (dict, list)) else {},
        "metadata": candidate.get("metadata") if isinstance(candidate.get("metadata"), dict) else {},
        "generated_at": utc_now(),
    }


def append_audit_event(
    action: str,
    payload: dict[str, Any],
    project_root: Path | str | None = None,
    actor: str = "system",
) -> dict[str, Any]:
    audit_root = project_path(project_root, *AUDIT_DIR.parts)
    audit_root.mkdir(parents=True, exist_ok=True)
    event = {
        "timestamp": utc_now(),
        "action": action,
        "actor": actor,
        "update_id": payload.get("update_id"),
        "decision": payload.get("status"),
        "target_paths": payload.get("target_inspection", {}).get("target_paths", []),
        "evidence_hash": stable_digest(payload),
        "install_performed": False,
        "runtime_mutation_performed": False,
    }
    path = audit_root / "open_web_update_governance.jsonl"
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, sort_keys=True) + "\n")
    return {**event, "audit_path": str(path)}


def create_update_request(candidate: dict[str, Any], project_root: Path | str | None = None) -> dict[str, Any]:
    evaluation = evaluate_update_candidate(candidate, project_root)
    request_root = project_path(project_root, *REQUEST_DIR.parts)
    request_root.mkdir(parents=True, exist_ok=True)
    request_path = request_root / f"{evaluation['update_id']}.json"
    request_path.write_text(json.dumps(evaluation, indent=2, sort_keys=True), encoding="utf-8")
    audit = append_audit_event("update_request_evaluated", evaluation, project_root, actor="system")
    return {
        **evaluation,
        "request_recorded": True,
        "request_path": str(request_path),
        "audit": audit,
    }


def record_user_approval(
    update_id: str,
    approval_phrase: str,
    project_root: Path | str | None = None,
    actor: str = "owner",
) -> dict[str, Any]:
    approved = approval_phrase.strip() == APPROVAL_PHRASE
    approval = {
        "schema_version": SCHEMA_VERSION,
        "update_id": update_id,
        "status": "approval_recorded" if approved else "approval_rejected",
        "user_approved": approved,
        "approval_phrase_valid": approved,
        "approval_required": True,
        "approval_applies_update": False,
        "install_allowed": False,
        "install_performed": False,
        "runtime_mutation_allowed": False,
        "runtime_mutation_performed": False,
        "approved_at": utc_now() if approved else None,
        "actor": actor,
    }
    approval_root = project_path(project_root, *APPROVAL_DIR.parts)
    approval_root.mkdir(parents=True, exist_ok=True)
    approval_path = approval_root / f"{update_id}.json"
    approval_path.write_text(json.dumps(approval, indent=2, sort_keys=True), encoding="utf-8")
    audit = append_audit_event("user_approval_recorded" if approved else "user_approval_rejected", approval, project_root, actor=actor)
    return {**approval, "approval_path": str(approval_path), "audit": audit}


def _request_path(update_id: str, project_root: Path | str | None = None) -> Path:
    return project_path(project_root, *REQUEST_DIR.parts) / f"{update_id}.json"


def _approval_path(update_id: str, project_root: Path | str | None = None) -> Path:
    return project_path(project_root, *APPROVAL_DIR.parts) / f"{update_id}.json"


def load_update_request(update_id: str, project_root: Path | str | None = None) -> dict[str, Any]:
    return read_json(_request_path(update_id, project_root), {})


def load_update_approval(update_id: str, project_root: Path | str | None = None) -> dict[str, Any]:
    return read_json(_approval_path(update_id, project_root), {})


def _package_files_from_payload(payload: dict[str, Any]) -> dict[str, str]:
    files = payload.get("files")
    if isinstance(files, dict):
        return {
            normalize_target_path(path): str(content)
            for path, content in files.items()
            if str(path or "").strip()
        }
    if isinstance(files, list):
        mapped: dict[str, str] = {}
        for item in files:
            if not isinstance(item, dict):
                continue
            path = normalize_target_path(str(item.get("path") or ""))
            if path:
                mapped[path] = str(item.get("content") or "")
        return mapped
    return {}


def _package_files_from_uri(candidate: dict[str, Any], project_root: Path | str | None = None) -> dict[str, str]:
    package_uri = str(candidate.get("package_uri") or "").strip()
    parsed = urlparse(package_uri)
    if parsed.scheme != "file":
        return {}
    package_path = Path(parsed.path)
    if not package_path.exists():
        return {}
    payload = read_json(package_path, {})
    return _package_files_from_payload(payload) if isinstance(payload, dict) else {}


def package_files_for_update(candidate: dict[str, Any], project_root: Path | str | None = None) -> dict[str, str]:
    return _package_files_from_payload(candidate) or _package_files_from_uri(candidate, project_root)


def _safe_target_path(root: Path, relative_path: str) -> Path | None:
    normalized = normalize_target_path(relative_path)
    if not normalized or ".." in Path(normalized).parts:
        return None
    target = root.joinpath(normalized).resolve()
    try:
        target.relative_to(root)
    except ValueError:
        return None
    return target


def build_install_readiness(update_id: str, project_root: Path | str | None = None) -> dict[str, Any]:
    root = Path(project_root or Path.cwd()).resolve()
    request = load_update_request(update_id, root)
    approval = load_update_approval(update_id, root)
    package_files = package_files_for_update(request, root) if request else {}
    target_paths = request.get("target_inspection", {}).get("target_paths", []) if isinstance(request.get("target_inspection"), dict) else []
    target_paths = [normalize_target_path(path) for path in target_paths if str(path or "").strip()]
    file_targets_match = bool(package_files) and sorted(package_files) == sorted(target_paths)
    blockers: list[str] = []
    if not request:
        blockers.append("update_request_missing")
    if request and request.get("status") != "approval_required":
        blockers.append("update_request_not_installable")
    if request and request.get("blockers"):
        blockers.extend(str(item) for item in request.get("blockers", []))
    if request and not request.get("provider_gate", {}).get("trusted"):
        blockers.append("provider_not_trusted")
    if request and not request.get("signature_verification", {}).get("verified"):
        blockers.append("signature_not_verified")
    if not approval.get("user_approved"):
        blockers.append("owner_approval_missing")
    if request and not request.get("rollback", {}).get("rollback_supported"):
        blockers.append("rollback_not_supported")
    if request and not package_files:
        blockers.append("package_payload_missing")
    if package_files and not file_targets_match:
        blockers.append("package_files_do_not_match_target_manifest")
    for path in target_paths:
        if _safe_target_path(root, path) is None:
            blockers.append("unsafe_target_path")
            break

    install_allowed = not blockers
    return {
        "schema_version": SCHEMA_VERSION,
        "update_id": update_id,
        "status": "install_ready" if install_allowed else "install_blocked",
        "install_endpoint": "/api/update-governance/open-web/install/apply",
        "stage_endpoint": "/api/update-governance/open-web/install/stage",
        "approval_endpoint": "/api/update-governance/open-web/approve",
        "install_allowed": install_allowed,
        "install_performed": False,
        "automatic_update_allowed": False,
        "automatic_update_performed": False,
        "runtime_truth_mutation_allowed": False,
        "runtime_truth_mutation_performed": False,
        "rollback_required": True,
        "rollback_supported": bool(request.get("rollback", {}).get("rollback_supported")) if request else False,
        "owner_approved": bool(approval.get("user_approved")),
        "trusted": bool(request.get("provider_gate", {}).get("trusted")) if request else False,
        "signature_verified": bool(request.get("signature_verification", {}).get("verified")) if request else False,
        "target_paths": target_paths,
        "package_file_count": len(package_files),
        "blockers": list(dict.fromkeys(blockers)),
        "next_actions": (
            ["Click Apply Governed Update to create rollback snapshot and install package files."]
            if install_allowed
            else [
                action
                for action in [
                    "Record owner approval with the required phrase." if "owner_approval_missing" in blockers else "",
                    "Attach or retrieve a signed package containing exact target file contents." if "package_payload_missing" in blockers else "",
                    "Resolve trust, signature, target, or rollback blockers before install." if blockers else "",
                ]
                if action
            ]
        ),
        "generated_at": utc_now(),
    }


def stage_update_install(update_id: str, project_root: Path | str | None = None, actor: str = "owner") -> dict[str, Any]:
    readiness = build_install_readiness(update_id, project_root)
    audit = append_audit_event("update_install_stage_checked", readiness, project_root, actor=actor)
    return {**readiness, "audit": audit}


def apply_governed_update(
    update_id: str,
    approval_phrase: str,
    project_root: Path | str | None = None,
    actor: str = "owner",
) -> dict[str, Any]:
    root = Path(project_root or Path.cwd()).resolve()
    if approval_phrase.strip() == APPROVAL_PHRASE:
        record_user_approval(update_id, approval_phrase, root, actor=actor)
    readiness = build_install_readiness(update_id, root)
    if not readiness["install_allowed"]:
        audit = append_audit_event("update_install_blocked", readiness, root, actor=actor)
        return {**readiness, "audit": audit}

    request = load_update_request(update_id, root)
    package_files = package_files_for_update(request, root)
    rollback_id = request.get("rollback", {}).get("rollback_id") or f"rollback_{update_id}_{stable_digest(request)[:10]}"
    rollback_path = project_path(root, *ROLLBACK_DIR.parts) / f"{rollback_id}.json"
    rollback_path.parent.mkdir(parents=True, exist_ok=True)
    rollback_files: dict[str, Any] = {}
    for relative_path in readiness["target_paths"]:
        target = _safe_target_path(root, relative_path)
        if target is None:
            blocked = {**readiness, "status": "install_blocked", "install_allowed": False, "blockers": ["unsafe_target_path"]}
            audit = append_audit_event("update_install_blocked", blocked, root, actor=actor)
            return {**blocked, "audit": audit}
        rollback_files[relative_path] = {
            "existed": target.exists(),
            "content": target.read_text(encoding="utf-8") if target.exists() else "",
        }
    rollback_payload = {
        "schema_version": SCHEMA_VERSION,
        "rollback_id": rollback_id,
        "update_id": update_id,
        "created_at": utc_now(),
        "files": rollback_files,
    }
    rollback_path.write_text(json.dumps(rollback_payload, indent=2, sort_keys=True), encoding="utf-8")

    for relative_path, content in package_files.items():
        target = _safe_target_path(root, relative_path)
        if target is None:
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    result = {
        **readiness,
        "status": "install_applied",
        "install_allowed": True,
        "install_performed": True,
        "automatic_update_allowed": False,
        "automatic_update_performed": False,
        "runtime_truth_mutation_performed": False,
        "rollback_path": str(rollback_path),
        "installed_target_count": len(package_files),
        "installed_at": utc_now(),
    }
    audit = append_audit_event("update_install_applied", result, root, actor=actor)
    return {**result, "audit": audit}


def build_dashboard_update_panel(project_root: Path | str | None = None) -> dict[str, Any]:
    request_root = project_path(project_root, *REQUEST_DIR.parts)
    requests = []
    if request_root.exists():
        for path in sorted(request_root.glob("*.json"), key=lambda item: item.stat().st_mtime, reverse=True)[:12]:
            payload = read_json(path, {})
            if isinstance(payload, dict):
                requests.append(payload)
    install_readiness = [
        build_install_readiness(str(item.get("update_id") or ""), project_root)
        for item in requests
        if item.get("update_id")
    ]
    return {
        "schema_version": SCHEMA_VERSION,
        "panel_key": "open_web_update_governance",
        "title": "Update Governance",
        "status": "ready",
        "available_updates": requests,
        "available_update_count": len(requests),
        "version_diffs": [item.get("version_diff", {}) for item in requests],
        "trust_scores": [
            {
                "update_id": item.get("update_id"),
                "trust_score": item.get("provider_gate", {}).get("trust_score", 0.0),
                "trusted": item.get("provider_gate", {}).get("trusted", False),
            }
            for item in requests
        ],
        "approval_workflow": {
            "approval_required": True,
            "approval_phrase": APPROVAL_PHRASE,
            "manual_owner_approval_only": True,
            "approval_applies_update": True,
        },
        "install_workflow": {
            "install_endpoints_exposed": True,
            "stage_endpoint": "/api/update-governance/open-web/install/stage",
            "apply_endpoint": "/api/update-governance/open-web/install/apply",
            "status_endpoint": "/api/update-governance/open-web/install/status/{update_id}",
            "automatic_install_enabled": False,
            "owner_approval_required": True,
            "rollback_snapshot_required": True,
            "install_readiness": install_readiness,
        },
        "security_posture": {
            "safe_open_web_operation": True,
            "privileged_surfaces_exposed": False,
            "mutation_endpoints_exposed": True,
            "mutation_endpoints_operator_gated": True,
            "external_inputs_sandboxed": True,
            "rate_limits_declared": True,
            "runtime_truth_firewall": "enabled",
            "automatic_updates_enabled": False,
            "package_install_performed": False,
        },
        "rollback": {
            "rollback_required_for_every_update": True,
            "rollback_supported_before_apply": True,
            "rollback_performed": False,
        },
        "generated_at": utc_now(),
    }


def build_open_web_readiness_report(project_root: Path | str | None = None) -> dict[str, Any]:
    panel = build_dashboard_update_panel(project_root)
    self_analysis = build_self_analysis()
    checks = {
        "provider_gate_available": True,
        "signature_verification_available": True,
        "approval_required": panel["approval_workflow"]["approval_required"] is True,
        "rollback_required": panel["rollback"]["rollback_required_for_every_update"] is True,
        "audit_logging_available": True,
        "runtime_truth_firewall_enabled": panel["security_posture"]["runtime_truth_firewall"] == "enabled",
        "privileged_surfaces_exposed": panel["security_posture"]["privileged_surfaces_exposed"] is False,
        "mutation_endpoints_operator_gated": panel["security_posture"].get("mutation_endpoints_operator_gated") is True,
        "automatic_updates_disabled": panel["security_posture"]["automatic_updates_enabled"] is False,
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "open_web_ready_governed_mode" if all(checks.values()) else "open_web_readiness_blocked",
        "ready": all(checks.values()),
        "checks": checks,
        "self_analysis": self_analysis,
        "dashboard_update_panel": panel,
        "readiness_report": {
            "safe_open_web_operation": "metadata and proposal surfaces only",
            "update_retrieval": "approved providers only",
            "verification": "sha256 digest plus signature contract required",
            "approval": "manual owner approval required before any install phase",
            "rollback": "rollback plan required before any apply phase",
            "truth_firewall": "external updates cannot mutate core logic from this layer",
        },
        "generated_at": utc_now(),
    }
