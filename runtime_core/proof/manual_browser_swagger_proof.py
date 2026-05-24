
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

VERSION = "v17.79"
CONTRACT_NAME = "Manual Browser + Swagger Proof Binder"

BINDER_PATH = Path("data/proof/manual_browser_swagger_proof_binder.json")
BINDER_MD_PATH = Path("data/proof/manual_browser_swagger_proof_binder.md")
EVIDENCE_TEMPLATE_PATH = Path("data/proof/manual_browser_swagger_evidence_template.json")
CHECKLIST_PATH = Path("data/proof/manual_browser_swagger_checklist.md")
DASHBOARD_PAYLOAD_PATH = Path("data/dashboard/manual_browser_swagger_proof_payload.json")
STOP_GO_PATH = Path("data/proof/v17_79_manual_browser_swagger_stop_go.json")
STOP_GO_MD_PATH = Path("data/proof/v17_79_manual_browser_swagger_stop_go.md")

PRIOR_REPORTS = {
    "v17_75_e2e_proof": "data/proof/full_end_to_end_proof_pack.json",
    "v17_76_platform_smoke": "data/proof/platform_endpoint_smoke_proof.json",
    "v17_77_launch_hardening": "data/launch_hardening/platform_launch_hardening_report.json",
    "v17_78_desktop_startup": "data/desktop_packaging/startup_reliability_report.json",
}

BROWSER_URLS = [
    {
        "id": "swagger_docs",
        "url": "http://127.0.0.1:8000/docs",
        "proof_type": "browser",
        "expected": "Swagger UI opens and shows Claire API routes.",
        "required": True,
    },
    {
        "id": "operator_dashboard_state",
        "url": "http://127.0.0.1:8000/operator/dashboard/state",
        "proof_type": "browser_json",
        "expected": "JSON response includes contract_version, mission, route_gate, surfaces, proof, updates.",
        "required": True,
    },
    {
        "id": "search_capabilities",
        "url": "http://127.0.0.1:8000/operator/search/capabilities",
        "proof_type": "browser_json",
        "expected": "JSON response shows permanent search bar, normal web search prepared, runtime search enabled, agent command prepared.",
        "required": True,
    },
    {
        "id": "runtime_truth",
        "url": "http://127.0.0.1:8000/runtime/truth",
        "proof_type": "browser_json",
        "expected": "Runtime truth endpoint responds with canonical truth data or visible missing state.",
        "required": True,
    },
    {
        "id": "route_audit",
        "url": "http://127.0.0.1:8000/routes/audit",
        "proof_type": "browser_json",
        "expected": "Route audit confirms discovery/breakthrough/innovation and AutoDesign/Design Portal route rules.",
        "required": True,
    },
    {
        "id": "autodesign_handoff",
        "url": "http://127.0.0.1:8000/autodesign/handoff",
        "proof_type": "browser_json",
        "expected": "AutoDesign handoff contract responds and does not fake missing design data.",
        "required": True,
    },
    {
        "id": "design_portal_output",
        "url": "http://127.0.0.1:8000/design-portal/output",
        "proof_type": "browser_json",
        "expected": "Design Portal output contract responds with design sections or visible missing state.",
        "required": True,
    },
    {
        "id": "internet_readiness",
        "url": "http://127.0.0.1:8000/internet/readiness",
        "proof_type": "browser_json",
        "expected": "Internet readiness responds; live uncontrolled web remains disabled.",
        "required": True,
    },
    {
        "id": "update_regression_lock",
        "url": "http://127.0.0.1:8000/updates/regression-lock",
        "proof_type": "browser_json",
        "expected": "Update governance lock responds; automatic/background execution remains disabled.",
        "required": True,
    },
    {
        "id": "platform_smoke",
        "url": "http://127.0.0.1:8000/proof/platform-smoke",
        "proof_type": "browser_json",
        "expected": "Platform smoke proof responds with domain status and Stop/Go.",
        "required": True,
    },
    {
        "id": "desktop_startup",
        "url": "http://127.0.0.1:8000/desktop/startup",
        "proof_type": "browser_json",
        "expected": "Desktop startup reliability report responds.",
        "required": True,
    },
]

SWAGGER_POST_TESTS = [
    {
        "id": "search_runtime_query",
        "method": "POST",
        "path": "/operator/search/query",
        "body": {"query": "runtime truth", "mode": "runtime", "limit": 5},
        "expected": "Returns completed runtime/system search response with result list shape.",
        "required": True,
    },
    {
        "id": "command_parse_autodesign",
        "method": "POST",
        "path": "/operator/command/parse",
        "body": {"query": "open autodesign"},
        "expected": "Returns command parse result; execution_enabled remains false.",
        "required": True,
    },
    {
        "id": "proof_platform_rebuild",
        "method": "POST",
        "path": "/proof/platform-smoke/rebuild",
        "body": {},
        "expected": "Rebuilds platform smoke proof and returns domain status.",
        "required": True,
    },
    {
        "id": "desktop_startup_rebuild",
        "method": "POST",
        "path": "/desktop/startup/rebuild",
        "body": {},
        "expected": "Rebuilds desktop startup report and returns Stop/Go status.",
        "required": True,
    },
]

DASHBOARD_PROOF_STEPS = [
    "Run START_CLAIRE_SAFE.bat.",
    "Confirm Swagger opens at http://127.0.0.1:8000/docs.",
    "Confirm the dashboard opens from frontend/command_center/modern/index.html.",
    "Wait for backend startup, then press dashboard Refresh/Search if Backend Offline appears.",
    "Confirm dashboard top status says Backend Online.",
    "Confirm the permanent search bar remains visible.",
    "Switch through workspaces: Mission, Routes, Discovery, AutoDesign, Design Portal, Portfolio, Acquisition, Internet, Updates, Proof, Diagnostics.",
    "Run Runtime search in the command/search bar with query: runtime truth.",
    "Run Command mode with query: open autodesign.",
    "Run Web mode with query: test web search gate. Confirm it returns prepared_not_executed, not fake web results.",
]


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    if not path.exists():
        return {}, {"path": str(path).replace("\\", "/"), "status": "missing"}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            return {}, {"path": str(path).replace("\\", "/"), "status": "invalid", "error": "JSON root is not object"}
        return payload, {"path": str(path).replace("\\", "/"), "status": "loaded"}
    except Exception as exc:
        return {}, {"path": str(path).replace("\\", "/"), "status": "invalid", "error": str(exc)}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def load_prior_reports(root: Path) -> Dict[str, Any]:
    reports: Dict[str, Any] = {}
    for name, rel_path in PRIOR_REPORTS.items():
        payload, source = read_json(root / rel_path)
        status = payload.get("status") or (payload.get("stop_go") or {}).get("status") or "missing"
        reports[name] = {
            "source": source,
            "status": status,
            "stop_go": payload.get("stop_go", {}),
            "recommendation": (payload.get("stop_go") or {}).get("recommendation") or payload.get("recommendation", ""),
        }
    return reports


def evidence_slots() -> List[Dict[str, Any]]:
    slots: List[Dict[str, Any]] = []
    for item in BROWSER_URLS:
        slots.append({
            "id": item["id"],
            "proof_type": item["proof_type"],
            "url": item["url"],
            "required": item["required"],
            "expected": item["expected"],
            "operator_status": "not_checked",
            "screenshot_file": "",
            "notes": "",
        })
    for item in SWAGGER_POST_TESTS:
        slots.append({
            "id": item["id"],
            "proof_type": "swagger_try_it_out",
            "method": item["method"],
            "path": item["path"],
            "body": item["body"],
            "required": item["required"],
            "expected": item["expected"],
            "operator_status": "not_checked",
            "screenshot_file": "",
            "notes": "",
        })
    for i, step in enumerate(DASHBOARD_PROOF_STEPS, start=1):
        slots.append({
            "id": f"dashboard_step_{i:02d}",
            "proof_type": "dashboard_manual",
            "step": step,
            "required": True,
            "expected": "Operator confirms manually.",
            "operator_status": "not_checked",
            "screenshot_file": "",
            "notes": "",
        })
    return slots


def create_evidence_template(root: Path) -> Dict[str, Any]:
    template = {
        "version": VERSION,
        "created_at": now(),
        "instructions": "After manually checking browser, dashboard, and Swagger results, set operator_status to passed, failed, or warning and optionally add screenshot_file and notes.",
        "allowed_operator_status": ["not_checked", "passed", "failed", "warning", "not_applicable"],
        "evidence_slots": evidence_slots(),
        "operator_final_review": {
            "status": "not_checked",
            "reviewer": "",
            "reviewed_at": "",
            "notes": "",
        },
    }
    write_json(root / EVIDENCE_TEMPLATE_PATH, template)
    return template


def determine_stop_go(priors: Dict[str, Any], evidence: Dict[str, Any]) -> Dict[str, Any]:
    blockers: List[str] = []
    warnings: List[str] = []

    for name, report in priors.items():
        source = report.get("source", {})
        if source.get("status") != "loaded":
            blockers.append(f"missing_prior_report:{name}")
        if report.get("status") == "STOP":
            warnings.append(f"prior_report_stop:{name}")

    required_slots = [slot for slot in evidence.get("evidence_slots", []) if slot.get("required")]
    not_checked = [slot["id"] for slot in required_slots if slot.get("operator_status") == "not_checked"]

    if not_checked:
        warnings.append(f"manual_evidence_not_yet_completed:{len(not_checked)}_required_slots")

    if blockers:
        status = "STOP"
        recommendation = "Fix missing prior proof reports before manual browser and Swagger proof."
    else:
        status = "READY_FOR_MANUAL_BROWSER_SWAGGER_PROOF"
        recommendation = "Open the URLs, complete the dashboard walkthrough, and run Swagger Try it out tests. Automatic web/update/agent execution remains disabled."

    return {
        "status": status,
        "blockers": sorted(set(blockers)),
        "warnings": sorted(set(warnings)),
        "manual_required_slots_not_checked": not_checked,
        "recommendation": recommendation,
    }


def write_binder_markdown(root: Path, binder: Dict[str, Any]) -> None:
    lines = [
        "# Claire v17.79 Manual Browser + Swagger Proof Binder",
        "",
        f"Generated: {binder['generated_at']}",
        "",
        f"Status: **{binder['stop_go']['status']}**",
        "",
        f"Recommendation: {binder['stop_go']['recommendation']}",
        "",
        "## Start",
        "",
        "```bat",
        "START_CLAIRE_SAFE.bat",
        "```",
        "",
        "## Browser URLs",
        "",
    ]
    for item in BROWSER_URLS:
        lines.append(f"- [{item['id']}] {item['url']}")
        lines.append(f"  - Expected: {item['expected']}")
    lines.extend([
        "",
        "## Swagger Try it out tests",
        "",
        "Open: http://127.0.0.1:8000/docs",
        "",
    ])
    for item in SWAGGER_POST_TESTS:
        lines.append(f"### {item['id']}")
        lines.append("")
        lines.append(f"- Method/path: `{item['method']} {item['path']}`")
        lines.append("- Body:")
        lines.append("")
        lines.append("```json")
        lines.append(json.dumps(item["body"], indent=2))
        lines.append("```")
        lines.append(f"- Expected: {item['expected']}")
        lines.append("")
    lines.extend([
        "## Dashboard walkthrough",
        "",
    ])
    for step in DASHBOARD_PROOF_STEPS:
        lines.append(f"- [ ] {step}")
    lines.extend([
        "",
        "## Evidence template",
        "",
        "`data/proof/manual_browser_swagger_evidence_template.json`",
        "",
        "Do not mark final launch ready until required evidence slots are checked.",
        "",
    ])
    if binder["stop_go"]["warnings"]:
        lines.append("## Warnings")
        lines.append("")
        for warning in binder["stop_go"]["warnings"]:
            lines.append(f"- {warning}")
        lines.append("")
    if binder["stop_go"]["blockers"]:
        lines.append("## Blockers")
        lines.append("")
        for blocker in binder["stop_go"]["blockers"]:
            lines.append(f"- {blocker}")
        lines.append("")
    write_text(root / BINDER_MD_PATH, "\n".join(lines))
    write_text(root / CHECKLIST_PATH, "\n".join(lines))
    write_text(root / STOP_GO_MD_PATH, "\n".join([
        "# Claire v17.79 Manual Browser + Swagger Stop / Go",
        "",
        f"Generated: {binder['generated_at']}",
        "",
        f"Status: **{binder['stop_go']['status']}**",
        "",
        f"Recommendation: {binder['stop_go']['recommendation']}",
        "",
        "Next: complete the manual evidence template and screenshots.",
    ]))


def build_manual_browser_swagger_proof_binder(project_root: Optional[Path | str] = None) -> Dict[str, Any]:
    root = Path(project_root or Path.cwd()).resolve()
    priors = load_prior_reports(root)
    evidence = create_evidence_template(root)
    stop_go = determine_stop_go(priors, evidence)

    binder = {
        "version": VERSION,
        "contract_name": CONTRACT_NAME,
        "generated_at": now(),
        "status": stop_go["status"],
        "stop_go": stop_go,
        "prior_reports": priors,
        "browser_urls": BROWSER_URLS,
        "swagger_post_tests": SWAGGER_POST_TESTS,
        "dashboard_proof_steps": DASHBOARD_PROOF_STEPS,
        "evidence_template_path": str(EVIDENCE_TEMPLATE_PATH).replace("\\", "/"),
        "manual_checklist_path": str(CHECKLIST_PATH).replace("\\", "/"),
        "governance": {
            "manual_browser_proof_required": True,
            "manual_swagger_proof_required": True,
            "manual_dashboard_walkthrough_required": True,
            "screenshots_recommended": True,
            "live_internet_disabled": True,
            "automatic_updates_disabled": True,
            "background_execution_disabled": True,
            "autonomous_agent_execution_disabled": True,
            "normal_web_search_prepared_but_not_live": True,
            "no_fake_manual_proof": True,
        },
        "next": [
            "Run START_CLAIRE_SAFE.bat",
            "Run OPEN_CLAIRE_PROOF_URLS.bat",
            "Complete Swagger Try it out tests",
            "Fill data/proof/manual_browser_swagger_evidence_template.json or upload screenshots",
            "v17.80 Launch Candidate Freeze after manual proof is acceptable",
        ],
    }

    write_json(root / BINDER_PATH, binder)
    write_json(root / STOP_GO_PATH, {"version": VERSION, "generated_at": binder["generated_at"], **stop_go})
    write_binder_markdown(root, binder)

    dashboard_payload = {
        "version": VERSION,
        "generated_at": binder["generated_at"],
        "status": binder["status"],
        "recommendation": stop_go["recommendation"],
        "browser_url_count": len(BROWSER_URLS),
        "swagger_post_test_count": len(SWAGGER_POST_TESTS),
        "dashboard_step_count": len(DASHBOARD_PROOF_STEPS),
        "manual_required_slots_not_checked": len(stop_go["manual_required_slots_not_checked"]),
        "governance": binder["governance"],
    }
    write_json(root / DASHBOARD_PAYLOAD_PATH, dashboard_payload)

    return binder


def manual_browser_swagger_proof_summary(project_root: Optional[Path | str] = None) -> Dict[str, Any]:
    binder = build_manual_browser_swagger_proof_binder(project_root)
    return {
        "version": VERSION,
        "generated_at": now(),
        "status": binder.get("status"),
        "recommendation": binder.get("stop_go", {}).get("recommendation"),
        "browser_urls": [item["url"] for item in binder.get("browser_urls", [])],
        "swagger_post_tests": binder.get("swagger_post_tests", []),
        "manual_required_slots_not_checked": len(binder.get("stop_go", {}).get("manual_required_slots_not_checked", [])),
    }
