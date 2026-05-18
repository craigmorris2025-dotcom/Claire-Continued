from __future__ import annotations

import importlib


def test_s184_cockpit_action_registry_exists_and_preserves_locks():
    mod = importlib.import_module("claire.api.cockpit_action_registry")
    registry = mod.get_cockpit_action_registry()

    assert registry["version"] == "v19.89.8-S184"
    assert registry["registry_name"] == "cockpit_action_registry"
    locks = registry["authority_model"]
    assert locks["backend_owns_truth"] is True
    assert locks["cockpit_presentation_only"] is True
    assert locks["runtime_truth_write_blocked"] is True
    assert locks["runtime_mutation_blocked"] is True
    assert locks["automatic_updates_blocked"] is True
    assert locks["autonomous_execution_blocked"] is True
    assert locks["manual_promotion_mandatory"] is True
    assert locks["quarantine_mandatory"] is True
    assert locks["continuous_crawling_blocked"] is True


def test_s184_allowed_actions_are_backend_contracts_not_frontend_assumptions():
    mod = importlib.import_module("claire.api.cockpit_action_registry")
    registry = mod.get_cockpit_action_registry()
    ids = set(registry["actions_by_id"])

    required = {
        "inspect_payload_health",
        "inspect_runtime_locks",
        "review_evidence_basket",
        "export_reviewed_package",
        "start_bounded_web_job",
        "inspect_source_lineage",
        "request_mutation_proposal",
        "apply_runtime_mutation",
        "enable_continuous_crawling",
        "enable_automatic_updates",
    }
    assert required.issubset(ids)
    assert registry["actions_by_id"]["start_bounded_web_job"]["requires_quarantine"] is True
    assert registry["actions_by_id"]["request_mutation_proposal"]["state"] == "proposal_only"


def test_s184_unsafe_actions_remain_blocked():
    mod = importlib.import_module("claire.api.cockpit_action_registry")
    registry = mod.get_cockpit_action_registry()

    for action in registry["actions"]:
        if action["mutates_runtime_truth"] or action["triggers_autonomous_execution"]:
            assert action["state"] == "blocked"
            assert action["blocked_reason"]

    mod.assert_registry_safe()
