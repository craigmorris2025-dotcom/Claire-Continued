from __future__ import annotations
from typing import Any

def build_governance() -> dict[str, Any]:
    return {
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "fail_closed_governance": True,
        "read_only": True,
        "non_invasive": True,
        "runtime_authority": False,
        "runtime_truth_mutation": False,
        "runtime_mutation": False,
        "mutation_authority": False,
        "autonomous_execution": False,
        "automatic_updates": False,
        "auto_update_authority": False,
        "browser_execution": False,
        "javascript_execution": False,
        "live_crawling": False,
        "continuous_live_crawling": False,
        "live_web_execution_enabled": False,
        "evidence_quarantine_required": True,
        "evidence_quarantine_mandatory": True,
        "manual_promotion_required": True,
        "manual_promotion_mandatory": True,
        "promotion_authority": False,
        "app_patch_required": False,
        "app_py_patch_required": False,
        "direct_app_patch": False,
        "uncontrolled_app_patching": False,
        "mutation_routes_exposed": False,
        "auto_update_routes_exposed": False,
        "authority_exposed": False,
    }

def flatten_governance(payload: dict[str, Any]) -> dict[str, Any]:
    governance = build_governance()
    merged = dict(payload)
    merged.update(governance)
    merged["governance"] = governance
    return merged

# BEGIN CLAIRE_S43_FIX7_GOVERNANCE_COMPAT
def build_authority_block() -> dict:
    return {
        "runtime_authority": "blocked",
        "runtime_truth_mutation": "blocked",
        "mutation_authority": "blocked",
        "autonomous_execution": "blocked",
        "automatic_updates": "blocked",
        "browser_execution": "blocked",
        "javascript_execution": "blocked",
        "live_crawling": "blocked",
        "manual_promotion": "required",
        "evidence_quarantine": "mandatory",
    }


def build_compat_governance() -> dict:
    base = build_governance()
    base.update({
        "runtime_truth_mutation_allowed": False,
        "runtime_mutation_allowed": False,
        "mutation_allowed": False,
        "autonomous_agent_execution_enabled": False,
        "autonomous_execution_enabled": False,
        "automatic_updates_enabled": False,
        "browser_execution_enabled": False,
        "javascript_execution_enabled": False,
        "network_request_performed": False,
        "network_request_performed_during_install": False,
    })
    return base


def flatten_compat(payload: dict) -> dict:
    merged = flatten_governance(payload)
    merged.update(build_compat_governance())
    merged["authority"] = build_authority_block()
    return merged
# END CLAIRE_S43_FIX7_GOVERNANCE_COMPAT

# BEGIN CLAIRE_S43_FIX8_GOVERNANCE_COMPAT
def build_authority_block() -> dict:
    return {
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "fail_closed_governance": True,
        "runtime_authority": "blocked",
        "runtime_truth_mutation": "blocked",
        "mutation_authority": "blocked",
        "browser_execution_authority": "blocked",
        "javascript_execution_authority": "blocked",
        "autonomous_execution_authority": "blocked",
        "automatic_update_authority": "blocked",
        "live_web_execution_authority": "blocked",
        "live_crawling_authority": "blocked",
        "manual_promotion": "required",
        "evidence_quarantine": "mandatory",
    }


def build_compat_governance() -> dict:
    base = build_governance()
    base.update({
        "runtime_truth_mutation_allowed": False,
        "runtime_mutation_allowed": False,
        "mutation_allowed": False,
        "automatic_update_allowed": False,
        "autonomous_agent_execution_enabled": False,
        "autonomous_execution_enabled": False,
        "automatic_updates_enabled": False,
        "runtime_truth_mutation_enabled": False,
        "runtime_mutation_enabled": False,
        "browser_execution_enabled": False,
        "javascript_execution_enabled": False,
        "network_request_performed": False,
        "network_request_performed_during_install": False,
        "body_read_performed": False,
    })
    return base


def flatten_compat(payload: dict) -> dict:
    merged = flatten_governance(payload)
    merged.update(build_compat_governance())
    merged["authority"] = build_authority_block()
    return merged
# END CLAIRE_S43_FIX8_GOVERNANCE_COMPAT

# BEGIN CLAIRE_S43_FIX9_GOVERNANCE_COMPAT
def build_authority_block() -> dict:
    return {
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "fail_closed_governance": True,
        "runtime_authority": "blocked",
        "runtime_truth_mutation": "blocked",
        "mutation_authority": "blocked",
        "browser_execution_authority": "blocked",
        "javascript_execution_authority": "blocked",
        "autonomous_execution_authority": "blocked",
        "automatic_update_authority": "blocked",
        "live_web_execution_authority": "blocked",
        "live_crawling_authority": "blocked",
        "operator_mutation_enabled": False,
        "runtime_mutation_enabled": False,
        "runtime_truth_mutation_enabled": False,
        "autonomous_execution_expansion": False,
        "automatic_update_expansion": False,
        "browser_execution_expansion": False,
        "javascript_execution_expansion": False,
        "manual_promotion": "required",
        "evidence_quarantine": "mandatory",
    }


def build_compat_governance() -> dict:
    base = build_governance()
    base.update({
        "available": True,
        "runtime_truth_mutation_allowed": False,
        "runtime_mutation_allowed": False,
        "mutation_allowed": False,
        "automatic_update_allowed": False,
        "autonomous_agent_execution_enabled": False,
        "autonomous_execution_enabled": False,
        "automatic_updates_enabled": False,
        "runtime_truth_mutation_enabled": False,
        "runtime_mutation_enabled": False,
        "operator_mutation_enabled": False,
        "browser_execution_enabled": False,
        "javascript_execution_enabled": False,
        "network_request_performed": False,
        "network_request_performed_during_install": False,
        "body_read_performed": False,
        "body_scraping_performed": False,
        "endpoint_registered_with_app": False,
        "live_server_required": False,
    })
    return base


def flatten_compat(payload: dict) -> dict:
    merged = flatten_governance(payload)
    merged.update(build_compat_governance())
    merged["authority"] = build_authority_block()
    return merged
# END CLAIRE_S43_FIX9_GOVERNANCE_COMPAT

# BEGIN CLAIRE_S43_FIX10_GOVERNANCE_COMPAT
def build_quarantine_block() -> dict:
    return {
        "runtime_truth_write_allowed": False,
        "manual_promotion_required": True,
        "evidence_quarantine_required": True,
        "evidence_quarantine_mandatory": True,
        "promotion_authority": False,
    }


def build_authority_block() -> dict:
    return {
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "fail_closed_governance": True,
        "runtime_authority": "blocked",
        "runtime_truth_mutation": "blocked",
        "mutation_authority": "blocked",
        "browser_execution_authority": "blocked",
        "javascript_execution_authority": "blocked",
        "autonomous_execution_authority": "blocked",
        "automatic_update_authority": "blocked",
        "live_web_execution_authority": "blocked",
        "live_crawling_authority": "blocked",
        "operator_mutation_enabled": False,
        "runtime_mutation_enabled": False,
        "runtime_truth_mutation_enabled": False,
        "autonomous_execution_expansion": False,
        "automatic_update_expansion": False,
        "browser_execution_expansion": False,
        "javascript_execution_expansion": False,
        "manual_promotion": "required",
        "evidence_quarantine": "mandatory",
    }


def build_compat_governance() -> dict:
    base = build_governance()
    base.update({
        "available": True,
        "runtime_truth_mutation_allowed": False,
        "runtime_mutation_allowed": False,
        "mutation_allowed": False,
        "automatic_update_allowed": False,
        "autonomous_agent_execution_enabled": False,
        "autonomous_execution_enabled": False,
        "automatic_updates_enabled": False,
        "runtime_truth_mutation_enabled": False,
        "runtime_mutation_enabled": False,
        "operator_mutation_enabled": False,
        "browser_execution_enabled": False,
        "javascript_execution_enabled": False,
        "network_request_performed": False,
        "network_request_performed_during_install": False,
        "body_read_performed": False,
        "body_scraping_performed": False,
        "endpoint_registered_with_app": False,
        "live_server_required": False,
        "response_mode": "read_only_artifact",
    })
    return base


def flatten_compat(payload: dict) -> dict:
    merged = flatten_governance(payload)
    merged.update(build_compat_governance())
    merged["authority"] = build_authority_block()
    merged["quarantine"] = build_quarantine_block()
    return merged
# END CLAIRE_S43_FIX10_GOVERNANCE_COMPAT
