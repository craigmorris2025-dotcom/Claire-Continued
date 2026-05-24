
# Claire Syntalion v18.58
# Dashboard Live Search Route Mount Adapter
#
# This module provides an explicit, governed mount adapter for the dashboard
# live-search endpoint router. It never auto-mounts routes on import.

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Mapping, Optional

try:
    from .dashboard_search_endpoint_result_contract import create_dashboard_search_router
except Exception:  # pragma: no cover - fail closed if prior layer is unavailable
    create_dashboard_search_router = None


CONTRACT_VERSION = 'v18.58.dashboard_live_search_route_mount_adapter'

MOUNT_READY = 'mount_ready'
MOUNT_BLOCKED = 'mount_blocked'
MOUNTED = 'mounted'
MOUNT_FAILED = 'mount_failed'


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def _string(value: Any, default: str = '') -> str:
    if value is None:
        return default
    if isinstance(value, str):
        value = value.strip()
        return value if value else default
    return str(value).strip() or default


@dataclass(frozen=True)
class DashboardLiveSearchRouteMountPolicy:
    explicit_enable_required: bool = True
    auto_mount_on_import: bool = False
    route_mount_mutation_allowed_by_default: bool = False
    manual_enable_required: bool = True
    review_required: bool = True
    fail_closed: bool = True
    immutable_runtime_truth: bool = True
    runtime_truth_mutated: bool = False
    autonomous_execution_enabled: bool = False
    automatic_updates_enabled: bool = False
    router_factory_only_until_enabled: bool = True
    expected_prefix: str = '/api/dashboard/search'

    def to_dict(self) -> Dict[str, Any]:
        return {
            'explicit_enable_required': self.explicit_enable_required,
            'auto_mount_on_import': self.auto_mount_on_import,
            'route_mount_mutation_allowed_by_default': self.route_mount_mutation_allowed_by_default,
            'manual_enable_required': self.manual_enable_required,
            'review_required': self.review_required,
            'fail_closed': self.fail_closed,
            'immutable_runtime_truth': self.immutable_runtime_truth,
            'runtime_truth_mutated': self.runtime_truth_mutated,
            'autonomous_execution_enabled': self.autonomous_execution_enabled,
            'automatic_updates_enabled': self.automatic_updates_enabled,
            'router_factory_only_until_enabled': self.router_factory_only_until_enabled,
            'expected_prefix': self.expected_prefix,
        }


def _governance(extra: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    payload = {
        'review_required': True,
        'runtime_truth_mutated': False,
        'autonomous_execution': False,
        'automatic_updates': False,
        'fail_closed': True,
        'route_mount_is_explicit_only': True,
    }
    if extra:
        payload.update(dict(extra))
    return payload


def inspect_dashboard_live_search_route_mount(
    *,
    explicit_enable: bool = False,
    prefix: str = '/api/dashboard/search',
) -> Dict[str, Any]:
    clean_prefix = _string(prefix, '/api/dashboard/search')
    policy = DashboardLiveSearchRouteMountPolicy(expected_prefix=clean_prefix)
    router_factory_available = create_dashboard_search_router is not None

    if not explicit_enable:
        status = MOUNT_BLOCKED
        reason = 'explicit_route_mount_enable_required'
    elif not router_factory_available:
        status = MOUNT_BLOCKED
        reason = 'dashboard_search_router_factory_unavailable'
    else:
        status = MOUNT_READY
        reason = ''

    return {
        'contract_version': CONTRACT_VERSION,
        'status': status,
        'reason': reason,
        'created_at': _utc_now(),
        'prefix': clean_prefix,
        'router_factory_available': router_factory_available,
        'mount_attempted': False,
        'mounted': False,
        'routes': [
            {'method': 'POST', 'path': clean_prefix + '/live'},
            {'method': 'GET', 'path': clean_prefix + '/smoke/google'},
        ],
        'policy': policy.to_dict(),
        'governance': _governance({'explicit_enable': bool(explicit_enable)}),
    }


def create_dashboard_live_search_route_mount_adapter(
    *,
    explicit_enable: bool = False,
    prefix: str = '/api/dashboard/search',
) -> Dict[str, Any]:
    readiness = inspect_dashboard_live_search_route_mount(
        explicit_enable=explicit_enable,
        prefix=prefix,
    )
    if readiness['status'] != MOUNT_READY:
        return {
            **readiness,
            'router': None,
            'adapter_status': readiness['status'],
        }

    try:
        router = create_dashboard_search_router()
    except Exception as exc:
        return {
            **readiness,
            'status': MOUNT_FAILED,
            'adapter_status': MOUNT_FAILED,
            'reason': 'router_factory_exception',
            'router': None,
            'error_type': type(exc).__name__,
            'governance': _governance({'explicit_enable': bool(explicit_enable)}),
        }

    return {
        **readiness,
        'status': MOUNT_READY,
        'adapter_status': MOUNT_READY,
        'reason': '',
        'router': router,
        'governance': _governance({'explicit_enable': True}),
    }


def mount_dashboard_live_search_routes(
    app: Any,
    *,
    explicit_enable: bool = False,
    prefix: str = '/api/dashboard/search',
) -> Dict[str, Any]:
    policy = DashboardLiveSearchRouteMountPolicy(expected_prefix=_string(prefix, '/api/dashboard/search'))

    if not explicit_enable:
        return {
            'contract_version': CONTRACT_VERSION,
            'status': MOUNT_BLOCKED,
            'reason': 'explicit_route_mount_enable_required',
            'created_at': _utc_now(),
            'prefix': policy.expected_prefix,
            'mount_attempted': False,
            'mounted': False,
            'policy': policy.to_dict(),
            'governance': _governance({'explicit_enable': False}),
        }

    if app is None or not hasattr(app, 'include_router'):
        return {
            'contract_version': CONTRACT_VERSION,
            'status': MOUNT_BLOCKED,
            'reason': 'fastapi_app_with_include_router_required',
            'created_at': _utc_now(),
            'prefix': policy.expected_prefix,
            'mount_attempted': False,
            'mounted': False,
            'policy': policy.to_dict(),
            'governance': _governance({'explicit_enable': True}),
        }

    adapter = create_dashboard_live_search_route_mount_adapter(
        explicit_enable=True,
        prefix=policy.expected_prefix,
    )
    router = adapter.get('router')
    if router is None:
        return {
            **{k: v for k, v in adapter.items() if k != 'router'},
            'mount_attempted': False,
            'mounted': False,
            'policy': policy.to_dict(),
            'governance': _governance({'explicit_enable': True}),
        }

    try:
        app.include_router(router)
    except Exception as exc:
        return {
            'contract_version': CONTRACT_VERSION,
            'status': MOUNT_FAILED,
            'reason': 'include_router_exception',
            'created_at': _utc_now(),
            'prefix': policy.expected_prefix,
            'mount_attempted': True,
            'mounted': False,
            'error_type': type(exc).__name__,
            'policy': policy.to_dict(),
            'governance': _governance({'explicit_enable': True}),
        }

    return {
        'contract_version': CONTRACT_VERSION,
        'status': MOUNTED,
        'reason': '',
        'created_at': _utc_now(),
        'prefix': policy.expected_prefix,
        'mount_attempted': True,
        'mounted': True,
        'routes': [
            {'method': 'POST', 'path': policy.expected_prefix + '/live'},
            {'method': 'GET', 'path': policy.expected_prefix + '/smoke/google'},
        ],
        'policy': policy.to_dict(),
        'governance': _governance({'explicit_enable': True}),
    }


__all__ = [
    'CONTRACT_VERSION',
    'DashboardLiveSearchRouteMountPolicy',
    'MOUNT_BLOCKED',
    'MOUNT_FAILED',
    'MOUNT_READY',
    'MOUNTED',
    'create_dashboard_live_search_route_mount_adapter',
    'inspect_dashboard_live_search_route_mount',
    'mount_dashboard_live_search_routes',
]
