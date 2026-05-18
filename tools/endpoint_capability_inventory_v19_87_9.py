#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
import os
import re
import urllib.error
import urllib.request
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Optional


PROJECT_ROOT = Path.cwd()
AUDIT_DIR = PROJECT_ROOT / "docs" / "audits" / "v19_87_9_endpoint_capability_inventory"

IGNORE_DIRS = {
    ".git", ".venv", "venv", "env", "__pycache__", ".pytest_cache",
    "node_modules", ".mypy_cache", ".ruff_cache"
}
CODE_EXTS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".html", ".css", ".json",
    ".toml", ".ini", ".yml", ".yaml", ".bat", ".ps1", ".sh", ".md", ".txt"
}

KEY_PROBES = [
    "/", "/health", "/docs", "/openapi.json",
    "/dashboard/payload/status", "/dashboard/payload",
    "/api/dashboard/search/provider/status",
    "/api/dashboard/search/provider/probe",
    "/api/dashboard/search/live",
    "/api/dashboard/search/smoke/google",
]


@dataclass
class RouteHit:
    file: str
    line: int
    kind: str
    path: str
    method: str
    excerpt: str
    system_area: str


@dataclass
class EndpointRef:
    file: str
    line: int
    value: str
    kind: str
    excerpt: str
    system_area: str


@dataclass
class LiveProbe:
    path: str
    url: str
    status: str
    http_status: Optional[int]
    content_type: str = ""
    bytes_read: int = 0
    error: str = ""


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
        for filename in files:
            p = Path(root) / filename
            if p.suffix.lower() in CODE_EXTS or p.suffix == "":
                yield p


def all_project_files() -> list[Path]:
    return list(iter_files(PROJECT_ROOT))


def read_text(path: Path) -> str:
    try:
        if path.stat().st_size > 3_000_000:
            return ""
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def area_for(path: Path, text: str = "") -> str:
    s = (rel(path) + " " + text[:500]).lower()
    if "cockpit" in s or "dashboard" in s or "frontend" in s:
        return "dashboard_cockpit_frontend"
    if "search" in s or "web" in s or "internet" in s or "provider" in s or "probe" in s or "source_catalog" in s:
        return "live_web_source_provider"
    if "runtime" in s or "cycle" in s or "scheduler" in s or "orchestr" in s:
        return "runtime_orchestration"
    if "evidence" in s or "review" in s or "trust" in s:
        return "evidence_review_governance"
    if "api" in s or "route" in s or "backend" in s or "server" in s:
        return "backend_api_routes"
    if "launcher" in s or s.endswith(".bat") or s.endswith(".ps1") or s.endswith(".sh"):
        return "launcher_startup"
    if "test" in s:
        return "tests_contracts"
    return "uncategorized"


def scan_routes() -> list[RouteHit]:
    hits: list[RouteHit] = []
    decorator = re.compile(r'@([\w\.]+)\.(get|post|put|delete|patch|options|head)\(\s*["\']([^"\']+)["\']')
    add_api_route = re.compile(r'\.add_api_route\(\s*["\']([^"\']+)["\']')
    route_object = re.compile(r'APIRouter\(')
    include_router = re.compile(r'\.include_router\(')

    for path in all_project_files():
        if path.suffix.lower() != ".py":
            continue
        text = read_text(path)
        area = area_for(path, text)
        for n, line in enumerate(text.splitlines(), start=1):
            for m in decorator.finditer(line):
                hits.append(RouteHit(rel(path), n, "decorator", m.group(3), m.group(2).upper(), line.strip()[:300], area))
            for m in add_api_route.finditer(line):
                hits.append(RouteHit(rel(path), n, "add_api_route", m.group(1), "UNKNOWN", line.strip()[:300], area))
            if include_router.search(line):
                hits.append(RouteHit(rel(path), n, "include_router", "", "INCLUDE", line.strip()[:300], area))
            if route_object.search(line):
                hits.append(RouteHit(rel(path), n, "api_router_object", "", "ROUTER", line.strip()[:300], area))
    return sorted(hits, key=lambda x: (x.system_area, x.path, x.file, x.line))


def scan_endpoint_refs() -> list[EndpointRef]:
    refs: list[EndpointRef] = []
    patterns = [
        ("fetch", re.compile(r'fetch\(\s*["\']([^"\']+)["\']')),
        ("axios", re.compile(r'axios\.(?:get|post|put|delete|patch)\(\s*["\']([^"\']+)["\']')),
        ("url_localhost", re.compile(r'http://(?:127\.0\.0\.1|localhost):8000[^"\'\s<>)]+')),
        ("path_literal", re.compile(r'["\'](/(?:api|dashboard|health|docs|openapi|runtime|search|source|provider|probe|evidence|review|catalog)[^"\']*)["\']')),
    ]
    keyword_re = re.compile(r'(fetch\(|axios\.|127\.0\.0\.1:8000|localhost:8000|/dashboard|/api/|/health|/runtime|/search|/provider|/source|/catalog|/evidence|/review)')

    for path in all_project_files():
        if path.suffix.lower() not in CODE_EXTS:
            continue
        text = read_text(path)
        if not text:
            continue
        area = area_for(path, text)
        for n, line in enumerate(text.splitlines(), start=1):
            if not keyword_re.search(line):
                continue
            found = False
            for kind, pattern in patterns:
                for m in pattern.finditer(line):
                    refs.append(EndpointRef(rel(path), n, m.group(1) if m.lastindex else m.group(0), kind, line.strip()[:300], area))
                    found = True
            if not found:
                refs.append(EndpointRef(rel(path), n, "", "keyword_only", line.strip()[:300], area))
    unique = {}
    for r in refs:
        unique[(r.file, r.line, r.value, r.kind)] = r
    return sorted(unique.values(), key=lambda x: (x.system_area, x.value, x.file, x.line))


def scan_source_catalog_surfaces() -> list[EndpointRef]:
    refs: list[EndpointRef] = []
    terms = [
        "source_catalog", "source catalog", "SourceCatalog", "allowlist", "whitelist",
        "provider", "trust", "rate_limit", "probe", "live_search", "live search",
        "controlled", "internet", "web_search", "evidence_basket", "lineage"
    ]
    for path in all_project_files():
        text = read_text(path)
        if not text:
            continue
        low = text.lower()
        if not any(t.lower() in low for t in terms):
            continue
        area = area_for(path, text)
        for n, line in enumerate(text.splitlines(), start=1):
            if any(t.lower() in line.lower() for t in terms):
                refs.append(EndpointRef(rel(path), n, "", "source_catalog_or_live_web_surface", line.strip()[:300], area))
    return refs


def probe(path: str) -> LiveProbe:
    url = f"http://127.0.0.1:8000{path}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Claire-endpoint-capability-audit"})
        with urllib.request.urlopen(req, timeout=3) as res:
            data = res.read(4096)
            return LiveProbe(path, url, "ok", int(res.status), res.headers.get("content-type", ""), len(data), "")
    except urllib.error.HTTPError as exc:
        return LiveProbe(path, url, "http_error", int(exc.code), exc.headers.get("content-type", "") if exc.headers else "", 0, str(exc))
    except Exception as exc:
        return LiveProbe(path, url, "unreachable", None, "", 0, f"{type(exc).__name__}: {exc}")


def openapi_paths() -> dict[str, Any]:
    try:
        with urllib.request.urlopen("http://127.0.0.1:8000/openapi.json", timeout=5) as res:
            data = json.loads(res.read().decode("utf-8", errors="ignore"))
        return {"available": True, "paths": sorted(data.get("paths", {}).keys())}
    except Exception as exc:
        return {"available": False, "error": f"{type(exc).__name__}: {exc}", "paths": []}


def normalize_ref(value: str) -> str:
    if not value:
        return ""
    value = value.replace("http://127.0.0.1:8000", "").replace("http://localhost:8000", "")
    return value.split("?")[0]


def build_capability_map(routes: list[RouteHit], refs: list[EndpointRef], probes: list[LiveProbe], openapi: dict[str, Any], catalog_refs: list[EndpointRef]) -> dict[str, Any]:
    static_routes = sorted({r.path for r in routes if r.path})
    live_paths = set(openapi.get("paths", []))
    referenced_paths = sorted({normalize_ref(r.value) for r in refs if normalize_ref(r.value).startswith("/")})
    missing_live = [p for p in referenced_paths if p not in live_paths and not p.startswith("/docs")]

    by_area: dict[str, dict[str, int]] = {}
    for r in routes:
        by_area.setdefault(r.system_area, {"routes": 0, "endpoint_refs": 0, "source_catalog_refs": 0})
        by_area[r.system_area]["routes"] += 1
    for r in refs:
        by_area.setdefault(r.system_area, {"routes": 0, "endpoint_refs": 0, "source_catalog_refs": 0})
        by_area[r.system_area]["endpoint_refs"] += 1
    for r in catalog_refs:
        by_area.setdefault(r.system_area, {"routes": 0, "endpoint_refs": 0, "source_catalog_refs": 0})
        by_area[r.system_area]["source_catalog_refs"] += 1

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "policy": {
            "audit_only": True,
            "mutated_files": False,
            "rewired_dashboard": False,
            "enabled_live_internet": False,
            "restored_quarantine": False,
            "runtime_truth_mutated": False,
        },
        "counts": {
            "static_route_hits": len(routes),
            "unique_static_route_paths": len(static_routes),
            "endpoint_references": len(refs),
            "unique_referenced_paths": len(referenced_paths),
            "live_openapi_paths": len(live_paths),
            "referenced_paths_missing_from_live_openapi": len(missing_live),
            "source_catalog_live_web_surface_refs": len(catalog_refs),
        },
        "by_system_area": by_area,
        "key_probe_results": [asdict(p) for p in probes],
        "referenced_paths_missing_from_live_openapi": missing_live,
        "static_route_paths": static_routes,
        "live_openapi_paths": sorted(live_paths),
        "referenced_paths": referenced_paths,
        "live_operation_chain_needed": [
            "launcher/startup",
            "FastAPI app",
            "backend route mounts",
            "canonical payload endpoints",
            "cockpit/frontend fetches",
            "source catalog",
            "allowlist/trust/rate-limit policy",
            "provider adapter",
            "controlled probe",
            "source result schema",
            "evidence basket",
            "review gate",
            "runtime route decision",
            "cockpit output rendering",
        ],
    }


def write_reports() -> None:
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    routes = scan_routes()
    refs = scan_endpoint_refs()
    catalog_refs = scan_source_catalog_surfaces()
    probes = [probe(p) for p in KEY_PROBES]
    openapi = openapi_paths()
    cap = build_capability_map(routes, refs, probes, openapi, catalog_refs)

    files = {
        "ENDPOINT_CAPABILITY_MAP.json": cap,
        "BACKEND_ROUTE_INVENTORY.json": [asdict(x) for x in routes],
        "FRONTEND_AND_INTERNAL_ENDPOINT_REFERENCES.json": [asdict(x) for x in refs],
        "LIVE_WEB_SOURCE_CATALOG_SURFACES.json": [asdict(x) for x in catalog_refs],
        "KEY_ENDPOINT_PROBES.json": [asdict(x) for x in probes],
        "LIVE_OPENAPI_PATHS.json": openapi,
    }
    for name, data in files.items():
        (AUDIT_DIR / name).write_text(json.dumps(data, indent=2), encoding="utf-8")

    md = []
    md.append("# Claire v19.87.9 Endpoint Capability Inventory")
    md.append("")
    md.append(f"Generated: {cap['generated_at']}")
    md.append("")
    md.append("## Policy")
    for k, v in cap["policy"].items():
        md.append(f"- {k}: **{v}**")
    md.append("")
    md.append("## Counts")
    for k, v in cap["counts"].items():
        md.append(f"- {k}: **{v}**")
    md.append("")
    md.append("## Key endpoint probes")
    for p in probes:
        md.append(f"- `{p.path}` → {p.status} / {p.http_status} / {p.error}")
    md.append("")
    md.append("## System areas")
    for area, counts in sorted(cap["by_system_area"].items()):
        md.append(f"### {area}")
        for k, v in counts.items():
            md.append(f"- {k}: {v}")
        md.append("")
    md.append("## Missing live OpenAPI paths referenced by code/frontend")
    for p in cap["referenced_paths_missing_from_live_openapi"][:100]:
        md.append(f"- `{p}`")
    md.append("")
    md.append("## Live operation chain")
    for item in cap["live_operation_chain_needed"]:
        md.append(f"- {item}")
    md.append("")
    (AUDIT_DIR / "ENDPOINT_CAPABILITY_SUMMARY.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print("Claire v19.87.9 endpoint capability inventory complete.")
    print(f"Audit directory: {AUDIT_DIR}")
    for k, v in cap["counts"].items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    write_reports()
