
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

VERSION = "v17.70"
CONTRACT_NAME = "Internet Readiness Verification"

OUTPUT_PATH = Path("data/internet_readiness/internet_readiness_verification.json")
DASHBOARD_PAYLOAD_PATH = Path("data/dashboard/internet_readiness_payload.json")

INTERNET_LAYER_FILES = {
    "internet_activation": [
        "claire/internet_activation/config.py",
        "claire/internet_activation/service.py",
        "data/internet_activation/internet_activation_manifest.json",
    ],
    "internet_runtime_integration": [
        "claire/internet_runtime_integration/bridge.py",
        "claire/internet_runtime_integration/dashboard_payload.py",
        "claire/internet_runtime_integration/output_merger.py",
        "data/internet_runtime_integration/internet_runtime_integration_manifest.json",
    ],
    "persistent_internet_campaigns": [
        "claire/persistent_internet_campaigns/service.py",
        "data/persistent_internet_campaigns/persistent_internet_campaigns_manifest.json",
    ],
    "governed_campaign_scheduler": [
        "claire/governed_campaign_scheduler/lock.py",
        "claire/governed_campaign_scheduler/store.py",
        "data/governed_campaign_scheduler/governed_campaign_scheduler_manifest.json",
    ],
    "internet_runtime_stability": [
        "claire/internet_runtime_stability/health.py",
        "claire/internet_runtime_stability/service.py",
        "data/internet_runtime_stability/internet_runtime_stability_manifest.json",
    ],
    "dynamic_source_trust": [
        "claire/dynamic_source_trust/store.py",
        "data/dynamic_source_trust/dynamic_source_trust_manifest.json",
    ],
    "internet_operations_dashboard": [
        "claire/internet_operations_dashboard/service.py",
        "data/internet_operations_dashboard/internet_operations_dashboard_manifest.json",
    ],
    "governed_connectivity": [
        "claire/governed_internet_connectivity/runtime.py",
        "data/governed_internet_connectivity/connectivity_manifest.json",
    ],
    "live_connectivity": [
        "claire/real_governed_live_connectivity/runtime.py",
        "data/real_governed_live_connectivity/live_connectivity_manifest.json",
    ],
}

UPDATE_GOVERNANCE_FILES = {
    "update_orchestrator": [
        "claire/platform/update_governance/update_orchestrator.py",
        "claire/platform/update_governance/update_plan.py",
    ],
    "rollback": [
        "claire/platform/update_governance/rollback_orchestrator.py",
        "claire/platform/update_governance/rollback_policy.py",
    ],
    "validation_gauntlet": [
        "claire/platform/update_governance/validation_gauntlet.py",
    ],
    "safe_installer": [
        "safe_install_claire_version.py",
    ],
}

ENV_KEYS = [
    "PLATFORM_SEARCH_PROVIDER",
    "TAVILY_API_KEY",
    "BRAVE_SEARCH_API_KEY",
    "SERPAPI_API_KEY",
    "BING_SEARCH_API_KEY",
    "PLATFORM_INTERNET_ALLOW_UNKNOWN_DOMAINS",
    "PLATFORM_INTERNET_MAX_RESULTS",
    "PLATFORM_INTERNET_TIMEOUT_SECONDS",
    "PLATFORM_INTERNET_MAX_BYTES",
]

REQUIRED_GOVERNANCE_SIGNALS = [
    "allowlist",
    "quarantine",
    "source_trust",
    "retry",
    "degraded",
    "scheduler_lock",
    "rollback",
    "validation",
    "operator_review",
]


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def rel(root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve())).replace("\\", "/")
    except Exception:
        return str(path).replace("\\", "/")


def read_text(path: Path, max_bytes: int = 600_000) -> str:
    try:
        if not path.exists() or not path.is_file():
            return ""
        if path.stat().st_size > max_bytes:
            return path.read_bytes()[:max_bytes].decode("utf-8", errors="replace")
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


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


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def file_group_status(root: Path, groups: Dict[str, List[str]]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for name, paths in groups.items():
        present = [p for p in paths if (root / p).exists()]
        missing = [p for p in paths if not (root / p).exists()]
        out[name] = {
            "status": "present" if present else "missing",
            "present": present,
            "missing": missing,
            "score": len(present),
            "out_of": len(paths),
        }
    return out


def env_status(root: Path) -> Dict[str, Any]:
    env_example = read_text(root / ".env.example")
    env_file = read_text(root / ".env")
    env_combined = env_example + "\n" + env_file

    key_status = {}
    for key in ENV_KEYS:
        in_example = key in env_example
        in_env = key in env_file or bool(os.environ.get(key))
        value_present = bool(os.environ.get(key)) or any(
            line.strip().startswith(key + "=") and line.split("=", 1)[1].strip() not in {"", "changeme", "CHANGE_ME", "your_key_here"}
            for line in env_file.splitlines()
        )
        key_status[key] = {
            "declared_in_env_example": in_example,
            "declared_in_env_or_process": in_env,
            "value_present": value_present,
            "safe_to_print_value": False,
        }

    provider_present = any(
        key_status[key]["value_present"]
        for key in ["TAVILY_API_KEY", "BRAVE_SEARCH_API_KEY", "SERPAPI_API_KEY", "BING_SEARCH_API_KEY"]
    )
    provider_declared = key_status["PLATFORM_SEARCH_PROVIDER"]["declared_in_env_example"] or key_status["PLATFORM_SEARCH_PROVIDER"]["declared_in_env_or_process"]

    allow_unknown = None
    for source in [env_file, env_example]:
        for line in source.splitlines():
            if line.strip().startswith("PLATFORM_INTERNET_ALLOW_UNKNOWN_DOMAINS="):
                allow_unknown = line.split("=", 1)[1].strip()

    return {
        "keys": key_status,
        "provider_declared": provider_declared,
        "provider_key_present": provider_present,
        "allow_unknown_domains_value": allow_unknown,
        "unknown_domains_blocked_or_unspecified": allow_unknown in {None, "", "0", "false", "False", "FALSE"},
        "env_files_present": {
            ".env": (root / ".env").exists(),
            ".env.example": (root / ".env.example").exists(),
        },
    }


def scan_governance_signals(root: Path) -> Dict[str, Any]:
    search_roots = [
        root / "claire",
        root / "data",
        root / "docs",
        root / "manifests",
    ]
    hits = {signal: [] for signal in REQUIRED_GOVERNANCE_SIGNALS}
    suffixes = {".py", ".json", ".md", ".txt", ".yml", ".yaml", ".toml", ".ini"}

    for base in search_roots:
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in suffixes:
                continue
            if any(part in {".git", ".venv", "__pycache__", ".pytest_cache", "backups", "rollback"} for part in path.parts):
                continue
            text = read_text(path, 250_000).lower()
            for signal in REQUIRED_GOVERNANCE_SIGNALS:
                token = signal.lower()
                variants = {token, token.replace("_", " "), token.replace("_", "-")}
                if any(variant in text for variant in variants):
                    hits[signal].append(rel(root, path))

    return {
        signal: {
            "present": bool(paths),
            "sample_paths": sorted(set(paths))[:25],
        }
        for signal, paths in hits.items()
    }


def scheduler_status(root: Path) -> Dict[str, Any]:
    lock_candidates = []
    schedule_candidates = []
    for base in [root / "data", root / "claire", root / "docs"]:
        if not base.exists():
            continue
        for path in base.rglob("*"):
            lower = rel(root, path).lower()
            if "lock" in lower and ("scheduler" in lower or "campaign" in lower or "internet" in lower):
                lock_candidates.append(rel(root, path))
            if "scheduler" in lower or "schedule" in lower or "campaign" in lower:
                schedule_candidates.append(rel(root, path))
    return {
        "lock_candidates": sorted(set(lock_candidates))[:80],
        "schedule_candidates": sorted(set(schedule_candidates))[:100],
        "scheduler_lock_evidence": bool(lock_candidates),
        "schedule_evidence": bool(schedule_candidates),
    }


def determine_readiness(layer_status: Dict[str, Any], update_status: Dict[str, Any], env: Dict[str, Any], governance: Dict[str, Any], scheduler: Dict[str, Any]) -> Tuple[str, List[str], List[str]]:
    blockers: List[str] = []
    warnings: List[str] = []

    required_layers = [
        "internet_activation",
        "internet_runtime_integration",
        "internet_runtime_stability",
        "dynamic_source_trust",
        "governed_campaign_scheduler",
    ]

    for layer in required_layers:
        if layer_status.get(layer, {}).get("score", 0) == 0:
            blockers.append(f"missing_required_internet_layer:{layer}")

    if not env["provider_declared"]:
        warnings.append("PLATFORM_SEARCH_PROVIDER is not declared.")
    if not env["provider_key_present"]:
        warnings.append("No live search provider API key detected. Static readiness can pass, but live internet use remains disabled.")

    if not env["unknown_domains_blocked_or_unspecified"]:
        blockers.append("unknown_domains_are_not_blocked")

    for signal in ["allowlist", "quarantine", "source_trust", "degraded"]:
        if not governance.get(signal, {}).get("present"):
            blockers.append(f"missing_governance_signal:{signal}")

    if not scheduler["scheduler_lock_evidence"]:
        blockers.append("scheduler_lock_evidence_missing")

    if update_status.get("rollback", {}).get("score", 0) == 0:
        warnings.append("Rollback governance files not found. Automatic update readiness cannot pass later without rollback proof.")
    if update_status.get("validation_gauntlet", {}).get("score", 0) == 0:
        warnings.append("Update validation gauntlet files not found. Automatic update readiness cannot pass later without validation proof.")

    if blockers:
        return "blocked", blockers, warnings
    if warnings:
        return "warning", blockers, warnings
    return "passed_static_readiness", blockers, warnings


def build_internet_readiness(project_root: Optional[Path | str] = None) -> Dict[str, Any]:
    root = Path(project_root or Path.cwd()).resolve()

    layer_status = file_group_status(root, INTERNET_LAYER_FILES)
    update_status = file_group_status(root, UPDATE_GOVERNANCE_FILES)
    env = env_status(root)
    governance = scan_governance_signals(root)
    scheduler = scheduler_status(root)

    status, blockers, warnings = determine_readiness(layer_status, update_status, env, governance, scheduler)

    readiness = {
        "version": VERSION,
        "contract_name": CONTRACT_NAME,
        "generated_at": now(),
        "status": status,
        "mode": "static_verification_no_internet_calls",
        "internet_layers": layer_status,
        "update_governance": update_status,
        "environment": env,
        "governance_signals": governance,
        "scheduler": scheduler,
        "blockers": sorted(set(blockers)),
        "warnings": sorted(set(warnings)),
        "readiness": {
            "static_internet_readiness": status in {"passed_static_readiness", "warning"},
            "live_internet_enabled": False,
            "automatic_updates_enabled": False,
            "safe_to_attempt_live_probe_after_operator_review": status in {"passed_static_readiness", "warning"} and env["provider_key_present"],
            "safe_for_automatic_updates": False,
            "requires_v17_71_to_v17_74_update_pack_governance": True,
        },
        "governance": {
            "no_uncontrolled_browsing": True,
            "no_hidden_background_updates": True,
            "source_allowlist_required": True,
            "source_trust_required": True,
            "quarantine_required": True,
            "degraded_mode_required": True,
            "rollback_required_before_automatic_updates": True,
            "operator_review_required": True,
        },
        "next": [
            "v17.71 Governed Update Pack Staging",
            "v17.72 Rollback-Aware Update Plan Contract",
            "v17.73 Automatic Update Runner Gate",
            "v17.74 Update Governance Regression Lock",
            "v17.75 Full end-to-end proof pack",
        ],
    }

    write_json(root / OUTPUT_PATH, readiness)

    dashboard_payload = {
        "version": VERSION,
        "generated_at": readiness["generated_at"],
        "status": readiness["status"],
        "mode": readiness["mode"],
        "blockers": readiness["blockers"],
        "warnings": readiness["warnings"],
        "readiness": readiness["readiness"],
        "internet_layer_scores": {
            name: {"score": item["score"], "out_of": item["out_of"], "status": item["status"]}
            for name, item in layer_status.items()
        },
        "update_governance_scores": {
            name: {"score": item["score"], "out_of": item["out_of"], "status": item["status"]}
            for name, item in update_status.items()
        },
        "provider_key_present": env["provider_key_present"],
        "unknown_domains_blocked_or_unspecified": env["unknown_domains_blocked_or_unspecified"],
    }
    write_json(root / DASHBOARD_PAYLOAD_PATH, dashboard_payload)

    return readiness


def internet_readiness_summary(project_root: Optional[Path | str] = None) -> Dict[str, Any]:
    readiness = build_internet_readiness(project_root)
    return {
        "version": VERSION,
        "generated_at": now(),
        "status": readiness.get("status"),
        "mode": readiness.get("mode"),
        "readiness": readiness.get("readiness"),
        "blockers": readiness.get("blockers", []),
        "warnings": readiness.get("warnings", []),
    }
