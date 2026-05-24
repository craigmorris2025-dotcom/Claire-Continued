from __future__ import annotations

import json


def test_post_ui_response_reference_recovers_search_surface_contracts(tmp_path):
    from runtime_core.proof.post_ui_response_reference import extract_post_ui_response_reference

    (tmp_path / "response_search.json").write_text(
        json.dumps(
            {
                "contract_version": "v18.73.1.operator_dashboard_compat_endpoint_repair",
                "endpoint_status": "ready",
                "status": "search_results_ready",
                "query": "google",
                "manual_enable": True,
                "visible_result_count": 1,
                "result_cards": [{"title": "Google", "url": "https://google.com"}],
                "canonical_paths": ["/api/dashboard/search/live", "/api/dashboard/search/smoke/google"],
                "compatibility_paths": ["/operator/search", "/operator/search/live"],
                "governance": {
                    "review_required": True,
                    "runtime_truth_mutated": False,
                    "autonomous_execution": False,
                    "automatic_updates": False,
                    "uncontrolled_browsing": False,
                    "fail_closed": True,
                    "operator_review_required": True,
                },
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "response_probe.json").write_text(
        json.dumps(
            {
                "contract_version": "v18.72.2.active_launcher_provider_probe_router_repair",
                "status": "operator_probe_not_ready",
                "provider_probe_status": "mounted_guarded",
                "operator_probe_ready": False,
                "manual_enable_required": True,
                "routes": {"provider_probe": "/api/dashboard/search/provider/probe"},
                "governance": {
                    "review_required": True,
                    "runtime_truth_mutated": False,
                    "autonomous_execution": False,
                    "automatic_updates": False,
                    "uncontrolled_browsing": False,
                    "fail_closed": True,
                    "operator_review_required": True,
                },
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "response_capabilities.json").write_text(
        json.dumps(
            {
                "contract_version": "v18.73.1.operator_dashboard_compat_endpoint_repair",
                "status": "capabilities_ready",
                "backend_search_available": True,
                "capabilities": ["search"],
                "governance": {"review_required": True, "fail_closed": True, "runtime_truth_mutated": False},
            }
        ),
        encoding="utf-8",
    )

    payload = extract_post_ui_response_reference(tmp_path)

    assert payload["status"] == "ready"
    assert payload["documents_used_as_runtime_programming"] is False
    assert payload["required_surface_contracts"]["governed_search_response"] is True
    assert payload["required_surface_contracts"]["provider_probe_status"] is True
    assert payload["required_surface_contracts"]["operator_search_capabilities"] is True
    assert payload["required_surface_contracts"]["fail_closed_no_truth_mutation"] is True
    assert any(item["route"] == "/api/dashboard/search/live" for item in payload["recovered_routes"])
