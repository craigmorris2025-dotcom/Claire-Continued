
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

VERSION = "v17.83"
CONTRACT_NAME = "Internet Provider Configuration Gate"

PROVIDER_GATE_PATH = Path("data/internet_provider/provider_configuration_gate.json")
PROVIDER_TEMPLATE_PATH = Path("data/internet_provider/provider_config_template.json")
ALLOWLIST_TEMPLATE_PATH = Path("data/internet_provider/source_allowlist_template.json")
QUARANTINE_POLICY_PATH = Path("data/internet_provider/quarantine_policy.json")
DASHBOARD_PAYLOAD_PATH = Path("data/dashboard/internet_provider_gate_payload.json")
STOP_GO_PATH = Path("data/internet_provider/v17_83_internet_provider_stop_go.json")
STOP_GO_MD_PATH = Path("data/internet_provider/v17_83_internet_provider_stop_go.md")
ENV_EXAMPLE_PATH = Path("data/internet_provider/.env.internet.example")

SUPPORTED_PROVIDERS = {
    "brave": {
        "label": "Brave Search API",
        "env_key": "BRAVE_SEARCH_API_KEY",
        "official_setup_url_note": "Use your Brave Search API key; do not paste it into ChatGPT.",
    },
    "bing": {
        "label": "Bing Web Search API",
        "env_key": "BING_SEARCH_API_KEY",
        "official_setup_url_note": "Use your Microsoft/Bing search API key; do not paste it into ChatGPT.",
    },
    "serpapi": {
        "label": "SerpAPI",
        "env_key": "SERPAPI_API_KEY",
        "official_setup_url_note": "Use your SerpAPI key; do not paste it into ChatGPT.",
    },
    "tavily": {
        "label": "Tavily Search API",
        "env_key": "TAVILY_API_KEY",
        "official_setup_url_note": "Use your Tavily key; do not paste it into ChatGPT.",
    },
    "none": {
        "label": "No Provider Configured",
        "env_key": "",
        "official_setup_url_note": "Runtime/system search remains available. Live web remains disabled.",
    },
}

REQUIRED_GOVERNANCE = {
    "source_trust_required": True,
    "allowlist_or_quarantine_required": True,
    "evidence_capture_required": True,
    "rate_limits_required": True,
    "operator_visible_results_required": True,
    "no_hidden_background_browsing": True,
    "no_automatic_update_execution": True,
    "no_autonomous_agent_execution": True,
}

DEFAULT_LIMITS = {
    "max_results_per_query": 8,
    "request_timeout_seconds": 12,
    "max_bytes_per_result": 250000,
    "max_queries_per_minute": 6,
    "max_queries_per_session": 30,
    "require_operator_visible_results": True,
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def read_json(path: Path) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    if not path.exists():
        return {}, {"path": str(path).replace("\\", "/"), "status": "missing"}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            return {}, {"path": str(path).replace("\\", "/"), "status": "invalid", "error": "JSON root is not object"}
        return payload, {"path": str(path).replace("\\", "/"), "status": "loaded"}
    except Exception as exc:
        return {}, {"path": str(path).replace("\\", "/"), "status": "invalid", "error": str(exc)}


def redact(value: str) -> str:
    if not value:
        return ""
    if len(value) <= 6:
        return "***"
    return value[:2] + "***" + value[-2:]


def env_status() -> Dict[str, Any]:
    provider = os.getenv("CLAIRE_SEARCH_PROVIDER", "none").strip().lower() or "none"
    if provider not in SUPPORTED_PROVIDERS:
        provider_known = False
        provider_info = {
            "label": "Unknown provider",
            "env_key": "",
            "official_setup_url_note": "Provider not supported by this gate.",
        }
    else:
        provider_known = True
        provider_info = SUPPORTED_PROVIDERS[provider]

    key_name = provider_info.get("env_key", "")
    key_value = os.getenv(key_name, "") if key_name else ""

    configured_keys = {}
    for name, info in SUPPORTED_PROVIDERS.items():
        env_key = info.get("env_key", "")
        if not env_key:
            continue
        value = os.getenv(env_key, "")
        configured_keys[env_key] = {
            "present": bool(value),
            "redacted": redact(value),
        }

    return {
        "selected_provider": provider,
        "provider_known": provider_known,
        "provider_label": provider_info.get("label"),
        "required_key_name": key_name,
        "required_key_present": bool(key_value),
        "configured_keys": configured_keys,
        "provider_note": provider_info.get("official_setup_url_note"),
    }


def build_provider_template(root: Path) -> Dict[str, Any]:
    template = {
        "version": VERSION,
        "created_at": now(),
        "instructions": [
            "Choose exactly one provider by setting CLAIRE_SEARCH_PROVIDER in your environment or .env.",
            "Never paste API keys into ChatGPT.",
            "This template does not enable live web execution by itself.",
            "After provider configuration, run this gate and then a separate governed live-search probe build.",
        ],
        "supported_providers": SUPPORTED_PROVIDERS,
        "required_environment_variables": {
            "CLAIRE_SEARCH_PROVIDER": "one of: none, brave, bing, serpapi, tavily",
            "BRAVE_SEARCH_API_KEY": "required only if CLAIRE_SEARCH_PROVIDER=brave",
            "BING_SEARCH_API_KEY": "required only if CLAIRE_SEARCH_PROVIDER=bing",
            "SERPAPI_API_KEY": "required only if CLAIRE_SEARCH_PROVIDER=serpapi",
            "TAVILY_API_KEY": "required only if CLAIRE_SEARCH_PROVIDER=tavily",
        },
        "default_limits": DEFAULT_LIMITS,
        "governance": REQUIRED_GOVERNANCE,
    }
    write_json(root / PROVIDER_TEMPLATE_PATH, template)

    env_example = """# Claire Internet Provider Example
# Do not paste real API keys into ChatGPT.
# Copy needed lines into your local .env only.

CLAIRE_SEARCH_PROVIDER=none

# Choose one provider later:
# CLAIRE_SEARCH_PROVIDER=brave
# BRAVE_SEARCH_API_KEY=your_key_here

# CLAIRE_SEARCH_PROVIDER=bing
# BING_SEARCH_API_KEY=your_key_here

# CLAIRE_SEARCH_PROVIDER=serpapi
# SERPAPI_API_KEY=your_key_here

# CLAIRE_SEARCH_PROVIDER=tavily
# TAVILY_API_KEY=your_key_here
"""
    write_text(root / ENV_EXAMPLE_PATH, env_example)
    return template


def build_allowlist_template(root: Path) -> Dict[str, Any]:
    allowlist = {
        "version": VERSION,
        "created_at": now(),
        "policy": "review_before_trust",
        "allowlist_enabled": False,
        "quarantine_unknown_domains": True,
        "trusted_domains": [
            {
                "domain": "sec.gov",
                "trust_tier": "primary_public_record",
                "enabled": True,
                "notes": "Public filings and official company records.",
            },
            {
                "domain": "federalreserve.gov",
                "trust_tier": "primary_public_record",
                "enabled": True,
                "notes": "Federal Reserve source for economic policy and data.",
            },
            {
                "domain": "bls.gov",
                "trust_tier": "primary_public_record",
                "enabled": True,
                "notes": "Official labor/economic data.",
            },
            {
                "domain": "energy.gov",
                "trust_tier": "primary_public_record",
                "enabled": True,
                "notes": "Energy information and technology program source.",
            },
        ],
        "operator_review_required_for_new_domains": True,
    }
    write_json(root / ALLOWLIST_TEMPLATE_PATH, allowlist)
    return allowlist


def build_quarantine_policy(root: Path) -> Dict[str, Any]:
    policy = {
        "version": VERSION,
        "created_at": now(),
        "quarantine_enabled": True,
        "unknown_domain_default": "quarantine",
        "quarantine_reasons": [
            "unknown_domain",
            "low_source_trust",
            "missing_date",
            "possible_generated_content",
            "conflicting_claims",
            "paywalled_or_unverifiable",
        ],
        "result_visibility": "operator_visible_with_warning",
        "may_feed_runtime_truth": False,
        "operator_can_promote_after_review": True,
        "promotion_requires": [
            "source URL",
            "retrieval timestamp",
            "claim/evidence extraction",
            "trust tier assignment",
            "operator approval",
        ],
    }
    write_json(root / QUARANTINE_POLICY_PATH, policy)
    return policy


def prior_readiness(root: Path) -> Dict[str, Any]:
    internet, internet_source = read_json(root / "data/internet_readiness/internet_readiness_verification.json")
    search_caps, search_source = read_json(root / "data/operator/search_command/search_command_capabilities.json")
    freeze, freeze_source = read_json(root / "data/launch_candidate/v17_80_launch_candidate_freeze.json")

    return {
        "internet_readiness": {
            "source": internet_source,
            "status": internet.get("status", "missing"),
            "readiness": internet.get("readiness", {}),
        },
        "search_command_capabilities": {
            "source": search_source,
            "status": search_caps.get("status", "missing"),
            "modes": search_caps.get("modes", {}),
            "live_web_conditions": search_caps.get("live_web_conditions", {}),
        },
        "launch_candidate_freeze": {
            "source": freeze_source,
            "status": freeze.get("status", "missing"),
        },
    }


def determine_stop_go(environment: Dict[str, Any], prior: Dict[str, Any]) -> Dict[str, Any]:
    blockers: List[str] = []
    warnings: List[str] = []

    provider = environment["selected_provider"]
    if provider != "none" and not environment["provider_known"]:
        blockers.append("unsupported_search_provider")
    if provider != "none" and not environment["required_key_present"]:
        blockers.append(f"missing_required_provider_key:{environment['required_key_name']}")
    if provider == "none":
        warnings.append("no_search_provider_selected")

    internet_source_status = prior["internet_readiness"]["source"].get("status")
    search_source_status = prior["search_command_capabilities"]["source"].get("status")
    if internet_source_status != "loaded":
        blockers.append("missing_internet_readiness_report")
    if search_source_status != "loaded":
        blockers.append("missing_search_command_capabilities")

    readiness = prior["internet_readiness"].get("readiness", {})
    if readiness.get("automatic_updates_enabled", False) is not False:
        blockers.append("automatic_updates_not_disabled")
    if readiness.get("live_internet_enabled", False) is not False:
        warnings.append("prior_readiness_live_internet_flag_not_false")

    if blockers:
        status = "STOP_PROVIDER_CONFIG_INCOMPLETE"
        recommendation = "Configure provider/environment and rerun the gate. Do not attempt live search yet."
    elif provider == "none":
        status = "PROVIDER_NOT_CONFIGURED_RUNTIME_SEARCH_ONLY"
        recommendation = "Runtime/system search remains available. Configure a provider later for normal web search."
    else:
        status = "PROVIDER_CONFIGURED_READY_FOR_GOVERNED_PROBE"
        recommendation = "Provider configuration is detected. Next build may run a governed single-query live probe with quarantine and evidence capture."

    return {
        "status": status,
        "blockers": sorted(set(blockers)),
        "warnings": sorted(set(warnings)),
        "recommendation": recommendation,
        "live_search_enabled_now": False,
        "normal_web_search_execution_enabled": False,
        "governed_probe_allowed_now": False,
    }


def write_markdown(root: Path, gate: Dict[str, Any]) -> None:
    sg = gate["stop_go"]
    lines = [
        "# Claire v17.83 Internet Provider Configuration Gate",
        "",
        f"Generated: {gate['generated_at']}",
        "",
        f"Status: **{sg['status']}**",
        "",
        f"Recommendation: {sg['recommendation']}",
        "",
        "## Provider",
        "",
        f"- Selected provider: `{gate['environment']['selected_provider']}`",
        f"- Provider known: `{gate['environment']['provider_known']}`",
        f"- Required key name: `{gate['environment']['required_key_name']}`",
        f"- Required key present: `{gate['environment']['required_key_present']}`",
        "",
        "## Safety",
        "",
        "- This build does not run web searches.",
        "- This build does not enable live internet.",
        "- This build does not enable automatic updates.",
        "- This build does not enable autonomous agent execution.",
        "",
        "## Templates created",
        "",
        f"- `{PROVIDER_TEMPLATE_PATH}`",
        f"- `{ALLOWLIST_TEMPLATE_PATH}`",
        f"- `{QUARANTINE_POLICY_PATH}`",
        f"- `{ENV_EXAMPLE_PATH}`",
        "",
        "## Next",
        "",
        "After provider configuration is detected, the next safe step is a governed single-query live probe with evidence capture and quarantine.",
        "",
    ]
    if sg["blockers"]:
        lines.append("## Blockers")
        lines.append("")
        for item in sg["blockers"]:
            lines.append(f"- {item}")
        lines.append("")
    if sg["warnings"]:
        lines.append("## Warnings")
        lines.append("")
        for item in sg["warnings"]:
            lines.append(f"- {item}")
        lines.append("")
    write_text(root / STOP_GO_MD_PATH, "\n".join(lines))


def build_internet_provider_gate(project_root: Optional[Path | str] = None) -> Dict[str, Any]:
    root = Path(project_root or Path.cwd()).resolve()

    template = build_provider_template(root)
    allowlist = build_allowlist_template(root)
    quarantine = build_quarantine_policy(root)
    environment = env_status()
    prior = prior_readiness(root)
    stop_go = determine_stop_go(environment, prior)

    gate = {
        "version": VERSION,
        "contract_name": CONTRACT_NAME,
        "generated_at": now(),
        "status": stop_go["status"],
        "stop_go": stop_go,
        "environment": environment,
        "provider_template_path": str(PROVIDER_TEMPLATE_PATH).replace("\\", "/"),
        "allowlist_template_path": str(ALLOWLIST_TEMPLATE_PATH).replace("\\", "/"),
        "quarantine_policy_path": str(QUARANTINE_POLICY_PATH).replace("\\", "/"),
        "env_example_path": str(ENV_EXAMPLE_PATH).replace("\\", "/"),
        "prior_readiness": prior,
        "limits": DEFAULT_LIMITS,
        "governance": {
            **REQUIRED_GOVERNANCE,
            "provider_configuration_gate_only": True,
            "live_search_enabled": False,
            "normal_web_search_execution_enabled": False,
            "governed_research_execution_enabled": False,
            "single_query_probe_enabled": False,
            "automatic_updates_disabled": True,
            "agent_execution_disabled": True,
            "no_fake_web_results": True,
        },
        "next": [
            "Set CLAIRE_SEARCH_PROVIDER and matching API key locally if desired",
            "Rerun this provider gate",
            "v17.84 Governed Single-Query Live Search Probe only after provider is configured",
        ],
    }

    write_json(root / PROVIDER_GATE_PATH, gate)
    write_json(root / STOP_GO_PATH, {"version": VERSION, "generated_at": gate["generated_at"], **stop_go})
    write_markdown(root, gate)

    dashboard_payload = {
        "version": VERSION,
        "generated_at": gate["generated_at"],
        "status": gate["status"],
        "recommendation": stop_go["recommendation"],
        "selected_provider": environment["selected_provider"],
        "provider_known": environment["provider_known"],
        "required_key_present": environment["required_key_present"],
        "live_search_enabled": False,
        "normal_web_search_execution_enabled": False,
        "governance": gate["governance"],
    }
    write_json(root / DASHBOARD_PAYLOAD_PATH, dashboard_payload)

    return gate


def internet_provider_gate_summary(project_root: Optional[Path | str] = None) -> Dict[str, Any]:
    gate = build_internet_provider_gate(project_root)
    return {
        "version": VERSION,
        "generated_at": now(),
        "status": gate.get("status"),
        "recommendation": gate.get("stop_go", {}).get("recommendation"),
        "selected_provider": gate.get("environment", {}).get("selected_provider"),
        "required_key_present": gate.get("environment", {}).get("required_key_present"),
        "live_search_enabled": False,
        "normal_web_search_execution_enabled": False,
        "next": gate.get("next", []),
    }
