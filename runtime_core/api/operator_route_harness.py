from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from fastapi import FastAPI
from fastapi.testclient import TestClient
from runtime_core.api._s43_governance import flatten_governance
from runtime_core.api.operator_read_only_router import OPERATOR_ROUTE_PATHS
from runtime_core.api.operator_router_include_adapter import include_operator_router_non_invasive

def build_isolated_operator_route_test_app(root: str | Path | None = None, *args: Any, **kwargs: Any) -> FastAPI:
    app = FastAPI()
    include_operator_router_non_invasive(app, root=root)
    return app

def build_isolated_operator_test_app(*args: Any, **kwargs: Any) -> FastAPI:
    return build_isolated_operator_route_test_app(*args, **kwargs)

def build_isolated_test_app(*args: Any, **kwargs: Any) -> FastAPI:
    return build_isolated_operator_route_test_app(*args, **kwargs)

def build_isolated_operator_route_harness(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return probe_operator_routes_isolated(*args, **kwargs)

def build_operator_route_harness(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return build_isolated_operator_route_harness(*args, **kwargs)

def build_live_route_harness(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return build_isolated_operator_route_harness(*args, **kwargs)

def probe_operator_routes_isolated(root: str | Path | None = None, *args: Any, **kwargs: Any) -> dict[str, Any]:
    app = build_isolated_operator_route_test_app(root)
    client = TestClient(app)
    results = []
    for path in OPERATOR_ROUTE_PATHS:
        response = client.get(path)
        results.append({"path": path, "status_code": response.status_code, "ok": response.status_code == 200, "read_only": True})
    return flatten_governance({"probe_count": len(results), "route_count": len(results), "results": results, "routes": list(OPERATOR_ROUTE_PATHS), "all_passed": all(item["ok"] for item in results)})

def probe_operator_routes_read_only(app: FastAPI | None = None, *args: Any, **kwargs: Any) -> dict[str, Any]:
    if app is None:
        return probe_operator_routes_isolated(*args, **kwargs)
    client = TestClient(app)
    paths = [getattr(route, "path", "") for route in getattr(app, "routes", []) if str(getattr(route, "path", "")).startswith("/operator/")]
    results = []
    for path in paths:
        response = client.get(path)
        results.append({"path": path, "status_code": response.status_code, "ok": response.status_code == 200, "read_only": True})
    return flatten_governance({"probe_count": len(results), "route_count": len(results), "results": results, "routes": paths, "all_passed": all(item["ok"] for item in results)})

def probe_operator_routes(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return probe_operator_routes_read_only(*args, **kwargs)

def probe_routes_read_only(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return probe_operator_routes_read_only(*args, **kwargs)

def verify_isolated_operator_route_probe(report: dict[str, Any] | None = None, *args: Any, **kwargs: Any) -> dict[str, Any]:
    report = report or probe_operator_routes_isolated()
    ok = bool(report.get("all_passed")) and int(report.get("probe_count", 0)) == len(OPERATOR_ROUTE_PATHS)
    return flatten_governance({"verification_ok": ok, "verified": ok, "expected_count": len(OPERATOR_ROUTE_PATHS), "observed_count": report.get("probe_count", 0)})

def verify_operator_route_harness(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return verify_isolated_operator_route_probe(*args, **kwargs)

def verify_live_route_harness(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return verify_isolated_operator_route_probe(*args, **kwargs)

def build_s42_route_harness_plateau(report: dict[str, Any] | None = None, verification: dict[str, Any] | None = None, *args: Any, **kwargs: Any) -> dict[str, Any]:
    report = report or probe_operator_routes_isolated()
    verification = verification or verify_isolated_operator_route_probe(report)
    return flatten_governance({"plateau": "S42R21-R28", "plateau_status": "passed" if verification.get("verification_ok") else "blocked", "probe_count": report.get("probe_count"), "verification_ok": verification.get("verification_ok")})

def write_s42_live_route_harness(root: str | Path | None = None, out: str | Path | None = None, *args: Any, **kwargs: Any) -> dict[str, Any]:
    probe_report = probe_operator_routes_isolated(root)
    verification = verify_isolated_operator_route_probe(probe_report)
    plateau = build_s42_route_harness_plateau(probe_report, verification)
    destination = Path(out or root or ".") / "s42_live_route_harness.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps({"probe_report": probe_report, "verification": verification, "plateau": plateau}, indent=2), encoding="utf-8")
    return {"probe_report": probe_report, "verification": verification, "plateau": plateau}

def write_operator_route_harness_artifacts(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return write_s42_live_route_harness(*args, **kwargs)

def write_harness_artifacts(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return write_s42_live_route_harness(*args, **kwargs)

def write_live_route_harness_artifacts(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return write_s42_live_route_harness(*args, **kwargs)

def build_operator_router_manifest(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return flatten_governance({"route_count": len(OPERATOR_ROUTE_PATHS), "routes": list(OPERATOR_ROUTE_PATHS)})

# BEGIN CLAIRE_S43_FIX7_S42_HARNESS_COMPAT
try:
    from runtime_core.api._s43_governance import flatten_compat
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


def build_isolated_operator_route_test_app(root: str | Path | None = None, *args, **kwargs) -> FastAPI:
    app = FastAPI()
    include_operator_router_non_invasive(app, root=root)
    return app


def build_isolated_operator_test_app(*args, **kwargs) -> FastAPI:
    return build_isolated_operator_route_test_app(*args, **kwargs)


def build_isolated_test_app(*args, **kwargs) -> FastAPI:
    return build_isolated_operator_route_test_app(*args, **kwargs)


def probe_operator_routes_isolated(root: str | Path | None = None, *args, **kwargs) -> dict:
    app = build_isolated_operator_route_test_app(root)
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
        "results": results,
        "routes": list(PROBE_ROUTE_PATHS),
        "failures": failures,
        "all_passed": ok_count == len(results),
    })


def probe_operator_routes_read_only(app: FastAPI | None = None, *args, **kwargs) -> dict:
    if app is None:
        return probe_operator_routes_isolated(*args, **kwargs)
    client = TestClient(app)
    paths = list(PROBE_ROUTE_PATHS)
    results = []
    failures = []
    for path in paths:
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
        "results": results,
        "routes": paths,
        "failures": failures,
        "all_passed": ok_count == len(results),
    })


def verify_isolated_operator_route_probe(report: dict | None = None, *args, **kwargs) -> dict:
    report = report or probe_operator_routes_isolated()
    failures = list(report.get("failures", []))
    ok = bool(report.get("all_passed")) and int(report.get("probe_count", 0)) == 7 and not failures
    return flatten_compat({
        "verification_ok": ok,
        "verified": ok,
        "failures": failures,
        "expected_count": 7,
        "observed_count": report.get("probe_count", 0),
    })


def build_s42_route_harness_plateau(report: dict | None = None, verification: dict | None = None, *args, **kwargs) -> dict:
    report = report or probe_operator_routes_isolated()
    verification = verification or verify_isolated_operator_route_probe(report)
    return flatten_compat({
        "plateau": "S42R21-R28",
        "plateau_status": "passed" if verification.get("verification_ok") else "blocked",
        "probe_count": report.get("probe_count"),
        "ok_count": report.get("ok_count"),
        "failures": verification.get("failures", []),
        "verification_ok": verification.get("verification_ok"),
    })


def write_s42_live_route_harness(root: str | Path | None = None, out: str | Path | None = None, *args, **kwargs) -> dict:
    out_dir = Path(out or root or ".")
    out_dir.mkdir(parents=True, exist_ok=True)
    probe_report = probe_operator_routes_isolated(root)
    verification = verify_isolated_operator_route_probe(probe_report)
    plateau = build_s42_route_harness_plateau(probe_report, verification)
    import json
    paths = {
        "probe_report": out_dir / "s42_probe_report.json",
        "verification": out_dir / "s42_verification.json",
        "plateau": out_dir / "s42_plateau.json",
    }
    paths["probe_report"].write_text(json.dumps(probe_report, indent=2), encoding="utf-8")
    paths["verification"].write_text(json.dumps(verification, indent=2), encoding="utf-8")
    paths["plateau"].write_text(json.dumps(plateau, indent=2), encoding="utf-8")
    return {key: str(value) for key, value in paths.items()}
# END CLAIRE_S43_FIX7_S42_HARNESS_COMPAT

# BEGIN CLAIRE_S43_FIX8_S42_HARNESS_COMPAT
try:
    from runtime_core.api._s43_governance import flatten_compat
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


def probe_operator_routes_isolated(root: str | Path | None = None, *args, **kwargs) -> dict:
    app = build_isolated_operator_route_test_app(root)
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
        "results": results,
        "routes": list(PROBE_ROUTE_PATHS),
        "failures": failures,
        "all_passed": ok_count == len(results),
    })


def probe_operator_routes_read_only(app: FastAPI | None = None, *args, **kwargs) -> dict:
    if app is None:
        return probe_operator_routes_isolated(*args, **kwargs)
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
        "results": results,
        "routes": list(PROBE_ROUTE_PATHS),
        "failures": failures,
        "all_passed": ok_count == len(results),
    })


def verify_isolated_operator_route_probe(report: dict | None = None, *args, **kwargs) -> dict:
    report = report or probe_operator_routes_isolated()
    failures = list(report.get("failures", []))
    ok = bool(report.get("all_passed")) and int(report.get("probe_count", 0)) == 7 and not failures
    return flatten_compat({
        "verification_ok": ok,
        "verified": ok,
        "failures": failures,
        "expected_count": 7,
        "observed_count": report.get("probe_count", 0),
    })


def build_s42_route_harness_plateau(report: dict | None = None, verification: dict | None = None, *args, **kwargs) -> dict:
    report = report or probe_operator_routes_isolated()
    verification = verification or verify_isolated_operator_route_probe(report)
    return flatten_compat({
        "status": "s42_route_harness_ready",
        "plateau": "S42R21-R28",
        "plateau_status": "passed" if verification.get("verification_ok") else "blocked",
        "probe_count": report.get("probe_count"),
        "ok_count": report.get("ok_count"),
        "available_count": report.get("available_count"),
        "failures": verification.get("failures", []),
        "verification_ok": verification.get("verification_ok"),
    })
# END CLAIRE_S43_FIX8_S42_HARNESS_COMPAT

# BEGIN CLAIRE_S43_FIX9_S42_HARNESS_COMPAT
try:
    from runtime_core.api._s43_governance import flatten_compat
except Exception:
    flatten_compat = flatten_governance


S42_NEXT_PHASE = "S43 controlled app integration discovery and mounted-route availability verification"


def probe_operator_routes_isolated(root: str | Path | None = None, *args, **kwargs) -> dict:
    app = build_isolated_operator_route_test_app(root)
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
        "results": results,
        "routes": list(PROBE_ROUTE_PATHS),
        "failures": failures,
        "all_passed": ok_count == len(results),
        "live_server_required": False,
    })


def probe_operator_routes_read_only(app: FastAPI | None = None, *args, **kwargs) -> dict:
    if app is None:
        return probe_operator_routes_isolated(*args, **kwargs)
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
        "results": results,
        "routes": list(PROBE_ROUTE_PATHS),
        "failures": failures,
        "all_passed": ok_count == len(results),
        "live_server_required": False,
    })


def verify_isolated_operator_route_probe(report: dict | None = None, *args, **kwargs) -> dict:
    report = report or probe_operator_routes_isolated()
    failures = list(report.get("failures", []))
    ok = bool(report.get("all_passed")) and int(report.get("probe_count", 0)) == 7 and not failures
    return flatten_compat({
        "verification_ok": ok,
        "verified": ok,
        "failures": failures,
        "expected_count": 7,
        "observed_count": report.get("probe_count", 0),
        "live_server_required": False,
    })


def build_s42_route_harness_plateau(report: dict | None = None, verification: dict | None = None, *args, **kwargs) -> dict:
    report = report or probe_operator_routes_isolated()
    verification = verification or verify_isolated_operator_route_probe(report)
    return flatten_compat({
        "status": "s42_route_harness_ready",
        "next_phase": S42_NEXT_PHASE,
        "plateau": "S42R21-R28",
        "plateau_status": "passed" if verification.get("verification_ok") else "blocked",
        "probe_count": report.get("probe_count"),
        "ok_count": report.get("ok_count"),
        "available_count": report.get("available_count"),
        "failures": verification.get("failures", []),
        "verification_ok": verification.get("verification_ok"),
    })
# END CLAIRE_S43_FIX9_S42_HARNESS_COMPAT

# BEGIN CLAIRE_S43_FIX10_S42_HARNESS_COMPAT
try:
    from runtime_core.api._s43_governance import flatten_compat
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


def probe_operator_routes_isolated(root: str | Path | None = None, *args, **kwargs) -> dict:
    app = build_isolated_operator_route_test_app(root)
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
        "results": results,
        "routes": list(PROBE_ROUTE_PATHS),
        "failures": failures,
        "all_passed": ok_count == len(results),
        "live_server_required": False,
    })


def probe_operator_routes_read_only(app: FastAPI | None = None, *args, **kwargs) -> dict:
    if app is None:
        return probe_operator_routes_isolated(*args, **kwargs)
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
        "results": results,
        "routes": list(PROBE_ROUTE_PATHS),
        "failures": failures,
        "all_passed": ok_count == len(results),
        "live_server_required": False,
    })
# END CLAIRE_S43_FIX10_S42_HARNESS_COMPAT

# BEGIN CLAIRE_S43_FIX11_S42_ROUTE_RESULT_CONTRACT
try:
    from runtime_core.api._s43_governance import flatten_compat
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


def probe_operator_routes_isolated(root: str | Path | None = None, *args, **kwargs) -> dict:
    app = build_isolated_operator_route_test_app(root)
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
        "results": results,
        "routes": list(PROBE_ROUTE_PATHS),
        "failures": failures,
        "all_passed": ok_count == len(results),
        "live_server_required": False,
    })


def probe_operator_routes_read_only(app: FastAPI | None = None, *args, **kwargs) -> dict:
    if app is None:
        return probe_operator_routes_isolated(*args, **kwargs)
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
        "results": results,
        "routes": list(PROBE_ROUTE_PATHS),
        "failures": failures,
        "all_passed": ok_count == len(results),
        "live_server_required": False,
    })
# END CLAIRE_S43_FIX11_S42_ROUTE_RESULT_CONTRACT
