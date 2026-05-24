
from __future__ import annotations

from fastapi import APIRouter

from claire.design_portal.output_contract import (
    build_design_portal_output,
    design_portal_output_summary,
)

router = APIRouter(tags=["Design Portal"])


@router.get("/design-portal/output")
def get_design_portal_output():
    return build_design_portal_output()


@router.get("/design-portal/status")
def get_design_portal_status():
    summary = design_portal_output_summary()
    return {
        "schema_version": "claire.design_portal.status.v1",
        "status": summary.get("status") or summary.get("design_portal_status") or "review",
        "output_endpoint": "/design-portal/output",
        "contract_endpoint": "/design-portal/contract",
        "build_from_run_endpoint": "/design-portal/build-from-run",
        "cad_intent_endpoint": "/cad/intent",
        "cad_export_contract_endpoint": "/cad/export-contract",
        "cad_export_endpoint": None,
        "cad_export_enabled": False,
        "operator_review_required": True,
        "summary": summary,
    }


@router.get("/design-portal/contract")
def get_design_portal_contract():
    output = build_design_portal_output()
    return {
        "schema_version": "claire.design_portal.contract.v1",
        "status": output.get("status", "review"),
        "contract_name": output.get("contract_name", "Design Portal Output Contract"),
        "required_sections": output.get("required_sections", []),
        "package_readiness": output.get("package_readiness", {}),
        "output": output,
        "cad_intent_endpoint": "/cad/intent",
        "cad_export_contract_endpoint": "/cad/export-contract",
        "cad_export_enabled": False,
    }


@router.get("/design-portal/output/summary")
def get_design_portal_output_summary():
    return design_portal_output_summary()


@router.post("/design-portal/output/rebuild")
def rebuild_design_portal_output():
    return build_design_portal_output()


@router.post("/design-portal/build-from-run")
def build_design_portal_from_run():
    output = build_design_portal_output()
    return {
        "schema_version": "claire.design_portal.build_from_run.v1",
        "status": "contract_rebuilt",
        "runtime_mutation_performed": False,
        "cad_export_performed": False,
        "operator_review_required": True,
        "output_endpoint": "/design-portal/output",
        "contract_endpoint": "/design-portal/contract",
        "output": output,
    }


@router.get("/design/portal/output")
def get_design_portal_output_alias():
    return build_design_portal_output()


@router.get("/cad/intent")
def get_cad_intent():
    summary = design_portal_output_summary()
    return {
        "schema_version": "claire.cad.intent.v1",
        "status": "intent_review_ready",
        "intent": "CAD export remains intentionally unavailable until the design portal contract is accepted and CAD adapter endpoints are implemented.",
        "design_portal_status": summary.get("status") or summary.get("design_portal_status") or "review",
        "design_contract_endpoint": "/design-portal/contract",
        "cad_export_contract_endpoint": "/cad/export-contract",
        "cad_export_endpoint": None,
        "cad_export_enabled": False,
        "cad_artifact_endpoint": None,
        "operator_review_required": True,
        "install_required": False,
    }


@router.get("/cad/export-contract")
def get_cad_export_contract():
    summary = design_portal_output_summary()
    return {
        "schema_version": "claire.cad.export_contract.v1",
        "status": "contract_prepared_export_disabled",
        "design_contract_endpoint": "/design-portal/contract",
        "cad_intent_endpoint": "/cad/intent",
        "cad_export_endpoint": None,
        "cad_artifact_endpoint": None,
        "cad_export_enabled": False,
        "implementation_ready": False,
        "operator_review_required": True,
        "runtime_mutation_performed": False,
        "supported_future_formats": ["STEP", "STL", "OBJ", "GLB", "GLTF", "DXF"],
        "required_before_export": [
            "accepted_design_portal_contract",
            "validated_blueprint_package",
            "operator_export_approval",
            "cad_adapter_owner",
            "artifact_retrieval_contract",
        ],
        "design_portal_status": summary.get("status") or summary.get("design_portal_status") or "review",
    }
