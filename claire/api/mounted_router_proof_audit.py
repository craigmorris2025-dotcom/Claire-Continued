"""Mounted router proof audit for guarded metadata probe registration.

S33R6 is inspection-only.
It does not register routes, patch app.py, perform network access, read response
bodies, launch browsers, mutate runtime truth, trigger autonomous execution, or
run automatic updates.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any, Dict, List, Optional


ROOT = Path(__file__).resolve().parents[2]
CLAIRE_ROOT = ROOT / "claire"
APP_FILE = CLAIRE_ROOT / "app.py"
API_DIR = CLAIRE_ROOT / "api"


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def _unparse(node: ast.AST) -> str:
    try:
        return ast.unparse(node)
    except Exception:
        return "<unparseable>"


def _literal_or_source(node: ast.AST) -> Any:
    try:
        return ast.literal_eval(node)
    except Exception:
        return _unparse(node)


def _imports_by_alias(tree: ast.AST) -> Dict[str, str]:
    aliases: Dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                local = alias.asname or alias.name
                aliases[local] = f"{module}.{alias.name}".strip(".")
        elif isinstance(node, ast.Import):
            for alias in node.names:
                local = alias.asname or alias.name.split(".")[0]
                aliases[local] = alias.name
    return aliases


def _discover_app_include_router_calls() -> List[Dict[str, Any]]:
    source = _read(APP_FILE)
    if not source:
        return []

    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return [{"error": "app_py_syntax_error", "detail": str(exc)}]

    aliases = _imports_by_alias(tree)
    calls: List[Dict[str, Any]] = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if not (isinstance(node.func, ast.Attribute) and node.func.attr == "include_router"):
            continue

        router_expression: Optional[str] = None
        router_import: Optional[str] = None
        if node.args:
            router_expression = _unparse(node.args[0])
            base = router_expression.split(".")[0]
            router_import = aliases.get(base)

        prefix = None
        tags = None
        for kw in node.keywords:
            if kw.arg == "prefix":
                prefix = _literal_or_source(kw.value)
            if kw.arg == "tags":
                tags = _literal_or_source(kw.value)

        calls.append(
            {
                "line": getattr(node, "lineno", None),
                "router_expression": router_expression,
                "router_import": router_import,
                "prefix": prefix,
                "tags": tags,
            }
        )

    return calls


def _discover_router_exports() -> List[Dict[str, Any]]:
    exports: List[Dict[str, Any]] = []
    if not API_DIR.exists():
        return exports

    for path in sorted(API_DIR.glob("*.py")):
        source = _read(path)
        if "APIRouter" not in source:
            continue

        try:
            tree = ast.parse(source)
        except SyntaxError as exc:
            exports.append(
                {
                    "module_path": str(path.relative_to(ROOT)).replace("\\", "/"),
                    "syntax_error": str(exc),
                    "router_variables": [],
                }
            )
            continue

        router_vars: List[Dict[str, Any]] = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.Assign):
                continue
            if not isinstance(node.value, ast.Call):
                continue

            callee = _unparse(node.value.func)
            if "APIRouter" not in callee:
                continue

            names = []
            for target in node.targets:
                if isinstance(target, ast.Name):
                    names.append(target.id)

            kwargs: Dict[str, Any] = {}
            for kw in node.value.keywords:
                if kw.arg:
                    kwargs[kw.arg] = _literal_or_source(kw.value)

            for name in names:
                router_vars.append({"name": name, "kwargs": kwargs})

        if router_vars:
            exports.append(
                {
                    "module_path": str(path.relative_to(ROOT)).replace("\\", "/"),
                    "module_import": "claire.api." + path.stem,
                    "router_variables": router_vars,
                }
            )

    return exports


def _prove_safe_router(
    include_calls: List[Dict[str, Any]], router_exports: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Conservative proof.

    A router is considered only "candidate_visible" here, not safe-proven,
    unless a future build adds an explicit allowlist. S33R6 intentionally does
    not infer safety from names alone.
    """

    candidates: List[Dict[str, Any]] = []

    export_map: Dict[str, Dict[str, Any]] = {}
    for export in router_exports:
        module_import = export.get("module_import")
        for router_var in export.get("router_variables", []):
            key = f"{module_import}.{router_var.get('name')}"
            export_map[key] = {
                "module_import": module_import,
                "router_name": router_var.get("name"),
                "kwargs": router_var.get("kwargs", {}),
                "module_path": export.get("module_path"),
            }

    for call in include_calls:
        router_import = call.get("router_import")
        router_expression = call.get("router_expression")
        if not router_expression:
            continue

        possible_keys = []
        if router_import:
            possible_keys.append(router_import)
        if "." in router_expression and router_import:
            suffix = ".".join(router_expression.split(".")[1:])
            possible_keys.append(f"{router_import}.{suffix}")

        matched = [export_map[k] for k in possible_keys if k in export_map]
        if matched:
            candidates.append({"include_call": call, "matched_exports": matched})
        else:
            candidates.append({"include_call": call, "matched_exports": []})

    return {
        "safe_mounted_router_proven": False,
        "proof_level": "candidate_visible_only",
        "reason": (
            "Mounted routers and APIRouter exports were inspected, but S33R6 does "
            "not mark any router safe without an explicit allowlist/proof contract. "
            "Endpoint registration remains blocked."
        ),
        "candidate_matches": candidates,
    }


def get_mounted_router_proof_audit() -> Dict[str, Any]:
    include_calls = _discover_app_include_router_calls()
    router_exports = _discover_router_exports()
    proof = _prove_safe_router(include_calls, router_exports)

    return {
        "version": "v19.89.8-S33R6",
        "status": "mounted_router_proof_audit_visible",
        "changed_app_py": False,
        "route_registered": False,
        "endpoint_registration_allowed": False,
        "network_request": "blocked",
        "response_body_reads": "blocked",
        "browser_execution": "blocked",
        "runtime_truth_mutation": "blocked",
        "autonomous_execution": "blocked",
        "automatic_updates": "blocked",
        "manual_promotion_required": True,
        "evidence_quarantine_required": True,
        "app_file_inspected": APP_FILE.exists(),
        "api_dir_inspected": API_DIR.exists(),
        "include_router_calls": include_calls,
        "api_router_exports": router_exports,
        "proof": proof,
        "next_allowed_step": (
            "Add explicit safe-router allowlist/proof contract, or keep endpoint "
            "registration blocked and continue cockpit-only readiness."
        ),
    }
