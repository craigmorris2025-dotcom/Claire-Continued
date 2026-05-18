"""v19.37-v19.41 governed runtime expansion pack.

This module extends the web-to-pipeline launch candidate path without
replacing older contracts. It provides deterministic, testable contracts
for evidence baskets, runtime route decisions, quality gates, dashboard
payloads, and operator review packages.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Mapping, Optional
import hashlib
import re


TRUSTED_DOMAINS = {
    'openai.com', 'nist.gov', 'sec.gov', 'federalregister.gov',
    'arxiv.org', 'mit.edu', 'stanford.edu', 'nature.com',
    'science.org', 'reuters.com', 'apnews.com', 'github.com'
}

ROUTE_KEYWORDS = {
    'portfolio_action_ready': {'portfolio', 'stock', 'market', 'equity', 'investment', 'finance', 'sector'},
    'design_output_ready': {'architecture', 'build', 'software', 'system', 'prototype', 'component', 'implementation'},
    'breakthrough_classified': {'breakthrough', 'invention', 'novel', 'patent', 'research', 'discovery'},
    'trend_thesis_ready': {'trend', 'signals', 'emerging', 'growth', 'adoption', 'demand'},
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def _tokens(text: str) -> List[str]:
    return re.findall(r'[a-z0-9]+', (text or '').lower())


def _domain(url: str) -> str:
    value = (url or '').strip().lower()
    value = value.replace('https://', '').replace('http://', '')
    return value.split('/')[0].replace('www.', '')


def _stable_id(prefix: str, *parts: str) -> str:
    h = hashlib.sha256('|'.join(parts).encode('utf-8')).hexdigest()[:12]
    return f'{prefix}-{h}'


@dataclass
class GovernedEvidenceItem:
    title: str
    url: str
    snippet: str
    source_type: str = 'web'
    trust_score: float = 0.0
    freshness_score: float = 0.5
    relevance_score: float = 0.0
    governance_status: str = 'pending'
    warnings: List[str] = field(default_factory=list)
    evidence_id: str = ''

    def finalize(self, query: str) -> 'GovernedEvidenceItem':
        domain = _domain(self.url)
        query_tokens = set(_tokens(query))
        body_tokens = set(_tokens(' '.join([self.title, self.snippet, self.url])))
        overlap = len(query_tokens & body_tokens)
        self.relevance_score = min(1.0, overlap / max(1, len(query_tokens)))
        self.trust_score = 0.9 if domain in TRUSTED_DOMAINS else 0.55 if domain else 0.25
        if not self.url.startswith(('http://', 'https://')):
            self.warnings.append('non_http_url')
            self.trust_score = min(self.trust_score, 0.3)
        if self.relevance_score < 0.2:
            self.warnings.append('low_relevance')
        if self.trust_score < 0.5:
            self.warnings.append('low_source_trust')
        self.governance_status = 'approved' if self.trust_score >= 0.5 and self.relevance_score >= 0.2 else 'review_required'
        self.evidence_id = _stable_id('ev', query, self.url, self.title)
        return self

    def to_dict(self) -> Dict[str, Any]:
        return dict(self.__dict__)


@dataclass
class EvidenceBasket:
    query: str
    items: List[GovernedEvidenceItem]
    created_at: str = field(default_factory=_utc_now)
    basket_id: str = ''
    governance_status: str = 'pending'
    quality_score: float = 0.0
    warnings: List[str] = field(default_factory=list)

    def finalize(self) -> 'EvidenceBasket':
        self.items = [item.finalize(self.query) for item in self.items]
        self.basket_id = _stable_id('basket', self.query, self.created_at, str(len(self.items)))
        if not self.items:
            self.governance_status = 'blocked'
            self.warnings.append('empty_evidence_basket')
            self.quality_score = 0.0
            return self
        approved = [i for i in self.items if i.governance_status == 'approved']
        self.quality_score = round(sum((i.trust_score + i.relevance_score) / 2 for i in self.items) / len(self.items), 4)
        if len(approved) >= 1 and self.quality_score >= 0.35:
            self.governance_status = 'approved'
        else:
            self.governance_status = 'review_required'
            self.warnings.append('insufficient_approved_evidence')
        return self

    def to_dict(self) -> Dict[str, Any]:
        return {
            'basket_id': self.basket_id,
            'query': self.query,
            'created_at': self.created_at,
            'governance_status': self.governance_status,
            'quality_score': self.quality_score,
            'warnings': list(self.warnings),
            'items': [i.to_dict() for i in self.items],
        }


def build_evidence_basket(query: str, raw_results: List[Mapping[str, Any]]) -> EvidenceBasket:
    items = [GovernedEvidenceItem(
        title=str(r.get('title', '')).strip() or 'Untitled result',
        url=str(r.get('url', '')).strip(),
        snippet=str(r.get('snippet', '')).strip(),
        source_type=str(r.get('source_type', 'web')).strip() or 'web',
    ) for r in raw_results]
    return EvidenceBasket(query=query.strip(), items=items).finalize()


def select_runtime_route(query: str, basket: EvidenceBasket) -> Dict[str, Any]:
    query_token_set = set(_tokens(query))
    scored = []
    for terminal, keys in ROUTE_KEYWORDS.items():
        score = len(query_token_set & keys)
        if score:
            scored.append((score, terminal))
    if basket.governance_status == 'blocked':
        terminal = 'blocked'
        route = 'blocked'
    elif basket.governance_status == 'review_required':
        terminal = 'insufficient_data'
        route = 'evidence_review'
    elif scored:
        terminal = sorted(scored, reverse=True)[0][1]
        route = terminal.replace('_ready', '').replace('_classified', '')
    else:
        terminal = 'discovery_ready'
        route = 'discovery'
    return {
        'route': route,
        'terminal_state': terminal,
        'confidence': round(min(0.95, 0.45 + basket.quality_score), 4),
        'reason': 'selected from query intent and governed evidence quality',
    }


def build_pipeline_ingestion_payload(query: str, basket: EvidenceBasket) -> Dict[str, Any]:
    return {
        'ingestion_id': _stable_id('ingest', query, basket.basket_id),
        'query': query,
        'source': 'governed_web_search',
        'evidence_basket_id': basket.basket_id,
        'approved_evidence_count': len([i for i in basket.items if i.governance_status == 'approved']),
        'total_evidence_count': len(basket.items),
        'quality_score': basket.quality_score,
        'signals': [
            {
                'evidence_id': i.evidence_id,
                'title': i.title,
                'url': i.url,
                'snippet': i.snippet,
                'trust_score': i.trust_score,
                'relevance_score': i.relevance_score,
            }
            for i in basket.items
        ],
    }


def evaluate_quality_gate(basket: EvidenceBasket, route_decision: Mapping[str, Any]) -> Dict[str, Any]:
    passed = basket.governance_status == 'approved' and route_decision.get('terminal_state') not in {'blocked'}
    warnings = list(basket.warnings)
    if route_decision.get('confidence', 0) < 0.55:
        warnings.append('low_route_confidence')
    return {
        'gate': 'v19_37_to_v19_41_runtime_quality_gate',
        'passed': bool(passed),
        'status': 'passed' if passed else 'review_required',
        'warnings': warnings,
        'quality_score': basket.quality_score,
    }


def build_dashboard_sync_payload(query: str, basket: EvidenceBasket, ingestion: Mapping[str, Any], route_decision: Mapping[str, Any], quality_gate: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        'panel_contract_version': 'v19.40',
        'main_result': {
            'title': 'Web-to-pipeline runtime proof',
            'query': query,
            'terminal_state': route_decision['terminal_state'],
            'route': route_decision['route'],
            'quality_gate_status': quality_gate['status'],
        },
        'panels': {
            'search': {'query': query, 'result_count': len(basket.items)},
            'evidence': basket.to_dict(),
            'pipeline_ingestion': dict(ingestion),
            'route_selection': dict(route_decision),
            'quality_gate': dict(quality_gate),
        },
        'operator_review': {
            'review_required': quality_gate['status'] != 'passed',
            'summary': f"Route {route_decision['route']} reached {route_decision['terminal_state']} with quality {basket.quality_score}.",
        },
    }


def execute_web_to_pipeline_runtime(query: str, raw_results: Optional[List[Mapping[str, Any]]] = None) -> Dict[str, Any]:
    raw_results = list(raw_results or [])
    basket = build_evidence_basket(query, raw_results)
    ingestion = build_pipeline_ingestion_payload(query, basket)
    route_decision = select_runtime_route(query, basket)
    quality_gate = evaluate_quality_gate(basket, route_decision)
    dashboard = build_dashboard_sync_payload(query, basket, ingestion, route_decision, quality_gate)
    return {
        'version': 'v19.37-v19.41',
        'query': query,
        'evidence_basket': basket.to_dict(),
        'pipeline_ingestion': ingestion,
        'route_decision': route_decision,
        'terminal_state': route_decision['terminal_state'],
        'quality_gate': quality_gate,
        'dashboard_payload': dashboard,
        'reviewable_output': dashboard['operator_review'],
    }
