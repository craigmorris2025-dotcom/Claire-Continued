"""S35 no-network endpoint contract test.

This module validates endpoint contract shape without performing a network call.
"""

from __future__ import annotations

from typing import Any, Dict

from runtime_core.api.guarded_metadata_probe_endpoint import (
    GuardedMetadataProbeRequest,
    get_guarded_metadata_probe_endpoint_candidate,
)


def get_s35_no_network_endpoint_contract_test() -> Dict[str, Any]:
    candidate = get_guarded_metadata_probe_endpoint_candidate()

    sample_validates = True
    validation_error = None
    try:
        GuardedMetadataProbeRequest(
            target_url="https://www.googleapis.com",
            operator_trigger_id="contract_test_only",
            reason="no network contract test",
        )
    except Exception as exc:
        sample_validates = False
        validation_error = str(exc)

    passed = (
        sample_validates
        and candidate.get("router_defined") is True
        and candidate.get("router_registered_by_this_module") is False
    )

    return {
        "version": "v19.89.8-S35R5",
        "status": "contract_test_passed" if passed else "contract_test_failed",
        "contract_test_passed": passed,
        "sample_request_validates": sample_validates,
        "validation_error": validation_error,
        "endpoint_candidate": candidate.get("endpoint"),
        "method": candidate.get("method"),
        "network_request_performed": False,
        "route_registered_by_test": False,
        "response_body_reads": "blocked",
        "browser_execution": "blocked",
        "runtime_truth_mutation": "blocked",
        "autonomous_execution": "blocked",
        "automatic_updates": "blocked",
    }
