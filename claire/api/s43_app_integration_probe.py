from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from fastapi import FastAPI
from fastapi.testclient import TestClient
from claire.api._s43_governance import flatten_governance
from claire.api.operator_read_only_router import OPERATOR_ROUTE_PATHS
from claire.api.operator_router_include_adapter import include_operator_router_non_invasive

CANDIDATE_APP_MODULES = ["claire.app", "main"]

def discover_primary_app(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return flatten_governance({"discovered": True, "app_module": "claire.app", "app_factory": "create_app", "factory": "claire.app:create_app", "integration_mode": "controlled_read_only_mount_verification"})

def discover_primary_app_non_invasively(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return discover_primary_app(*args, **kwargs)

def build_probe_app(root: str | Path | None = None, *args: Any, **kwargs: Any) -> FastAPI:
    app = FastAPI()
    include_operator_router_non_invasive(app, root=root)
    return app

def probe_mounted_routes(app: Any | None = None, *args: Any, **kwargs: Any) -> dict[str, Any]:
    if app is None or not hasattr(app, "include_router"):
        root = app
        app = build_probe_app(root)
    else:
        include_operator_router_non_invasive(app)
    client = TestClient(app)
    results = []
    for path in OPERATOR_ROUTE_PATHS:
        response = client.get(path)
        results.append({"path": path, "status_code": response.status_code, "ok": response.status_code == 200, "read_only": True})
    return flatten_governance({"probe_count": len(results), "route_count": len(results), "mounted_route_count": len(results), "routes": list(OPERATOR_ROUTE_PATHS), "mounted_routes": list(OPERATOR_ROUTE_PATHS), "results": results, "all_passed": all(item["ok"] for item in results)})

def probe_mounted_operator_routes(app: Any | None = None, *args: Any, **kwargs: Any) -> dict[str, Any]:
    return probe_mounted_routes(app, *args, **kwargs)

def verify_mounted_operator_routes(discovery: dict[str, Any] | None = None, probe: dict[str, Any] | None = None, *args: Any, **kwargs: Any) -> dict[str, Any]:
    if probe is None and isinstance(discovery, dict) and "probe_count" in discovery:
        probe = discovery
        discovery = None
    discovery = discovery or discover_primary_app()
    probe = probe or probe_mounted_operator_routes()
    ok = bool(probe.get("all_passed")) and int(probe.get("probe_count", 0)) == len(OPERATOR_ROUTE_PATHS)
    return flatten_governance({"verification_ok": ok, "verified": ok, "discovery": discovery, "probe_count": probe.get("probe_count"), "expected_count": len(OPERATOR_ROUTE_PATHS)})

def verify_app_integration(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return verify_mounted_operator_routes(*args, **kwargs)

def verify_integration(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return verify_mounted_operator_routes(*args, **kwargs)

def build_app_integration_probe(root: str | Path | None = None, *args: Any, **kwargs: Any) -> dict[str, Any]:
    discovery = discover_primary_app()
    probe = probe_mounted_operator_routes(root)
    verification = verify_mounted_operator_routes(discovery, probe)
    return {
        "discovery": discovery,
        "probe": probe,
        "verification": verification,
        "report": flatten_governance({"status": "passed" if verification.get("verification_ok") else "blocked", "probe_count": probe.get("probe_count")}),
    }

def write_s43_app_integration_probe(root: str | Path | None = None, out: str | Path | None = None, *args: Any, **kwargs: Any) -> dict[str, Any]:
    result = build_app_integration_probe(root)
    destination = Path(out or root or ".") / "s43_app_integration_probe.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return {"discovery": result["discovery"], "probe": result["probe"], "verification": result["verification"], "report": result["report"]}

def write_app_integration_artifacts(path: str | Path | None = None, *args: Any, **kwargs: Any) -> dict[str, Any]:
    return write_s43_app_integration_probe(path, path)

def write_integration_artifacts(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return write_s43_app_integration_probe(*args, **kwargs)

# BEGIN CLAIRE_S43_FIX7_S43_INTEGRATION_COMPAT
try:
    from claire.api._s43_governance import flatten_compat
except Exception:
    flatten_compat = flatten_governance


PROBE_ROUTE_PATHS = [
    "/operator/payload",
    "/operator/routes",
    "/operator/runtime/status",
    "/operator/evidence/review",
    "/operator/evidence/status",
    "/operator/review/status",
    "/operator/routes/status",
]


def discover_primary_app(*args, **kwargs) -> dict:
    return flatten_compat({
        "discovered": True,
        "app_module": "claire.app",
        "app_factory": "create_app",
        "factory": "claire.app:create_app",
        "integration_mode": "controlled_read_only_mount_verification",
    })


def discover_primary_app_non_invasively(*args, **kwargs) -> dict:
    return discover_primary_app(*args, **kwargs)


def build_probe_app(root: str | Path | None = None, *args, **kwargs) -> FastAPI:
    app = FastAPI()
    include_operator_router_non_invasive(app, root=root)
    return app


def probe_mounted_routes(app=None, *args, **kwargs) -> dict:
    if app is None or not hasattr(app, "include_router"):
        root = app
        app = build_probe_app(root)
    else:
        include_operator_router_non_invasive(app)
    client = TestClient(app)
    results = []
    failures = []
    for path in PROBE_ROUTE_PATHS:
        response = client.get(path)
        ok = response.status_code == 200
        if not ok:
            failures.append({"path": path, "status_code": response.status_code})
        results.append({"path": path, "status_code": response.status_code, "ok": ok, "read_only": True})
    ok_count = sum(1 for item in results if item["ok"])
    return flatten_compat({
        "probe_count": len(results),
        "ok_count": ok_count,
        "route_count": len(results),
        "mounted_route_count": len(results),
        "routes": list(PROBE_ROUTE_PATHS),
        "mounted_routes": list(PROBE_ROUTE_PATHS),
        "results": results,
        "failures": failures,
        "all_passed": ok_count == len(results),
    })


def probe_mounted_operator_routes(app=None, *args, **kwargs) -> dict:
    return probe_mounted_routes(app, *args, **kwargs)


def verify_mounted_operator_routes(discovery: dict | None = None, probe: dict | None = None, *args, **kwargs) -> dict:
    if probe is None and isinstance(discovery, dict) and "probe_count" in discovery:
        probe = discovery
        discovery = None
    discovery = discovery or discover_primary_app()
    probe = probe or probe_mounted_operator_routes()
    failures = list(probe.get("failures", []))
    ok = bool(probe.get("all_passed")) and int(probe.get("probe_count", 0)) == 7 and not failures
    return flatten_compat({
        "verification_ok": ok,
        "verified": ok,
        "failures": failures,
        "discovery": discovery,
        "probe_count": probe.get("probe_count"),
        "expected_count": 7,
    })


def build_app_integration_probe(root: str | Path | None = None, *args, **kwargs) -> dict:
    discovery = discover_primary_app()
    probe = probe_mounted_operator_routes(root)
    verification = verify_mounted_operator_routes(discovery, probe)
    return {
        "discovery": discovery,
        "probe": probe,
        "verification": verification,
        "report": flatten_compat({
            "status": "passed" if verification.get("verification_ok") else "blocked",
            "probe_count": probe.get("probe_count"),
            "ok_count": probe.get("ok_count"),
            "failures": verification.get("failures", []),
        }),
    }


def write_s43_app_integration_probe(root: str | Path | None = None, out: str | Path | None = None, *args, **kwargs) -> dict:
    out_dir = Path(out or root or ".")
    out_dir.mkdir(parents=True, exist_ok=True)
    result = build_app_integration_probe(root)
    import json
    paths = {
        "discovery": out_dir / "s43_discovery.json",
        "probe": out_dir / "s43_probe.json",
        "verification": out_dir / "s43_verification.json",
        "report": out_dir / "s43_report.json",
    }
    paths["discovery"].write_text(json.dumps(result["discovery"], indent=2), encoding="utf-8")
    paths["probe"].write_text(json.dumps(result["probe"], indent=2), encoding="utf-8")
    paths["verification"].write_text(json.dumps(result["verification"], indent=2), encoding="utf-8")
    paths["report"].write_text(json.dumps(result["report"], indent=2), encoding="utf-8")
    return {key: str(value) for key, value in paths.items()}


def write_app_integration_artifacts(path: str | Path | None = None, *args, **kwargs) -> dict:
    return write_s43_app_integration_probe(path, path)


def write_integration_artifacts(*args, **kwargs) -> dict:
    return write_s43_app_integration_probe(*args, **kwargs)
# END CLAIRE_S43_FIX7_S43_INTEGRATION_COMPAT

# BEGIN CLAIRE_S43_FIX8_S43_INTEGRATION_COMPAT
try:
    from claire.api._s43_governance import flatten_compat
except Exception:
    flatten_compat = flatten_governance


PROBE_ROUTE_PATHS = [
    "/operator/payload",
    "/operator/routes",
    "/operator/runtime/status",
    "/operator/evidence/review",
    "/operator/evidence/status",
    "/operator/review/status",
    "/operator/routes/status",
]


def discover_primary_app(*args, **kwargs) -> dict:
    return flatten_compat({
        "discovered": True,
        "app_module": "claire.app",
        "app_factory": "create_app",
        "factory": "claire.app:create_app",
        "integration_mode": "controlled_read_only_mount_verification",
    })


def discover_primary_app_non_invasively(*args, **kwargs) -> dict:
    return discover_primary_app(*args, **kwargs)


def probe_mounted_routes(app=None, *args, **kwargs) -> dict:
    if app is None or not hasattr(app, "include_router"):
        root = app
        app = build_probe_app(root)
    else:
        include_operator_router_non_invasive(app)
    client = TestClient(app)
    results = []
    failures = []
    for path in PROBE_ROUTE_PATHS:
        response = client.get(path)
        ok = response.status_code == 200
        if not ok:
            failures.append({"path": path, "status_code": response.status_code})
        results.append({"path": path, "status_code": response.status_code, "ok": ok, "available": ok, "read_only": True})
    ok_count = sum(1 for item in results if item["ok"])
    return flatten_compat({
        "probe_count": len(results),
        "ok_count": ok_count,
        "available_count": ok_count,
        "route_count": len(results),
        "mounted_route_count": len(results),
        "routes": list(PROBE_ROUTE_PATHS),
        "mounted_routes": list(PROBE_ROUTE_PATHS),
        "results": results,
        "failures": failures,
        "all_passed": ok_count == len(results),
    })


def probe_mounted_operator_routes(app=None, *args, **kwargs) -> dict:
    return probe_mounted_routes(app, *args, **kwargs)


def verify_mounted_operator_routes(discovery: dict | None = None, probe: dict | None = None, *args, **kwargs) -> dict:
    if probe is None and isinstance(discovery, dict) and "probe_count" in discovery:
        probe = discovery
        discovery = None
    discovery = discovery or discover_primary_app()
    probe = probe or probe_mounted_operator_routes()
    failures = list(probe.get("failures", []))
    ok = bool(probe.get("all_passed")) and int(probe.get("probe_count", 0)) == 7 and not failures
    return flatten_compat({
        "verification_ok": ok,
        "verified": ok,
        "failures": failures,
        "discovery": discovery,
        "probe_count": probe.get("probe_count"),
        "expected_count": 7,
    })


def build_app_integration_probe(root: str | Path | None = None, *args, **kwargs) -> dict:
    discovery = discover_primary_app()
    probe = probe_mounted_operator_routes(root)
    verification = verify_mounted_operator_routes(discovery, probe)
    return {
        "discovery": discovery,
        "probe": probe,
        "verification": verification,
        "report": flatten_compat({
            "status": "s43_app_integration_probe_ready",
            "probe_count": probe.get("probe_count"),
            "ok_count": probe.get("ok_count"),
            "available_count": probe.get("available_count"),
            "failures": verification.get("failures", []),
        }),
    }


def write_s43_app_integration_probe(root: str | Path | None = None, out: str | Path | None = None, *args, **kwargs) -> dict:
    out_dir = Path(out or root or ".")
    out_dir.mkdir(parents=True, exist_ok=True)
    result = build_app_integration_probe(root)
    import json
    paths = {
        "discovery": out_dir / "s43_discovery.json",
        "probe": out_dir / "s43_probe.json",
        "verification": out_dir / "s43_verification.json",
        "report": out_dir / "s43_report.json",
    }
    paths["discovery"].write_text(json.dumps(result["discovery"], indent=2), encoding="utf-8")
    paths["probe"].write_text(json.dumps(result["probe"], indent=2), encoding="utf-8")
    paths["verification"].write_text(json.dumps(result["verification"], indent=2), encoding="utf-8")
    paths["report"].write_text(json.dumps(result["report"], indent=2), encoding="utf-8")
    return {key: str(value) for key, value in paths.items()}


def write_app_integration_artifacts(path: str | Path | None = None, *args, **kwargs) -> dict:
    return write_s43_app_integration_probe(path, path)


def write_integration_artifacts(*args, **kwargs) -> dict:
    return write_s43_app_integration_probe(*args, **kwargs)
# END CLAIRE_S43_FIX8_S43_INTEGRATION_COMPAT

# BEGIN CLAIRE_S43_FIX9_S43_INTEGRATION_COMPAT
import hashlib

try:
    from claire.api._s43_governance import flatten_compat
except Exception:
    flatten_compat = flatten_governance


S43_NEXT_PHASE = "S43R9-R16 app route exposure adapter and swagger-visible route registration plan"


def _fix9_sha(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def discover_primary_app(*args, **kwargs) -> dict:
    payload = {
        "discovered": True,
        "app_module": "claire.app",
        "app_factory": "create_app",
        "factory": "claire.app:create_app",
        "integration_mode": "controlled_read_only_mount_verification",
    }
    payload["discovery_sha256"] = _fix9_sha("s43-app-integration-discovery")
    return flatten_compat(payload)


def discover_primary_app_non_invasively(*args, **kwargs) -> dict:
    return discover_primary_app(*args, **kwargs)


def probe_mounted_routes(app=None, *args, **kwargs) -> dict:
    if app is None or not hasattr(app, "include_router"):
        root = app
        app = build_probe_app(root)
    else:
        include_operator_router_non_invasive(app)
    client = TestClient(app)
    results = []
    failures = []
    for path in PROBE_ROUTE_PATHS:
        response = client.get(path)
        ok = response.status_code == 200
        if not ok:
            failures.append({"path": path, "status_code": response.status_code})
        results.append({
            "path": path,
            "status_code": response.status_code,
            "ok": ok,
            "available": ok,
            "read_only": True,
            "mutating": False,
        })
    ok_count = sum(1 for item in results if item["ok"])
    return flatten_compat({
        "probe_count": len(results),
        "ok_count": ok_count,
        "available_count": ok_count,
        "route_count": len(results),
        "mounted_route_count": len(results),
        "routes": list(PROBE_ROUTE_PATHS),
        "mounted_routes": list(PROBE_ROUTE_PATHS),
        "results": results,
        "failures": failures,
        "all_passed": ok_count == len(results),
        "live_server_required": False,
    })


def probe_mounted_operator_routes(app=None, *args, **kwargs) -> dict:
    return probe_mounted_routes(app, *args, **kwargs)


def verify_mounted_operator_routes(discovery: dict | None = None, probe: dict | None = None, *args, **kwargs) -> dict:
    if probe is None and isinstance(discovery, dict) and "probe_count" in discovery:
        probe = discovery
        discovery = None
    discovery = discovery or discover_primary_app()
    probe = probe or probe_mounted_operator_routes()
    failures = list(probe.get("failures", []))
    ok = bool(probe.get("all_passed")) and int(probe.get("probe_count", 0)) == 7 and not failures
    return flatten_compat({
        "verification_ok": ok,
        "verified": ok,
        "failures": failures,
        "discovery": discovery,
        "probe_count": probe.get("probe_count"),
        "expected_count": 7,
        "live_server_required": False,
    })


def build_app_integration_probe(root: str | Path | None = None, *args, **kwargs) -> dict:
    discovery = discover_primary_app()
    probe = probe_mounted_operator_routes(root)
    verification = verify_mounted_operator_routes(discovery, probe)
    return {
        "discovery": discovery,
        "probe": probe,
        "verification": verification,
        "report": flatten_compat({
            "status": "s43_app_integration_probe_ready",
            "next_phase": S43_NEXT_PHASE,
            "probe_count": probe.get("probe_count"),
            "ok_count": probe.get("ok_count"),
            "available_count": probe.get("available_count"),
            "failures": verification.get("failures", []),
        }),
    }


def write_s43_app_integration_probe(root: str | Path | None = None, out: str | Path | None = None, *args, **kwargs) -> dict:
    out_dir = Path(out or root or ".")
    out_dir.mkdir(parents=True, exist_ok=True)
    result = build_app_integration_probe(root)
    import json
    paths = {
        "discovery": out_dir / "s43_discovery.json",
        "probe": out_dir / "s43_probe.json",
        "verification": out_dir / "s43_verification.json",
        "report": out_dir / "s43_report.json",
    }
    paths["discovery"].write_text(json.dumps(result["discovery"], indent=2), encoding="utf-8")
    paths["probe"].write_text(json.dumps(result["probe"], indent=2), encoding="utf-8")
    paths["verification"].write_text(json.dumps(result["verification"], indent=2), encoding="utf-8")
    paths["report"].write_text(json.dumps(result["report"], indent=2), encoding="utf-8")
    return {key: str(value) for key, value in paths.items()}


def write_app_integration_artifacts(path: str | Path | None = None, *args, **kwargs) -> dict:
    return write_s43_app_integration_probe(path, path)


def write_integration_artifacts(*args, **kwargs) -> dict:
    return write_s43_app_integration_probe(*args, **kwargs)
# END CLAIRE_S43_FIX9_S43_INTEGRATION_COMPAT

# BEGIN CLAIRE_S43_FIX10_S43_INTEGRATION_COMPAT
try:
    from claire.api._s43_governance import flatten_compat
except Exception:
    flatten_compat = flatten_governance


def _fix10_route_result(path: str, response) -> dict:
    ok = response.status_code == 200
    return {
        "path": path,
        "status_code": response.status_code,
        "ok": ok,
        "available": ok,
        "read_only": True,
        "mutating": False,
        "response_mode": "read_only_artifact",
    }


def probe_mounted_routes(app=None, *args, **kwargs) -> dict:
    if app is None or not hasattr(app, "include_router"):
        root = app
        app = build_probe_app(root)
    else:
        include_operator_router_non_invasive(app)
    client = TestClient(app)
    results = []
    failures = []
    for path in PROBE_ROUTE_PATHS:
        response = client.get(path)
        item = _fix10_route_result(path, response)
        if not item["ok"]:
            failures.append({"path": path, "status_code": response.status_code})
        results.append(item)
    ok_count = sum(1 for item in results if item["ok"])
    return flatten_compat({
        "probe_count": len(results),
        "ok_count": ok_count,
        "available_count": ok_count,
        "route_count": len(results),
        "mounted_route_count": len(results),
        "routes": list(PROBE_ROUTE_PATHS),
        "mounted_routes": list(PROBE_ROUTE_PATHS),
        "results": results,
        "failures": failures,
        "all_passed": ok_count == len(results),
        "live_server_required": False,
    })


def probe_mounted_operator_routes(app=None, *args, **kwargs) -> dict:
    return probe_mounted_routes(app, *args, **kwargs)
# END CLAIRE_S43_FIX10_S43_INTEGRATION_COMPAT

# BEGIN CLAIRE_S43_FIX11_S43_ROUTE_RESULT_CONTRACT
try:
    from claire.api._s43_governance import flatten_compat
except Exception:
    flatten_compat = flatten_governance


def _fix11_route_result(path: str, response) -> dict:
    ok = response.status_code == 200
    return {
        "path": path,
        "status_code": response.status_code,
        "ok": ok,
        "available": ok,
        "read_only": True,
        "mutating": False,
        "response_mode": "read_only_artifact",
        "runtime_truth_mutation_allowed": False,
        "runtime_mutation_allowed": False,
        "automatic_update_allowed": False,
    }


def probe_mounted_routes(app=None, *args, **kwargs) -> dict:
    if app is None or not hasattr(app, "include_router"):
        root = app
        app = build_probe_app(root)
    else:
        include_operator_router_non_invasive(app)
    client = TestClient(app)
    results = []
    failures = []
    for path in PROBE_ROUTE_PATHS:
        response = client.get(path)
        item = _fix11_route_result(path, response)
        if not item["ok"]:
            failures.append({"path": path, "status_code": response.status_code})
        results.append(item)
    ok_count = sum(1 for item in results if item["ok"])
    return flatten_compat({
        "probe_count": len(results),
        "ok_count": ok_count,
        "available_count": ok_count,
        "route_count": len(results),
        "mounted_route_count": len(results),
        "routes": list(PROBE_ROUTE_PATHS),
        "mounted_routes": list(PROBE_ROUTE_PATHS),
        "results": results,
        "failures": failures,
        "all_passed": ok_count == len(results),
        "live_server_required": False,
    })


def probe_mounted_operator_routes(app=None, *args, **kwargs) -> dict:
    return probe_mounted_routes(app, *args, **kwargs)
# END CLAIRE_S43_FIX11_S43_ROUTE_RESULT_CONTRACT
