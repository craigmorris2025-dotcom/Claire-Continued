# v18.53 live search dashboard smoke exports
try:
    from .live_search_dashboard_smoke import (
        assert_dashboard_payload_review_safe,
        build_blocked_dashboard_payload,
        build_live_search_dashboard_payload,
        execute_live_search_dashboard_smoke,
        live_search_dashboard_smoke_enabled,
        normalize_dashboard_query,
    )
except Exception:
    pass

# v18.54 visible query-result verification exports
try:
    from .visible_query_result_verification import (
        VISIBLE_QUERY_RESULT_CONTRACT,
        assert_visible_query_result_review_safe,
        build_visible_query_blocked_payload,
        normalize_visible_query,
        verify_visible_query_result,
        visible_query_result_verification_enabled,
    )
except Exception:
    pass

# v18.55 dashboard search result binding exports
try:
    from .dashboard_search_result_binding import (
        DashboardBoundSearchResult,
        DashboardSearchBindingPolicy,
        bind_dashboard_search_results,
        bind_first_visible_query_result,
        normalize_dashboard_result,
    )
except Exception:
    # Package import must remain fail-closed and must not break unrelated runtime imports.
    pass

# v18.56 dashboard query execution bridge exports
try:
    from .dashboard_search_query_execution_bridge import (
        DashboardQueryExecutionPolicy,
        bridge_google_smoke_query,
        execute_dashboard_live_search_query,
    )
except Exception:
    pass

# v18.57 dashboard search endpoint result contract exports
try:
    from .dashboard_search_endpoint_result_contract import (
        DashboardSearchEndpointPolicy,
        build_dashboard_search_endpoint_response,
        create_dashboard_search_router,
        execute_dashboard_search_endpoint_request,
        google_endpoint_smoke_response,
    )
except Exception:
    pass

# v18.58 dashboard live search route mount adapter exports
try:
    from .dashboard_live_search_route_mount_adapter import (
        DashboardLiveSearchRouteMountPolicy,
        create_dashboard_live_search_route_mount_adapter,
        inspect_dashboard_live_search_route_mount,
        mount_dashboard_live_search_routes,
    )
except Exception:
    pass

# v18.59 dashboard live search ui fetch binding exports
try:
    from .dashboard_live_search_ui_fetch_binding import (
        DashboardLiveSearchUIFetchPolicy,
        build_dashboard_live_search_fetch_config,
        build_dashboard_live_search_javascript,
        build_dashboard_live_search_request_payload,
        build_review_safe_result_card_html,
    )
except Exception:
    pass

# v18.60 dashboard search bar html integration gate exports
try:
    from .dashboard_search_bar_html_integration_gate import (
        DashboardSearchBarHTMLIntegrationPolicy,
        apply_governed_live_search_html_integration,
        build_governed_live_search_html_block,
        build_governed_live_search_script_tag,
        integrate_governed_live_search_into_html_text,
    )
except Exception:
    pass

# v18.61 mounted live search endpoint smoke test exports
try:
    from .mounted_live_search_endpoint_smoke_test import (
        MountedLiveSearchEndpointSmokePolicy,
        build_mounted_live_search_smoke_app,
        run_live_post_blocking_smoke,
        run_mounted_google_endpoint_smoke,
    )
except Exception:
    pass

# v18.62 live search active app mount gate exports
try:
    from .live_search_active_app_mount_gate import (
        LiveSearchActiveAppMountPolicy,
        build_governed_live_search_router_for_active_app,
        inspect_active_app_candidates,
        mount_governed_live_search_into_app,
        mount_into_discovered_active_app,
    )
except Exception:
    pass

# v18.63 active app mounted route verification exports
try:
    from .active_app_mounted_route_verification import (
        ActiveAppMountedRouteVerificationPolicy,
        create_verification_fastapi_app,
        inspect_app_route_table,
        mount_routes_for_verification,
        run_active_app_mounted_route_verification,
    )
except Exception:
    pass

# v18.64 dashboard to endpoint fetch proof exports
try:
    from .dashboard_to_endpoint_fetch_proof import (
        DashboardToEndpointFetchProofPolicy,
        build_dashboard_fetch_request_payload,
        execute_fetch_payload_against_endpoint_contract,
        google_fetch_proof_executor,
        run_dashboard_to_endpoint_google_fetch_proof,
        run_dashboard_to_endpoint_manual_enable_block_proof,
    )
except Exception:
    pass

# v18.65 first active dashboard google result proof exports
try:
    from .first_active_dashboard_google_result_proof import (
        FirstActiveDashboardGoogleResultProofPolicy,
        build_first_active_dashboard_google_operator_checklist,
        inspect_active_dashboard_google_search_surface,
        run_first_active_dashboard_google_result_proof,
    )
except Exception:
    pass

# v18.66 accelerated governed live web activation pack exports
try:
    from .accelerated_governed_live_web_activation_pack import (
        AcceleratedGovernedLiveWebActivationPolicy,
        build_accelerated_web_activation_operator_summary,
        deterministic_google_activation_executor,
        inspect_activation_environment,
        inspect_activation_modules,
        inspect_controlled_provider_activation_readiness,
        inspect_dashboard_activation_surface,
        run_accelerated_governed_live_web_activation_pack,
        run_dashboard_google_activation_proof,
        run_endpoint_google_activation_proof,
        run_mounted_route_activation_proof,
    )
except Exception:
    pass

# v18.67 real controlled provider result proof exports
try:
    from .real_controlled_provider_result_proof import (
        RealControlledProviderResultProofPolicy,
        deterministic_google_provider_probe,
        discover_real_provider_adapter,
        inspect_real_provider_env_flags,
        normalize_provider_response_to_dashboard_endpoint,
        run_controlled_provider_result_proof,
        run_deterministic_controlled_provider_google_proof,
        run_operator_real_provider_probe_if_enabled,
    )
except Exception:
    pass

# v18.68 real provider operator probe route exports
try:
    from .real_provider_operator_probe_route import (
        RealProviderOperatorProbeRoutePolicy,
        build_operator_probe_request_payload,
        build_operator_probe_smoke_app,
        build_operator_provider_probe_status,
        create_real_provider_operator_probe_router,
        execute_operator_provider_probe_request,
        run_operator_provider_google_probe_proof,
    )
except Exception:
    pass

# v18.69 operator probe active app mount exports
try:
    from .operator_probe_active_app_mount import (
        OperatorProbeActiveAppMountPolicy,
        build_operator_probe_mount_smoke_app,
        build_operator_probe_router_for_active_app,
        inspect_operator_probe_route_table,
        mount_operator_probe_routes_into_app,
    )
except Exception:
    pass

# v18.70 consolidated web activation packs exports
try:
    from .consolidated_web_activation_packs import (
        ConsolidatedWebActivationPolicy,
        inspect_provider_probe_ui_binding,
        mount_combined_web_activation_routes,
        run_combined_web_activation_smoke_app,
        run_web_activation_checkpoint,
    )
except Exception:
    pass

# v18.71 active app final web activation mount verification exports
try:
    from .active_app_final_web_activation_mount_verification import (
        ActiveAppFinalWebActivationMountPolicy,
        inspect_active_app_candidates,
        mount_final_web_activation_routes_into_app,
        run_active_app_final_web_activation_mount_verification,
        run_final_web_activation_operator_report,
        verify_app_has_final_web_activation_routes,
        verify_final_web_activation_endpoints,
    )
except Exception:
    pass

# v18.73.2 dashboard search/provider probe separation exports
try:
    from .dashboard_search_provider_probe_separation_repair import (
        DashboardSearchSeparationPolicy,
        build_dashboard_search_separation_report,
        inspect_dashboard_search_provider_probe_separation,
    )
except Exception:
    pass
