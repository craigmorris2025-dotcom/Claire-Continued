from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROOF_PATH = Path("data/proof/dependency_to_dependency_e2e_proof.json")
PROOF_MD_PATH = Path("docs/engineering/dependency_to_dependency_e2e_proof.md")


CHAIN_STEPS: list[dict[str, Any]] = [
    {
        "id": "dashboard_state",
        "label": "Dashboard state",
        "method": "GET",
        "endpoint": "/api/dashboard/state",
        "owner": "claire.dashboard.cockpit_dashboard_state",
        "requires": [],
        "must_have": ["status", "system_wiring", "active_control_map", "endpoint_reconciliation"],
        "handoff": ["system_wiring", "records", "active_control_map"],
    },
    {
        "id": "active_control_map",
        "label": "Active control map",
        "method": "GET",
        "endpoint": "/api/dashboard/active-control-map",
        "owner": "claire.api.dashboard_active_control_map",
        "requires": ["dashboard_state"],
        "must_have": ["status", "controls", "authority"],
        "handoff": ["controls", "primary_endpoint", "secondary_endpoints"],
    },
    {
        "id": "runtime_status",
        "label": "Runtime status",
        "method": "GET",
        "endpoint": "/runtime/status",
        "owner": "claire.api.operator_cockpit_runtime",
        "requires": ["active_control_map"],
        "must_have": ["status", "runtime"],
        "handoff": ["runtime", "truth", "queues"],
    },
    {
        "id": "provider_readiness",
        "label": "Provider readiness",
        "method": "GET",
        "endpoint": "/api/search/providers/status",
        "owner": "claire.api.governed_provider_readiness_routes",
        "requires": ["runtime_status"],
        "must_have": ["status", "readiness"],
        "handoff": ["provider_count", "execution_allowed", "blocked_capabilities"],
    },
    {
        "id": "governed_search_plan",
        "label": "Governed search plan",
        "method": "GET",
        "endpoint": "/api/search/governed/query/payload",
        "owner": "claire.api.governed_query_compiler_routes",
        "requires": ["provider_readiness"],
        "must_have": ["status"],
        "handoff": ["query_contract", "cards", "actions", "policy"],
    },
    {
        "id": "evidence_quarantine",
        "label": "Evidence quarantine",
        "method": "GET",
        "endpoint": "/api/evidence/quarantine/payload",
        "owner": "claire.api.governed_quarantine_evidence_routes",
        "requires": ["governed_search_plan"],
        "must_have": ["status"],
        "handoff": ["quarantine", "review_queue", "actions"],
    },
    {
        "id": "pipeline_evaluate",
        "label": "Pipeline evaluate",
        "method": "POST",
        "endpoint": "/evaluate",
        "owner": "claire.api.routes_pipeline",
        "requires": ["evidence_quarantine"],
        "body": {
            "raw_input": "governed AI compliance opportunity",
            "mode": "deterministic",
            "source_mode": "simulated_live_packet",
        },
        "must_have": ["status", "run_id", "route_selected", "scores"],
        "handoff": ["run_id", "route_selected", "scores", "post_run_handoff"],
    },
    {
        "id": "portfolio_artifact",
        "label": "Portfolio artifact",
        "method": "GET",
        "endpoint": "/api/portfolio/artifacts/latest",
        "owner": "claire.api.portfolio_artifacts",
        "requires": ["pipeline_evaluate"],
        "must_have": ["status"],
        "handoff": ["metadata", "artifact_routes", "final_package_requirements"],
    },
    {
        "id": "design_portal_contract",
        "label": "Design Portal contract",
        "method": "GET",
        "endpoint": "/design-portal/contract",
        "owner": "claire.api.routes_design_portal_output",
        "requires": ["portfolio_artifact"],
        "must_have": ["status", "cad_export_enabled"],
        "handoff": ["output", "package_readiness", "cad_intent_endpoint"],
    },
    {
        "id": "cad_intent",
        "label": "CAD intent",
        "method": "GET",
        "endpoint": "/cad/intent",
        "owner": "claire.api.routes_design_portal_output",
        "requires": ["design_portal_contract"],
        "must_have": ["status", "cad_export_enabled", "design_contract_endpoint"],
        "handoff": ["design_contract_endpoint", "cad_export_enabled", "operator_review_required"],
    },
    {
        "id": "update_governance",
        "label": "Update governance",
        "method": "GET",
        "endpoint": "/api/update-governance/open-web/panel",
        "owner": "claire.api.routes_open_web_update_governance",
        "requires": ["cad_intent"],
        "must_have": ["status", "install_workflow", "security_posture"],
        "handoff": ["available_updates", "install_workflow", "approval_workflow"],
    },
    {
        "id": "endpoint_reconciliation",
        "label": "Endpoint reconciliation",
        "method": "GET",
        "endpoint": "/api/system/endpoint-reconciliation",
        "owner": "claire.api.routes_endpoint_reconciliation_report",
        "requires": ["update_governance"],
        "must_have": ["status", "unresolved_count", "aliases"],
        "handoff": ["status", "compatibility_alias_count", "unresolved_count"],
    },
    {
        "id": "industry_standard_package",
        "label": "Industry standard endpoint package",
        "method": "GET",
        "endpoint": "/api/system/industry-standard-endpoint-package",
        "owner": "claire.api.routes_industry_standard_endpoint_package",
        "requires": ["endpoint_reconciliation"],
        "must_have": ["status", "standards", "endpoint_expectations"],
        "handoff": ["standards", "endpoint_expectations", "acceptance_checks"],
    },
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _route_paths(app: Any) -> set[str]:
    return {getattr(route, "path", "") for route in getattr(app, "routes", []) if getattr(route, "path", "")}


def _payload_has(payload: Any, key: str) -> bool:
    if not isinstance(payload, dict):
        return False
    if key in payload:
        return True
    nested = {
        child_key
        for value in payload.values()
        if isinstance(value, dict)
        for child_key in value.keys()
    }
    return key in nested


def _execute_step(client: Any, step: dict[str, Any]) -> dict[str, Any]:
    method = step["method"].upper()
    endpoint = step["endpoint"]
    if method == "GET":
        response = client.get(endpoint)
    else:
        response = client.post(endpoint, json=step.get("body", {}))
    try:
        payload = response.json()
    except Exception:
        payload = {"raw_body": response.text[:600]}
    missing = [key for key in step.get("must_have", []) if not _payload_has(payload, key)]
    ok = 200 <= response.status_code < 300 and isinstance(payload, dict) and not missing
    return {
        "id": step["id"],
        "label": step["label"],
        "method": method,
        "endpoint": endpoint,
        "owner": step["owner"],
        "requires": step.get("requires", []),
        "status": "passed" if ok else "blocked",
        "http_status": response.status_code,
        "missing_required_fields": missing,
        "handoff_fields": step.get("handoff", []),
        "payload_keys": sorted(payload.keys())[:60] if isinstance(payload, dict) else [],
        "payload_status": payload.get("status") if isinstance(payload, dict) else None,
    }


def _handoff_edges(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_id = {item["id"]: item for item in results}
    edges: list[dict[str, Any]] = []
    for step in CHAIN_STEPS:
        for dependency in step.get("requires", []):
            source = by_id.get(dependency, {})
            target = by_id.get(step["id"], {})
            edges.append(
                {
                    "from": dependency,
                    "to": step["id"],
                    "source_passed": source.get("status") == "passed",
                    "target_passed": target.get("status") == "passed",
                    "status": "passed" if source.get("status") == "passed" and target.get("status") == "passed" else "blocked",
                }
            )
    return edges


def _write_files(root: Path, proof: dict[str, Any]) -> None:
    proof_path = root / PROOF_PATH
    proof_path.parent.mkdir(parents=True, exist_ok=True)
    proof_path.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path = root / PROOF_MD_PATH
    md_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Dependency-to-Dependency End-to-End Proof",
        "",
        f"Status: `{proof['status']}`",
        f"Generated: `{proof['generated_at']}`",
        "",
        "## Chain",
    ]
    for step in proof["steps"]:
        lines.append(f"- {step['status']}: {step['method']} {step['endpoint']} -> {step['owner']}")
    lines.extend(["", "## Boundaries", "- Live provider/network success is not required for this proof.", "- CAD export remains blocked; CAD intent is reviewable.", "- Automatic update apply remains owner-gated."])
    md_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def build_dependency_chain_proof(app: Any, project_root: Path | str | None = None) -> dict[str, Any]:
    from fastapi.testclient import TestClient

    mounted = _route_paths(app)
    client = TestClient(app)
    mounted_missing = [step["endpoint"] for step in CHAIN_STEPS if step["endpoint"] not in mounted]
    steps = [_execute_step(client, step) for step in CHAIN_STEPS]
    edges = _handoff_edges(steps)
    blocked_steps = [step["id"] for step in steps if step["status"] != "passed"]
    blocked_edges = [edge for edge in edges if edge["status"] != "passed"]
    clean = not mounted_missing and not blocked_steps and not blocked_edges
    proof = {
        "schema_version": "claire.dependency_chain_proof.v1",
        "status": "clean_e2e_review_proof" if clean else "blocked",
        "generated_at": _now(),
        "chain_name": "Dependency-to-Dependency End-to-End Proof Lock",
        "mounted_route_count": len(mounted),
        "mounted_missing": mounted_missing,
        "step_count": len(steps),
        "passed_step_count": len([step for step in steps if step["status"] == "passed"]),
        "blocked_steps": blocked_steps,
        "blocked_edges": blocked_edges,
        "steps": steps,
        "handoff_edges": edges,
        "causal_engine_intake": {
            "status": "contract_ready_runtime_mutation_blocked",
            "reason": "Causal and emergence contracts are mounted for assessment; deeper causal runtime integration remains downstream of route and endpoint proof lock.",
            "active_runtime_mutation": False,
        },
        "boundaries": {
            "live_external_provider_success_required": False,
            "cad_export_enabled": False,
            "automatic_update_apply_enabled": False,
            "compatibility_aliases_allowed_until_frontend_cleanup": True,
        },
    }
    root = Path(project_root or Path.cwd()).resolve()
    _write_files(root, proof)
    return proof
