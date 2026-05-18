# Claire Syntalion v18.55
# Dashboard Search Bar Real Result Binding
#
# This module is intentionally review-safe. It binds governed live-search
# result objects into a dashboard-facing payload without mutating runtime
# truth, triggering autonomous execution, or approving automatic updates.

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Mapping, Optional
from urllib.parse import urlparse


CONTRACT_VERSION = 'v18.55.dashboard_search_result_binding'

BLOCKED_STATUS = 'blocked'
READY_STATUS = 'results_ready'
EMPTY_STATUS = 'no_results'

IMMUTABLE_RUNTIME_TRUTH_MUTATED = False
AUTONOMOUS_EXECUTION_ENABLED = False
AUTOMATIC_UPDATES_ENABLED = False


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def _string(value: Any, default: str = '') -> str:
    if value is None:
        return default
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def _safe_url(value: Any) -> str:
    url = _string(value)
    if not url:
        return ''
    parsed = urlparse(url)
    if parsed.scheme not in {'http', 'https'}:
        return ''
    if not parsed.netloc:
        return ''
    return url


def _domain_from_url(url: str) -> str:
    parsed = urlparse(url)
    return parsed.netloc.lower().strip()


def _number(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _clamp(value: Any, low: float = 0.0, high: float = 1.0) -> float:
    number = _number(value, low)
    if number < low:
        return low
    if number > high:
        return high
    return number


@dataclass(frozen=True)
class DashboardBoundSearchResult:
    title: str
    url: str
    domain: str
    snippet: str = ''
    provider: str = 'unknown'
    rank: int = 0
    trust_score: float = 0.0
    result_id: str = ''
    evidence_id: str = ''
    review_required: bool = True
    clickable: bool = True
    render_state: str = 'visible'

    def to_dict(self) -> Dict[str, Any]:
        return {
            'title': self.title,
            'url': self.url,
            'domain': self.domain,
            'snippet': self.snippet,
            'provider': self.provider,
            'rank': self.rank,
            'trust_score': self.trust_score,
            'result_id': self.result_id,
            'evidence_id': self.evidence_id,
            'review_required': self.review_required,
            'clickable': self.clickable,
            'render_state': self.render_state,
        }


@dataclass(frozen=True)
class DashboardSearchBindingPolicy:
    manual_enable_required: bool = True
    review_required: bool = True
    fail_closed: bool = True
    immutable_runtime_truth: bool = True
    runtime_truth_mutated: bool = False
    autonomous_execution_enabled: bool = False
    automatic_updates_enabled: bool = False
    max_visible_results: int = 10
    absolute_paths_disallowed: bool = True
    allow_clickable_results: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            'manual_enable_required': self.manual_enable_required,
            'review_required': self.review_required,
            'fail_closed': self.fail_closed,
            'immutable_runtime_truth': self.immutable_runtime_truth,
            'runtime_truth_mutated': self.runtime_truth_mutated,
            'autonomous_execution_enabled': self.autonomous_execution_enabled,
            'automatic_updates_enabled': self.automatic_updates_enabled,
            'max_visible_results': self.max_visible_results,
            'absolute_paths_disallowed': self.absolute_paths_disallowed,
            'allow_clickable_results': self.allow_clickable_results,
        }


def normalize_dashboard_result(raw: Mapping[str, Any], *, rank: int = 0) -> Optional[DashboardBoundSearchResult]:
    title = _string(raw.get('title') or raw.get('name') or raw.get('display_title'))
    url = _safe_url(raw.get('url') or raw.get('link') or raw.get('href'))
    if not url:
        return None

    domain = _string(raw.get('domain')) or _domain_from_url(url)
    if not title:
        title = domain or url

    snippet = _string(
        raw.get('snippet')
        or raw.get('summary')
        or raw.get('description')
        or raw.get('body_preview')
        or raw.get('preview')
    )

    provider = _string(raw.get('provider') or raw.get('source_provider') or raw.get('adapter'), 'unknown')
    trust_score = _clamp(
        raw.get('trust_score')
        if raw.get('trust_score') is not None
        else raw.get('trust')
        if raw.get('trust') is not None
        else raw.get('normalized_trust_score')
        if raw.get('normalized_trust_score') is not None
        else 0.0
    )

    result_id = _string(raw.get('result_id') or raw.get('id') or f'dashboard-result-{rank}')
    evidence_id = _string(raw.get('evidence_id') or raw.get('basket_id') or raw.get('evidence_ref'))

    return DashboardBoundSearchResult(
        title=title,
        url=url,
        domain=domain,
        snippet=snippet,
        provider=provider,
        rank=int(raw.get('rank') or rank),
        trust_score=trust_score,
        result_id=result_id,
        evidence_id=evidence_id,
        review_required=True,
        clickable=True,
        render_state='visible',
    )


def bind_dashboard_search_results(
    *,
    query: str,
    session_id: str,
    results: Iterable[Mapping[str, Any]],
    provider: str = 'unknown',
    governance_state: Optional[Mapping[str, Any]] = None,
    evidence_basket: Optional[Mapping[str, Any]] = None,
    provider_health: Optional[Mapping[str, Any]] = None,
    manual_enable_confirmed: bool = False,
    max_visible_results: int = 10,
) -> Dict[str, Any]:
    clean_query = _string(query)
    clean_session_id = _string(session_id, 'unbound-session')
    policy = DashboardSearchBindingPolicy(max_visible_results=max(1, int(max_visible_results or 10)))

    if not clean_query:
        return {
            'contract_version': CONTRACT_VERSION,
            'status': BLOCKED_STATUS,
            'reason': 'empty_query',
            'query': clean_query,
            'session_id': clean_session_id,
            'provider': provider,
            'created_at': _utc_now(),
            'results': [],
            'visible_result_count': 0,
            'dashboard_render': {
                'search_bar_bound': True,
                'results_panel_state': BLOCKED_STATUS,
                'empty_state_message': 'Enter a query to run governed search.',
            },
            'policy': policy.to_dict(),
            'governance': {
                'manual_enable_confirmed': bool(manual_enable_confirmed),
                'review_required': True,
                'runtime_truth_mutated': False,
                'autonomous_execution': False,
                'automatic_updates': False,
            },
            'evidence_basket': evidence_basket or {},
            'provider_health': provider_health or {},
        }

    if not manual_enable_confirmed:
        return {
            'contract_version': CONTRACT_VERSION,
            'status': BLOCKED_STATUS,
            'reason': 'manual_enable_not_confirmed',
            'query': clean_query,
            'session_id': clean_session_id,
            'provider': provider,
            'created_at': _utc_now(),
            'results': [],
            'visible_result_count': 0,
            'dashboard_render': {
                'search_bar_bound': True,
                'results_panel_state': BLOCKED_STATUS,
                'empty_state_message': 'Manual governed search enable flag is required before rendering live results.',
            },
            'policy': policy.to_dict(),
            'governance': {
                'manual_enable_confirmed': False,
                'review_required': True,
                'runtime_truth_mutated': False,
                'autonomous_execution': False,
                'automatic_updates': False,
            },
            'evidence_basket': evidence_basket or {},
            'provider_health': provider_health or {},
        }

    normalized: List[DashboardBoundSearchResult] = []
    for index, raw in enumerate(list(results or []), start=1):
        if not isinstance(raw, Mapping):
            continue
        bound = normalize_dashboard_result(raw, rank=index)
        if bound is not None:
            normalized.append(bound)
        if len(normalized) >= policy.max_visible_results:
            break

    status = READY_STATUS if normalized else EMPTY_STATUS
    empty_message = '' if normalized else 'No governed live web results were returned for this query.'

    governance = {
        'manual_enable_confirmed': True,
        'review_required': True,
        'runtime_truth_mutated': False,
        'autonomous_execution': False,
        'automatic_updates': False,
        'fail_closed': True,
        'governance_state': dict(governance_state or {}),
    }

    return {
        'contract_version': CONTRACT_VERSION,
        'status': status,
        'reason': '' if normalized else 'no_valid_results',
        'query': clean_query,
        'session_id': clean_session_id,
        'provider': _string(provider, 'unknown'),
        'created_at': _utc_now(),
        'results': [item.to_dict() for item in normalized],
        'visible_result_count': len(normalized),
        'dashboard_render': {
            'search_bar_bound': True,
            'results_panel_state': 'visible' if normalized else EMPTY_STATUS,
            'result_card_contract': 'title_url_snippet_domain_trust_provider',
            'click_action': 'operator_review_open_url',
            'empty_state_message': empty_message,
        },
        'policy': policy.to_dict(),
        'governance': governance,
        'evidence_basket': dict(evidence_basket or {}),
        'provider_health': dict(provider_health or {}),
    }


def bind_first_visible_query_result(
    query: str,
    url: str,
    *,
    title: str = '',
    snippet: str = '',
    provider: str = 'manual_test',
    session_id: str = 'manual-visible-query-session',
) -> Dict[str, Any]:
    return bind_dashboard_search_results(
        query=query,
        session_id=session_id,
        provider=provider,
        manual_enable_confirmed=True,
        results=[
            {
                'title': title or query,
                'url': url,
                'snippet': snippet,
                'provider': provider,
                'trust_score': 1.0,
                'result_id': 'first-visible-query-result',
                'evidence_id': 'review-visible-smoke',
            }
        ],
        evidence_basket={
            'evidence_capture_enabled': True,
            'runtime_truth_mutated': False,
            'review_required': True,
        },
        provider_health={
            'provider': provider,
            'status': 'available',
            'manual_enable_required': True,
        },
    )


__all__ = [
    'AUTOMATIC_UPDATES_ENABLED',
    'AUTONOMOUS_EXECUTION_ENABLED',
    'BLOCKED_STATUS',
    'CONTRACT_VERSION',
    'DashboardBoundSearchResult',
    'DashboardSearchBindingPolicy',
    'EMPTY_STATUS',
    'IMMUTABLE_RUNTIME_TRUTH_MUTATED',
    'READY_STATUS',
    'bind_dashboard_search_results',
    'bind_first_visible_query_result',
    'normalize_dashboard_result',
]
