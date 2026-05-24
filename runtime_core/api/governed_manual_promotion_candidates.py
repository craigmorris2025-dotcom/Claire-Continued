from __future__ import annotations

import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

LOCKED_AUTHORITY = {
    "backend_owns_truth": True,
    "cockpit_presentation_only": True,
    "fail_closed_governance": True,
    "runtime_authority_blocked": True,
    "browser_execution_blocked": True,
    "javascript_execution_blocked": True,
    "runtime_truth_mutation_blocked": True,
    "autonomous_execution_blocked": True,
    "automatic_updates_blocked": True,
    "evidence_quarantine_required": True,
    "manual_promotion_required": True,
    "continuous_live_crawling_blocked": True,
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def stable_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_json(data: Any) -> str:
    return sha256_text(stable_json(data))


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
    return path


def _project_root(root: str | Path | None = None) -> Path:
    return Path(root).resolve() if root else Path.cwd().resolve()


def _load_latest_json(folder: Path, glob_pattern: str = "*.json") -> tuple[Path, dict[str, Any]]:
    candidates = sorted(folder.glob(glob_pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    if not candidates:
        raise FileNotFoundError(f"No JSON artifacts found in {folder}")
    path = candidates[0]
    return path, read_json(path)


def _normalize_claims(extraction: dict[str, Any]) -> list[dict[str, Any]]:
    claims: list[dict[str, Any]] = []
    for key in ("claims", "structured_claims", "knowledge_claims"):
        raw = extraction.get(key)
        if isinstance(raw, list):
            for index, item in enumerate(raw):
                claim = dict(item) if isinstance(item, dict) else {"claim_text": str(item)}
                claim.setdefault("claim_id", f"claim-{index + 1:04d}")
                claim.setdefault("claim_type", claim.get("type", "unclassified"))
                claim.setdefault("confidence", claim.get("confidence", "requires_review"))
                claims.append(claim)
    if not claims:
        extracted = extraction.get("extracted_knowledge") or extraction.get("knowledge") or extraction
        if isinstance(extracted, dict):
            for key, value in extracted.items():
                if key.startswith("_") or key in {"metadata", "governance", "locked_authority"}:
                    continue
                if isinstance(value, (str, int, float, bool)) and str(value).strip():
                    claims.append({"claim_id": f"claim-{len(claims)+1:04d}", "claim_type": key, "claim_text": str(value), "confidence": "requires_review"})
                elif isinstance(value, list):
                    for item in value[:50]:
                        claims.append({"claim_id": f"claim-{len(claims)+1:04d}", "claim_type": key, "claim_text": stable_json(item) if isinstance(item, dict) else str(item), "confidence": "requires_review"})
    return claims


def _evidence_sha_from_payload(payload: dict[str, Any]) -> str:
    for key in ("evidence_sha256", "source_sha256", "payload_sha256", "sha256"):
        value = payload.get(key)
        if isinstance(value, str) and value:
            return value
    return sha256_json(payload)


def build_evidence_review_manifest(root: str | Path | None = None, extraction_path: str | Path | None = None, basket_path: str | Path | None = None) -> dict[str, Any]:
    root_path = _project_root(root)
    output_dir = root_path / "output" / "review_manifests"
    if extraction_path:
        extraction_file = Path(extraction_path)
        extraction = read_json(extraction_file)
    else:
        extraction_file, extraction = _load_latest_json(root_path / "output" / "structured_knowledge")
    if basket_path:
        basket_file = Path(basket_path)
        basket = read_json(basket_file)
    else:
        try:
            basket_file, basket = _load_latest_json(root_path / "output" / "evidence_baskets")
        except FileNotFoundError:
            basket_file, basket = Path("missing-evidence-basket.json"), {}
    claims = _normalize_claims(extraction)
    seed = {"extraction_sha256": sha256_json(extraction), "basket_sha256": sha256_json(basket), "claims": claims, "locked_authority": LOCKED_AUTHORITY}
    candidate_id = "S38-CANDIDATE-" + sha256_json(seed)[:16].upper()
    manifest = {
        "schema_version": "s38r9.review_manifest.v1",
        "candidate_id": candidate_id,
        "created_at": utc_now_iso(),
        "phase": "S38R9",
        "status": "review_manifest_created",
        "operator_review_state": "not_reviewed",
        "promotion_state": "not_promoted",
        "runtime_truth_mutated": False,
        "manual_promotion_required": True,
        "locked_authority": dict(LOCKED_AUTHORITY),
        "lineage": {
            "extraction_path": str(extraction_file),
            "evidence_basket_path": str(basket_file),
            "extraction_sha256": sha256_json(extraction),
            "evidence_basket_sha256": sha256_json(basket),
            "evidence_sha256": _evidence_sha_from_payload(basket or extraction),
        },
        "claim_count": len(claims),
        "structured_claims": claims,
        "review_requirements": [
            "operator must inspect source lineage",
            "operator must inspect extracted claims",
            "operator must inspect contradiction registry",
            "operator must explicitly approve before any future truth promotion",
        ],
        "governance_warnings": [
            "proposal-only artifact",
            "quarantined evidence only",
            "does not mutate runtime truth",
            "does not enable automatic updates",
        ],
    }
    manifest["manifest_sha256"] = sha256_json(manifest)
    write_json(output_dir / f"{candidate_id}.review_manifest.json", manifest)
    return manifest


def score_promotion_candidate(root: str | Path | None = None, manifest_path: str | Path | None = None) -> dict[str, Any]:
    root_path = _project_root(root)
    output_dir = root_path / "output" / "promotion_candidate_scores"
    manifest_file, manifest = (Path(manifest_path), read_json(Path(manifest_path))) if manifest_path else _load_latest_json(root_path / "output" / "review_manifests")
    claims = manifest.get("structured_claims") or []
    lineage = manifest.get("lineage") or {}
    warnings = list(manifest.get("governance_warnings") or [])
    score = 0
    dimensions: dict[str, Any] = {}
    dimensions["source_lineage_present"] = bool(lineage.get("evidence_sha256"))
    score += 20 if dimensions["source_lineage_present"] else 0
    dimensions["claims_present"] = len(claims) > 0
    score += 20 if dimensions["claims_present"] else 0
    dimensions["claim_count"] = len(claims)
    score += min(len(claims), 10)
    dimensions["manual_promotion_required"] = manifest.get("manual_promotion_required") is True
    score += 15 if dimensions["manual_promotion_required"] else -50
    dimensions["runtime_truth_mutated"] = manifest.get("runtime_truth_mutated") is True
    if dimensions["runtime_truth_mutated"]:
        score = min(score, 0)
        warnings.append("runtime truth mutation detected; candidate must be rejected")
    dimensions["locked_authority_consistent"] = manifest.get("locked_authority", {}).get("runtime_truth_mutation_blocked") is True
    score += 20 if dimensions["locked_authority_consistent"] else -25
    readiness = "blocked"
    if score >= 70 and not dimensions["runtime_truth_mutated"]:
        readiness = "eligible_for_manual_review"
    if score >= 85 and not dimensions["runtime_truth_mutated"]:
        readiness = "strong_manual_review_candidate"
    result = {
        "schema_version": "s38r10.promotion_candidate_score.v1",
        "created_at": utc_now_iso(),
        "phase": "S38R10",
        "candidate_id": manifest.get("candidate_id"),
        "status": "candidate_scored",
        "readiness": readiness,
        "promotion_readiness_score": max(0, min(score, 100)),
        "score_dimensions": dimensions,
        "manual_promotion_required": True,
        "runtime_truth_mutated": False,
        "promotion_state": "not_promoted",
        "source_manifest_path": str(manifest_file),
        "source_manifest_sha256": sha256_json(manifest),
        "governance_warnings": sorted(set(warnings)),
        "locked_authority": dict(LOCKED_AUTHORITY),
    }
    result["score_sha256"] = sha256_json(result)
    write_json(output_dir / f"{result.get('candidate_id') or 'unknown-candidate'}.promotion_score.json", result)
    return result


def _claim_key(claim: dict[str, Any]) -> str:
    text = str(claim.get("claim_text") or claim.get("text") or claim.get("value") or "").strip().lower()
    ctype = str(claim.get("claim_type") or claim.get("type") or "unclassified").strip().lower()
    return sha256_text(f"{ctype}:{text}")


def _detect_contradictions(claims: list[dict[str, Any]]) -> list[dict[str, Any]]:
    contradictions: list[dict[str, Any]] = []
    by_type: dict[str, list[dict[str, Any]]] = {}
    for claim in claims:
        by_type.setdefault(str(claim.get("claim_type", "unclassified")).lower(), []).append(claim)
    for claim_type, typed_claims in by_type.items():
        seen: dict[str, dict[str, Any]] = {}
        for claim in typed_claims:
            subject = str(claim.get("subject") or claim.get("entity") or "").strip().lower()
            predicate = str(claim.get("predicate") or claim.get("attribute") or claim_type).strip().lower()
            value = str(claim.get("value") or claim.get("claim_text") or "").strip().lower()
            key = f"{subject}:{predicate}"
            previous = seen.get(key)
            previous_value = str((previous or {}).get("value") or (previous or {}).get("claim_text") or "").strip().lower()
            if key and previous and value and value != previous_value:
                contradictions.append({"contradiction_id": "contradiction-" + sha256_json([previous, claim])[:12], "claim_type": claim_type, "reason": "same subject/predicate appears with different values", "claim_a": previous.get("claim_id"), "claim_b": claim.get("claim_id"), "severity": "requires_operator_review"})
            elif key and value:
                seen[key] = claim
    return contradictions


def build_lineage_contradiction_registry(root: str | Path | None = None, manifest_path: str | Path | None = None) -> dict[str, Any]:
    root_path = _project_root(root)
    output_dir = root_path / "output" / "lineage_contradiction_registry"
    manifest_file, manifest = (Path(manifest_path), read_json(Path(manifest_path))) if manifest_path else _load_latest_json(root_path / "output" / "review_manifests")
    claims = manifest.get("structured_claims") or []
    claim_entries = []
    duplicate_keys: dict[str, list[str]] = {}
    for claim in claims:
        key = _claim_key(claim)
        claim_id = str(claim.get("claim_id") or key[:12])
        duplicate_keys.setdefault(key, []).append(claim_id)
        claim_entries.append({"claim_id": claim_id, "claim_key": key, "candidate_id": manifest.get("candidate_id"), "source_evidence_sha256": manifest.get("lineage", {}).get("evidence_sha256"), "source_manifest_sha256": sha256_json(manifest), "claim_type": claim.get("claim_type", "unclassified")})
    duplicates = [{"claim_key": key, "claim_ids": ids, "duplicate_count": len(ids)} for key, ids in duplicate_keys.items() if len(ids) > 1]
    contradictions = _detect_contradictions(claims)
    registry = {
        "schema_version": "s38r11.lineage_contradiction_registry.v1",
        "created_at": utc_now_iso(),
        "phase": "S38R11",
        "candidate_id": manifest.get("candidate_id"),
        "status": "lineage_registry_created",
        "source_manifest_path": str(manifest_file),
        "source_manifest_sha256": sha256_json(manifest),
        "claim_lineage": claim_entries,
        "duplicate_claims": duplicates,
        "contradictions": contradictions,
        "contradiction_count": len(contradictions),
        "duplicate_count": len(duplicates),
        "manual_review_required": True,
        "runtime_truth_mutated": False,
        "promotion_state": "not_promoted",
        "locked_authority": dict(LOCKED_AUTHORITY),
    }
    registry["registry_sha256"] = sha256_json(registry)
    write_json(output_dir / f"{registry.get('candidate_id') or 'unknown-candidate'}.lineage_contradiction_registry.json", registry)
    return registry


def build_manual_promotion_package(root: str | Path | None = None, manifest_path: str | Path | None = None, score_path: str | Path | None = None, registry_path: str | Path | None = None) -> dict[str, Any]:
    root_path = _project_root(root)
    output_dir = root_path / "output" / "manual_promotion_packages"
    manifest_file, manifest = (Path(manifest_path), read_json(Path(manifest_path))) if manifest_path else _load_latest_json(root_path / "output" / "review_manifests")
    candidate_id = manifest.get("candidate_id") or "unknown-candidate"
    score_file, score = (Path(score_path), read_json(Path(score_path))) if score_path else _load_latest_json(root_path / "output" / "promotion_candidate_scores", f"{candidate_id}*.json")
    registry_file, registry = (Path(registry_path), read_json(Path(registry_path))) if registry_path else _load_latest_json(root_path / "output" / "lineage_contradiction_registry", f"{candidate_id}*.json")
    blocked_reasons = []
    if manifest.get("runtime_truth_mutated") is True or score.get("runtime_truth_mutated") is True or registry.get("runtime_truth_mutated") is True:
        blocked_reasons.append("runtime truth mutation detected")
    if registry.get("contradiction_count", 0) > 0:
        blocked_reasons.append("contradictions require operator review before approval")
    if score.get("promotion_readiness_score", 0) < 70:
        blocked_reasons.append("promotion readiness score below manual review threshold")
    package = {
        "schema_version": "s38r12.manual_promotion_package.v1",
        "created_at": utc_now_iso(),
        "phase": "S38R12",
        "candidate_id": candidate_id,
        "status": "manual_promotion_package_created",
        "package_state": "manual_review_ready" if not blocked_reasons else "manual_review_blocked_pending_resolution",
        "blocked_reasons": blocked_reasons,
        "operator_decision": "pending",
        "manual_promotion_required": True,
        "runtime_truth_mutated": False,
        "automatic_update_performed": False,
        "promotion_state": "not_promoted",
        "candidate_summary": {"claim_count": manifest.get("claim_count", 0), "readiness": score.get("readiness"), "promotion_readiness_score": score.get("promotion_readiness_score"), "contradiction_count": registry.get("contradiction_count", 0), "duplicate_count": registry.get("duplicate_count", 0)},
        "artifact_lineage": {"review_manifest_path": str(manifest_file), "review_manifest_sha256": sha256_json(manifest), "promotion_score_path": str(score_file), "promotion_score_sha256": sha256_json(score), "lineage_registry_path": str(registry_file), "lineage_registry_sha256": sha256_json(registry)},
        "approval_checklist": ["verify evidence source was approved before fetch", "verify evidence remained quarantined", "verify extracted claims are correct", "resolve or accept contradiction registry findings", "confirm proposed destination surface in a future controlled promotion phase", "record explicit operator approval before any future truth mutation"],
        "locked_authority": dict(LOCKED_AUTHORITY),
        "governance_warnings": ["operator-review proposal only", "does not update Claire runtime truth", "does not enable autonomous execution", "does not enable automatic updates"],
    }
    package["package_sha256"] = sha256_json(package)
    write_json(output_dir / f"{candidate_id}.manual_promotion_package.json", package)
    return package


def run_s38r9_r12_pipeline(root: str | Path | None = None) -> dict[str, Any]:
    root_path = _project_root(root)
    manifest = build_evidence_review_manifest(root_path)
    score = score_promotion_candidate(root_path)
    registry = build_lineage_contradiction_registry(root_path)
    package = build_manual_promotion_package(root_path)
    return {"schema_version": "s38r9_r12.pipeline_result.v1", "created_at": utc_now_iso(), "phase": "S38R9-R12", "status": "manual_promotion_candidate_pipeline_complete", "candidate_id": manifest.get("candidate_id"), "runtime_truth_mutated": False, "automatic_update_performed": False, "manual_promotion_required": True, "outputs": {"review_manifest": manifest, "promotion_score": score, "lineage_contradiction_registry": registry, "manual_promotion_package": package}, "locked_authority": dict(LOCKED_AUTHORITY)}
