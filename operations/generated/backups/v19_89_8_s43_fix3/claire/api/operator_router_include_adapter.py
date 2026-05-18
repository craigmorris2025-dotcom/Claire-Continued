from __future__ import annotations

"""Non-invasive read-only operator router include adapter.

This module is intentionally passive. It can inspect, plan, and optionally include
an operator router when a caller explicitly passes an app object. It does not
import or patch app.py, does not mutate runtime truth, and exposes no execution,
update, browser, or JavaScript authority.
"""

from dataclasses import dataclass, asdict
from importlib import import_module
from typing import Any


CANDIDATE_APP_MODULES: tuple[str, ...] = (
    "claire.app",
    "main",
)

CANDIDATE_APP_ATTRIBUTES: tuple[str, ...] = (
    "app",
    "application",
)

GOVERNANCE: dict[str, bool] = {
    "non_invasive": True,
    "read_only": True,
    "app_py_patching": False,
    "runtime_authority": False,
    "runtime_truth_mutation": False,
    "autonomous_execution": False,
    "automatic_updates": False,
    "browser_execution": False,
    "javascript_execution": False,
}


@dataclass(frozen=True)
class AppDiscoveryCandidate:
    module: str
    attribute: str | None
    available: bool
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _has_include_router(app: Any) -> bool:
    return callable(getattr(app, "include_router", None))


def discover_app_candidates() -> dict[str, Any]:
    """Return a passive inventory of candidate app modules/attributes."""
    candidates: list[dict[str, Any]] = []

    for module_name in CANDIDATE_APP_MODULES:
        try:
            module = import_module(module_name)
        except Exception as exc:  # pragma: no cover - defensive discovery only
            candidates.append(
                AppDiscoveryCandidate(
                    module=module_name,
                    attribute=None,
                    available=False,
                    reason=f"import_failed:{exc.__class__.__name__}",
                ).to_dict()
            )
            continue

        found_attribute = False
        for attr in CANDIDATE_APP_ATTRIBUTES:
            app = getattr(module, attr, None)
            if app is None:
                continue
            found_attribute = True
            candidates.append(
                AppDiscoveryCandidate(
                    module=module_name,
                    attribute=attr,
                    available=_has_include_router(app),
                    reason="fastapi_like_app_found" if _has_include_router(app) else "attribute_not_fastapi_like",
                ).to_dict()
            )

        create_app = getattr(module, "create_app", None)
        if callable(create_app):
            candidates.append(
                AppDiscoveryCandidate(
                    module=module_name,
                    attribute="create_app",
                    available=True,
                    reason="factory_found_not_invoked",
                ).to_dict()
            )
            found_attribute = True

        if not found_attribute:
            candidates.append(
                AppDiscoveryCandidate(
                    module=module_name,
                    attribute=None,
                    available=False,
                    reason="module_imported_no_known_app_attribute",
                ).to_dict()
            )

    return {
        "phase": "S42/S43 operator include adapter discovery",
        "candidates": candidates,
        "governance": GOVERNANCE.copy(),
    }


def discover_app_path() -> dict[str, Any]:
    """Compatibility wrapper used by earlier S43 probes."""
    inventory = discover_app_candidates()
    selected = next((c for c in inventory["candidates"] if c.get("available")), None)
    return {
        "selected": selected,
        "candidates": inventory["candidates"],
        "governance": GOVERNANCE.copy(),
    }


def build_include_plan(prefix: str = "/operator") -> dict[str, Any]:
    return {
        "action": "include_router",
        "target_prefix": prefix,
        "non_invasive": True,
        "requires_explicit_app_object": True,
        "patch_app_py": False,
        "governance": GOVERNANCE.copy(),
    }


def build_router_include_plan(prefix: str = "/operator") -> dict[str, Any]:
    return build_include_plan(prefix=prefix)


def include_operator_router_if_allowed(app: Any, *, allow_include: bool = False) -> dict[str, Any]:
    """Optionally include the read-only router only when explicitly allowed.

    Default behavior is no-op to preserve non-invasive discovery tests.
    """
    if not allow_include:
        return {
            "included": False,
            "reason": "explicit_allow_include_required",
            "governance": GOVERNANCE.copy(),
        }

    if not _has_include_router(app):
        return {
            "included": False,
            "reason": "app_missing_include_router",
            "governance": GOVERNANCE.copy(),
        }

    from claire.api.operator_read_only_router import router

    app.include_router(router)
    return {
        "included": True,
        "reason": "read_only_operator_router_included_by_explicit_call",
        "governance": GOVERNANCE.copy(),
    }


def include_operator_router(app: Any, *, allow_include: bool = False) -> dict[str, Any]:
    return include_operator_router_if_allowed(app, allow_include=allow_include)


def mount_operator_router(app: Any, *, allow_include: bool = False) -> dict[str, Any]:
    return include_operator_router_if_allowed(app, allow_include=allow_include)
