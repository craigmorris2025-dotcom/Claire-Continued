from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime_core.dashboard.cockpit_dashboard_state import build_cockpit_dashboard_state
from runtime_core.pipeline.canonical_pipeline_sources import build_canonical_pipeline_source_index
from runtime_core.platform.operational_readiness import build_operational_readiness


REPORT_JSON = ROOT / "reports" / "CURRENT_RUNTIME_PIPELINE_ANALYSIS.json"
REPORT_MD = ROOT / "reports" / "CURRENT_RUNTIME_PIPELINE_ANALYSIS.md"


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


def active_source_pack_summary() -> dict[str, Any]:
    manifest = read_json(ROOT / "data" / "source_packs" / "local_upload_source_packs.json", {})
    packs = manifest.get("packs", []) if isinstance(manifest, dict) else []
    active = [
        pack for pack in packs
        if isinstance(pack, dict)
        and pack.get("active_guidance") is not False
        and pack.get("runtime_ingestion_allowed") is not False
    ]
    reference_only = [pack for pack in packs if isinstance(pack, dict) and pack.get("active_guidance") is False]
    return {
        "schema_version": manifest.get("schema_version") if isinstance(manifest, dict) else None,
        "active_pack_count": len(active),
        "validation_reference_pack_count": len(reference_only),
        "active_packs": [
            {
                "pack_id": pack.get("pack_id"),
                "root_path": pack.get("root_path"),
                "trust_tier": pack.get("trust_tier"),
                "file_count": len(pack.get("files", [])) if isinstance(pack.get("files"), list) else 0,
                "route_roles": pack.get("route_roles", []),
            }
            for pack in active
        ],
        "validation_reference_packs": [
            {
                "pack_id": pack.get("pack_id"),
                "trust_tier": pack.get("trust_tier"),
                "file_count": len(pack.get("files", [])) if isinstance(pack.get("files"), list) else 0,
                "rule": "not used for active route or scoring authority",
            }
            for pack in reference_only
        ],
    }


def route_analysis(source_index: dict[str, Any], dashboard: dict[str, Any]) -> dict[str, Any]:
    current = dashboard.get("current_run_truth", {}) if isinstance(dashboard.get("current_run_truth"), dict) else {}
    route = current.get("route_selected") or dashboard.get("lifecycle", {}).get("route_selected")
    contracts = source_index.get("route_contracts", {})
    if route in {"portfolio_creation_optimization", "portfolio_intelligence", "portfolio_candidate"}:
        contract_key = "portfolio_normal_path"
    elif route in {"existing_system_replacement", "system_replacement", "superior_system_design"}:
        contract_key = "existing_system_replacement_path"
    elif "breakthrough" in str(route):
        contract_key = "breakthrough_design_path"
    else:
        contract_key = "acquisition_package_path" if dashboard.get("records", {}).get("acquirers") else "portfolio_normal_path"
    contract = contracts.get(contract_key, {})
    stages = dashboard.get("lifecycle", {}).get("stages", [])
    stage_count = dashboard.get("lifecycle", {}).get("stage_count") or len(stages) if isinstance(stages, list) else 0
    records = dashboard.get("records", {}) if isinstance(dashboard.get("records"), dict) else {}
    return {
        "current_route": route,
        "selected_contract": contract_key,
        "contract": contract,
        "stage_count": stage_count,
        "route_fit": {
            "portfolio_records": len(records.get("portfolio", [])) if isinstance(records.get("portfolio"), list) else 0,
            "signal_records": len(records.get("signals", [])) if isinstance(records.get("signals"), list) else 0,
            "acquirer_records": len(records.get("acquirers", [])) if isinstance(records.get("acquirers"), list) else 0,
            "design_records": len(records.get("design", [])) if isinstance(records.get("design"), list) else 0,
            "learning_records": len(records.get("learning", [])) if isinstance(records.get("learning"), list) else 0,
        },
    }


def stale_guidance_analysis(source_packs: dict[str, Any]) -> dict[str, Any]:
    legacy = source_packs.get("validation_reference_packs", [])
    return {
        "status": "documents_demoted_to_validation_reference" if legacy else "no_document_reference_pack_declared",
        "risk_before": "uploaded docs could be retrieved as active source-pack guidance and pull route/scoring behavior instead of leaving behavior to code contracts",
        "current_rule": "document packs remain traceable for developer validation/audit only; runtime ingestion and command matching skip active_guidance=false",
        "legacy_pack_count": len(legacy) if isinstance(legacy, list) else 0,
        "remaining_risks": [
            "large historical reports and backup audits still exist in the repo and should not be used as runtime guide sources",
            "some old test/report files still mention artifact/legacy dashboard language",
            "connected live search was blocked by Windows socket permissions in the non-escalated proof run",
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    route = report["route_analysis"]
    readiness = report["operational_readiness"]
    source = report["source_authority"]
    proof = report.get("live_proof", {})
    lines = [
        "# Current Runtime and Pipeline Analysis",
        "",
        f"Generated: {report['generated_at']}",
        f"Status: {report['status']}",
        "",
        "## What The System Is",
        "",
        "Claire is currently organized as a governed 30-stage lifecycle runtime. It should execute code contracts and governed state/evidence, not uploaded documents. Its logical order is: signals or existing-system intake -> governance -> trend discovery -> thesis -> gap/discovery -> portfolio as the normal path, or replacement/breakthrough/design only when thresholds justify it -> market/strategy -> portfolio -> acquirer fit -> final package -> lifecycle memory.",
        "",
        "## Build Reference Boundary",
        "",
        f"- Canonical pipeline docs: `{source['pipeline_source_count']}`",
        f"- Canonical master docs: `{source['master_source_count']}`",
        f"- Missing canonical sources: `{len(source['missing_sources'])}`",
        f"- Runtime-ingestable source packs: `{report['source_packs']['active_pack_count']}`",
        f"- Validation-reference packs: `{report['source_packs']['validation_reference_pack_count']}`",
        "",
        "## Runtime Route",
        "",
        f"- Current route: `{route['current_route']}`",
        f"- Selected route contract: `{route['selected_contract']}`",
        f"- Stage count: `{route['stage_count']}`",
        f"- Portfolio records: `{route['route_fit']['portfolio_records']}`",
        f"- Signal records: `{route['route_fit']['signal_records']}`",
        f"- Acquirer records: `{route['route_fit']['acquirer_records']}`",
        f"- Learning records: `{route['route_fit']['learning_records']}`",
        "",
        "## Operational Readiness",
        "",
        f"- Status: `{readiness.get('status')}`",
        f"- Current run present: `{readiness.get('checks', {}).get('current_run_spine_present')}`",
        f"- Advancement path respected: `{readiness.get('checks', {}).get('advancement_path_policy_respected')}`",
        f"- Portfolio candidates present: `{readiness.get('checks', {}).get('portfolio_candidates_present')}`",
        "",
        "## Live Proof",
        "",
        f"- Proof status: `{proof.get('status')}`",
        f"- Connected query status: `{proof.get('connected_search', {}).get('query_status')}`",
        f"- Portfolio view: `{proof.get('portfolio_routes', {}).get('view_url')}`",
        "",
        "## Current Correction",
        "",
        f"- Stale guidance status: `{report['stale_guidance']['status']}`",
        f"- Rule: {report['stale_guidance']['current_rule']}",
        "",
        "## Plain-English Understanding",
        "",
        "The system should not be inventing first, and it should not be programmed by uploaded documents at runtime. The docs are build/audit references only. Runtime behavior should come from code contracts, governed state, live/promoted evidence, and lifecycle memory. It should ingest governed signals or an existing system, validate and normalize evidence, detect trends and gaps, generate a discovery only when the evidence supports one, choose the advancement path, then route into portfolio, breakthrough/design, or existing-system replacement. On the replacement path it must decompose the current system, design the superior system, validate buildability/viability/manufacturability/feasibility, create the professional business portfolio, identify acquirer fit, and construct the final package. Nothing should promote itself into runtime truth without operator review.",
    ]
    return "\n".join(lines) + "\n"


def run() -> dict[str, Any]:
    source_index = build_canonical_pipeline_source_index(ROOT)
    dashboard = build_cockpit_dashboard_state(ROOT)
    readiness = build_operational_readiness(ROOT)
    source_packs = active_source_pack_summary()
    live_proof = read_json(ROOT / "reports" / "LIVE_PORTFOLIO_PROOF_REPORT.json", {})
    source_authority = {
        "status": source_index.get("status"),
        "pipeline_source_count": source_index.get("source_count"),
        "master_source_count": source_index.get("master_source_count"),
        "missing_sources": source_index.get("missing", []),
        "operator_rules": source_index.get("operator_rules", {}),
        "final_package_requirements": source_index.get("final_package_requirements", []),
    }
    report = {
        "schema_version": "claire.current_runtime_pipeline_analysis.v1",
        "generated_at": utc_now(),
        "status": "analyzed",
        "source_authority": source_authority,
        "source_packs": source_packs,
        "route_analysis": route_analysis(source_index, dashboard),
        "operational_readiness": {
            "status": readiness.get("status"),
            "checks": readiness.get("checks", {}),
            "current_run_truth": readiness.get("current_run_truth", {}),
        },
        "live_proof": live_proof,
        "stale_guidance": stale_guidance_analysis(source_packs),
        "report_paths": {
            "json": str(REPORT_JSON),
            "markdown": str(REPORT_MD),
        },
    }
    write_json(REPORT_JSON, report)
    REPORT_MD.write_text(render_markdown(report), encoding="utf-8")
    return report


if __name__ == "__main__":
    payload = run()
    print(json.dumps({
        "status": payload["status"],
        "source_authority": payload["source_authority"],
        "route_analysis": payload["route_analysis"],
        "stale_guidance": payload["stale_guidance"],
        "reports": payload["report_paths"],
    }, indent=2, sort_keys=True))
