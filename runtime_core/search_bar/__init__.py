"""Claire search bar governance package."""

# v18.06 governed web execution simulation audit exports
try:
    from .governed_web_execution_simulation_audit import (
        CONFIRMATION_TEXT,
        GovernedWebExecutionSimulationAuditTrail,
        assert_non_executing_audit_event,
        build_simulation_audit_event,
    )
except Exception:
    pass

# v18.07 governed web simulation result viewer exports
try:
    from .governed_web_simulation_result_viewer import (
        assert_viewer_card_is_non_executing,
        build_simulation_result_card,
        build_simulation_result_view,
    )
except Exception:
    pass

# v18.08 governed web simulation dashboard api exports
try:
    from .governed_web_simulation_dashboard_api import (
        assert_dashboard_api_response_non_executing,
        build_dashboard_api_response,
    )
except Exception:
    pass

# v18.09 governed web simulation dashboard route adapter exports
try:
    from .governed_web_simulation_dashboard_route_adapter import (
        DEFAULT_ROUTE_PATH,
        assert_route_response_non_executing,
        describe_governed_web_simulation_dashboard_route,
        handle_governed_web_simulation_dashboard_route,
    )
except Exception:
    pass

# v18.10 governed web simulation fastapi route exports
try:
    from .governed_web_simulation_fastapi_route import (
        assert_fastapi_route_response_non_executing,
        create_governed_web_simulation_router,
        describe_fastapi_route_registration,
        governed_web_simulation_dashboard_endpoint,
        register_governed_web_simulation_route,
    )
except Exception:
    pass

# v18.11 governed web simulation route mount verifier exports
try:
    from .governed_web_simulation_route_mount_verifier import (
        RouteMountProbeApp,
        assert_mount_verification_non_executing,
        describe_route_mount_verifier,
        verify_governed_web_simulation_route_mount,
    )
except Exception:
    pass

# v18.11.1 governed web simulation route mount verifier repair exports
try:
    from .governed_web_simulation_route_mount_verifier import (
        RouteMountProbeApp,
        assert_mount_verification_non_executing,
        describe_route_mount_verifier,
        verify_governed_web_simulation_route_mount,
    )
except Exception:
    pass

# v18.12 governed web provider readiness exports
try:
    from .governed_web_provider_readiness import (
        REQUIRED_PROVIDER_GATES,
        assert_provider_readiness_non_executing,
        describe_provider_readiness_contract,
        evaluate_provider_readiness,
    )
except Exception:
    pass

# v18.13 governed web allowlist registry exports
try:
    from .governed_web_allowlist_registry import (
        DEFAULT_TRUST_LEVEL,
        GovernedWebAllowlistRegistry,
        assert_allowlist_registry_non_executing,
        describe_allowlist_registry_contract,
    )
except Exception:
    pass

# v18.14 governed web rate limit policy exports
try:
    from .governed_web_rate_limit_policy import (
        DEFAULT_COOLDOWN_SECONDS,
        DEFAULT_REQUESTS_PER_HOUR,
        DEFAULT_REQUESTS_PER_MINUTE,
        assert_rate_limit_policy_non_executing,
        build_rate_limit_policy,
        describe_rate_limit_policy_contract,
    )
except Exception:
    pass

# v18.15 governed web source trust policy exports
try:
    from .governed_web_source_trust_policy import (
        TRUST_TIERS,
        assert_source_trust_policy_non_executing,
        assess_source_trust,
        describe_source_trust_policy_contract,
    )
except Exception:
    pass

# v18.16 governed web read only dry run gate exports
try:
    from .governed_web_read_only_dry_run_gate import (
        REQUIRED_CONFIRMATION_TEXT,
        assert_read_only_dry_run_gate_non_executing,
        describe_read_only_dry_run_gate,
        evaluate_read_only_dry_run_eligibility,
    )
except Exception:
    pass

# v18.17 governed web dry run simulator exports
try:
    from .governed_web_read_only_dry_run_simulator import (
        assert_dry_run_simulator_non_executing,
        build_demo_request,
        describe_dry_run_simulator,
        simulate_governed_read_only_web_request,
    )
except Exception:
    pass

# v18.17.1 governed web dry run simulator repair exports
try:
    from .governed_web_read_only_dry_run_simulator import (
        assert_dry_run_simulator_non_executing,
        build_demo_request,
        describe_dry_run_simulator,
        simulate_governed_read_only_web_request,
    )
except Exception:
    pass

# v18.18 governed read-only live web adapter boundary exports
try:
    from .governed_web_read_only_live_adapter import (
        GovernedReadOnlyLiveWebAdapter,
        assert_live_adapter_boundary_non_executing,
        build_live_adapter_demo_request,
        describe_live_adapter_boundary,
    )
except Exception:
    pass
