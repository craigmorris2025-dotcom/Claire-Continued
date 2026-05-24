from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "claire.industry_standard_endpoint_package.v1"
PACKAGE_PATH = Path("data/endpoint_contracts/industry_standard_endpoint_package.json")
PACKAGE_MD_PATH = Path("docs/engineering/industry_standard_endpoint_package.md")


STANDARD_CONTROLS: list[dict[str, Any]] = [
    {
        "standard": "OpenAPI 3.1",
        "purpose": "Machine-readable HTTP contract for external and dashboard callers.",
        "claire_control": "/openapi.json plus this endpoint expectation package",
        "evidence": ["mounted_fastapi_routes", "endpoint_expectations"],
    },
    {
        "standard": "OWASP ASVS / OWASP LLM Top 10",
        "purpose": "Input validation, output handling, prompt/tool boundary, and body-read safety.",
        "claire_control": "operator-gated request bodies, no autonomous body reads, no unsafe tool execution",
        "evidence": ["authority_profile", "review_required", "body_read_policy"],
    },
    {
        "standard": "NIST AI RMF",
        "purpose": "Govern, Map, Measure, and Manage AI/runtime route risk.",
        "claire_control": "governed route gates, review queues, readiness scoring, runtime truth",
        "evidence": ["risk_domain", "readiness_gate", "operator_review"],
    },
    {
        "standard": "ISO/IEC 42001",
        "purpose": "AI management-system discipline for lifecycle, change control, and review.",
        "claire_control": "change-control and update-governance routes remain owner approved",
        "evidence": ["approval_required", "automatic_install_blocked"],
    },
    {
        "standard": "NIST CSF 2.0",
        "purpose": "Govern, Identify, Protect, Detect, Respond, and Recover posture for operations.",
        "claire_control": "status, proof, rollback, and readiness endpoints",
        "evidence": ["status_endpoint", "rollback_endpoint", "proof_endpoint"],
    },
    {
        "standard": "NIST SSDF / SP 800-218",
        "purpose": "Secure software development and release gate practice.",
        "claire_control": "tests, py_compile, package staging, owner review before install",
        "evidence": ["test_binding", "stage_endpoint", "apply_endpoint"],
    },
    {
        "standard": "SLSA",
        "purpose": "Package integrity, provenance, rollback, and tamper-resistance expectations.",
        "claire_control": "governed update package file manifest and rollback snapshot requirement",
        "evidence": ["package_manifest", "rollback_snapshot_required"],
    },
    {
        "standard": "CycloneDX SBOM",
        "purpose": "Dependency and component transparency for endpoint-delivered install packages.",
        "claire_control": "package payload must expose files, checksums, and dependency metadata before apply",
        "evidence": ["package_files", "dependency_inventory"],
    },
    {
        "standard": "OpenTelemetry",
        "purpose": "Trace, metric, and log expectations for runtime route operations.",
        "claire_control": "runtime status, proof pack, route integrity, and event outputs",
        "evidence": ["runtime_status", "proof_pack", "route_integrity"],
    },
]


CRITICAL_ENDPOINTS: list[dict[str, Any]] = [
    {
        "family": "dashboard_truth",
        "method": "GET",
        "path": "/api/dashboard/state",
        "expected_status": "200 JSON",
        "caller": "frontend/command_center/modern/claire_dashboard.js",
        "owner": "claire.dashboard.cockpit_dashboard_state",
        "body_policy": "no request body",
        "review_required": False,
        "mutation": "none",
        "readiness_gate": "dashboard payload loads",
    },
    {
        "family": "active_controls",
        "method": "GET",
        "path": "/api/dashboard/active-control-map",
        "expected_status": "200 JSON",
        "caller": "frontend active controls panel",
        "owner": "claire.api.dashboard_active_control_map",
        "body_policy": "no request body",
        "review_required": False,
        "mutation": "none",
        "readiness_gate": "visible controls expose backend endpoints",
    },
    {
        "family": "provider_readiness",
        "method": "GET",
        "path": "/api/search/providers/status",
        "expected_status": "200 JSON",
        "caller": "internet/settings/provider surfaces",
        "owner": "claire.api.governed_provider_readiness_routes",
        "body_policy": "no request body",
        "review_required": False,
        "mutation": "none",
        "readiness_gate": "provider stack status returned without secrets",
    },
    {
        "family": "governed_live_probe",
        "method": "POST",
        "path": "/internet/live-probe/run",
        "expected_status": "200/403 JSON depending operator gate",
        "caller": "web ops / governed probe",
        "owner": "claire.api.routes_governed_live_probe",
        "body_policy": "metadata query body only; response body read remains blocked unless explicitly gated",
        "review_required": True,
        "mutation": "quarantine/proof record only",
        "readiness_gate": "operator-confirmed one-shot metadata probe",
    },
    {
        "family": "update_governance",
        "method": "POST",
        "path": "/api/update-governance/open-web/install/stage",
        "expected_status": "202/409 JSON",
        "caller": "updates panel",
        "owner": "claire.api.routes_open_web_update_governance",
        "body_policy": "update_id required",
        "review_required": True,
        "mutation": "stage only; no apply without approval and package payload",
        "readiness_gate": "owner approval plus package payload manifest",
    },
    {
        "family": "update_governance",
        "method": "POST",
        "path": "/api/update-governance/open-web/install/apply",
        "expected_status": "202/409 JSON",
        "caller": "updates panel",
        "owner": "claire.api.routes_open_web_update_governance",
        "body_policy": "update_id and approval phrase required",
        "review_required": True,
        "mutation": "operator-gated package apply with rollback snapshot",
        "readiness_gate": "install_readiness == install_ready",
    },
    {
        "family": "pipeline_evaluate",
        "method": "POST",
        "path": "/evaluate",
        "expected_status": "200 JSON",
        "caller": "runtime proof chain",
        "owner": "claire.api.routes_pipeline",
        "body_policy": "raw_input/query accepted; deterministic default",
        "review_required": False,
        "mutation": "run output artifacts only",
        "readiness_gate": "pipeline returns lifecycle output",
    },
    {
        "family": "design_portal",
        "method": "GET",
        "path": "/design-portal/status",
        "expected_status": "200 JSON",
        "caller": "design portal dashboard panel",
        "owner": "claire.api.routes_design_portal_output",
        "body_policy": "no request body",
        "review_required": False,
        "mutation": "none",
        "readiness_gate": "contract status is visible before CAD export",
    },
    {
        "family": "design_portal",
        "method": "GET",
        "path": "/design-portal/contract",
        "expected_status": "200 JSON",
        "caller": "design portal dashboard panel",
        "owner": "claire.api.routes_design_portal_output",
        "body_policy": "no request body",
        "review_required": False,
        "mutation": "none",
        "readiness_gate": "contract sections and package readiness exposed",
    },
    {
        "family": "cad_intent",
        "method": "GET",
        "path": "/cad/intent",
        "expected_status": "200 JSON",
        "caller": "Design/CAD readiness surface",
        "owner": "claire.api.routes_design_portal_output",
        "body_policy": "no request body",
        "review_required": False,
        "mutation": "none",
        "readiness_gate": "CAD intent is reviewable; export remains later",
    },
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _route_methods(route: Any) -> list[str]:
    methods = getattr(route, "methods", None)
    if not methods:
        return []
    return sorted(method for method in methods if method not in {"HEAD", "OPTIONS"})


def _mounted_routes(app: Any | None) -> list[dict[str, Any]]:
    if app is None:
        return []
    mounted = []
    for route in getattr(app, "routes", []):
        path = getattr(route, "path", "")
        if not path:
            continue
        mounted.append(
            {
                "path": path,
                "methods": _route_methods(route),
                "name": getattr(route, "name", ""),
                "include_in_schema": bool(getattr(route, "include_in_schema", True)),
            }
        )
    return sorted(mounted, key=lambda item: (item["path"], ",".join(item["methods"])))


def build_endpoint_standard_settings(app: Any | None = None) -> dict[str, Any]:
    mounted_paths = {route["path"] for route in _mounted_routes(app)}
    expected_paths = {item["path"] for item in CRITICAL_ENDPOINTS}
    missing = sorted(path for path in expected_paths if mounted_paths and path not in mounted_paths)
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "ready" if not missing else "review",
        "generated_at": _now(),
        "package_endpoint": "/api/system/industry-standard-endpoint-package",
        "dashboard_endpoint": "/dashboard/system/industry-standard-endpoint-package",
        "openapi_endpoint": "/openapi.json",
        "package_file": str(PACKAGE_PATH).replace("\\", "/"),
        "doc_file": str(PACKAGE_MD_PATH).replace("\\", "/"),
        "standards_count": len(STANDARD_CONTROLS),
        "critical_endpoint_count": len(CRITICAL_ENDPOINTS),
        "mounted_expected_count": len(expected_paths) - len(missing),
        "missing_expected_paths": missing,
        "automatic_install_enabled": False,
        "owner_review_required_for_mutations": True,
        "cad_export_enabled": False,
        "cad_intent_reviewable": True,
    }


def _acceptance_checks(mounted_routes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    mounted_paths = {route["path"] for route in mounted_routes}
    checks = []
    for endpoint in CRITICAL_ENDPOINTS:
        checks.append(
            {
                "path": endpoint["path"],
                "method": endpoint["method"],
                "family": endpoint["family"],
                "mounted": endpoint["path"] in mounted_paths if mounted_paths else None,
                "owner": endpoint["owner"],
                "review_required": endpoint["review_required"],
                "expected_status": endpoint["expected_status"],
            }
        )
    return checks


def _write_package_files(root: Path, payload: dict[str, Any]) -> None:
    package_path = root / PACKAGE_PATH
    package_path.parent.mkdir(parents=True, exist_ok=True)
    package_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path = root / PACKAGE_MD_PATH
    md_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Industry Standard Endpoint Package",
        "",
        f"Schema: `{payload['schema_version']}`",
        f"Status: `{payload['status']}`",
        "",
        "## Standards",
    ]
    for item in STANDARD_CONTROLS:
        lines.append(f"- {item['standard']}: {item['claire_control']}")
    lines.extend(["", "## Critical Endpoints"])
    for item in CRITICAL_ENDPOINTS:
        lines.append(f"- {item['method']} {item['path']} ({item['family']}): {item['owner']}")
    md_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def build_industry_standard_endpoint_package(app: Any | None = None, project_root: Path | str | None = None) -> dict[str, Any]:
    mounted_routes = _mounted_routes(app)
    settings = build_endpoint_standard_settings(app)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "status": settings["status"],
        "generated_at": settings["generated_at"],
        "package_name": "Endpoint Reconciliation + End-to-End Proof Lock",
        "purpose": "Prove what Claire expects at important endpoints using industry-standard contract, governance, security, package-integrity, and observability controls.",
        "standards": STANDARD_CONTROLS,
        "endpoint_expectations": CRITICAL_ENDPOINTS,
        "acceptance_checks": _acceptance_checks(mounted_routes),
        "settings": settings,
        "mounted_route_count": len(mounted_routes),
        "mounted_routes": mounted_routes,
        "proof_chain": [
            "frontend control or dashboard settings",
            "active backend endpoint",
            "runtime owner module",
            "pipeline/evaluate or governed route trigger",
            "evidence, score, route, lifecycle, or update readiness output",
            "artifact or dashboard payload",
            "operator review before mutation/install/export",
        ],
        "mutation_policy": {
            "automatic_updates_enabled": False,
            "install_apply_requires_owner_phrase": True,
            "runtime_truth_mutation_default": "blocked",
            "cad_export_default": "not_exposed_yet",
        },
    }
    root = Path(project_root or Path.cwd()).resolve()
    _write_package_files(root, payload)
    return payload

