

"""

Claire Syntalion v19.88.3

Live Source Catalog Activation routes.



These endpoints expose backend-owned operational truth for live-source catalog

readiness. They do not generate speculative feed results and do not mutate

runtime truth.

"""



from __future__ import annotations



import importlib

import json

import os

from datetime import datetime, timezone

from pathlib import Path

from typing import Any



from fastapi import APIRouter





router = APIRouter(prefix="/api/feeds/live-source-catalog", tags=["live-source-catalog"])





REQUIRED_CANONICAL_SURFACES = (

    "/health",

    "/dashboard/payload/status",

    "/runtime/continuous/status",

    "/api/dashboard/search/provider/status",

)



SOURCE_UNIVERSE_HINTS = (

    "source_universe",

    "source_universes",

    "source_catalog",

    "live_source_catalog",

    "governed_source",

    "trusted_source",

    "allowlist",

    "provider_registry",

)





def _utc_now() -> str:

    return datetime.now(timezone.utc).isoformat()





def _project_root() -> Path:

    return Path(__file__).resolve().parents[2]





def _safe_read_json(path: Path) -> Any | None:

    try:

        if path.exists() and path.is_file():

            return json.loads(path.read_text(encoding="utf-8"))

    except Exception:

        return None

    return None





def _discover_source_files() -> list[dict[str, Any]]:

    root = _project_root()

    allowed_roots = [

        root / "claire",

        root / "backend",

        root / "data",

        root / "config",

        root / "configs",

        root / "operations",

    ]



    discovered: list[dict[str, Any]] = []



    for base in allowed_roots:

        if not base.exists():

            continue



        for path in base.rglob("*"):

            if not path.is_file():

                continue



            lower_path = str(path.relative_to(root)).lower()



            if not any(hint in lower_path for hint in SOURCE_UNIVERSE_HINTS):

                continue



            if path.suffix.lower() not in {".json", ".yaml", ".yml", ".py", ".toml", ".md", ".txt"}:

                continue



            item: dict[str, Any] = {

                "path": str(path.relative_to(root)).replace("\\", "/"),

                "kind": path.suffix.lower().lstrip(".") or "file",

                "size_bytes": path.stat().st_size,

            }



            if path.suffix.lower() == ".json":

                data = _safe_read_json(path)

                if isinstance(data, dict):

                    item["json_keys"] = sorted(list(data.keys()))[:20]

                    for key in ("sources", "providers", "allowlist", "trusted_sources", "universes"):

                        value = data.get(key)

                        if isinstance(value, list):

                            item[f"{key}_count"] = len(value)

                        elif isinstance(value, dict):

                            item[f"{key}_count"] = len(value.keys())

                elif isinstance(data, list):

                    item["json_list_count"] = len(data)



            discovered.append(item)



    discovered.sort(key=lambda x: x["path"])

    return discovered[:200]





def _optional_import_status() -> list[dict[str, Any]]:

    candidates = (

        "runtime_core.api.dashboard_search_provider_routes",

        "runtime_core.api.search_provider_routes",

        "claire.search.provider_registry",

        "claire.search.source_universe",

        "claire.governance.source_universe",

        "claire.governance.source_catalog",

        "claire.runtime.continuous_runtime",

    )

    results: list[dict[str, Any]] = []



    for module_name in candidates:

        try:

            importlib.import_module(module_name)

            results.append({"module": module_name, "available": True})

        except Exception as exc:

            results.append({

                "module": module_name,

                "available": False,

                "reason": exc.__class__.__name__,

            })



    return results





def _env_governance_state() -> dict[str, Any]:

    live_flags = {

        "PLATFORM_ALLOW_REAL_SEARCH_PROVIDER": os.getenv("PLATFORM_ALLOW_REAL_SEARCH_PROVIDER"),

        "PLATFORM_ALLOW_CONTROLLED_HEAD_PROBE": os.getenv("PLATFORM_ALLOW_CONTROLLED_HEAD_PROBE"),

        "PLATFORM_ALLOW_CONTROLLED_METADATA_GET": os.getenv("PLATFORM_ALLOW_CONTROLLED_METADATA_GET"),

        "PLATFORM_ALLOW_CONTROLLED_LIMITED_BODY_GET": os.getenv("PLATFORM_ALLOW_CONTROLLED_LIMITED_BODY_GET"),

    }



    enabled = {

        key: str(value).strip().lower() in {"1", "true", "yes", "on"}

        for key, value in live_flags.items()

    }



    return {

        "live_execution_flags_present": {key: value is not None for key, value in live_flags.items()},

        "live_execution_flags_enabled": enabled,

        "fail_closed_default": not any(enabled.values()),

    }





def _catalog_truth() -> dict[str, Any]:

    discovered_files = _discover_source_files()

    optional_modules = _optional_import_status()

    governance = _env_governance_state()



    module_available_count = sum(1 for item in optional_modules if item.get("available"))

    source_file_count = len(discovered_files)



    catalog_available = source_file_count > 0 or module_available_count > 0



    if not catalog_available:

        state = "not_configured"

    elif governance["fail_closed_default"]:

        state = "configured_fail_closed"

    else:

        state = "configured_live_gated"



    return {

        "version": "19.88.3",

        "surface": "live_source_catalog",

        "timestamp_utc": _utc_now(),

        "state": state,

        "catalog_available": catalog_available,

        "source_file_count": source_file_count,

        "optional_module_available_count": module_available_count,

        "governance": governance,

        "canonical_dependencies": list(REQUIRED_CANONICAL_SURFACES),

        "discovered_source_files": discovered_files,

        "optional_module_status": optional_modules,

        "truth_contract": {

            "backend_owns_truth": True,

            "cockpit_presentation_only": True,

            "speculative_outputs": False,

            "runtime_truth_mutation": False,

            "fail_closed_governance": True,

        },

    }





@router.get("/status")

def live_source_catalog_status() -> dict[str, Any]:

    truth = _catalog_truth()

    return {

        "ok": truth["catalog_available"],

        "status": truth["state"],

        "message": (

            "Live source catalog surface is mounted and reporting backend-owned readiness truth."

            if truth["catalog_available"]

            else "Live source catalog surface is mounted, but no governed source catalog/provider universe was discovered."

        ),

        **truth,

    }





@router.get("/health")

def live_source_catalog_health() -> dict[str, Any]:

    truth = _catalog_truth()

    healthy = truth["catalog_available"]

    return {

        "ok": healthy,

        "status": "healthy" if healthy else "not_configured",

        "surface": "live_source_catalog_health",

        "timestamp_utc": _utc_now(),

        "catalog_available": truth["catalog_available"],

        "source_file_count": truth["source_file_count"],

        "optional_module_available_count": truth["optional_module_available_count"],

        "fail_closed_default": truth["governance"]["fail_closed_default"],

        "truth_contract": truth["truth_contract"],

    }

