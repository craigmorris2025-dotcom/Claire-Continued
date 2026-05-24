from __future__ import annotations

import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime_core.ingestion.source_boundary import FORBIDDEN_PREFIXES, INGESTION_ALLOWLIST
from runtime_core.pipeline.canonical_pipeline_sources import build_canonical_pipeline_source_index


REPORT_JSON = ROOT / "reports" / "SOURCE_AUTHORITY_AND_CLEANUP_AUDIT.json"
REPORT_MD = ROOT / "reports" / "SOURCE_AUTHORITY_AND_CLEANUP_AUDIT.md"


SOURCE_PACKS = ROOT / "data" / "source_packs" / "local_upload_source_packs.json"
CONTEXT_ISOLATION_MANIFEST = ROOT / "data" / "cleanup" / "context_isolation_manifest.json"

GENERATED_OR_LEGACY_ZONES = [
    "data/build_manifests",
    "data/cleanup",
    "data/proof",
    "data/runtime",
    "docs/audits",
    "docs/build_reports",
    "docs/cleanup",
    "docs/core_completion",
    "reports",
    "reports/backups",
    "tests/_quarantine_legacy_surfaces",
]

ACTIVE_GUIDE_PATTERNS = [
    "canonical_pipeline_source_index.json",
    "local_upload_source_packs.json",
    "pipeline",
    "Master docs",
]

LEGACY_LANGUAGE = [
    "legacy",
    "dashboard_v4",
    "dashboard_v5",
    "v17_",
    "v17.",
    "Singularity-Aligned",
    "Success Roadmap",
    "proof_pack",
    "placeholder",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_json(path: Path, fallback: Any) -> Any:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback
    return fallback


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except Exception:
        return str(path).replace("\\", "/")


def resolve_declared_file(root_path: Path, filename: str) -> Path:
    exact = root_path / filename
    if exact.exists():
        return exact
    numbered = sorted(root_path.glob(f"*. {filename}")) if root_path.exists() else []
    if numbered:
        return numbered[0]
    if "Operator Instruction Manual" in filename and root_path.exists():
        manual = sorted(root_path.glob("*Operator Instruction Manual.pdf"))
        if manual:
            return manual[0]
    return exact


def source_pack_audit() -> dict[str, Any]:
    manifest = read_json(SOURCE_PACKS, {})
    packs = manifest.get("packs", []) if isinstance(manifest, dict) else []
    declared: dict[str, list[str]] = defaultdict(list)
    pack_reports = []
    missing = []
    role_clashes = []
    for pack in packs if isinstance(packs, list) else []:
        if not isinstance(pack, dict):
            continue
        pack_id = str(pack.get("pack_id") or "")
        root_path = Path(str(pack.get("root_path") or ""))
        active = pack.get("active_guidance") is not False and pack.get("runtime_ingestion_allowed") is not False
        files = pack.get("files", []) if isinstance(pack.get("files"), list) else []
        file_reports = []
        for filename in files:
            path = resolve_declared_file(root_path, str(filename))
            exists = path.exists()
            declared[str(filename)].append(pack_id)
            if not exists:
                missing.append({"pack_id": pack_id, "filename": str(filename), "path": str(path).replace("\\", "/")})
            file_reports.append(
                {
                    "filename": str(filename),
                    "path": str(path).replace("\\", "/"),
                    "exists": exists,
                    "size_bytes": path.stat().st_size if exists else 0,
                }
            )
        if active and str(pack.get("trust_tier")) == "legacy_reference_only":
            role_clashes.append({"pack_id": pack_id, "reason": "legacy trust tier cannot be active guidance"})
        pack_reports.append(
            {
                "pack_id": pack_id,
                "label": pack.get("label"),
                "active_guidance": active,
                "trust_tier": pack.get("trust_tier"),
                "source_universe": pack.get("source_universe"),
                "root_path": str(root_path).replace("\\", "/"),
                "file_count": len(files),
                "files_present": len([item for item in file_reports if item["exists"]]),
                "files_missing": len([item for item in file_reports if not item["exists"]]),
                "files": file_reports,
            }
        )
    duplicates = [
        {"filename": filename, "packs": packs}
        for filename, packs in declared.items()
        if len(packs) > 1
    ]
    return {
        "status": "clean" if not missing and not duplicates and not role_clashes else "attention_required",
        "pack_count": len(pack_reports),
        "active_pack_count": len([item for item in pack_reports if item["active_guidance"]]),
        "legacy_pack_count": len([item for item in pack_reports if not item["active_guidance"]]),
        "missing_files": missing,
        "duplicate_file_declarations": duplicates,
        "role_clashes": role_clashes,
        "packs": pack_reports,
    }


def generated_zone_audit() -> dict[str, Any]:
    isolation_manifest = read_json(CONTEXT_ISOLATION_MANIFEST, {})
    excluded = set(isolation_manifest.get("excluded_paths", []) if isinstance(isolation_manifest.get("excluded_paths"), list) else [])
    isolation_active = isolation_manifest.get("status") == "active" and isolation_manifest.get("runtime_guidance_allowed") is False
    zones = []
    total_files = 0
    unisolated_files = 0
    quarantine_candidates = []
    for zone in GENERATED_OR_LEGACY_ZONES:
        path = ROOT / zone
        files = [item for item in path.rglob("*") if item.is_file()] if path.exists() else []
        total_files += len(files)
        isolated = isolation_active and zone in excluded
        if not isolated:
            unisolated_files += len(files)
        legacy_hits = []
        for item in files[:5000]:
            name = item.as_posix()
            if any(pattern.lower() in name.lower() for pattern in LEGACY_LANGUAGE):
                legacy_hits.append(rel(item))
        if files and zone not in {"reports", "data/runtime"}:
            quarantine_candidates.append(
                {
                    "path": zone,
                    "file_count": len(files),
                    "reason": "generated_or_historical_zone_not_active_guidance",
                    "action": "excluded_from_runtime_guidance" if isolated else "archive_or_exclude_from_runtime_guidance_after approval",
                }
            )
        zones.append(
            {
                "path": zone,
                "exists": path.exists(),
                "file_count": len(files),
                "runtime_guidance_isolated": isolated,
                "legacy_language_hit_count": len(legacy_hits),
                "sample_legacy_hits": legacy_hits[:20],
            }
        )
    return {
        "total_files_in_generated_legacy_zones": total_files,
        "unisolated_files_in_generated_legacy_zones": unisolated_files,
        "context_isolation": {
            "status": "active" if isolation_active else "missing_or_inactive",
            "manifest": rel(CONTEXT_ISOLATION_MANIFEST),
            "excluded_path_count": len(excluded),
            "all_generated_zones_excluded": all(zone in excluded for zone in GENERATED_OR_LEGACY_ZONES),
        },
        "zones": zones,
        "quarantine_candidates": quarantine_candidates,
    }


def active_runtime_boundary_audit() -> dict[str, Any]:
    return {
        "status": "enforced",
        "allowed_runtime_ingestion_files": INGESTION_ALLOWLIST,
        "forbidden_prefixes": FORBIDDEN_PREFIXES,
        "interpretation": "continuous runtime ingestion is restricted to explicit state/evidence files; docs, build manifests, reports, dashboards, tools, and generated candidate stores are blocked from direct stage-1 ingestion",
    }


def clash_analysis(source_pack: dict[str, Any], source_index: dict[str, Any], zones: dict[str, Any]) -> dict[str, Any]:
    clashes = []
    if source_pack["missing_files"]:
        clashes.append("declared_source_pack_files_missing")
    if source_pack["duplicate_file_declarations"]:
        clashes.append("same_file_declared_in_multiple_source_packs")
    if source_pack["role_clashes"]:
        clashes.append("legacy_pack_marked_active")
    if source_index.get("missing"):
        clashes.append("canonical_pipeline_or_master_source_missing")
    if zones.get("unisolated_files_in_generated_legacy_zones", zones["total_files_in_generated_legacy_zones"]) > 1000:
        clashes.append("generated_legacy_zones_dominate_repository_context")
    return {
        "status": "clashes_detected" if clashes else "no_source_authority_clashes",
        "clashes": clashes,
        "rules_now_required": [
            "Runtime route behavior must come from code contracts, governed state/evidence, and lifecycle memory.",
            "Uploaded docs are validation references only; source packs can participate in runtime matching only when active_guidance is true and runtime_ingestion_allowed is true.",
            "legacy_reference_only packs are comparison material, never route/scoring authority.",
            "data/build_manifests, docs/audits, docs/core_completion, data/proof, cleanup reports, and old dashboard generations must be treated as generated history.",
            "No deletion or archive move should run until the quarantine plan is reviewed.",
        ],
    }


def cleanup_plan(source_pack: dict[str, Any], zones: dict[str, Any]) -> list[dict[str, Any]]:
    plan = [
        {
            "step": 1,
            "title": "Freeze active guide sources",
            "action": "keep uploaded docs as build/audit validation references only; do not use them as runtime route/scoring authority",
            "destructive": False,
        },
        {
            "step": 2,
            "title": "Exclude legacy generated zones from guidance",
            "action": "enforce exclusion of build manifests, old proof packs, historical reports, old dashboard generations, and quarantined tests from command/source-pack matching",
            "destructive": False,
        },
        {
            "step": 3,
            "title": "Review quarantine candidates",
            "action": "operator reviews generated_or_historical_zone_not_active_guidance entries before any archive move",
            "destructive": False,
            "candidate_count": len(zones.get("quarantine_candidates", [])),
        },
        {
            "step": 4,
            "title": "Rename portfolio artifact language",
            "action": "replace user-facing artifact/brief terminology with business portfolio/final package terminology while leaving internal file routes backward-compatible",
            "destructive": False,
        },
        {
            "step": 5,
            "title": "Archive after approval",
            "action": "move reviewed generated/legacy files into an archive root only after a green route/runtime test gate",
            "destructive": True,
            "requires_explicit_operator_approval": True,
        },
    ]
    if source_pack.get("missing_files"):
        plan.insert(
            1,
            {
                "step": 1.5,
                "title": "Repair missing source declarations",
                "action": "fix or remove source-pack file declarations that do not exist",
                "destructive": False,
            },
        )
    return plan


def render_markdown(report: dict[str, Any]) -> str:
    source = report["source_pack_audit"]
    clash = report["clash_analysis"]
    zones = report["generated_zone_audit"]
    lines = [
        "# Source Authority and Cleanup Audit",
        "",
        f"Generated: {report['generated_at']}",
        f"Status: {report['status']}",
        "",
        "## Source Packs",
        "",
        f"- Packs: `{source['pack_count']}`",
        f"- Active packs: `{source['active_pack_count']}`",
        f"- Legacy/reference packs: `{source['legacy_pack_count']}`",
        f"- Missing declared files: `{len(source['missing_files'])}`",
        f"- Duplicate file declarations: `{len(source['duplicate_file_declarations'])}`",
        f"- Role clashes: `{len(source['role_clashes'])}`",
        "",
        "## Canonical Authority",
        "",
        f"- Pipeline sources: `{report['canonical_source_index'].get('source_count')}`",
        f"- Master sources: `{report['canonical_source_index'].get('master_source_count')}`",
        f"- Missing canonical sources: `{len(report['canonical_source_index'].get('missing', []))}`",
        "",
        "## Generated / Legacy Context",
        "",
        f"- Files in generated/legacy zones: `{zones['total_files_in_generated_legacy_zones']}`",
        f"- Quarantine candidate zones: `{len(zones['quarantine_candidates'])}`",
        "",
        "## Clash Analysis",
        "",
        f"- Status: `{clash['status']}`",
        *[f"- `{item}`" for item in clash["clashes"]],
        "",
        "## Required Rule",
        "",
        "The system must treat uploaded pipeline/master docs as build/audit validation references only. Runtime behavior must be driven by code contracts, governed state/evidence, lifecycle memory, and explicit operator promotion. Generated history can be audited, but it must not steer stage conditions, scoring, or final package expectations.",
        "",
        "## Cleanup Plan",
        "",
        *[f"{item['step']}. {item['title']} - {item['action']}" for item in report["cleanup_plan"]],
    ]
    return "\n".join(lines) + "\n"


def run() -> dict[str, Any]:
    source_pack = source_pack_audit()
    source_index = build_canonical_pipeline_source_index(ROOT)
    zones = generated_zone_audit()
    clashes = clash_analysis(source_pack, source_index, zones)
    report = {
        "schema_version": "claire.source_authority_cleanup_audit.v1",
        "generated_at": utc_now(),
        "status": "attention_required" if clashes["clashes"] else "clean",
        "source_pack_audit": source_pack,
        "canonical_source_index": {
            "status": source_index.get("status"),
            "source_count": source_index.get("source_count"),
            "master_source_count": source_index.get("master_source_count"),
            "missing": source_index.get("missing", []),
            "operator_rules": source_index.get("operator_rules", {}),
        },
        "runtime_boundary": active_runtime_boundary_audit(),
        "generated_zone_audit": zones,
        "clash_analysis": clashes,
        "cleanup_plan": cleanup_plan(source_pack, zones),
        "report_paths": {"json": str(REPORT_JSON), "markdown": str(REPORT_MD)},
    }
    write_json(REPORT_JSON, report)
    REPORT_MD.write_text(render_markdown(report), encoding="utf-8")
    return report


if __name__ == "__main__":
    payload = run()
    print(json.dumps({
        "status": payload["status"],
        "source_pack_audit": {
            "status": payload["source_pack_audit"]["status"],
            "missing_files": len(payload["source_pack_audit"]["missing_files"]),
            "duplicate_file_declarations": len(payload["source_pack_audit"]["duplicate_file_declarations"]),
            "role_clashes": len(payload["source_pack_audit"]["role_clashes"]),
        },
        "clash_analysis": payload["clash_analysis"],
        "generated_legacy_files": payload["generated_zone_audit"]["total_files_in_generated_legacy_zones"],
        "reports": payload["report_paths"],
    }, indent=2, sort_keys=True))
