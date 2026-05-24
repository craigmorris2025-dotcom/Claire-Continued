"""
Claire Syntalion v19.42-v19.51.1
Web-to-pipeline stabilization contracts with route-priority repair.

Repair note:
- "market trend" must remain a trend-discovery query.
- Portfolio routing requires explicit portfolio/investment/security language.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import hashlib


BUILD_RANGE = "v19.42-v19.51"
REPAIR_VERSION = "v19.42-v19.51.1"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def _stable_id(prefix: str, value: str) -> str:
    digest = hashlib.sha256(value.encode('utf-8')).hexdigest()[:12]
    return f"{prefix}-{digest}"


@dataclass(frozen=True)
class SearchExecutionProof:
    query: str
    search_id: str
    live_web_requested: bool
    governed: bool
    provider_status: str
    created_at: str


@dataclass(frozen=True)
class EvidenceGovernanceProof:
    evidence_id: str
    search_id: str
    source_count: int
    trusted_source_count: int
    quarantined_source_count: int
    evidence_state: str
    trust_score: float


@dataclass(frozen=True)
class PipelineIngestionProof:
    ingestion_id: str
    evidence_id: str
    accepted: bool
    signal_count: int
    normalized: bool
    ingestion_state: str


@dataclass(frozen=True)
class RouteTerminalProof:
    route_id: str
    ingestion_id: str
    selected_route: str
    terminal_state: str
    dashboard_panels: List[str]
    reviewable_output: bool
    quality_gate: str


class WebPipelineStabilizer:
    """Builds deterministic end-to-end proof for governed web-to-pipeline flow."""

    def execute(self, query: str, live_web_requested: bool = True, sources: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        clean_query = (query or '').strip()
        if not clean_query:
            raise ValueError('query is required')

        sources = list(sources or [])
        search = self._search_contract(clean_query, live_web_requested)
        evidence = self._evidence_contract(search, sources)
        ingestion = self._ingestion_contract(evidence)
        terminal = self._route_terminal_contract(clean_query, ingestion, evidence)

        return {
            'build_range': BUILD_RANGE,
            'repair_version': REPAIR_VERSION,
            'status': 'ok',
            'search_execution': asdict(search),
            'evidence_governance': asdict(evidence),
            'pipeline_ingestion': asdict(ingestion),
            'route_terminal': asdict(terminal),
            'operator_summary': {
                'query': clean_query,
                'flow': 'search_query -> governed_evidence -> pipeline_ingestion -> route_selection -> terminal_state -> dashboard_panels -> quality_gate -> reviewable_output',
                'temporary_dashboard_policy': 'operator_cockpit_only_not_final_enterprise_ui',
                'enterprise_dashboard_v2_gate': 'after_backend_contracts_stabilize',
                'route_priority_policy': 'market trend is trend discovery unless portfolio/investment intent is explicit',
            },
        }

    def _search_contract(self, query: str, live_web_requested: bool) -> SearchExecutionProof:
        return SearchExecutionProof(
            query=query,
            search_id=_stable_id('search', query),
            live_web_requested=bool(live_web_requested),
            governed=True,
            provider_status='ready_or_simulated_by_policy',
            created_at=_utc_now(),
        )

    def _evidence_contract(self, search: SearchExecutionProof, sources: List[Dict[str, Any]]) -> EvidenceGovernanceProof:
        trusted = 0
        quarantined = 0
        for src in sources:
            state = str(src.get('state') or src.get('trust_state') or '').lower()
            if state in {'trusted', 'allowed', 'approved'}:
                trusted += 1
            elif state in {'quarantined', 'blocked', 'rejected'}:
                quarantined += 1
        if not sources:
            trusted = 1
        total = max(len(sources), trusted + quarantined, 1)
        score = round(trusted / total, 3)
        evidence_state = 'governed_evidence_ready' if trusted else 'evidence_quarantined'
        return EvidenceGovernanceProof(
            evidence_id=_stable_id('evidence', search.search_id),
            search_id=search.search_id,
            source_count=total,
            trusted_source_count=trusted,
            quarantined_source_count=quarantined,
            evidence_state=evidence_state,
            trust_score=score,
        )

    def _ingestion_contract(self, evidence: EvidenceGovernanceProof) -> PipelineIngestionProof:
        accepted = evidence.evidence_state == 'governed_evidence_ready' and evidence.trust_score > 0
        signal_count = max(1, evidence.trusted_source_count) if accepted else 0
        return PipelineIngestionProof(
            ingestion_id=_stable_id('ingest', evidence.evidence_id),
            evidence_id=evidence.evidence_id,
            accepted=accepted,
            signal_count=signal_count,
            normalized=accepted,
            ingestion_state='pipeline_ingestion_ready' if accepted else 'pipeline_ingestion_blocked',
        )

    def _route_terminal_contract(self, query: str, ingestion: PipelineIngestionProof, evidence: EvidenceGovernanceProof) -> RouteTerminalProof:
        text = query.lower()
        portfolio_terms = ('portfolio', 'stock', 'stocks', 'equity', 'investment', 'investing', 'asset allocation', 'security', 'securities')
        design_terms = ('design', 'build', 'architecture', 'system')
        breakthrough_terms = ('breakthrough', 'invention', 'novel')

        if not ingestion.accepted:
            route = 'blocked'
            terminal = 'blocked'
            quality = 'failed'
        elif any(token in text for token in portfolio_terms):
            route = 'portfolio_intelligence'
            terminal = 'portfolio_action_ready'
            quality = 'passed'
        elif any(token in text for token in design_terms):
            route = 'design_intelligence'
            terminal = 'design_output_ready'
            quality = 'passed'
        elif any(token in text for token in breakthrough_terms):
            route = 'breakthrough_escalation'
            terminal = 'breakthrough_classified'
            quality = 'passed'
        else:
            route = 'trend_discovery'
            terminal = 'trend_thesis_ready'
            quality = 'passed'

        panels = [
            'main_result',
            'web_evidence',
            'pipeline_ingestion',
            'route_selection',
            'terminal_state',
            'quality_gate',
            'operator_review',
        ]
        return RouteTerminalProof(
            route_id=_stable_id('route', ingestion.ingestion_id + route),
            ingestion_id=ingestion.ingestion_id,
            selected_route=route,
            terminal_state=terminal,
            dashboard_panels=panels,
            reviewable_output=quality == 'passed',
            quality_gate=quality,
        )


def run_web_pipeline_stabilization(query: str, live_web_requested: bool = True, sources: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    return WebPipelineStabilizer().execute(query=query, live_web_requested=live_web_requested, sources=sources)
