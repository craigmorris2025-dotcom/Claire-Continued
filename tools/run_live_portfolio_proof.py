from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime_core.api.governed_connected_search import (
    PROMOTION_CONFIRM_TEXT,
    build_connected_search_response,
    build_hybrid_result,
    promote_latest_metadata_to_evidence,
    provider_state,
)
from runtime_core.api.routes_continuous_runtime import create_cycle_payload
from runtime_core.dashboard.cockpit_dashboard_state import build_cockpit_dashboard_state
from runtime_core.design.artifact_package import build_design_artifact_package
from runtime_core.platform.operational_readiness import build_operational_readiness
from runtime_core.platform.update_governance.open_web_update_governance import (
    build_dashboard_update_panel,
    build_open_web_readiness_report,
    create_update_request,
    stable_digest,
)
from runtime_core.proof.verified_output_proof import persist_verified_output_proof_binder


REPORT_DIR = ROOT / "reports"
PROOF_PATH = REPORT_DIR / "LIVE_PORTFOLIO_PROOF_REPORT.json"
PROOF_MARKDOWN = REPORT_DIR / "LIVE_PORTFOLIO_PROOF_REPORT.md"


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


def signed_local_update_candidate() -> dict[str, Any]:
    candidate = {
        "update_id": "live_portfolio_proof_update_probe",
        "provider_id": "local_operator",
        "package_uri": "file:///local/operator/live-portfolio-proof-update.json",
        "version_from": "local-current",
        "version_to": "local-governed-proof",
        "capabilities": [
            "connected_search_metadata_fetch",
            "update_governance_panel",
            "portfolio_construction",
            "design_portal_package",
        ],
        "target_paths": ["claire/api/portfolio_artifacts.py"],
        "metadata": {
            "summary": "Proposal-only update probe proving governance can evaluate update candidates without auto-applying changes.",
            "proof_scope": "metadata_fetch_and_portfolio_output",
        },
    }
    digest_payload = {
        "update_id": candidate["update_id"],
        "provider_id": candidate["provider_id"],
        "version_from": candidate["version_from"],
        "version_to": candidate["version_to"],
        "capabilities": candidate["capabilities"],
        "target_paths": candidate["target_paths"],
        "metadata": candidate["metadata"],
    }
    digest = stable_digest(digest_payload)
    candidate["expected_sha256"] = digest
    candidate["signature"] = f"sha256:{digest}"
    return candidate


def render_markdown(report: dict[str, Any]) -> str:
    portfolio = report.get("business_portfolio", {})
    scoring = portfolio.get("scoring", {}) if isinstance(portfolio, dict) else {}
    validation = portfolio.get("market_validation", {}) if isinstance(portfolio, dict) else {}
    design = report.get("design_portal_package", {})
    connected = report.get("connected_search", {})
    update = report.get("update_governance", {})
    binder = report.get("verified_output_proof_binder", {})
    lines = [
        "# Claire Live Portfolio Proof Report",
        "",
        f"Generated: {report.get('generated_at')}",
        f"Status: {report.get('status')}",
        "",
        "## Connected Search",
        "",
        f"- Provider status: `{connected.get('provider_status')}`",
        f"- Query status: `{connected.get('query_status')}`",
        f"- Provider used: `{connected.get('provider_used')}`",
        f"- Results quarantined: `{connected.get('result_count')}`",
        f"- Promoted evidence: `{connected.get('promoted_count')}`",
        "",
        "## Runtime Portfolio",
        "",
        f"- Run ID: `{report.get('run_id')}`",
        f"- Route: `{portfolio.get('runtime_basis', {}).get('route_selected')}`",
        f"- Portfolio status: `{portfolio.get('status')}`",
        f"- Industry: `{portfolio.get('industry')}`",
        f"- Viability score: `{scoring.get('viability_score')}`",
        f"- Investment readiness score: `{scoring.get('investment_readiness_score')}`",
        f"- Market value status: `{validation.get('valuation', {}).get('verified_current_market_value_status')}`",
        "",
        "## Verified Output Proof Binder",
        "",
        f"- Binder status: `{binder.get('status')}`",
        f"- Completion: `{binder.get('completion_percent')}`",
        f"- Proof phase complete: `{binder.get('proof_phase_complete')}`",
        "",
        "## Design Portal",
        "",
        f"- Package status: `{design.get('status')}`",
        f"- Package directory: `{design.get('package_dir')}`",
        f"- CAD viewer required: `{design.get('cad_viewer_required')}`",
        f"- Video viewer required: `{design.get('video_viewer_required')}`",
        "",
        "## Update Governance",
        "",
        f"- Readiness: `{update.get('readiness_status')}`",
        f"- Available update records: `{update.get('available_update_count')}`",
        f"- Automatic updates performed: `{update.get('automatic_update_performed')}`",
        "",
        "## Portfolio Routes",
        "",
        f"- View: `{report.get('portfolio_routes', {}).get('view_url')}`",
        f"- Download: `{report.get('portfolio_routes', {}).get('download_url')}`",
    ]
    return "\n".join(lines) + "\n"


def run(query: str) -> dict[str, Any]:
    provider = provider_state()
    connected = build_connected_search_response(
        query,
        max_results=6,
        sources=[
            {"domain": "sec.gov", "label": "SEC filings"},
            {"domain": "nist.gov", "label": "NIST standards"},
            {"domain": "gartner.com", "label": "Gartner market signal"},
        ],
    )
    promoted = {"status": "skipped", "promoted_count": 0}
    hybrid = {"status": "skipped"}
    if connected.get("status") == "metadata_results_quarantined":
        promoted = promote_latest_metadata_to_evidence(PROMOTION_CONFIRM_TEXT)
        hybrid = build_hybrid_result(query)

    update_readiness = build_open_web_readiness_report(ROOT)
    update_request = create_update_request(signed_local_update_candidate(), ROOT)
    cycle = create_cycle_payload(trigger="live_portfolio_proof")
    state = build_cockpit_dashboard_state(ROOT)
    operational = build_operational_readiness(ROOT)
    design_package = build_design_artifact_package(state.get("design_portal_workbench", {}), ROOT)

    run_id = cycle.get("cycle", {}).get("cycle_id")
    current_run = read_json(ROOT / "data" / "continuous_runtime" / "current_run.json", {})
    portfolio_routes = current_run.get("portfolio_artifact", {}) if isinstance(current_run, dict) else {}
    portfolio_path = ROOT / "data" / "continuous_runtime" / "artifacts" / "portfolio" / str(run_id) / "portfolio_brief.json"
    portfolio_payload = read_json(portfolio_path, {})
    business_portfolio = portfolio_payload.get("business_portfolio", {}) if isinstance(portfolio_payload, dict) else {}
    proof_binder = persist_verified_output_proof_binder(current_run, portfolio_payload, ROOT) if current_run else {}

    proof_checks = {
        "provider_configured": provider.get("provider_known") is True,
        "connected_query_attempted": connected.get("status") in {"metadata_results_quarantined", "provider_error", "blocked"},
        "promoted_or_reported": promoted.get("status") in {"promoted_to_evidence", "skipped"},
        "runtime_completed": cycle.get("cycle", {}).get("candidate_counts", {}).get("portfolios", 0) >= 1,
        "business_portfolio_created": business_portfolio.get("portfolio_type") == "industry_standard_business_portfolio",
        "verified_output_proof_binder_created": proof_binder.get("schema_version") == "claire.verified_output_proof_binder.v1",
        "design_portal_packaged": design_package.get("status") == "design_artifact_package_ready",
        "update_governance_ready": update_readiness.get("ready") is True,
        "automatic_update_not_performed": update_request.get("automatic_update_performed") is False,
    }
    report = {
        "schema_version": "claire.live_portfolio_proof.v1",
        "generated_at": utc_now(),
        "status": "proof_ready" if all(proof_checks.values()) else "proof_partial",
        "query": query,
        "run_id": run_id,
        "proof_checks": proof_checks,
        "connected_search": {
            "provider_status": "ready" if provider.get("execution_allowed") or any(item.get("execution_allowed") for item in provider.get("provider_stack_states", [])) else "blocked",
            "query_status": connected.get("status"),
            "provider_used": connected.get("provider", {}).get("provider_used") or connected.get("provider", {}).get("provider"),
            "result_count": len(connected.get("results", [])) if isinstance(connected.get("results"), list) else 0,
            "promoted_count": promoted.get("promoted_count", 0),
            "hybrid_status": hybrid.get("status"),
            "authority": connected.get("authority", {}),
            "provider_errors": connected.get("provider", {}).get("provider_errors", []) if isinstance(connected.get("provider"), dict) else [],
            "blocked_reason": connected.get("reason"),
            "provider_error": connected.get("provider_error"),
        },
        "business_portfolio": business_portfolio,
        "verified_output_proof_binder": {
            "status": proof_binder.get("status"),
            "completion_percent": proof_binder.get("completion_percent"),
            "proof_phase_complete": proof_binder.get("proof_phase_complete"),
            "area_scores": proof_binder.get("area_scores", {}),
            "paths": proof_binder.get("paths", {}),
        },
        "portfolio_routes": portfolio_routes,
        "design_portal_package": design_package,
        "update_governance": {
            "readiness_status": update_readiness.get("status"),
            "available_update_count": build_dashboard_update_panel(ROOT).get("available_update_count"),
            "latest_request_status": update_request.get("status"),
            "request_path": update_request.get("request_path"),
            "automatic_update_performed": update_request.get("automatic_update_performed"),
            "install_performed": update_request.get("install_performed"),
        },
        "operational_readiness": {
            "status": operational.get("status"),
            "checks": operational.get("checks", {}),
        },
        "report_paths": {
            "json": str(PROOF_PATH),
            "markdown": str(PROOF_MARKDOWN),
        },
    }
    write_json(PROOF_PATH, report)
    PROOF_MARKDOWN.write_text(render_markdown(report), encoding="utf-8")
    return report


if __name__ == "__main__":
    proof = run("autonomous invention enterprise R&D portfolio acquisition market gap 2026")
    print(json.dumps({
        "status": proof["status"],
        "run_id": proof["run_id"],
        "connected_search": proof["connected_search"],
        "portfolio_view": proof["portfolio_routes"].get("view_url"),
        "design_package": proof["design_portal_package"].get("package_dir"),
        "report": proof["report_paths"],
    }, indent=2, sort_keys=True))
