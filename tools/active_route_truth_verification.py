from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path.cwd()
OUT = ROOT / "audit" / "v19_83_2_active_route_truth"
REQUIRED = [
    ("GET", "/dashboard/payload"),
    ("GET", "/dashboard/payload/status"),
    ("GET", "/api/dashboard/payload"),
    ("GET", "/api/dashboard/payload/status"),
    ("GET", "/runtime/continuous/status"),
    ("POST", "/runtime/continuous/start"),
    ("POST", "/runtime/continuous/pause"),
    ("GET", "/runtime/continuous/review-queue"),
    ("POST", "/runs/start"),
    ("GET", "/runs/latest"),
    ("GET", "/universes"),
]


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def scan_routes() -> list[dict]:
    rows = []
    for base_name in ["claire", "src/claire", "backend"]:
        base = ROOT / base_name
        if not base.exists():
            continue
        for path in base.rglob("*.py"):
            text = read(path)
            for method, route in re.findall(r'@(?:router|app)\.(get|post|put|delete|patch)\(\s*["\']([^"\']+)["\']', text):
                rows.append({"method": method.upper(), "path": route, "file": path.relative_to(ROOT).as_posix()})
    return rows


def cockpit_truth() -> dict:
    shell = ROOT / "frontend" / "cockpit" / "shell" / "cockpit_shell.html"
    js = ROOT / "frontend" / "cockpit" / "shell" / "assets" / "claire_authored_enterprise_cockpit_shell.js"
    launcher = ROOT / "LAUNCH_CLAIRE.bat"
    shell_text = read(shell)
    js_text = read(js)
    launcher_text = read(launcher)
    return {
        "shell": {
            "path": shell.relative_to(ROOT).as_posix() if shell.exists() else str(shell),
            "exists": shell.exists(),
            "contains_authored_cockpit": "claire-enterprise-cockpit" in shell_text,
            "contains_dev_terms": any(t in shell_text.lower() for t in ["swagger", "openapi", "/docs"]),
        },
        "authored_js": {
            "path": js.relative_to(ROOT).as_posix() if js.exists() else str(js),
            "exists": js.exists(),
            "contains_dashboard_payload": "/dashboard/payload" in js_text,
            "contains_api_payload_fallback": "/api/dashboard/payload" in js_text,
            "contains_continuous_runtime": "/runtime/continuous/status" in js_text,
            "contains_dev_terms": any(t in js_text.lower() for t in ["swagger", "openapi", "/docs"]),
        },
        "launcher": {
            "path": launcher.relative_to(ROOT).as_posix() if launcher.exists() else str(launcher),
            "exists": launcher.exists(),
            "mentions_cockpit_shell": "cockpit_shell" in launcher_text,
            "mentions_port_8000": "8000" in launcher_text,
        },
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    routes = scan_routes()
    required = []
    for method, route in REQUIRED:
        matches = [r for r in routes if r["method"] == method and r["path"] == route]
        required.append({"method": method, "path": route, "mounted_in_source": len(matches) > 0, "match_count": len(matches), "matches": matches})

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "root": str(ROOT),
        "route_hits": len(routes),
        "required": required,
        "missing": [r for r in required if not r["mounted_in_source"]],
        "duplicates": [r for r in required if r["match_count"] > 1],
        "cockpit": cockpit_truth(),
    }
    (OUT / "active_route_truth_report.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    md = ["# Claire v19.83.2 Active Route Truth Report", "", f"Generated: {payload['generated_at']}", ""]
    md.append("## Required Routes")
    for r in required:
        status = "OK" if r["mounted_in_source"] else "MISSING"
        dup = " DUPLICATE" if r["match_count"] > 1 else ""
        md.append(f"- {status}{dup}: `{r['method']} {r['path']}` ({r['match_count']} source matches)")
    md.append("")
    md.append("## Cockpit")
    md.append(f"- Shell exists: {payload['cockpit']['shell']['exists']}")
    md.append(f"- Authored shell marker: {payload['cockpit']['shell']['contains_authored_cockpit']}")
    md.append(f"- JS payload fallback: {payload['cockpit']['authored_js']['contains_api_payload_fallback']}")
    md.append(f"- Launcher mentions cockpit shell: {payload['cockpit']['launcher']['mentions_cockpit_shell']}")
    (OUT / "active_route_truth_report.md").write_text("\n".join(md), encoding="utf-8")

    print("Active route truth report written:")
    print(OUT / "active_route_truth_report.md")
    print(OUT / "active_route_truth_report.json")


if __name__ == "__main__":
    main()
