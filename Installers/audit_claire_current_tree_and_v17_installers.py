# Claire Syntalion Read-Only Audit Script
# Current tree + last installer audit
#
# Place this file in the Claire project root and run:
#
#     python audit_claire_current_tree_and_v17_installers.py
#
# This script is READ-ONLY. It does not create, edit, or delete project files.

from __future__ import annotations

import ast
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any


ROOT = Path(__file__).resolve().parent

EXPECTED_V17_LAYERS = {
    "strategic_decision_intelligence": {
        "version_range": "v16.96-v17.00",
        "module_dir": "src/claire/strategic_decision_intelligence",
        "test_dir": "tests/strategic_decision_intelligence",
        "data_dir": "data/strategic_decision_intelligence",
        "doc_dir": "docs/strategic_decision_intelligence",
        "manifest": "data/strategic_decision_intelligence/strategic_decision_manifest.json",
        "expected_files": [
            "__init__.py",
            "models.py",
            "decision_scenario_engine.py",
            "bounded_outcome_simulator.py",
            "intervention_strategy_selector.py",
            "expected_actual_outcome_tracker.py",
            "strategic_decision_regression_lock.py",
            "runtime.py",
        ],
    },
    "governed_internet_connectivity": {
        "version_range": "v17.01-v17.10",
        "module_dir": "src/claire/governed_internet_connectivity",
        "test_dir": "tests/governed_internet_connectivity",
        "data_dir": "data/governed_internet_connectivity",
        "doc_dir": "docs/governed_internet_connectivity",
        "manifest": "data/governed_internet_connectivity/connectivity_manifest.json",
        "expected_files": [
            "__init__.py",
            "models.py",
            "source_policy.py",
            "fetch_request_engine.py",
            "source_reliability.py",
            "evidence_extractor.py",
            "async_ingestion_queue.py",
            "continuous_monitor.py",
            "signal_refresh_scheduler.py",
            "watchlist_engine.py",
            "connectivity_regression_lock.py",
            "runtime.py",
        ],
    },
    "real_governed_live_connectivity": {
        "version_range": "v17.11-v17.20",
        "module_dir": "src/claire/real_governed_live_connectivity",
        "test_dir": "tests/real_governed_live_connectivity",
        "data_dir": "data/real_governed_live_connectivity",
        "doc_dir": "docs/real_governed_live_connectivity",
        "manifest": "data/real_governed_live_connectivity/real_live_connectivity_manifest.json",
        "expected_files": [
            "__init__.py",
            "models.py",
            "source_policy_bridge.py",
            "rate_limit_guard.py",
            "http_client_adapter.py",
            "search_adapter.py",
            "content_normalizer.py",
            "evidence_persistence.py",
            "retry_deadletter.py",
            "live_ingestion_worker.py",
            "live_connectivity_regression_lock.py",
            "runtime.py",
        ],
    },
    "continuous_autonomous_intelligence": {
        "version_range": "v17.21-v17.30",
        "module_dir": "src/claire/continuous_autonomous_intelligence",
        "test_dir": "tests/continuous_autonomous_intelligence",
        "data_dir": "data/continuous_autonomous_intelligence",
        "doc_dir": "docs/continuous_autonomous_intelligence",
        "manifest": "data/continuous_autonomous_intelligence/continuous_autonomous_intelligence_manifest.json",
        "expected_files": [
            "__init__.py",
            "models.py",
            "worker_registry.py",
            "event_bus.py",
            "priority_router.py",
            "heartbeat_monitor.py",
            "runtime_supervisor.py",
            "state_recovery.py",
            "campaign_continuity.py",
            "conflict_reconciliation.py",
            "escalation_contracts.py",
            "continuous_regression_lock.py",
            "runtime.py",
        ],
    },
    "distributed_production_runtime": {
        "version_range": "v17.31-v17.40",
        "module_dir": "src/claire/distributed_production_runtime",
        "test_dir": "tests/distributed_production_runtime",
        "data_dir": "data/distributed_production_runtime",
        "doc_dir": "docs/distributed_production_runtime",
        "manifest": "data/distributed_production_runtime/distributed_production_runtime_manifest.json",
        "expected_files": [
            "__init__.py",
            "models.py",
            "worker_pool.py",
            "queue_partitioning.py",
            "runtime_sharding.py",
            "workload_balancer.py",
            "streaming_pipeline.py",
            "daemon_contract.py",
            "cross_campaign_fusion.py",
            "telemetry.py",
            "health_dashboard.py",
            "production_regression_lock.py",
            "runtime.py",
        ],
    },
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def exists(path_text: str) -> bool:
    return (ROOT / path_text).exists()


def read_json(path: Path) -> Dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"_read_error": str(exc)}


def syntax_check_py(path: Path) -> Dict[str, Any]:
    try:
        ast.parse(path.read_text(encoding="utf-8"))
        return {"path": rel(path), "syntax": "ok"}
    except Exception as exc:
        return {"path": rel(path), "syntax": "error", "error": str(exc)}


def safe_tree(path: Path, max_depth: int = 3, current_depth: int = 0) -> List[str]:
    if not path.exists():
        return [f"{rel(path)} [missing]"]

    lines: List[str] = []
    indent = "  " * current_depth

    if current_depth == 0:
        lines.append(f"{rel(path) or '.'}/")

    if current_depth >= max_depth:
        return lines

    ignored = {
        ".git",
        ".venv",
        "venv",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        "node_modules",
        "dist",
        "build",
    }

    try:
        children = sorted(
            [child for child in path.iterdir() if child.name not in ignored],
            key=lambda p: (p.is_file(), p.name.lower()),
        )
    except PermissionError:
        lines.append(f"{indent}[permission denied]")
        return lines

    for child in children:
        marker = "/" if child.is_dir() else ""
        lines.append(f"{indent}  {child.name}{marker}")
        if child.is_dir():
            lines.extend(safe_tree(child, max_depth=max_depth, current_depth=current_depth + 1)[1:])

    return lines


def audit_layer(name: str, spec: Dict[str, Any]) -> Dict[str, Any]:
    module_dir = ROOT / spec["module_dir"]
    test_dir = ROOT / spec["test_dir"]
    data_dir = ROOT / spec["data_dir"]
    doc_dir = ROOT / spec["doc_dir"]
    manifest_path = ROOT / spec["manifest"]

    expected_module_paths = [module_dir / file_name for file_name in spec["expected_files"]]
    missing_modules = [rel(path) for path in expected_module_paths if not path.exists()]
    present_modules = [rel(path) for path in expected_module_paths if path.exists()]

    syntax_results = [
        syntax_check_py(path)
        for path in expected_module_paths
        if path.exists() and path.suffix == ".py"
    ]
    syntax_errors = [item for item in syntax_results if item["syntax"] != "ok"]

    tests = sorted(rel(path) for path in test_dir.glob("test_*.py")) if test_dir.exists() else []
    docs = sorted(rel(path) for path in doc_dir.glob("*.md")) if doc_dir.exists() else []
    manifest = read_json(manifest_path)

    completeness_score = 0
    checks = {
        "module_dir_exists": module_dir.exists(),
        "test_dir_exists": test_dir.exists(),
        "data_dir_exists": data_dir.exists(),
        "doc_dir_exists": doc_dir.exists(),
        "manifest_exists": manifest_path.exists(),
        "all_expected_modules_present": not missing_modules,
        "python_syntax_ok": not syntax_errors,
        "tests_present": bool(tests),
        "docs_present": bool(docs),
    }

    for value in checks.values():
        if value:
            completeness_score += 1

    return {
        "layer": name,
        "expected_version_range": spec["version_range"],
        "paths": {
            "module_dir": spec["module_dir"],
            "test_dir": spec["test_dir"],
            "data_dir": spec["data_dir"],
            "doc_dir": spec["doc_dir"],
            "manifest": spec["manifest"],
        },
        "checks": checks,
        "completeness_score": f"{completeness_score}/{len(checks)}",
        "present_modules": present_modules,
        "missing_modules": missing_modules,
        "syntax_errors": syntax_errors,
        "tests": tests,
        "docs": docs,
        "manifest_summary": manifest,
    }


def detect_installers() -> List[str]:
    patterns = [
        "install_v16_*.py",
        "install_v17_*.py",
        "install_*internet*.py",
        "install_*connectivity*.py",
        "install_*runtime*.py",
        "install_*intelligence*.py",
    ]

    found = set()
    for pattern in patterns:
        for path in ROOT.glob(pattern):
            if path.is_file():
                found.add(rel(path))

    return sorted(found)


def main() -> None:
    print("")
    print("=" * 80)
    print("CLAIRE CURRENT TREE + LAST INSTALLER AUDIT")
    print("=" * 80)
    print(f"Project root: {ROOT}")
    print(f"Audit time:   {utc_now()}")
    print("")
    print("This is READ-ONLY. No files were changed.")
    print("")

    root_items = [
        "main.py",
        "pyproject.toml",
        "requirements.txt",
        "pytest.ini",
        "version.json",
        "src",
        "src/claire",
        "tests",
        "data",
        "docs",
        "backend",
        "output",
        "exports",
    ]

    print("=" * 80)
    print("ROOT PRESENCE CHECK")
    print("=" * 80)
    for item in root_items:
        print(f"{'[OK]' if exists(item) else '[MISSING]'} {item}")

    print("")
    print("=" * 80)
    print("HIGH-LEVEL PROJECT TREE")
    print("=" * 80)
    for line in safe_tree(ROOT, max_depth=2):
        print(line)

    print("")
    print("=" * 80)
    print("DETECTED ROOT INSTALLER FILES")
    print("=" * 80)
    installers = detect_installers()
    if installers:
        for installer in installers:
            print(f"[FOUND] {installer}")
    else:
        print("[NONE FOUND] No v16/v17 installer scripts detected in project root.")

    print("")
    print("=" * 80)
    print("V17 LAYER AUDIT")
    print("=" * 80)

    report = {
        "audit_time": utc_now(),
        "project_root": str(ROOT),
        "detected_installers": installers,
        "layers": [],
    }

    for name, spec in EXPECTED_V17_LAYERS.items():
        result = audit_layer(name, spec)
        report["layers"].append(result)

        print("")
        print(f"Layer: {name}")
        print(f"Expected: {result['expected_version_range']}")
        print(f"Score: {result['completeness_score']}")

        for check_name, ok in result["checks"].items():
            print(f"  {'[OK]' if ok else '[MISSING]'} {check_name}")

        if result["missing_modules"]:
            print("  Missing modules:")
            for path in result["missing_modules"]:
                print(f"    - {path}")

        if result["syntax_errors"]:
            print("  Syntax errors:")
            for error in result["syntax_errors"]:
                print(f"    - {error['path']}: {error.get('error')}")

        if result["manifest_summary"] is None:
            print("  Manifest: missing")
        elif isinstance(result["manifest_summary"], dict) and "_read_error" in result["manifest_summary"]:
            print(f"  Manifest: read error: {result['manifest_summary']['_read_error']}")
        else:
            manifest = result["manifest_summary"]
            print(f"  Manifest status: {manifest.get('status')}")
            print(f"  Manifest version_range: {manifest.get('version_range')}")
            if manifest.get("not_included_yet"):
                print("  Not included yet:")
                for item in manifest.get("not_included_yet", []):
                    print(f"    - {item}")

    print("")
    print("=" * 80)
    print("SUMMARY JUDGMENT")
    print("=" * 80)
    print("These v17 files should be treated as installed architecture/runtime-contract layers")
    print("unless their audit score, syntax check, or tests prove otherwise.")
    print("")
    print("Before building Real Internet Readiness Core, fix any:")
    print("- missing module files")
    print("- syntax errors")
    print("- missing manifests")
    print("- failing tests")
    print("- unclear duplicate package paths")
    print("")

    print("=" * 80)
    print("OPTIONAL TEST COMMANDS TO RUN MANUALLY")
    print("=" * 80)
    print("python -m pytest tests/strategic_decision_intelligence -q")
    print("python -m pytest tests/governed_internet_connectivity -q")
    print("python -m pytest tests/real_governed_live_connectivity -q")
    print("python -m pytest tests/continuous_autonomous_intelligence -q")
    print("python -m pytest tests/distributed_production_runtime -q")
    print("")

    print("=" * 80)
    print("AUDIT COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
