"""Router integration adapter contract.

S34R8 defines a safe integration adapter boundary. It does not include the router
into the app and does not mutate app.py.
"""

from __future__ import annotations

from typing import Any, Dict

from runtime_core.api.guarded_metadata_probe_endpoint import router as guarded_metadata_probe_router


def get_guarded_metadata_probe_router_for_safe_include():
    """Return router object for a future explicitly-approved include operation.

    This function is intentionally inert unless called by a future installer or
    router module after allowlist/router proof passes.
    """
    return guarded_metadata_probe_router


def get_router_integration_adapter_contract() -> Dict[str, Any]:
    return {
        "version": "v19.89.8-S34R8",
        "status": "router_integration_adapter_defined",
        "adapter_function": "get_guarded_metadata_probe_router_for_safe_include",
        "router_available": guarded_metadata_probe_router is not None,
        "router_auto_registered": False,
        "app_py_patch_allowed": False,
        "safe_include_requires": [
            "explicit safe mounted router approval",
            "non-mutating registration plan allowed",
            "rollback snapshot",
            "compile changed modules only",
            "payload health check after install",
        ],
        "endpoint": "/api/governed-web/metadata-probe",
        "network_request": "blocked",
        "response_body_reads": "blocked",
        "browser_execution": "blocked",
        "runtime_truth_mutation": "blocked",
        "autonomous_execution": "blocked",
        "automatic_updates": "blocked",
    }
