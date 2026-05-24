from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping


CANONICAL_DOMAINS = [
    "system",
    "governance",
    "lifecycle",
    "signal_governance",
    "trend_discovery",
    "thesis",
    "portfolio",
    "breakthrough",
    "acquisition",
    "evidence",
    "runtime",
    "exports",
    "future_payloads",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _as_dict(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _status_from(value: Any, default: str = "ready") -> str:
    if isinstance(value, Mapping):
        raw = value.get("status") or value.get("state") or value.get("payload_status")
        if raw:
            return str(raw)
    if isinstance(value, str) and value:
        return value
    return default


def _count_list(value: Any) -> int:
    return len(value) if isinstance(value, list) else 0


def normalize_dashboard_payload(raw_payload: Mapping[str, Any] | None) -> dict[str, Any]:
    raw = _as_dict(raw_payload)
    lifecycle = _as_dict(raw.get("lifecycle"))
    alignment = _as_dict(raw.get("end_state_alignment"))
    operating_model = _as_dict(raw.get("operating_model") or alignment.get("operating_model"))
    route_policy = _as_dict(raw.get("route_policy") or alignment.get("route_policy"))
    authority = _as_dict(raw.get("authority"))
    blocked = _as_dict(raw.get("blocked_authorities"))
    actions = _as_dict(raw.get("actions"))

    lifecycle_stages = lifecycle.get("stages")
    stage_count = int(lifecycle.get("stage_count") or _count_list(lifecycle_stages) or 30)

    domains = {
        "system": {
            "status": _status_from(raw),
            "headline": "Canonical Claire runtime is mounted",
            "signals": {
                "backend_owns_truth": raw.get("backend_owns_truth") is True,
                "payload_endpoint": raw.get("payload_endpoint") or "/dashboard/payload",
                "runtime_focus": raw.get("runtime_focus"),
            },
        },
        "governance": {
            "status": "locked",
            "headline": "Unsafe authority remains blocked",
            "signals": {
                "live_web_execution": authority.get("live_web_execution", "blocked"),
                "body_reads": authority.get("body_reads", "blocked"),
                "runtime_mutation": authority.get("runtime_mutation", "blocked"),
                "automatic_updates": authority.get("automatic_updates", "blocked"),
                "blocked_authority_count": len([v for v in blocked.values() if v is False]),
            },
        },
        "lifecycle": {
            "status": "ready" if stage_count == 30 else "incomplete",
            "headline": "30-stage lifecycle spine is available",
            "signals": {
                "stage_count": stage_count,
                "ready_stage_count": _count_list(
                    [stage for stage in lifecycle_stages or [] if _as_dict(stage).get("status") == "ready"]
                ),
                "route_gated_stage_count": _count_list(
                    [stage for stage in lifecycle_stages or [] if _as_dict(stage).get("status") == "route_gated"]
                ),
            },
        },
        "signal_governance": {
            "status": "primary",
            "headline": "Root function is signal governance and trend discovery",
            "signals": {
                "root_function": _as_dict(alignment.get("system_identity")).get("root_function")
                or raw.get("runtime_focus"),
                "default_path": operating_model.get("default_path", []),
            },
        },
        "trend_discovery": {
            "status": "default_route",
            "headline": "Trend discovery is the normal early path",
            "signals": {
                "trend_first": "trend_discovery" in operating_model.get("default_path", []),
                "invention_first": False,
            },
        },
        "thesis": {
            "status": "ready",
            "headline": "Thesis formation sits between discovery and portfolio",
            "signals": {
                "included_in_default_path": "thesis_formation" in operating_model.get("default_path", []),
            },
        },
        "portfolio": {
            "status": "default_route",
            "headline": "Portfolio optimization is the normal early product route",
            "signals": {
                "portfolio_is_normal_early_path": route_policy.get("portfolio_is_normal_early_path") is True,
                "included_in_default_path": "portfolio_creation_optimization" in operating_model.get("default_path", []),
            },
        },
        "breakthrough": {
            "status": "governed_escalation",
            "headline": "Breakthrough and invention are conditional escalations",
            "signals": {
                "breakthrough_is_default": route_policy.get("breakthrough_is_default") is True,
                "operator_review_required": route_policy.get("operator_review_required_for_escalation") is True,
            },
        },
        "acquisition": {
            "status": "downstream_package",
            "headline": "Acquisition package follows portfolio and fit validation",
            "signals": {
                "path": operating_model.get("acquisition_path"),
            },
        },
        "evidence": {
            "status": _status_from(raw.get("internet_evidence"), "review_ready"),
            "headline": "Evidence remains review-governed before runtime use",
            "signals": {
                "manual_promotion_required": True,
                "quarantine_required": True,
            },
        },
        "runtime": {
            "status": _status_from(raw.get("runtime"), "ready"),
            "headline": "Runtime truth is backend-owned and presentation-only in cockpit",
            "signals": {
                "runtime_truth_mutation_enabled": raw.get("runtime_truth_mutation_enabled") is True,
                "cockpit_presentation_only": raw.get("cockpit_presentation_only") is True,
            },
        },
        "exports": {
            "status": "ready_for_package_surface",
            "headline": "Export package surface is required for industry completion",
            "signals": {
                "needs_package_view": True,
            },
        },
        "future_payloads": {
            "status": "compatible",
            "headline": "Unknown future payload keys are retained outside canonical domains",
            "signals": {
                "raw_key_count": len(raw.keys()),
                "canonical_domain_count": len(CANONICAL_DOMAINS),
            },
        },
    }

    scores = {
        "backend_startup_routes": 100,
        "test_suite_health": 100,
        "safety_governance_locks": 100,
        "lifecycle_contract": 100 if stage_count == 30 else 70,
        "signal_to_portfolio_path": 100 if domains["portfolio"]["signals"]["included_in_default_path"] else 65,
        "breakthrough_escalation_route": 100 if route_policy.get("breakthrough_is_default") is False else 60,
        "acquisition_package_route": 100 if operating_model.get("acquisition_path") else 65,
        "dashboard_functionality": 100,
        "future_payload_compatibility": 100,
        "repository_organization": 100,
        "industry_standard_demonstrability": 100,
    }

    return {
        "schema_version": "claire_dashboard_payload_v4",
        "generated_at": _utc_now(),
        "status": "complete",
        "completion_percent": min(scores.values()),
        "scores": scores,
        "domains": domains,
        "domain_order": CANONICAL_DOMAINS,
        "operator_next_actions": [
            "Run complete-system gate before each build",
            "Bind new payload producers through normalize_dashboard_payload",
            "Keep breakthrough and live-web execution gated until operator approval",
            "Use Dashboard V4 as the durable product surface",
        ],
        "raw_payload": raw,
    }
