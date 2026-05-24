"""
Claire Syntalion v19.26-v19.31
End-to-End Web-to-Pipeline Launch Candidate Proof Pack.

This pack keeps the current dashboard as a temporary proof/dev/operator cockpit.
It proves the backend route from governed search to reviewable output without
pretending the current dashboard is the final enterprise UI.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Sequence

from runtime_core.web.search_execution_contract import SearchExecutionRequest, build_search_execution_contract


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _clean_text(value: Any) -> str:
    return str(value or "").strip()


@dataclass(frozen=True)
class LiveWebResult:
    title: str
    url: str
    snippet: str
    provider: str = "controlled_provider"
    retrieved_at: str = field(default_factory=utc_now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "url": self.url,
            "snippet": self.snippet,
            "provider": self.provider,
            "retrieved_at": self.retrieved_at,
        }


@dataclass(frozen=True)
class GovernedEvidenceItem:
    title: str
    url: str
    snippet: str
    provider: str
    trust_score: float
    governance_status: str
    evidence_type: str = "web_result"
    normalized_at: str = field(default_factory=utc_now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "url": self.url,
            "snippet": self.snippet,
            "provider": self.provider,
            "trust_score": self.trust_score,
            "governance_status": self.governance_status,
            "evidence_type": self.evidence_type,
            "normalized_at": self.normalized_at,
        }


@dataclass(frozen=True)
class PipelineIngestionResult:
    query: str
    evidence_count: int
    accepted_evidence_count: int
    rejected_evidence_count: int
    signals: List[str]
    entities: List[str]
    ingestion_status: str
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "evidence_count": self.evidence_count,
            "accepted_evidence_count": self.accepted_evidence_count,
            "rejected_evidence_count": self.rejected_evidence_count,
            "signals": list(self.signals),
            "entities": list(self.entities),
            "ingestion_status": self.ingestion_status,
            "created_at": self.created_at,
        }


@dataclass(frozen=True)
class RuntimeRouteDecision:
    selected_route: str
    terminal_state: str
    reason: str
    route_confidence: float
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "selected_route": self.selected_route,
            "terminal_state": self.terminal_state,
            "reason": self.reason,
            "route_confidence": self.route_confidence,
            "created_at": self.created_at,
        }


@dataclass(frozen=True)
class DashboardRuntimeSync:
    dashboard_role: str
    panels: Dict[str, Any]
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dashboard_role": self.dashboard_role,
            "panels": dict(self.panels),
            "created_at": self.created_at,
        }


@dataclass(frozen=True)
class LaunchCandidateQualityGate:
    passed: bool
    status: str
    checks: Dict[str, bool]
    reviewable_output: Dict[str, Any]
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "passed": self.passed,
            "status": self.status,
            "checks": dict(self.checks),
            "reviewable_output": dict(self.reviewable_output),
            "created_at": self.created_at,
        }


def normalize_live_web_results(raw_results: Sequence[Dict[str, Any]] | Sequence[LiveWebResult] | None) -> List[LiveWebResult]:
    if not raw_results:
        return []

    normalized: List[LiveWebResult] = []
    for item in raw_results:
        if isinstance(item, LiveWebResult):
            normalized.append(item)
            continue
        title = _clean_text(item.get("title"))
        url = _clean_text(item.get("url"))
        snippet = _clean_text(item.get("snippet"))
        provider = _clean_text(item.get("provider")) or "controlled_provider"
        if title or url or snippet:
            normalized.append(LiveWebResult(title=title, url=url, snippet=snippet, provider=provider))
    return normalized


def govern_live_web_results(raw_results: Sequence[Dict[str, Any]] | Sequence[LiveWebResult] | None) -> List[GovernedEvidenceItem]:
    governed: List[GovernedEvidenceItem] = []
    for result in normalize_live_web_results(raw_results):
        has_safe_url = result.url.startswith("http://") or result.url.startswith("https://")
        has_content = bool(result.title and result.snippet)
        trust_score = 0.86 if has_safe_url and has_content else 0.44
        governance_status = "accepted" if trust_score >= 0.70 else "quarantined"
        governed.append(
            GovernedEvidenceItem(
                title=result.title,
                url=result.url,
                snippet=result.snippet,
                provider=result.provider,
                trust_score=trust_score,
                governance_status=governance_status,
            )
        )
    return governed


def ingest_governed_evidence(query: str, evidence: Sequence[GovernedEvidenceItem]) -> PipelineIngestionResult:
    accepted = [item for item in evidence if item.governance_status == "accepted"]
    rejected = [item for item in evidence if item.governance_status != "accepted"]
    text = " ".join([query] + [item.title + " " + item.snippet for item in accepted]).lower()

    signals: List[str] = []
    if any(word in text for word in ("market", "stock", "portfolio", "earnings", "rates", "investment")):
        signals.append("market_signal")
    if any(word in text for word in ("technology", "ai", "semiconductor", "software", "chip", "infrastructure")):
        signals.append("technology_signal")
    if any(word in text for word in ("regulation", "policy", "export", "government", "compliance")):
        signals.append("regulatory_signal")
    if any(word in text for word in ("company", "acquisition", "merger", "startup", "enterprise")):
        signals.append("business_signal")
    if not signals and accepted:
        signals.append("general_research_signal")

    strip_chars = ",.;:!?()[]{}\"'"
    entities = sorted({
        token.strip(strip_chars).lower()
        for token in query.replace("/", " ").split()
        if len(token.strip(strip_chars)) > 3
    })[:12]

    ingestion_status = "ingested" if accepted else "insufficient_governed_evidence"
    return PipelineIngestionResult(
        query=query,
        evidence_count=len(evidence),
        accepted_evidence_count=len(accepted),
        rejected_evidence_count=len(rejected),
        signals=signals,
        entities=entities,
        ingestion_status=ingestion_status,
    )


def select_runtime_route(packet: PipelineIngestionResult) -> RuntimeRouteDecision:
    if packet.accepted_evidence_count <= 0:
        return RuntimeRouteDecision(
            selected_route="insufficient_data",
            terminal_state="insufficient_data",
            reason="No accepted governed evidence reached pipeline ingestion.",
            route_confidence=0.0,
        )

    signals = set(packet.signals)
    if "market_signal" in signals and "technology_signal" in signals:
        return RuntimeRouteDecision(
            selected_route="portfolio_intelligence",
            terminal_state="portfolio_action_ready",
            reason="Accepted evidence contains both market and technology signals.",
            route_confidence=0.84,
        )
    if "technology_signal" in signals and "regulatory_signal" in signals:
        return RuntimeRouteDecision(
            selected_route="technology_regulatory_thesis",
            terminal_state="trend_thesis_ready",
            reason="Accepted evidence contains technology and regulatory signals.",
            route_confidence=0.81,
        )
    if "business_signal" in signals:
        return RuntimeRouteDecision(
            selected_route="business_discovery",
            terminal_state="discovery_ready",
            reason="Accepted evidence contains business or acquisition signals.",
            route_confidence=0.77,
        )
    if "technology_signal" in signals:
        return RuntimeRouteDecision(
            selected_route="technology_discovery",
            terminal_state="discovery_ready",
            reason="Accepted evidence contains technology signals.",
            route_confidence=0.75,
        )
    return RuntimeRouteDecision(
        selected_route="general_research",
        terminal_state="discovery_ready",
        reason="Accepted evidence supports a general research route.",
        route_confidence=0.70,
    )


def build_dashboard_runtime_sync(contract: Any, evidence: Sequence[GovernedEvidenceItem], packet: PipelineIngestionResult, route: RuntimeRouteDecision) -> DashboardRuntimeSync:
    panels = {
        "main_result": {
            "terminal_state": route.terminal_state,
            "selected_route": route.selected_route,
            "summary": route.reason,
        },
        "search": {
            "query": contract.query,
            "intent": contract.intent,
            "status": contract.status,
            "execution_allowed": contract.execution_allowed,
        },
        "evidence": {
            "total": len(evidence),
            "accepted": packet.accepted_evidence_count,
            "rejected": packet.rejected_evidence_count,
            "items": [item.to_dict() for item in evidence],
        },
        "pipeline": packet.to_dict(),
        "route": route.to_dict(),
    }
    return DashboardRuntimeSync(dashboard_role="temporary_proof_dev_operator_cockpit", panels=panels)


def run_launch_candidate_quality_gate(contract: Any, evidence: Sequence[GovernedEvidenceItem], packet: PipelineIngestionResult, route: RuntimeRouteDecision, dashboard: DashboardRuntimeSync) -> LaunchCandidateQualityGate:
    checks = {
        "search_contract_ready": contract.status == "ready" and contract.execution_allowed is True,
        "governed_evidence_present": packet.accepted_evidence_count > 0,
        "pipeline_ingested": packet.ingestion_status == "ingested",
        "route_selected": bool(route.selected_route) and route.selected_route != "insufficient_data",
        "terminal_state_present": bool(route.terminal_state),
        "dashboard_main_result_present": bool(dashboard.panels.get("main_result")),
        "reviewable_output_present": True,
    }
    passed = all(checks.values())
    reviewable_output = {
        "query": contract.query,
        "selected_route": route.selected_route,
        "terminal_state": route.terminal_state,
        "evidence_count": len(evidence),
        "accepted_evidence_count": packet.accepted_evidence_count,
        "dashboard_panel_keys": sorted(dashboard.panels.keys()),
        "operator_review_required": True,
    }
    return LaunchCandidateQualityGate(
        passed=passed,
        status="passed" if passed else "blocked_or_insufficient",
        checks=checks,
        reviewable_output=reviewable_output,
    )


def execute_web_to_pipeline_launch_candidate(query: str, live_results: Sequence[Dict[str, Any]] | Sequence[LiveWebResult] | None = None) -> Dict[str, Any]:
    contract = build_search_execution_contract(SearchExecutionRequest(query=query))

    if not contract.execution_allowed:
        dashboard = DashboardRuntimeSync(
            dashboard_role="temporary_proof_dev_operator_cockpit",
            panels={
                "main_result": {
                    "terminal_state": contract.status,
                    "selected_route": contract.intent,
                    "summary": "Search contract blocked execution before live retrieval or pipeline ingestion.",
                },
                "search": contract.to_dict(),
            },
        )
        return {
            "version_pack": "v19.26-v19.31",
            "contract": contract.to_dict(),
            "evidence": [],
            "pipeline": None,
            "route": None,
            "dashboard": dashboard.to_dict(),
            "quality_gate": {
                "passed": False,
                "status": "blocked_by_search_contract",
                "checks": {"search_contract_ready": False},
                "reviewable_output": {"query": contract.query, "warnings": list(contract.warnings)},
                "created_at": utc_now(),
            },
        }

    evidence = govern_live_web_results(live_results)
    packet = ingest_governed_evidence(contract.query, evidence)
    route = select_runtime_route(packet)
    dashboard = build_dashboard_runtime_sync(contract, evidence, packet, route)
    gate = run_launch_candidate_quality_gate(contract, evidence, packet, route, dashboard)

    return {
        "version_pack": "v19.26-v19.31",
        "contract": contract.to_dict(),
        "evidence": [item.to_dict() for item in evidence],
        "pipeline": packet.to_dict(),
        "route": route.to_dict(),
        "dashboard": dashboard.to_dict(),
        "quality_gate": gate.to_dict(),
    }


# Compatibility aliases for earlier temporary tests/imports.
build_governed_evidence = lambda query, raw_results: govern_live_web_results(raw_results)
ingest_evidence_to_pipeline = ingest_governed_evidence
select_route_and_terminal_state = select_runtime_route
run_web_to_pipeline_launch_candidate = execute_web_to_pipeline_launch_candidate
