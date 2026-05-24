
# Claire Syntalion v18.56
# Live Search Dashboard Query Execution Bridge
#
# This module connects the dashboard search bar query payload to governed
# live-search execution and dashboard result binding. It does not perform
# autonomous browsing, automatic updates, or runtime-truth mutation.

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Tuple
import os

try:
    from .dashboard_search_result_binding import bind_dashboard_search_results
except Exception:  # pragma: no cover - fail-closed fallback for damaged local installs
    bind_dashboard_search_results = None


CONTRACT_VERSION = 'v18.56.live_search_dashboard_query_execution_bridge'

ENV_REAL_SEARCH_PROVIDER = 'PLATFORM_ALLOW_REAL_SEARCH_PROVIDER'
ENV_LIMITED_BODY_GET = 'PLATFORM_ALLOW_CONTROLLED_LIMITED_BODY_GET'

BLOCKED_STATUS = 'blocked'
EXECUTED_STATUS = 'executed'
RESULTS_READY_STATUS = 'results_ready'
NO_RESULTS_STATUS = 'no_results'
EXECUTION_FAILED_STATUS = 'execution_failed'


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def _string(value: Any, default: str = '') -> str:
    if value is None:
        return default
    if isinstance(value, str):
        value = value.strip()
        return value if value else default
    return str(value).strip() or default


def _bool(value: Any, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {'1', 'true', 'yes', 'y', 'on', 'enabled'}
    return bool(value)


def _env_enabled(name: str) -> bool:
    return os.getenv(name, '').strip().lower() in {'1', 'true', 'yes', 'y', 'on', 'enabled'}


@dataclass(frozen=True)
class DashboardQueryExecutionPolicy:
    manual_enable_required: bool = True
    provider_env_flag_required: bool = True
    limited_body_env_flag_required: bool = True
    review_required: bool = True
    fail_closed: bool = True
    immutable_runtime_truth: bool = True
    runtime_truth_mutated: bool = False
    autonomous_execution_enabled: bool = False
    automatic_updates_enabled: bool = False
    max_results: int = 10
    bounded_execution: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            'manual_enable_required': self.manual_enable_required,
            'provider_env_flag_required': self.provider_env_flag_required,
            'limited_body_env_flag_required': self.limited_body_env_flag_required,
            'review_required': self.review_required,
            'fail_closed': self.fail_closed,
            'immutable_runtime_truth': self.immutable_runtime_truth,
            'runtime_truth_mutated': self.runtime_truth_mutated,
            'autonomous_execution_enabled': self.autonomous_execution_enabled,
            'automatic_updates_enabled': self.automatic_updates_enabled,
            'max_results': self.max_results,
            'bounded_execution': self.bounded_execution,
        }


def _blocked_payload(
    *,
    query: str,
    session_id: str,
    provider: str,
    reason: str,
    policy: DashboardQueryExecutionPolicy,
    extra: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    return {
        'contract_version': CONTRACT_VERSION,
        'status': BLOCKED_STATUS,
        'reason': reason,
        'query': query,
        'session_id': session_id,
        'provider': provider,
        'created_at': _utc_now(),
        'execution': {
            'attempted': False,
            'bounded': True,
            'manual_enable_confirmed': False,
            'provider_env_enabled': _env_enabled(ENV_REAL_SEARCH_PROVIDER),
            'limited_body_env_enabled': _env_enabled(ENV_LIMITED_BODY_GET),
        },
        'dashboard_payload': {
            'status': BLOCKED_STATUS,
            'reason': reason,
            'query': query,
            'session_id': session_id,
            'provider': provider,
            'results': [],
            'visible_result_count': 0,
            'dashboard_render': {
                'search_bar_bound': True,
                'results_panel_state': BLOCKED_STATUS,
                'empty_state_message': reason,
            },
        },
        'policy': policy.to_dict(),
        'governance': {
            'review_required': True,
            'runtime_truth_mutated': False,
            'autonomous_execution': False,
            'automatic_updates': False,
            'fail_closed': True,
        },
        'extra': dict(extra or {}),
    }


def _extract_results(executor_response: Any) -> Tuple[List[Mapping[str, Any]], Dict[str, Any]]:
    if executor_response is None:
        return [], {'raw_response_type': 'none'}

    if isinstance(executor_response, list):
        return [item for item in executor_response if isinstance(item, Mapping)], {'raw_response_type': 'list'}

    if isinstance(executor_response, Mapping):
        for key in ('results', 'items', 'search_results', 'provider_results'):
            value = executor_response.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, Mapping)], dict(executor_response)
        if executor_response.get('url') or executor_response.get('link') or executor_response.get('href'):
            return [executor_response], dict(executor_response)
        return [], dict(executor_response)

    return [], {'raw_response_type': type(executor_response).__name__}


def execute_dashboard_live_search_query(
    *,
    query: str,
    session_id: str = 'dashboard-live-search-session',
    provider: str = 'governed-provider',
    executor: Optional[Callable[..., Any]] = None,
    manual_enable_confirmed: bool = False,
    require_provider_env: bool = True,
    require_limited_body_env: bool = True,
    max_results: int = 10,
    request_context: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    clean_query = _string(query)
    clean_session_id = _string(session_id, 'dashboard-live-search-session')
    clean_provider = _string(provider, 'governed-provider')
    policy = DashboardQueryExecutionPolicy(
        provider_env_flag_required=bool(require_provider_env),
        limited_body_env_flag_required=bool(require_limited_body_env),
        max_results=max(1, int(max_results or 10)),
    )

    if not clean_query:
        return _blocked_payload(
            query=clean_query,
            session_id=clean_session_id,
            provider=clean_provider,
            reason='empty_query',
            policy=policy,
        )

    if not manual_enable_confirmed:
        return _blocked_payload(
            query=clean_query,
            session_id=clean_session_id,
            provider=clean_provider,
            reason='manual_enable_not_confirmed',
            policy=policy,
        )

    if require_provider_env and not _env_enabled(ENV_REAL_SEARCH_PROVIDER):
        return _blocked_payload(
            query=clean_query,
            session_id=clean_session_id,
            provider=clean_provider,
            reason='real_search_provider_env_not_enabled',
            policy=policy,
            extra={'required_env': ENV_REAL_SEARCH_PROVIDER},
        )

    if require_limited_body_env and not _env_enabled(ENV_LIMITED_BODY_GET):
        return _blocked_payload(
            query=clean_query,
            session_id=clean_session_id,
            provider=clean_provider,
            reason='limited_body_get_env_not_enabled',
            policy=policy,
            extra={'required_env': ENV_LIMITED_BODY_GET},
        )

    if executor is None:
        return _blocked_payload(
            query=clean_query,
            session_id=clean_session_id,
            provider=clean_provider,
            reason='no_executor_available',
            policy=policy,
        )

    try:
        executor_response = executor(
            query=clean_query,
            provider=clean_provider,
            session_id=clean_session_id,
            max_results=policy.max_results,
            request_context=dict(request_context or {}),
        )
    except Exception as exc:
        return {
            'contract_version': CONTRACT_VERSION,
            'status': EXECUTION_FAILED_STATUS,
            'reason': 'executor_exception',
            'query': clean_query,
            'session_id': clean_session_id,
            'provider': clean_provider,
            'created_at': _utc_now(),
            'execution': {
                'attempted': True,
                'bounded': True,
                'manual_enable_confirmed': True,
                'provider_env_enabled': _env_enabled(ENV_REAL_SEARCH_PROVIDER),
                'limited_body_env_enabled': _env_enabled(ENV_LIMITED_BODY_GET),
                'error_type': type(exc).__name__,
            },
            'dashboard_payload': {
                'status': BLOCKED_STATUS,
                'reason': 'executor_exception',
                'query': clean_query,
                'session_id': clean_session_id,
                'provider': clean_provider,
                'results': [],
                'visible_result_count': 0,
            },
            'policy': policy.to_dict(),
            'governance': {
                'review_required': True,
                'runtime_truth_mutated': False,
                'autonomous_execution': False,
                'automatic_updates': False,
                'fail_closed': True,
            },
        }

    raw_results, metadata = _extract_results(executor_response)
    limited_results = raw_results[:policy.max_results]

    if bind_dashboard_search_results is None:
        return _blocked_payload(
            query=clean_query,
            session_id=clean_session_id,
            provider=clean_provider,
            reason='dashboard_result_binding_unavailable',
            policy=policy,
        )

    dashboard_payload = bind_dashboard_search_results(
        query=clean_query,
        session_id=clean_session_id,
        provider=clean_provider,
        manual_enable_confirmed=True,
        results=limited_results,
        max_visible_results=policy.max_results,
        governance_state={
            'bridge_contract_version': CONTRACT_VERSION,
            'request_context': dict(request_context or {}),
        },
        evidence_basket={
            'evidence_capture_route': 'review_safe_dashboard_query_execution_bridge',
            'runtime_truth_mutated': False,
            'review_required': True,
        },
        provider_health={
            'provider': clean_provider,
            'status': 'available',
            'manual_enable_required': True,
        },
    )

    return {
        'contract_version': CONTRACT_VERSION,
        'status': EXECUTED_STATUS if dashboard_payload.get('status') == RESULTS_READY_STATUS else dashboard_payload.get('status', NO_RESULTS_STATUS),
        'reason': dashboard_payload.get('reason', ''),
        'query': clean_query,
        'session_id': clean_session_id,
        'provider': clean_provider,
        'created_at': _utc_now(),
        'execution': {
            'attempted': True,
            'bounded': True,
            'manual_enable_confirmed': True,
            'provider_env_enabled': _env_enabled(ENV_REAL_SEARCH_PROVIDER),
            'limited_body_env_enabled': _env_enabled(ENV_LIMITED_BODY_GET),
            'raw_result_count': len(raw_results),
            'bounded_result_count': len(limited_results),
        },
        'dashboard_payload': dashboard_payload,
        'policy': policy.to_dict(),
        'governance': {
            'review_required': True,
            'runtime_truth_mutated': False,
            'autonomous_execution': False,
            'automatic_updates': False,
            'fail_closed': True,
        },
        'provider_metadata': metadata,
    }


def bridge_google_smoke_query(*, manual_enable_confirmed: bool = True) -> Dict[str, Any]:
    def _google_executor(**kwargs: Any) -> Dict[str, Any]:
        return {
            'results': [
                {
                    'title': 'Google',
                    'url': 'https://www.google.com',
                    'snippet': 'Google search result smoke test.',
                    'provider': kwargs.get('provider', 'smoke-provider'),
                    'trust_score': 1.0,
                    'result_id': 'google-visible-smoke-result',
                    'evidence_id': 'google-visible-smoke-evidence',
                }
            ],
            'provider_status': 'ok',
        }

    return execute_dashboard_live_search_query(
        query='google',
        session_id='google-smoke-session',
        provider='smoke-provider',
        executor=_google_executor,
        manual_enable_confirmed=manual_enable_confirmed,
        require_provider_env=False,
        require_limited_body_env=False,
        max_results=3,
    )


__all__ = [
    'BLOCKED_STATUS',
    'CONTRACT_VERSION',
    'DashboardQueryExecutionPolicy',
    'ENV_LIMITED_BODY_GET',
    'ENV_REAL_SEARCH_PROVIDER',
    'EXECUTED_STATUS',
    'EXECUTION_FAILED_STATUS',
    'NO_RESULTS_STATUS',
    'RESULTS_READY_STATUS',
    'bridge_google_smoke_query',
    'execute_dashboard_live_search_query',
]
