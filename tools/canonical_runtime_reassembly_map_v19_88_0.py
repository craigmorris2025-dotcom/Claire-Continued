#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Optional

PROJECT_ROOT = Path.cwd()
AUDIT_DIR = PROJECT_ROOT / "docs" / "audits" / "v19_88_0_canonical_runtime_reassembly"

IGNORE_DIRS = {".git", ".venv", "venv", "env", "__pycache__", ".pytest_cache", "node_modules", ".mypy_cache", ".ruff_cache"}
CODE_EXTS = {".py", ".js", ".ts", ".tsx", ".jsx", ".html", ".json", ".toml", ".ini", ".yml", ".yaml", ".bat", ".ps1", ".sh", ".md", ".txt"}

REQUIRED_ENDPOINTS = [
    "/", "/health", "/docs", "/openapi.json",
    "/dashboard/payload/status", "/dashboard/payload",
    "/api/dashboard/search/provider/status",
    "/api/dashboard/search/provider/probe",
    "/api/dashboard/search/live",
    "/api/dashboard/search/smoke/google",
]

AREA_TERMS = {
    "dashboard_payload": ["dashboard_payload", "payload_bridge", "dashboard/payload", "canonical"],
    "cockpit_dashboard": ["cockpit", "dashboard", "operator_dashboard", "command_center"],
    "runtime": ["runtime", "continuous_runtime", "cycle", "scheduler", "orchestrat"],
    "live_web_provider": ["governed_web", "live_search", "provider", "probe", "internet", "web_search"],
    "source_catalog": ["source_universe", "source_catalog", "catalog", "universes"],
    "evidence_review": ["evidence", "review", "trust", "lineage", "basket"],
    "launcher_startup": ["launcher", "startup", "main.py", "uvicorn"],
}


@dataclass
class Hit:
    file: str
    line: int
    kind: str
    value: str
    excerpt: str
    area: str


@dataclass
class Probe:
    path: str
    status: str
    http_status: Optional[int]
    error: str
    content_type: str = ""
    bytes_read: int = 0


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")
    except Exception:
        return str(path).replace("\\", "/")


def iter_files(base: Path) -> Iterable[Path]:
    if not base.exists():
        return
    if base.is_file():
        yield base
        return
    for root, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for name in files:
            p = Path(root) / name
            if p.suffix.lower() in CODE_EXTS or p.suffix == "":
                yield p


def files() -> list[Path]:
    return list(iter_files(PROJECT_ROOT))


def read(path: Path) -> str:
    try:
        if path.stat().st_size > 3_000_000:
            return ""
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def area(path: Path, text: str = "") -> str:
    s = (rel(path) + " " + text[:800]).lower()
    for key, terms in AREA_TERMS.items():
        if any(t in s for t in terms):
            return key
    if "apirouter" in s or "/api/" in s:
        return "backend_api"
    return "uncategorized"


def scan() -> dict:
    route_re = re.compile(r'@([\w\.]+)\.(get|post|put|delete|patch|options|head)\(\s*["\']([^"\']+)["\']')
    router_re = re.compile(r'(\w+)\s*=\s*APIRouter\((.*)\)')
    include_re = re.compile(r'\.include_router\((.*)\)')
    factory_re = re.compile(r'def\s+(create_app|build_app|get_app|app_factory)\s*\(')
    endpoint_re = re.compile(r'(fetch\(\s*["\']([^"\']+)["\']|axios\.(?:get|post|put|delete|patch)\(\s*["\']([^"\']+)["\']|http://(?:127\.0\.0\.1|localhost):8000[^"\'\s<>)]+|["\'](/(?:api|dashboard|health|docs|openapi|runtime|search|source|provider|probe|evidence|review|catalog|universes)[^"\']*)["\'])')

    routes, routers, includes, factories, frontend_refs, launchers = [], [], [], [], [], []

    for path in files():
        text = read(path)
        if not text:
            continue
        ar = area(path, text)
        for n, line in enumerate(text.splitlines(), start=1):
            if path.suffix.lower() == ".py":
                for m in route_re.finditer(line):
                    routes.append(Hit(rel(path), n, m.group(2).upper(), m.group(3), line.strip()[:280], ar))
                if router_re.search(line):
                    routers.append(Hit(rel(path), n, "APIRouter", line.strip()[:180], line.strip()[:280], ar))
                if include_re.search(line):
                    includes.append(Hit(rel(path), n, "include_router", line.strip()[:180], line.strip()[:280], ar))
                if factory_re.search(line):
                    factories.append(Hit(rel(path), n, "app_factory", line.strip()[:180], line.strip()[:280], ar))
            if any(k in line for k in ["fetch(", "axios.", "/dashboard", "/api/", "/health", "/runtime", "/search", "/provider", "/source", "/catalog", "localhost:8000", "127.0.0.1:8000"]):
                for m in endpoint_re.finditer(line):
                    val = next((g for g in m.groups()[1:] if g), m.group(0))
                    val = val.replace("http://127.0.0.1:8000", "").replace("http://localhost:8000", "").split("?")[0]
                    frontend_refs.append(Hit(rel(path), n, "endpoint_ref", val, line.strip()[:280], ar))
            if path.suffix.lower() in {".bat", ".ps1", ".sh", ".py"} and any(k in line.lower() for k in ["uvicorn", "main.py", "8000", "dashboard", "cockpit", "frontend", "python "]):
                launchers.append(Hit(rel(path), n, "launcher_ref", "", line.strip()[:280], ar))

    return {
        "routes": [asdict(x) for x in routes],
        "routers": [asdict(x) for x in routers],
        "includes": [asdict(x) for x in includes],
        "factories": [asdict(x) for x in factories],
        "frontend_refs": [asdict(x) for x in frontend_refs],
        "launchers": [asdict(x) for x in launchers],
    }


def probe(path: str) -> Probe:
    try:
        req = urllib.request.Request(f"http://127.0.0.1:8000{path}", headers={"User-Agent": "Claire-v19.88.0"})
        with urllib.request.urlopen(req, timeout=3) as res:
            data = res.read(4096)
            return Probe(path, "ok", int(res.status), "", res.headers.get("content-type", ""), len(data))
    except urllib.error.HTTPError as exc:
        return Probe(path, "http_error", int(exc.code), str(exc), exc.headers.get("content-type", "") if exc.headers else "", 0)
    except Exception as exc:
        return Probe(path, "unreachable", None, f"{type(exc).__name__}: {exc}", "", 0)


def openapi() -> dict:
    try:
        with urllib.request.urlopen("http://127.0.0.1:8000/openapi.json", timeout=5) as res:
            data = json.loads(res.read().decode("utf-8", errors="ignore"))
        return {"server_running": True, "available": True, "paths": sorted(data.get("paths", {}).keys())}
    except Exception as exc:
        return {"server_running": False, "available": False, "paths": [], "error": f"{type(exc).__name__}: {exc}"}


def summarize(scanned: dict, probes: list[Probe], op: dict) -> dict:
    static_paths = sorted({x["value"] for x in scanned["routes"] if x["value"].startswith("/")})
    frontend_paths = sorted({x["value"] for x in scanned["frontend_refs"] if x["value"].startswith("/")})
    live_paths = set(op.get("paths", []))
    if not op.get("server_running"):
        live_interpretation = "server_not_running_or_port_refused_during_audit"
    elif op.get("available") and not live_paths:
        live_interpretation = "server_running_but_openapi_empty"
    else:
        live_interpretation = "server_running_with_openapi"
    return {
        "live_interpretation": live_interpretation,
        "counts": {
            "app_factories": len(scanned["factories"]),
            "router_objects": len(scanned["routers"]),
            "include_router_calls": len(scanned["includes"]),
            "python_route_hits": len(scanned["routes"]),
            "unique_static_route_paths": len(static_paths),
            "frontend_endpoint_refs": len(scanned["frontend_refs"]),
            "unique_frontend_paths": len(frontend_paths),
            "launcher_refs": len(scanned["launchers"]),
            "live_openapi_paths": len(live_paths),
        },
        "missing_required_operational_endpoints_live": [p for p in REQUIRED_ENDPOINTS if p not in live_paths],
        "frontend_paths_missing_live": [p for p in frontend_paths if p not in live_paths and not p.startswith("/docs")],
        "next_repair_order": [
            "If server_not_running_or_port_refused_during_audit, start python main.py and rerun the audit before repairing routes.",
            "Lock canonical startup: main.py -> runtime_core.app:create_app.",
            "Lock one canonical router registry.",
            "Mount /health, /docs, /openapi.json.",
            "Mount /dashboard/payload/status and /dashboard/payload.",
            "Mount governed search provider/status/probe/live routes.",
            "Mount live source catalog/source universe routes.",
            "Mount continuous runtime status routes.",
            "Bind cockpit status cards to canonical endpoints.",
            "Then prove live source catalog -> governed probe -> evidence -> runtime -> cockpit.",
        ],
    }


def write_reports() -> None:
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    scanned = scan()
    probes = [probe(p) for p in REQUIRED_ENDPOINTS]
    op = openapi()
    summary = summarize(scanned, probes, op)
    report = {
        "version": "19.88.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "policy": {
            "audit_only": True,
            "mutated_files": False,
            "mounted_routes": False,
            "rewired_dashboard": False,
            "enabled_live_internet": False,
            "runtime_truth_mutated": False,
        },
        "summary": summary,
        "live_probes": [asdict(x) for x in probes],
        "live_openapi": op,
        **scanned,
    }
    (AUDIT_DIR / "CANONICAL_RUNTIME_REASSEMBLY_MAP.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (AUDIT_DIR / "PYTHON_ROUTES.json").write_text(json.dumps(scanned["routes"], indent=2), encoding="utf-8")
    (AUDIT_DIR / "INCLUDE_ROUTER_CALLS.json").write_text(json.dumps(scanned["includes"], indent=2), encoding="utf-8")
    (AUDIT_DIR / "FRONTEND_EXPECTATIONS.json").write_text(json.dumps(scanned["frontend_refs"], indent=2), encoding="utf-8")
    md = ["# Claire v19.88.0 Canonical Runtime Reassembly Map", "", f"Generated: {report['generated_at']}", "", "## Policy"]
    for k, v in report["policy"].items():
        md.append(f"- {k}: **{v}**")
    md += ["", "## Live Interpretation", f"**{summary['live_interpretation']}**", "", "## Counts"]
    for k, v in summary["counts"].items():
        md.append(f"- {k}: **{v}**")
    md += ["", "## Missing Required Operational Endpoints"]
    for p in summary["missing_required_operational_endpoints_live"]:
        md.append(f"- `{p}`")
    md += ["", "## Next Repair Order"]
    for step in summary["next_repair_order"]:
        md.append(f"- {step}")
    (AUDIT_DIR / "CANONICAL_RUNTIME_REASSEMBLY_SUMMARY.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("Claire v19.88.0 canonical runtime reassembly map complete.")
    print(f"Audit directory: {AUDIT_DIR}")
    print(f"Live interpretation: {summary['live_interpretation']}")
    for k, v in summary["counts"].items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    write_reports()
