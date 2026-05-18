
# Claire Syntalion v18.57
# Dashboard Search Endpoint Result Return Contract
#
# This module converts governed live-search bridge output into a stable
# endpoint/dashboard response shape. It does not mutate app routes by itself.
# It provides an optional router factory for later explicit mounting.

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Mapping, Optional
import uuid

try:
    from .dashboard_search_query_execution_bridge import (
        execute_dashboard_live_search_query,
        bridge_google_smoke_query,
    )
except Exception:  # pragma: no cover - fail-closed fallback for damaged local installs
    execute_dashboard_live_search_query = None
    bridge_google_smoke_query = None


CONTRACT_VERSION = 'v18.57.dashboard_search_endpoint_result_return_contract'

ENDPOINT_READY = 'endpoint_response_ready'
ENDPOINT_BLOCKED = 'endpoint_blocked'
ENDPOINT_ERROR = 'endpoint_error'


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


def _new_session_id() -> str:
    return 'dashboard-search-' + uuid.uuid4().hex[:12]


@dataclass(frozen=True)
class DashboardSearchEndpointPolicy:
    manual_enable_required: bool = True
    review_required: bool = True
    fail_closed: bool = True
    immutable_runtime_truth: bool = True
    runtime_truth_mutated: bool = False
    autonomous_execution_enabled: bool = False
    automatic_updates_enabled: bool = False
    route_mount_required: bool = False
    router_factory_only: bool = True
    max_results: int = 10

    def to_dict(self) -> Dict[str, Any]:
        return {
            'manual_enable_required': self.manual_enable_required,
            'review_required': self.review_required,
            'fail_closed': self.fail_closed,
            'immutable_runtime_truth': self.immutable_runtime_truth,
            'runtime_truth_mutated': self.runtime_truth_mutated,
            'autonomous_execution_enabled': self.autonomous_execution_enabled,
            'automatic_updates_enabled': self.automatic_updates_enabled,
            'route_mount_required': self.route_mount_required,
            'router_factory_only': self.router_factory_only,
            'max_results': self.max_results,
        }


def _http_status_for_bridge(bridge_payload: Mapping[str, Any]) -> int:
    status = _string(bridge_payload.get('status'))
    reason = _string(bridge_payload.get('reason'))

    if status in {'executed', 'results_ready', 'no_results'}:
        return 200
    if reason in {'empty_query', 'manual_enable_not_confirmed'}:
        return 400
    if reason in {'real_search_provider_env_not_enabled', 'limited_body_get_env_not_enabled', 'no_executor_available'}:
        return 423
    if status == 'execution_failed':
        return 502
    return 409


def _endpoint_status_for_bridge(bridge_payload: Mapping[str, Any]) -> str:
    status = _string(bridge_payload.get('status'))
    if status in {'executed', 'results_ready', 'no_results'}:
        return ENDPOINT_READY
    if status in {'blocked'}:
        return ENDPOINT_BLOCKED
    return ENDPOINT_ERROR


def build_dashboard_search_endpoint_response(
    bridge_payload: Mapping[str, Any],
    *,
    endpoint: str = '/api/dashboard/search/live',
    request_id: str = '',
    policy: Optional[DashboardSearchEndpointPolicy] = None,
) -> Dict[str, Any]:
    policy = policy or DashboardSearchEndpointPolicy()
    dashboard_payload = bridge_payload.get('dashboard_payload') if isinstance(bridge_payload, Mapping) else None
    if not isinstance(dashboard_payload, Mapping):
        dashboard_payload = {
            'status': 'blocked',
            'reason': 'missing_dashboard_payload',
            'results': [],
            'visible_result_count': 0,
            'dashboard_render': {
                'search_bar_bound': True,
                'results_panel_state': 'blocked',
            },
        }

    results = dashboard_payload.get('results')
    if not isinstance(results, list):
        results = []

    http_status = _http_status_for_bridge(bridge_payload)
    endpoint_status = _endpoint_status_for_bridge(bridge_payload)

    response = {
        'contract_version': CONTRACT_VERSION,
        'endpoint_status': endpoint_status,
        'http_status': http_status,
        'endpoint': endpoint,
        'request_id': _string(request_id, 'endpoint-' + uuid.uuid4().hex[:10]),
        'created_at': _utc_now(),
        'query': _string(bridge_payload.get('query')),
        'session_id': _string(bridge_payload.get('session_id')),
        'provider': _string(bridge_payload.get('provider'), 'unknown'),
        'reason': _string(bridge_payload.get('reason')),
        'result_cards': results,
        'visible_result_count': int(dashboard_payload.get('visible_result_count') or len(results)),
        'dashboard_payload': dict(dashboard_payload),
        'bridge_payload': dict(bridge_payload),
        'dashboard_render': dict(dashboard_payload.get('dashboard_render') or {}),
        'policy': policy.to_dict(),
        'governance': {
            'review_required': True,
            'runtime_truth_mutated': False,
            'autonomous_execution': False,
            'automatic_updates': False,
            'fail_closed': True,
            'endpoint_return_only': True,
        },
    }
    return response


def execute_dashboard_search_endpoint_request(
    *,
    query: str,
    session_id: str = '',
    provider: str = 'governed-provider',
    executor: Optional[Callable[..., Any]] = None,
    manual_enable_confirmed: bool = False,
    require_provider_env: bool = True,
    require_limited_body_env: bool = True,
    max_results: int = 10,
    request_context: Optional[Mapping[str, Any]] = None,
    endpoint: str = '/api/dashboard/search/live',
    request_id: str = '',
) -> Dict[str, Any]:
    policy = DashboardSearchEndpointPolicy(max_results=max(1, int(max_results or 10)))

    if execute_dashboard_live_search_query is None:
        bridge_payload = {
            'status': 'blocked',
            'reason': 'dashboard_query_execution_bridge_unavailable',
            'query': _string(query),
            'session_id': _string(session_id, _new_session_id()),
            'provider': _string(provider, 'governed-provider'),
            'dashboard_payload': {
                'status': 'blocked',
                'reason': 'dashboard_query_execution_bridge_unavailable',
                'results': [],
                'visible_result_count': 0,
            },
            'governance': {
                'runtime_truth_mutated': False,
                'autonomous_execution': False,
                'automatic_updates': False,
            },
        }
    else:
        bridge_payload = execute_dashboard_live_search_query(
            query=query,
            session_id=_string(session_id, _new_session_id()),
            provider=provider,
            executor=executor,
            manual_enable_confirmed=manual_enable_confirmed,
            require_provider_env=require_provider_env,
            require_limited_body_env=require_limited_body_env,
            max_results=max_results,
            request_context=request_context,
        )

    return build_dashboard_search_endpoint_response(
        bridge_payload,
        endpoint=endpoint,
        request_id=request_id,
        policy=policy,
    )


def google_endpoint_smoke_response() -> Dict[str, Any]:
    if bridge_google_smoke_query is None:
        return execute_dashboard_search_endpoint_request(
            query='google',
            manual_enable_confirmed=False,
            require_provider_env=False,
            require_limited_body_env=False,
            request_id='google-endpoint-smoke-unavailable',
        )
    bridge_payload = bridge_google_smoke_query(manual_enable_confirmed=True)
    return build_dashboard_search_endpoint_response(
        bridge_payload,
        endpoint='/api/dashboard/search/live',
        request_id='google-endpoint-smoke',
        policy=DashboardSearchEndpointPolicy(max_results=3),
    )


def create_dashboard_search_router() -> Any:
    try:
        from fastapi import APIRouter
        from pydantic import BaseModel
    except Exception as exc:  # pragma: no cover
        raise RuntimeError('fastapi_router_unavailable') from exc

    class DashboardSearchRequest(BaseModel):
        query: str
        session_id: str = ''
        provider: str = 'governed-provider'
        manual_enable_confirmed: bool = False
        require_provider_env: bool = True
        require_limited_body_env: bool = True
        max_results: int = 10

    router = APIRouter(prefix='/api/dashboard/search', tags=['governed-dashboard-search'])

    @router.post('/live')
    def dashboard_live_search(request: DashboardSearchRequest) -> Dict[str, Any]:
        return execute_dashboard_search_endpoint_request(
            query=request.query,
            session_id=request.session_id,
            provider=request.provider,
            executor=None,
            manual_enable_confirmed=request.manual_enable_confirmed,
            require_provider_env=request.require_provider_env,
            require_limited_body_env=request.require_limited_body_env,
            max_results=request.max_results,
            request_context={'route': '/api/dashboard/search/live'},
        )

    @router.get('/smoke/google')
    def dashboard_google_smoke() -> Dict[str, Any]:
        return google_endpoint_smoke_response()

    return router


__all__ = [
    'CONTRACT_VERSION',
    'DashboardSearchEndpointPolicy',
    'ENDPOINT_BLOCKED',
    'ENDPOINT_ERROR',
    'ENDPOINT_READY',
    'build_dashboard_search_endpoint_response',
    'create_dashboard_search_router',
    'execute_dashboard_search_endpoint_request',
    'google_endpoint_smoke_response',
]
