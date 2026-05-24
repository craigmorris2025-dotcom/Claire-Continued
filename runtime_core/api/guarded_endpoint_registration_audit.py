"""S34 guarded endpoint registration audit.

This module proves whether the endpoint is registered. It does not patch app.py.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[2]
RUNTIME_ROOT = ROOT / "runtime_core"
APP_FILE = RUNTIME_ROOT / "app.py"
API_DIR = RUNTIME_ROOT / "api"


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def _discover_include_router_calls() -> List[Dict[str, Any]]:
    source = _read(APP_FILE)
    if not source:
        return []
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return [{"error": "app_py_syntax_error", "detail": str(exc)}]

    calls: List[Dict[str, Any]] = []
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

        calls.append(
            {
                "line": getattr(node, "lineno", None),
                "router_expression": router_expression,
            }
        )
    return calls


def get_guarded_endpoint_registration_audit() -> Dict[str, Any]:
    include_calls = _discover_include_router_calls()
    registered = any(
        "guarded_metadata_probe_endpoint" in str(call.get("router_expression"))
        for call in include_calls
    )

    return {
        "version": "v19.89.8-S34R2",
        "status": "registered" if registered else "blocked_not_registered",
        "endpoint_registered": registered,
        "app_py_patched_by_s34": False,
        "include_router_calls": include_calls,
        "network_request": "blocked_until_endpoint_invoked_with_gates",
        "response_body_reads": "blocked",
        "browser_execution": "blocked",
        "runtime_truth_mutation": "blocked",
        "autonomous_execution": "blocked",
        "automatic_updates": "blocked",
        "reason": (
            "Endpoint registration is blocked unless a safe mounted router is "
            "explicitly proven. This audit does not patch app.py."
        ),
    }
