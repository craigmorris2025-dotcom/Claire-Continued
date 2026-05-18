#!/usr/bin/env python3
"""
Claire v19.84.8 Cockpit Canonical Fetch Map

Purpose:
- Discover frontend fetch usage.
- Map cockpit fetches to canonical backend-owned routes.
- Detect frontend truth synthesis risks.
- Produce a canonical fetch dependency contract.

Read-only build.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]

REGISTRY_PATH = ROOT / "data" / "runtime_authority" / "canonical_route_owner_registry.json"

OUT_DIR = ROOT / "audits" / "v19_84_8_cockpit_canonical_fetch_map"
OUT_JSON = OUT_DIR / "cockpit_canonical_fetch_map.json"
OUT_MD = OUT_DIR / "cockpit_canonical_fetch_map.md"

FRONTEND_DIRS = [
    ROOT / "frontend",
    ROOT / "src" / "frontend",
]

FRONTEND_SUFFIXES = {".js", ".jsx", ".ts", ".tsx", ".html"}

FETCH_RE = re.compile(
    r"""(?:fetch|axios\.(?:get|post|put|delete)|XMLHttpRequest).*?['"](?P<route>/(?:api/)?[^'"]+)['"]""",
    re.DOTALL,
)

TRUTH_RISK_PATTERNS = [
    "mockData",
    "syntheticPayload",
    "fakePayload",
    "generatedPayload",
    "fallbackTruth",
    "hardcodedResults",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_registry() -> Dict[str, Any]:
    if not REGISTRY_PATH.exists():
        return {}
    try:
        return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"_load_error": repr(exc)}


def iter_frontend_files():
    ignored = {"node_modules", ".git", "__pycache__", "archive", "backups"}

    for base in FRONTEND_DIRS:
        if not base.exists():
            continue

        for path in base.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix.lower() not in FRONTEND_SUFFIXES:
                continue
            if any(part in ignored for part in path.parts):
                continue

            yield path


def discover_fetches() -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []

    for path in iter_frontend_files():
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        for match in FETCH_RE.finditer(text):
            route = match.group("route")

            findings.append({
                "file": str(path.relative_to(ROOT)),
                "route": route,
                "line": text[:match.start()].count("\n") + 1,
            })

    return findings


def discover_truth_risks() -> List[Dict[str, Any]]:
    risks: List[Dict[str, Any]] = []

    for path in iter_frontend_files():
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        for pattern in TRUTH_RISK_PATTERNS:
            if pattern in text:
                risks.append({
                    "file": str(path.relative_to(ROOT)),
                    "pattern": pattern,
                })

    return risks


def map_to_registry(fetches: List[Dict[str, Any]], registry: Dict[str, Any]) -> Dict[str, Any]:
    routes = registry.get("routes", {}) if isinstance(registry, dict) else {}

    grouped = defaultdict(list)
    for item in fetches:
        grouped[item["route"]].append(item)

    mapping: Dict[str, Any] = {}

    for route, refs in grouped.items():
        canonical = routes.get(route)

        mapping[route] = {
            "frontend_reference_count": len(refs),
            "frontend_references": refs,
            "registered": canonical is not None,
            "canonical_owner": canonical.get("canonical_owner") if canonical else None,
            "truth_owner": canonical.get("truth_owner") if canonical else None,
            "cockpit_role": canonical.get("cockpit_role") if canonical else None,
            "status": (
                "canonical"
                if canonical
                else "unregistered"
            ),
        }

    return mapping


def evaluate(mapping: Dict[str, Any], risks: List[Dict[str, Any]]) -> Dict[str, Any]:
    blockers: List[Dict[str, Any]] = []
    warnings: List[Dict[str, Any]] = []

    for route, item in mapping.items():
        if item["status"] == "unregistered":
            warnings.append({
                "route": route,
                "reason": "frontend_route_not_in_canonical_registry",
                "recommended_action": "Map route into canonical backend registry or remove cockpit dependency.",
            })

        if item.get("truth_owner") not in {None, "backend"}:
            blockers.append({
                "route": route,
                "reason": "non_backend_truth_owner_detected",
            })

    for risk in risks:
        warnings.append({
            "file": risk["file"],
            "reason": "potential_frontend_truth_synthesis",
            "pattern": risk["pattern"],
        })

    return {
        "status": "review_required" if blockers or warnings else "clean",
        "blockers": blockers,
        "warnings": warnings,
        "blocker_count": len(blockers),
        "warning_count": len(warnings),
    }


def build_map() -> Dict[str, Any]:
    registry = load_registry()
    fetches = discover_fetches()
    risks = discover_truth_risks()
    mapping = map_to_registry(fetches, registry)
    evaluation = evaluate(mapping, risks)

    return {
        "version": "v19.84.8",
        "build": "Cockpit Canonical Fetch Map",
        "generated_at": utc_now(),
        "read_only": True,
        "backend_owns_truth": True,
        "cockpit_owns_presentation_only": True,
        "fetch_reference_count": len(fetches),
        "mapped_route_count": len(mapping),
        "truth_risk_count": len(risks),
        "mapping": mapping,
        "truth_risks": risks,
        "evaluation": evaluation,
        "next_build": (
            "v19.84.9 Cockpit Binding Lock"
            if evaluation["blocker_count"] == 0
            else "v19.84.9 Cockpit Fetch Cleanup"
        ),
    }


def write_markdown(report: Dict[str, Any]) -> str:
    lines: List[str] = []

    lines.append("# Claire v19.84.8 Cockpit Canonical Fetch Map")
    lines.append("")
    lines.append(f"- Generated: `{report['generated_at']}`")
    lines.append(f"- Status: `{report['evaluation']['status']}`")
    lines.append(f"- Fetch references: `{report['fetch_reference_count']}`")
    lines.append(f"- Mapped routes: `{report['mapped_route_count']}`")
    lines.append(f"- Truth risks: `{report['truth_risk_count']}`")
    lines.append("")

    lines.append("## Route Mapping")
    lines.append("")

    for route, item in report["mapping"].items():
        lines.append(f"### `{route}`")
        lines.append(f"- Status: `{item['status']}`")
        lines.append(f"- Frontend references: `{item['frontend_reference_count']}`")

        if item["canonical_owner"]:
            lines.append(f"- Canonical owner: `{item['canonical_owner']}`")

        if item["truth_owner"]:
            lines.append(f"- Truth owner: `{item['truth_owner']}`")

        lines.append("")

    lines.append("## Truth Risks")
    lines.append("")

    if report["truth_risks"]:
        for risk in report["truth_risks"]:
            lines.append(f"- `{risk['file']}` → `{risk['pattern']}`")
    else:
        lines.append("No truth synthesis patterns detected.")

    lines.append("")
    lines.append(f"Next build: `{report['next_build']}`")
    lines.append("")

    return "\n".join(lines)


def write_report() -> Dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    report = build_map()

    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    OUT_MD.write_text(write_markdown(report), encoding="utf-8")

    return report


def main() -> int:
    report = write_report()

    print(json.dumps({
        "status": report["evaluation"]["status"],
        "version": report["version"],
        "mapped_routes": report["mapped_route_count"],
        "truth_risks": report["truth_risk_count"],
        "warnings": report["evaluation"]["warning_count"],
        "blockers": report["evaluation"]["blocker_count"],
        "next_build": report["next_build"],
    }, indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
