from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPORT_JSON = ROOT / "reports" / "ROUTE_CONTRACT_CONFLICT_AUDIT.json"
REPORT_MD = ROOT / "reports" / "ROUTE_CONTRACT_CONFLICT_AUDIT.md"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_json(path: Path, fallback: Any) -> Any:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback
    return fallback


def resolve_pack_file(root: Path, filename: str) -> Path:
    exact = root / filename
    if exact.exists():
        return exact
    numbered = sorted(root.glob(f"*. {filename}")) if root.exists() else []
    if numbered:
        return numbered[0]
    if "Operator Instruction Manual" in filename and root.exists():
        manual = sorted(root.glob("*Operator Instruction Manual.pdf"))
        if manual:
            return manual[0]
    return exact


def source_pack_conflicts() -> list[dict[str, Any]]:
    manifest = read_json(ROOT / "data" / "source_packs" / "local_upload_source_packs.json", {})
    packs = manifest.get("packs", []) if isinstance(manifest, dict) else []
    issues: list[dict[str, Any]] = []
    for pack in packs if isinstance(packs, list) else []:
        if not isinstance(pack, dict) or pack.get("active_guidance") is False:
            continue
        root = Path(str(pack.get("root_path") or ""))
        if not root.exists():
            issues.append({
                "severity": "high",
                "type": "active_source_pack_root_missing",
                "pack_id": pack.get("pack_id"),
                "path": str(root).replace("\\", "/"),
            })
            continue
        missing_files = [
            filename
            for filename in pack.get("files", [])
            if isinstance(filename, str) and not resolve_pack_file(root, filename).exists()
        ]
        if missing_files:
            issues.append({
                "severity": "medium",
                "type": "active_source_pack_files_unresolved",
                "pack_id": pack.get("pack_id"),
                "count": len(missing_files),
                "files": missing_files,
            })
    return issues


def route_contract_conflicts() -> list[dict[str, Any]]:
    index = read_json(ROOT / "data" / "pipeline" / "canonical_pipeline_source_index.json", {})
    issues: list[dict[str, Any]] = []
    if index.get("missing"):
        issues.append({
            "severity": "high",
            "type": "canonical_pipeline_sources_missing",
            "missing": index.get("missing"),
        })
    contracts = index.get("route_contracts", {}) if isinstance(index.get("route_contracts"), dict) else {}
    required = {
        "portfolio_normal_path",
        "breakthrough_design_path",
        "acquisition_package_path",
        "existing_system_replacement_path",
        "governed_update_path",
    }
    absent = sorted(required.difference(contracts))
    if absent:
        issues.append({"severity": "high", "type": "route_contract_absent", "contracts": absent})
    replacement = contracts.get("existing_system_replacement_path", {})
    must = set(replacement.get("must_produce", [])) if isinstance(replacement, dict) else set()
    for output in {"existing_system_decomposition", "superior_system_design", "portfolio_creation", "acquirer_identification", "final_package"}:
        if output not in must:
            issues.append({"severity": "high", "type": "replacement_contract_missing_output", "output": output})
    return issues


def runtime_continuity_conflicts() -> list[dict[str, Any]]:
    status = read_json(ROOT / "data" / "continuous_runtime" / "status.json", {})
    current = read_json(ROOT / "data" / "continuous_runtime" / "current_run.json", {})
    issues: list[dict[str, Any]] = []
    if status.get("mode") != "governed_24_7_discovery_monitoring":
        issues.append({"severity": "medium", "type": "runtime_mode_not_24_7", "mode": status.get("mode")})
    scheduler_policy = status.get("scheduler_policy", {}) if isinstance(status.get("scheduler_policy"), dict) else {}
    if scheduler_policy.get("daemon_installed") is not True and scheduler_policy.get("task_runner_installed") is not True:
        issues.append({
            "severity": "medium",
            "type": "scheduler_not_proven_active",
            "detail": "Runtime supports bounded continuous cycles, but no installed daemon or OS task runner is proven active.",
        })
    if not status.get("loop_running"):
        issues.append({"severity": "medium", "type": "continuous_loop_not_marked_running", "status": status.get("status")})
    if current.get("schema_version") == "claire.first_live_run_spine.v1":
        issues.append({
            "severity": "medium",
            "type": "first_live_rehearsal_schema_still_active",
            "detail": "The active snapshot is useful, but schema/status wording still frames the continuous lifecycle as a first-live rehearsal.",
        })
    if current.get("status") == "valid_first_live_rehearsal":
        issues.append({
            "severity": "medium",
            "type": "run_status_wording_rehearsal",
            "detail": "This should become a continuous lifecycle snapshot status, not a one-time proof-run status.",
        })
    return issues


def stale_language_conflicts() -> list[dict[str, Any]]:
    files = [
        ROOT / "claire" / "api" / "routes_continuous_runtime.py",
        ROOT / "claire" / "platform" / "operational_readiness.py",
        ROOT / "claire" / "dashboard" / "cockpit_dashboard_state.py",
        ROOT / "tools" / "analyze_runtime_pipeline_state.py",
    ]
    patterns = {
        "artifact_language": re.compile(r"\bartifact\b", re.I),
        "portfolio_first_language": re.compile(r"portfolio[_ -]?first|portfolio_primary_route", re.I),
        "first_live_rehearsal_language": re.compile(r"first_live|rehearsal", re.I),
    }
    issues: list[dict[str, Any]] = []
    for path in files:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for issue_type, pattern in patterns.items():
            count = len(pattern.findall(text))
            if count:
                severity = "low"
                if issue_type in {"first_live_rehearsal_language", "portfolio_first_language"}:
                    severity = "medium"
                issues.append({
                    "severity": severity,
                    "type": issue_type,
                    "path": str(path.relative_to(ROOT)).replace("\\", "/"),
                    "count": count,
                    "interpretation": "wording may bias the system toward proof-run/portfolio-only thinking unless kept as compatibility-only language",
                })
    return issues


def run() -> dict[str, Any]:
    issues = {
        "source_pack_conflicts": source_pack_conflicts(),
        "route_contract_conflicts": route_contract_conflicts(),
        "runtime_continuity_conflicts": runtime_continuity_conflicts(),
        "stale_language_conflicts": stale_language_conflicts(),
    }
    active_blockers = [
        item
        for group in issues.values()
        for item in group
        if item.get("severity") == "high"
    ]
    medium_risks = [
        item
        for group in issues.values()
        for item in group
        if item.get("severity") == "medium"
    ]
    payload = {
        "schema_version": "claire.route_contract_conflict_audit.v1",
        "generated_at": utc_now(),
        "status": "active_blockers_present" if active_blockers else "no_active_route_contract_blockers",
        "active_blocker_count": len(active_blockers),
        "medium_risk_count": len(medium_risks),
        "issues": issues,
        "route_forward": [
            "Treat run/cycle IDs as audit snapshots inside a continuous lifecycle, not as the product's mental model.",
            "Rename first-live rehearsal wording in runtime contracts to continuous lifecycle snapshot wording.",
            "Replace portfolio-first policy wording with advancement-path policy wording: portfolio is the normal business path, design/replacement routes activate when gates require them.",
            "Keep recovered Docs Main modules quarantined until normalized and tested.",
            "Wire research_live, design_proof, benchmarks, and recursive_longitudinal as validation layers after the source authority is stable.",
        ],
    }
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT_MD.write_text(render_markdown(payload), encoding="utf-8")
    return payload


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Route Contract Conflict Audit",
        "",
        f"Generated: {payload['generated_at']}",
        f"Status: `{payload['status']}`",
        f"Active blockers: `{payload['active_blocker_count']}`",
        f"Medium risks: `{payload['medium_risk_count']}`",
        "",
        "## Findings",
    ]
    for group, items in payload["issues"].items():
        lines.extend(["", f"### {group}"])
        if not items:
            lines.append("- none")
        for item in items:
            label = item.get("type")
            detail = item.get("detail") or item.get("path") or item.get("pack_id") or item.get("output") or ""
            lines.append(f"- `{item.get('severity')}` `{label}` {detail}")
    lines.extend(["", "## Clean Route Forward"])
    lines.extend(f"- {item}" for item in payload["route_forward"])
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    result = run()
    print(json.dumps({
        "status": result["status"],
        "active_blocker_count": result["active_blocker_count"],
        "medium_risk_count": result["medium_risk_count"],
        "reports": {"json": str(REPORT_JSON), "markdown": str(REPORT_MD)},
    }, indent=2, sort_keys=True))
