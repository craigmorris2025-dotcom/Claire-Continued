from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, Query, Response

from runtime_core.governance.governed_body_read_authorization import (
    build_authorization_actions,
    build_authorization_cards,
    build_authorization_payload,
)
from runtime_core.governance.governed_body_read_safety_plan import (
    build_body_read_safety_plan,
)
from runtime_core.governance.governed_body_read_preflight import (
    build_body_read_preflight_actions,
    build_body_read_preflight_cards,
    build_body_read_preflight_payload,
)
from runtime_core.governance.governed_cockpit_control_surface_force_mount import (
    get_cockpit_control_surface_payload,
)
from runtime_core.governance.governed_cockpit_operation_controls import build_operation_payload
from runtime_core.governance.governed_cockpit_operation_visuals import build_visual_payload
from runtime_core.governance.governed_cockpit_search_consolidation import (
    build_cockpit_search_actions,
    build_cockpit_search_cards,
    build_cockpit_search_stop_gate,
    build_cockpit_source_search_consolidation,
)
from runtime_core.governance.governed_manual_body_read_execution_envelope import build_execution_envelope_payload
from runtime_core.governance.governed_manual_body_read_gate import (
    build_manual_body_read_gate_actions,
    build_manual_body_read_gate_cards,
    build_manual_body_read_gate_payload,
    build_manual_body_read_status,
    build_manual_body_read_stop_gate,
)
from runtime_core.governance.governed_manual_metadata_probe_gate import (
    build_manual_metadata_probe_payload,
    build_manual_metadata_probe_preflight,
    build_s708_stop_gate,
)
from runtime_core.governance.governed_manual_provider_probe import build_manual_probe_preflight
from runtime_core.governance.governed_metadata_adapter_boundary import build_metadata_adapter_payload
from runtime_core.governance.governed_metadata_result_contract import build_metadata_status
from runtime_core.governance.governed_provider_capability_map import (
    build_provider_capability_actions,
    build_provider_capability_cards,
    get_provider_capability_map,
    get_provider_capability_payload,
    get_provider_capability_status,
    get_provider_capability_stop_gate,
)
from runtime_core.governance.governed_provider_config_inspector import build_provider_configuration_payload
from runtime_core.governance.governed_query_compiler import build_governed_query_plan, build_query_compiler_payload
from runtime_core.governance.governed_quarantine_evidence_store import build_quarantine_status
from runtime_core.governance.governed_content_safety_sanitizer import classify_content_risk
from runtime_core.governance.governed_source_evidence_intake import build_source_evidence_intake_payload
from runtime_core.governance.governed_source_policy_controls import (
    build_source_policy_actions,
    build_source_policy_cards,
    get_source_policy_controls,
    get_source_policy_payload,
    get_source_policy_status,
    get_source_policy_stop_gate,
)
from runtime_core.governance.governed_runtime_truth_promotion_preview import (
    build_cockpit_source_ingestion_actions,
    build_cockpit_source_ingestion_cards,
    build_cockpit_source_ingestion_payload,
    build_s900_stop_gate,
)
from runtime_core.governance.governed_web_readiness_audit import build_readiness_audit


router = APIRouter(tags=["governed safety"])

_CONTROL_SURFACE_JS = (
    "fetch('/api/cockpit/control-surface/payload',{cache:'no-store'})"
    ".then(r=>r.json()).then(p=>document.body.dataset.claireControlSurface=String(p.action_count||0));"
)


@router.get("/api/evidence/source/intake")
def evidence_source_intake(query: str = "", route_context: str = "web_source_search") -> Any:
    return build_source_evidence_intake_payload(query=query, route_context=route_context)


@router.get("/api/search/governed/query/compile")
def search_governed_query_compile(query: str = "", route_context: str = "web_source_search") -> Any:
    return build_governed_query_plan(query=query, route_context=route_context)


@router.get("/api/search/governed/query/payload")
def search_governed_query_payload(query: str = "", route_context: str = "web_source_search") -> Any:
    return build_query_compiler_payload(query=query, route_context=route_context)


@router.get("/api/search/providers/capability-map")
def search_providers_capability_map() -> Any:
    return get_provider_capability_map()


@router.get("/api/search/providers/capability/cards")
def search_providers_capability_cards() -> Any:
    return {"status": "ready", "cards": build_provider_capability_cards()}


@router.get("/api/search/providers/capability/actions")
def search_providers_capability_actions() -> Any:
    return {"status": "ready", "actions": build_provider_capability_actions()}


@router.get("/api/search/providers/capability/status")
def search_providers_capability_status() -> Any:
    return get_provider_capability_status()


@router.get("/api/search/providers/capability/payload")
def search_providers_capability_payload() -> Any:
    return get_provider_capability_payload()


@router.get("/api/search/providers/capability/stop-gate")
def search_providers_capability_stop_gate() -> Any:
    return get_provider_capability_stop_gate()


@router.get("/api/sources/policy/controls")
def sources_policy_controls() -> Any:
    return get_source_policy_controls()


@router.get("/api/sources/policy/cards")
def sources_policy_cards() -> Any:
    return {"status": "ready", "cards": build_source_policy_cards()}


@router.get("/api/sources/policy/actions")
def sources_policy_actions() -> Any:
    return {"status": "ready", "actions": build_source_policy_actions()}


@router.get("/api/sources/policy/status")
def sources_policy_status() -> Any:
    return get_source_policy_status()


@router.get("/api/sources/policy/payload")
def sources_policy_payload() -> Any:
    return get_source_policy_payload()


@router.get("/api/sources/policy/stop-gate")
def sources_policy_stop_gate() -> Any:
    return get_source_policy_stop_gate()


@router.get("/api/evidence/quarantine/status")
def evidence_quarantine_status() -> Any:
    return build_quarantine_status()


@router.get("/api/search/metadata/status")
def search_metadata_status() -> Any:
    return build_metadata_status()


@router.get("/api/search/provider/manual-probe/preflight")
def search_provider_manual_probe_preflight(query: str | None = Query(default=None)) -> Any:
    return build_manual_probe_preflight(query)


@router.get("/api/cockpit/search/consolidated-payload")
def cockpit_search_consolidated_payload(query: str | None = Query(default=None)) -> Any:
    return build_cockpit_source_search_consolidation(query)


@router.get("/api/cockpit/search/cards")
def cockpit_search_cards(query: str | None = Query(default=None)) -> Any:
    return build_cockpit_search_cards(query)


@router.get("/api/cockpit/search/actions")
def cockpit_search_actions(query: str | None = Query(default=None)) -> Any:
    return build_cockpit_search_actions(query)


@router.get("/api/cockpit/search/stop-gate")
def cockpit_search_stop_gate() -> Any:
    return build_cockpit_search_stop_gate()


@router.get("/api/search/readiness/audit")
def search_readiness_audit() -> Any:
    return build_readiness_audit()


@router.get("/api/search/providers/configuration/payload")
def search_providers_configuration_payload() -> Any:
    return build_provider_configuration_payload()


@router.get("/api/search/metadata/adapter/payload")
def search_metadata_adapter_payload(query: str | None = Query(default=None)) -> Any:
    return build_metadata_adapter_payload(query)


@router.get("/api/search/metadata/probe/manual/preflight")
def search_metadata_probe_manual_preflight(query: str | None = Query(default=None)) -> Any:
    return build_manual_metadata_probe_preflight(query)


@router.get("/api/search/metadata/probe/manual/payload")
def search_metadata_probe_manual_payload(query: str | None = Query(default=None)) -> Any:
    return build_manual_metadata_probe_payload(query)


@router.get("/api/cockpit/metadata-search/payload")
def cockpit_metadata_search_payload(query: str | None = Query(default=None)) -> Any:
    return {
        "payload_id": "s681_s708_cockpit_metadata_search_payload",
        "adapter_boundary": build_metadata_adapter_payload(query),
        "manual_probe": build_manual_metadata_probe_payload(query),
        "provider_configuration": build_provider_configuration_payload(),
        "readiness": build_readiness_audit(),
        "stop_gate": build_s708_stop_gate(),
    }


@router.get("/api/cockpit/web-search/payload")
def cockpit_web_search_payload() -> Any:
    return build_body_read_preflight_payload()


@router.get("/api/cockpit/web-search/cards")
def cockpit_web_search_cards() -> Any:
    return build_body_read_preflight_cards()


@router.get("/api/cockpit/web-search/actions")
def cockpit_web_search_actions() -> Any:
    return build_body_read_preflight_actions()


@router.post("/api/web/body-read/risk-classifier")
def web_body_read_risk_classifier(payload: dict[str, Any] = Body(default_factory=dict)) -> Any:
    candidates = payload.get("candidates") if isinstance(payload, dict) else None
    return build_body_read_safety_plan(candidates)


@router.get("/api/cockpit/body-read-gate/payload")
def cockpit_body_read_gate_payload() -> Any:
    return build_manual_body_read_gate_payload()


@router.get("/api/cockpit/body-read-gate/cards")
def cockpit_body_read_gate_cards() -> Any:
    return build_manual_body_read_gate_cards()


@router.get("/api/cockpit/body-read-gate/actions")
def cockpit_body_read_gate_actions() -> Any:
    return build_manual_body_read_gate_actions()


@router.get("/api/cockpit/body-read-gate/status")
def cockpit_body_read_gate_status() -> Any:
    return build_manual_body_read_status()


@router.get("/api/cockpit/body-read-gate/stop-gate")
def cockpit_body_read_gate_stop_gate() -> Any:
    return build_manual_body_read_stop_gate()


@router.post("/api/web/body-read/authorization/payload")
def web_body_read_authorization_payload(payload: dict[str, Any] = Body(default_factory=dict)) -> Any:
    requests = payload.get("requests") if isinstance(payload, dict) else None
    return build_authorization_payload(requests)


@router.get("/api/web/body-read/authorization/cards")
def web_body_read_authorization_cards() -> Any:
    return build_authorization_cards()


@router.get("/api/web/body-read/authorization/actions")
def web_body_read_authorization_actions() -> Any:
    return build_authorization_actions()


@router.post("/api/web/body-read/sanitizer/classify")
def web_body_read_sanitizer_classify(payload: dict[str, Any] = Body(default_factory=dict)) -> Any:
    return classify_content_risk(payload.get("content_type"), payload.get("source_family"))


@router.get("/api/cockpit/source-ingestion/payload")
def cockpit_source_ingestion_payload() -> Any:
    return build_cockpit_source_ingestion_payload()


@router.get("/api/cockpit/source-ingestion/cards")
def cockpit_source_ingestion_cards() -> Any:
    return build_cockpit_source_ingestion_cards()


@router.get("/api/cockpit/source-ingestion/actions")
def cockpit_source_ingestion_actions() -> Any:
    return build_cockpit_source_ingestion_actions()


@router.get("/api/cockpit/source-ingestion/status")
def cockpit_source_ingestion_status() -> Any:
    payload = build_cockpit_source_ingestion_payload()
    return {
        "status": "ready",
        "stage_range": payload["stage_range"],
        "terminal_state": payload["terminal_state"],
        "executable_actions": 0,
        "body_read_allowed": False,
        "runtime_mutation_enabled": False,
        "automatic_updates_enabled": False,
    }


@router.get("/api/cockpit/source-ingestion/stop-gate")
def cockpit_source_ingestion_stop_gate() -> Any:
    return build_s900_stop_gate()


@router.post("/api/web/body-read/execution-envelope/payload")
def web_body_read_execution_envelope_payload(payload: dict[str, Any] = Body(default_factory=dict)) -> Any:
    return build_execution_envelope_payload(payload.get("envelopes"))


@router.get("/api/cockpit/operations/payload")
def cockpit_operations_payload() -> Any:
    return build_operation_payload()


@router.get("/api/cockpit/operation-visuals/payload")
def cockpit_operation_visuals_payload() -> Any:
    return build_visual_payload()


@router.get("/api/cockpit/control-surface/payload")
def cockpit_control_surface_payload() -> Any:
    return get_cockpit_control_surface_payload()


@router.get("/api/cockpit/control-surface/assets/js")
def cockpit_control_surface_js_asset() -> Response:
    return Response(_CONTROL_SURFACE_JS, media_type="application/javascript")
