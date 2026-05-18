from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, List


VERSION = "v19.89.8-S901-S928"
PHASE = "S901-S928"
TITLE = "Cockpit Web/Search Payload Convergence Repair"


BLOCKED_CAPABILITIES: Dict[str, bool] = {
    "live_web_execution_enabled": False,
    "search_provider_execution_enabled": False,
    "browser_execution_enabled": False,
    "network_request_performed": False,
    "body_read_allowed": False,
    "autonomous_crawling_enabled": False,
    "automatic_updates_enabled": False,
    "runtime_mutation_enabled": False,
    "package_download_performed": False,
    "package_install_performed": False,
    "command_execution_enabled": False,
    "uncontrolled_web_execution_enabled": False,
}


@dataclass(frozen=True)
class PayloadOwner:
    key: str
    label: str
    endpoint: str
    cockpit_tab: str
    expected_visibility: str
    stage_range: str
    status: str = "expected"

    def to_card(self) -> Dict[str, Any]:
        return {
            "id": self.key,
            "title": self.label,
            "endpoint": self.endpoint,
            "tab": self.cockpit_tab,
            "stage_range": self.stage_range,
            "status": self.status,
            "expected_visibility": self.expected_visibility,
        }


@dataclass(frozen=True)
class GovernedAction:
    key: str
    title: str
    tab: str
    source: str
    action_type: str
    state: str
    reason: str
    endpoint: str
    requires_operator_review: bool = True
    executable_now: bool = False

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["authority"] = "presentation_only"
        data["safe_to_show"] = True
        return data


PAYLOAD_OWNERS: List[PayloadOwner] = [
    PayloadOwner(
        key="source_registry",
        label="Governed source registry and trust tiers",
        endpoint="/api/sources/registry",
        cockpit_tab="Governed Web",
        expected_visibility="source cards, trust tier cards, allowlist/denylist/quarantine policy",
        stage_range="S576-S582",
    ),
    PayloadOwner(
        key="search_plan",
        label="Governed search plan and query intent",
        endpoint="/api/search/governed/plans/sample",
        cockpit_tab="Governed Web",
        expected_visibility="query intent, source scope, blocked search execution notice",
        stage_range="S583-S589",
    ),
    PayloadOwner(
        key="evidence_cards",
        label="Governed evidence cards",
        endpoint="/api/evidence/governed/payload",
        cockpit_tab="Evidence & Review",
        expected_visibility="normalized evidence cards before raw JSON",
        stage_range="S590-S596",
    ),
    PayloadOwner(
        key="provider_readiness",
        label="Provider readiness and source families",
        endpoint="/api/search/providers/payload",
        cockpit_tab="Governed Web",
        expected_visibility="provider status, configured/missing/blocked source families",
        stage_range="S597-S603",
    ),
    PayloadOwner(
        key="source_gap_matrix",
        label="Source gap matrix and scope planner",
        endpoint="/api/sources/gaps/payload",
        cockpit_tab="Governed Web",
        expected_visibility="source gaps and search scope cards",
        stage_range="S604-S610",
    ),
    PayloadOwner(
        key="source_intake",
        label="Source evidence intake gate",
        endpoint="/api/evidence/source/intake/status",
        cockpit_tab="Evidence & Review",
        expected_visibility="safe intake states and review requirements",
        stage_range="S611-S617",
    ),
    PayloadOwner(
        key="query_compiler",
        label="Governed query compiler",
        endpoint="/api/search/governed/query/payload",
        cockpit_tab="Governed Web",
        expected_visibility="compiled query scope, risk flags, source constraints",
        stage_range="S618-S624",
    ),
    PayloadOwner(
        key="provider_capability",
        label="Provider capability map",
        endpoint="/api/search/providers/capability/payload",
        cockpit_tab="Governed Web",
        expected_visibility="provider capabilities, blocked operations, manual probe readiness",
        stage_range="S625-S631",
    ),
    PayloadOwner(
        key="source_policy",
        label="Source policy controls",
        endpoint="/api/sources/policy/payload",
        cockpit_tab="Governed Web",
        expected_visibility="allowlist, denylist, quarantine, trust-tier policy",
        stage_range="S632-S638",
    ),
    PayloadOwner(
        key="quarantine_metadata",
        label="Quarantine evidence store and metadata-only result contract",
        endpoint="/api/search/metadata/payload",
        cockpit_tab="Evidence & Review",
        expected_visibility="metadata-only result cards and quarantine state",
        stage_range="S639-S652",
    ),
    PayloadOwner(
        key="controlled_metadata_search",
        label="Controlled metadata search consolidation",
        endpoint="/api/cockpit/search/consolidated-payload",
        cockpit_tab="Governed Web",
        expected_visibility="manual probe gate, bridge preview, routing preview, consolidation stop gate",
        stage_range="S653-S680",
    ),
    PayloadOwner(
        key="metadata_activation_preflight",
        label="Metadata activation preflight",
        endpoint="/api/cockpit/metadata-search/payload",
        cockpit_tab="Governed Web",
        expected_visibility="readiness audit, provider config inspector, adapter boundary, manual probe preflight",
        stage_range="S681-S708",
    ),
    PayloadOwner(
        key="search_result_review",
        label="Search result review and citation candidates",
        endpoint="/api/cockpit/search-results/payload",
        cockpit_tab="Evidence & Review",
        expected_visibility="quarantine results, evidence normalizer, confidence, citation candidates, review actions",
        stage_range="S709-S736",
    ),
    PayloadOwner(
        key="web_search_body_read_planning",
        label="Controlled metadata proof and body-read planning",
        endpoint="/api/cockpit/web-search/payload",
        cockpit_tab="Governed Web",
        expected_visibility="metadata proof, body-read safety plan, request packet, preflight cards",
        stage_range="S737-S778",
    ),
    PayloadOwner(
        key="body_read_gate",
        label="Body-read gate and extraction safety",
        endpoint="/api/cockpit/body-read-gate/payload",
        cockpit_tab="Governed Web",
        expected_visibility="authorization, extraction scope, sanitizer, manual body-read gate",
        stage_range="S779-S834",
    ),
    PayloadOwner(
        key="source_ingestion",
        label="Body-read to reviewed source ingestion",
        endpoint="/api/cockpit/source-ingestion/payload",
        cockpit_tab="Evidence & Review",
        expected_visibility="execution envelope blocked, extraction preview, source ingestion draft, lineage, promotion preview",
        stage_range="S835-S900",
    ),
]


def _actions() -> List[GovernedAction]:
    return [
        GovernedAction(
            key="review_source_policy",
            title="Review source policy controls",
            tab="Actions",
            source="source_policy",
            action_type="review",
            state="available_non_executable",
            reason="Policy is visible for operator review; policy changes are not self-applied.",
            endpoint="/api/sources/policy/actions",
        ),
        GovernedAction(
            key="inspect_provider_configuration",
            title="Inspect provider configuration",
            tab="Actions",
            source="metadata_activation_preflight",
            action_type="inspect",
            state="available_non_executable",
            reason="Configuration can be inspected without exposing secrets and without performing network requests.",
            endpoint="/api/search/providers/configuration/payload",
        ),
        GovernedAction(
            key="prepare_manual_metadata_probe",
            title="Prepare manual metadata probe",
            tab="Actions",
            source="controlled_metadata_search",
            action_type="preflight",
            state="execution_blocked",
            reason="Manual metadata probe requires explicit future activation gate; provider execution remains blocked.",
            endpoint="/api/search/metadata/probe/manual/preflight",
        ),
        GovernedAction(
            key="review_quarantined_metadata_results",
            title="Review quarantined metadata results",
            tab="Actions",
            source="search_result_review",
            action_type="review",
            state="waiting_for_results",
            reason="No live metadata query has been executed by this convergence repair.",
            endpoint="/api/cockpit/search-results/actions",
        ),
        GovernedAction(
            key="review_body_read_request_packet",
            title="Review body-read request packet",
            tab="Actions",
            source="body_read_gate",
            action_type="review",
            state="body_read_blocked",
            reason="Body reads remain blocked; request packet is a planning/review surface only.",
            endpoint="/api/web/body-read/request-packet",
        ),
        GovernedAction(
            key="review_source_ingestion_draft",
            title="Review source ingestion draft",
            tab="Actions",
            source="source_ingestion",
            action_type="review",
            state="runtime_truth_blocked",
            reason="Runtime truth promotion remains blocked; draft lineage can be reviewed only.",
            endpoint="/api/cockpit/source-ingestion/actions",
        ),
        GovernedAction(
            key="confirm_s900_stop_gate",
            title="Confirm S900 stop gate",
            tab="Actions",
            source="source_ingestion",
            action_type="stop_gate",
            state="available_non_executable",
            reason="Confirms dashboard convergence readiness without unlocking web, body reads, or mutation.",
            endpoint="/api/internet/s900-stop-gate",
        ),
    ]


def _evidence_cards() -> List[Dict[str, Any]]:
    return [
        {
            "id": "metadata_search_evidence_queue",
            "title": "Metadata search evidence queue",
            "stage_range": "S639-S736",
            "state": "prepared_empty",
            "count": 0,
            "summary": "Queue is ready for metadata-only search results after a future controlled provider probe.",
            "raw_json_secondary": True,
            "blocked_reason": "No provider execution performed by S901-S928.",
        },
        {
            "id": "body_read_review_packet",
            "title": "Body-read review packet",
            "stage_range": "S737-S834",
            "state": "planning_only",
            "count": 0,
            "summary": "Body-read authorization and extraction scope are represented for review, but body reads are blocked.",
            "raw_json_secondary": True,
            "blocked_reason": "body_read_allowed is false.",
        },
        {
            "id": "source_ingestion_draft_lineage",
            "title": "Source ingestion draft and lineage",
            "stage_range": "S835-S900",
            "state": "draft_ready_no_promotion",
            "count": 0,
            "summary": "Reviewed source ingestion structures exist, but runtime truth promotion remains blocked.",
            "raw_json_secondary": True,
            "blocked_reason": "runtime_mutation_enabled is false.",
        },
    ]


def _governed_web_cards() -> List[Dict[str, Any]]:
    return [
        {
            "id": "metadata_search_activation",
            "title": "Metadata search activation preflight",
            "stage_range": "S681-S708",
            "status": "ready_for_future_manual_gate",
            "execution": "blocked",
            "summary": "Readiness audit, provider configuration inspector, adapter boundary, and manual probe preflight are represented.",
            "endpoint": "/api/cockpit/metadata-search/payload",
        },
        {
            "id": "controlled_metadata_proof",
            "title": "Controlled metadata search proof",
            "stage_range": "S737-S750",
            "status": "planned",
            "execution": "blocked",
            "summary": "The first real provider probe is not executed here; this card confirms the stop-gate structure.",
            "endpoint": "/api/search/metadata/controlled-proof/payload",
        },
        {
            "id": "body_read_gate",
            "title": "Body-read gate",
            "stage_range": "S751-S834",
            "status": "planning_ready",
            "execution": "blocked",
            "summary": "Body-read safety, extraction scope, sanitizer, and manual gate surfaces are ready for review only.",
            "endpoint": "/api/cockpit/body-read-gate/payload",
        },
        {
            "id": "source_ingestion",
            "title": "Reviewed source ingestion",
            "stage_range": "S835-S900",
            "status": "draft_ready_no_runtime_truth",
            "execution": "blocked",
            "summary": "Source ingestion draft, lineage validation, update proposal, and promotion preview remain non-mutating.",
            "endpoint": "/api/cockpit/source-ingestion/payload",
        },
    ]


def build_convergence_payload() -> Dict[str, Any]:
    actions = [action.to_dict() for action in _actions()]
    owners = [owner.to_card() for owner in PAYLOAD_OWNERS]
    evidence_cards = _evidence_cards()
    governed_web_cards = _governed_web_cards()

    return {
        "version": VERSION,
        "phase": PHASE,
        "title": TITLE,
        "status": "dashboard_convergence_ready",
        "highest_stage": "S928",
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "readiness": "governed_internet_update_ready",
        "convergence_summary": {
            "payload_owner_count": len(owners),
            "governed_action_count": len(actions),
            "evidence_card_count": len(evidence_cards),
            "governed_web_card_count": len(governed_web_cards),
            "actions_tab_expected_count": len(actions),
            "raw_json_secondary": True,
            "dashboard_should_show_current_runway": "S901-S928",
        },
        "blocked_capabilities": dict(BLOCKED_CAPABILITIES),
        "blocked_capability_names": [key for key, value in BLOCKED_CAPABILITIES.items() if value is False],
        "payload_owners": owners,
        "governed_web_cards": governed_web_cards,
        "evidence_cards": evidence_cards,
        "actions": actions,
        "system_cards": [
            {
                "id": "current_stage",
                "title": "Current synchronized stage",
                "value": "S901-S928",
                "summary": "Cockpit convergence repair should now surface S900-level web/source/search/body-read/source-ingestion state.",
            },
            {
                "id": "dangerous_authority",
                "title": "Dangerous authority",
                "value": "blocked",
                "summary": "No internet/update/body-read/runtime mutation authority is unlocked by this pack.",
            },
        ],
        "stop_gate": {
            "id": "S928",
            "status": "passed_when_tests_pass",
            "required_visual_results": [
                "Actions tab shows governed actions greater than zero.",
                "Governed Web tab shows metadata search, body-read gate, and source-ingestion cards.",
                "Evidence & Review tab shows normalized evidence cards before raw JSON.",
                "System tab shows S901-S928 synchronized status.",
            ],
            "next_safe_phase": "S929-S956 real controlled metadata-search activation gate",
        },
    }


def build_cards() -> List[Dict[str, Any]]:
    payload = build_convergence_payload()
    cards: List[Dict[str, Any]] = []
    cards.extend(payload["governed_web_cards"])
    cards.extend(payload["evidence_cards"])
    cards.extend(payload["system_cards"])
    return cards


def build_actions() -> List[Dict[str, Any]]:
    return build_convergence_payload()["actions"]


def build_status() -> Dict[str, Any]:
    payload = build_convergence_payload()
    return {
        "version": payload["version"],
        "phase": payload["phase"],
        "status": payload["status"],
        "highest_stage": payload["highest_stage"],
        "readiness": payload["readiness"],
        "backend_owns_truth": payload["backend_owns_truth"],
        "cockpit_presentation_only": payload["cockpit_presentation_only"],
        "action_count": payload["convergence_summary"]["governed_action_count"],
        "payload_owner_count": payload["convergence_summary"]["payload_owner_count"],
        "blocked_capabilities": payload["blocked_capabilities"],
    }


def build_stop_gate() -> Dict[str, Any]:
    payload = build_convergence_payload()
    blocked = payload["blocked_capabilities"]
    return {
        "phase": payload["phase"],
        "status": "ready",
        "passed": True,
        "checks": {
            "backend_payload_available": True,
            "actions_registered_for_cockpit": len(payload["actions"]) > 0,
            "evidence_cards_available": len(payload["evidence_cards"]) > 0,
            "governed_web_cards_available": len(payload["governed_web_cards"]) > 0,
            "live_web_still_blocked": blocked["live_web_execution_enabled"] is False,
            "body_read_still_blocked": blocked["body_read_allowed"] is False,
            "runtime_mutation_still_blocked": blocked["runtime_mutation_enabled"] is False,
            "package_install_still_blocked": blocked["package_install_performed"] is False,
            "command_execution_still_blocked": blocked["command_execution_enabled"] is False,
        },
        "next_phase": payload["stop_gate"]["next_safe_phase"],
    }
