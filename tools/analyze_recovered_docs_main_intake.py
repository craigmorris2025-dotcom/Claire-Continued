from __future__ import annotations

import ast
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOCS_MAIN = Path("C:/Users/craig/OneDrive/Desktop/Docs Main")
REPORT_JSON = ROOT / "reports" / "RECOVERED_DOCS_MAIN_CAPABILITY_INTAKE.json"
REPORT_MD = ROOT / "reports" / "RECOVERED_DOCS_MAIN_CAPABILITY_INTAKE.md"


GROUPS: dict[str, dict[str, Any]] = {
    "autonomous_governance": {
        "path": DOCS_MAIN / "autonomous_governance",
        "runtime_lane": "governance and escalation boundaries",
        "activation_status": "candidate_only_review_required",
        "why_it_matters": "Defines what Claire may do autonomously, what must pause for human review, and how self-change permissions should be bounded.",
    },
    "benchmarks": {
        "path": DOCS_MAIN / "benchmarks",
        "runtime_lane": "signal validation and backtesting",
        "activation_status": "candidate_only_review_required",
        "why_it_matters": "Adds hit-rate, false-positive, false-negative, regime, and benchmark reporting concepts for proving signal quality.",
    },
    "design_proof": {
        "path": DOCS_MAIN / "design_proof",
        "runtime_lane": "design portal feasibility proof",
        "activation_status": "candidate_only_review_required",
        "why_it_matters": "Maps directly to buildability, dependency risk, deployment model, implementation cost, and design maturity scoring.",
    },
    "recursive_longitudinal": {
        "path": DOCS_MAIN / "recursive_longitudinal",
        "runtime_lane": "recursive learning and longitudinal memory",
        "activation_status": "candidate_only_review_required",
        "why_it_matters": "Tracks recurring gaps, thesis evolution, run patterns, learning signals, and strategy memory across completed runs.",
    },
    "research_live": {
        "path": DOCS_MAIN / "research_live",
        "runtime_lane": "governed live research evidence quality",
        "activation_status": "candidate_only_review_required",
        "why_it_matters": "Adds source verification, evidence quality, claim verification, conflict resolution, citation lineage, and packet assembly concepts.",
    },
    "proof_products": {
        "path": DOCS_MAIN,
        "files": ["Proof products.txt", "claire_verified_output_proof_phase_plan.docx", "uptime_monitor.py"],
        "runtime_lane": "verified output proof and uptime monitoring",
        "activation_status": "candidate_only_review_required",
        "why_it_matters": "Defines portfolio/design proof binders and an uptime-monitoring concept, but should not override canonical route logic.",
    },
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def file_status(path: Path) -> dict[str, Any]:
    item: dict[str, Any] = {
        "filename": path.name,
        "path": str(path).replace("\\", "/"),
        "exists": path.exists(),
        "size_bytes": path.stat().st_size if path.exists() else 0,
        "kind": path.suffix.lower().lstrip(".") or "file",
        "compile_status": "not_python",
        "classes": [],
        "functions": [],
    }
    if not path.exists() or path.suffix.lower() != ".py":
        return item
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
        item["classes"] = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        item["functions"] = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        item["compile_status"] = "parse_ok"
    except SyntaxError as exc:
        item["compile_status"] = "syntax_error"
        item["syntax_error"] = {"line": exc.lineno, "message": exc.msg}
    except Exception as exc:
        item["compile_status"] = "read_error"
        item["error"] = str(exc)
    return item


def group_files(config: dict[str, Any]) -> list[Path]:
    base = Path(config["path"])
    if "files" in config:
        return [base / name for name in config["files"]]
    if not base.exists():
        return []
    return sorted(path for path in base.iterdir() if path.is_file())


def run() -> dict[str, Any]:
    groups: dict[str, Any] = {}
    for group_id, config in GROUPS.items():
        files = [file_status(path) for path in group_files(config)]
        groups[group_id] = {
            "path": str(Path(config["path"])).replace("\\", "/"),
            "runtime_lane": config["runtime_lane"],
            "activation_status": config["activation_status"],
            "why_it_matters": config["why_it_matters"],
            "file_count": len(files),
            "files": files,
        }
    syntax_errors = [
        {"group": group_id, "filename": item["filename"], "syntax_error": item.get("syntax_error")}
        for group_id, group in groups.items()
        for item in group["files"]
        if item.get("compile_status") == "syntax_error"
    ]
    payload = {
        "schema_version": "claire.recovered_docs_main_capability_intake.v1",
        "generated_at": utc_now(),
        "status": "candidate_inventory_complete",
        "rule": "Recovered Docs Main files are candidate capability modules only. They are not active runtime doctrine until reviewed, normalized, tested, and explicitly wired.",
        "groups": groups,
        "syntax_errors": syntax_errors,
        "recommended_order": [
            "research_live",
            "design_proof",
            "benchmarks",
            "recursive_longitudinal",
            "autonomous_governance",
            "proof_products",
        ],
        "next_wiring_targets": [
            "Attach research_live concepts to governed connected search evidence scoring.",
            "Attach design_proof concepts to design portal buildability and feasibility gates.",
            "Attach benchmarks to signal validation after proof outputs exist.",
            "Attach recursive_longitudinal after run history and proof binders are stable.",
            "Keep autonomous_governance as a hard review boundary, not an autopilot permission grant.",
        ],
    }
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT_MD.write_text(render_markdown(payload), encoding="utf-8")
    return payload


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Recovered Docs Main Capability Intake",
        "",
        f"Generated: {payload['generated_at']}",
        f"Status: `{payload['status']}`",
        "",
        payload["rule"],
        "",
        "## Groups",
    ]
    for group_id, group in payload["groups"].items():
        lines.extend(
            [
                "",
                f"### {group_id}",
                f"- Runtime lane: `{group['runtime_lane']}`",
                f"- Activation: `{group['activation_status']}`",
                f"- Files: `{group['file_count']}`",
                f"- Purpose: {group['why_it_matters']}",
            ]
        )
        for item in group["files"]:
            suffix = f", classes={item['classes']}" if item.get("classes") else ""
            lines.append(f"- `{item['filename']}`: `{item['compile_status']}`{suffix}")
    if payload["syntax_errors"]:
        lines.extend(["", "## Parse Issues"])
        for item in payload["syntax_errors"]:
            err = item.get("syntax_error") or {}
            lines.append(f"- `{item['group']}/{item['filename']}` line `{err.get('line')}`: {err.get('message')}")
    lines.extend(["", "## Recommended Order"])
    lines.extend(f"- `{item}`" for item in payload["recommended_order"])
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    result = run()
    print(json.dumps({
        "status": result["status"],
        "groups": {key: value["file_count"] for key, value in result["groups"].items()},
        "syntax_errors": result["syntax_errors"],
        "reports": {"json": str(REPORT_JSON), "markdown": str(REPORT_MD)},
    }, indent=2, sort_keys=True))
