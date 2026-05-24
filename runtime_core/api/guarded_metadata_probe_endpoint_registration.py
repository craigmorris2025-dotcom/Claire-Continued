"""Guarded metadata probe endpoint registration readiness.

Passive only:
- no route registration
- no network request
- no response body read
- no browser execution
- no runtime truth mutation
- no autonomous execution
- no automatic update
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[2]
RUNTIME_ROOT = ROOT / "runtime_core"
APP_FILE = RUNTIME_ROOT / "app.py"


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def _discover_include_router_calls(app_source: str) -> List[Dict[str, Any]]:
    calls: List[Dict[str, Any]] = []
    if not app_source:
        return calls

    try:
        tree = ast.parse(app_source)
    except SyntaxError:
        return calls

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if not (isinstance(node.func, ast.Attribute) and node.func.attr == "include_router"):
            continue

        router_expression = None
        if node.args:
            try:
                router_expression = ast.unparse(node.args[0])
            except Exception:
                router_expression = "<unparseable>"

        prefix = None
        for keyword in node.keywords:
            if keyword.arg == "prefix":
                try:
                    prefix = ast.literal_eval(keyword.value)
                except Exception:
                    try:
                        prefix = ast.unparse(keyword.value)
                    except Exception:
                        prefix = "<unparseable>"

        calls.append(
            {
                "line": getattr(node, "lineno", None),
                "router_expression": router_expression,
                "prefix": prefix,
            }
        )

    return calls


def _discover_api_router_modules() -> List[str]:
    api_dir = RUNTIME_ROOT / "api"
    if not api_dir.exists():
        return []
    modules: List[str] = []
    for path in sorted(api_dir.glob("*.py")):
        text = _read_text(path)
        if "APIRouter" in text or "include_router" in text:
            modules.append(str(path.relative_to(ROOT)).replace("\\", "/"))
    return modules


def get_guarded_metadata_probe_endpoint_registration() -> Dict[str, Any]:
    app_source = _read_text(APP_FILE)
    include_router_calls = _discover_include_router_calls(app_source)

    return {
        "version": "v19.89.8-S33R4R1-repair",
        "status": "readiness_visible_endpoint_not_registered",
        "route_registered": False,
        "safe_mounted_router_proven": False,
        "proven_router": None,
        "registration_strategy": "no_app_py_patch_passive_payload_readiness",
        "endpoint_candidate": "/api/governed-web/metadata-probe",
        "method_candidate": "POST",
        "operator_trigger_required": True,
        "manual_promotion_required": True,
        "evidence_quarantine_required": True,
        "runtime_authority": "blocked",
        "browser_execution_authority": "blocked",
        "runtime_truth_mutation": "blocked",
        "autonomous_execution": "blocked",
        "automatic_updates": "blocked",
        "response_body_reads": "blocked",
        "live_web_execution": "blocked_until_explicitly_gated",
        "network_request_during_install": False,
        "response_body_read_during_install": False,
        "changed_app_py": False,
        "inspected_app_py": APP_FILE.exists(),
        "include_router_calls_detected": include_router_calls,
        "api_router_modules_detected": _discover_api_router_modules(),
        "reason": (
            "S33R4R1 repair restored payload composition and exposes passive "
            "registration readiness only. Endpoint remains unregistered until "
            "a safe mounted router is explicitly proven."
        ),
        "rollback_rule": "rollback_on_compile_or_payload_failure",
    }
