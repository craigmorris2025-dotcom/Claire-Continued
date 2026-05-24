
# Claire Syntalion v18.65
# First Active Dashboard Google Result Proof
#
# This module proves the active dashboard surface is ready to show the first
# visible governed search result for: google -> Google / https://www.google.com.
# It uses the already-governed endpoint/fetch proof path and does not perform
# real internet calls, mutate runtime truth, enable autonomous execution, or
# perform automatic updates.

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


CONTRACT_VERSION = "v18.65.first_active_dashboard_google_result_proof"

DEFAULT_DASHBOARD_PATH = Path("frontend/command_center/modern/index.html")
DEFAULT_JS_PATH = Path("frontend/command_center/modern/governed_live_search_ui_binding.js")
GOOGLE_URL = "https://www.google.com"

REQUIRED_DASHBOARD_IDS = [
    "claire-governed-live-search-form",
    "claire-governed-live-search-input",
    "claire-governed-live-search-manual-enable",
    "claire-governed-live-search-status",
    "claire-governed-live-search-results",
]

REQUIRED_DASHBOARD_TEXT = [
    "Governed Live Web Search",
    "Manual governed live-search enable",
    "Type google and press Search",
    "governed_live_search_ui_binding.js",
]

REQUIRED_JS_TEXT = [
    "window.ClaireLiveSearch",
    "/api/dashboard/search/live",
    "manual_enable_confirmed: true",
    "result_cards",
    "Manual governed search enable is required.",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class FirstActiveDashboardGoogleResultProofPolicy:
    real_internet_calls_allowed: bool = False
    active_dashboard_html_required: bool = True
    ui_fetch_binding_required: bool = True
    manual_enable_required: bool = True
    injected_executor_only: bool = True
    review_required: bool = True
    fail_closed: bool = True
    immutable_runtime_truth: bool = True
    runtime_truth_mutated: bool = False
    autonomous_execution_enabled: bool = False
    automatic_updates_enabled: bool = False
    proof_only: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "real_internet_calls_allowed": self.real_internet_calls_allowed,
            "active_dashboard_html_required": self.active_dashboard_html_required,
            "ui_fetch_binding_required": self.ui_fetch_binding_required,
            "manual_enable_required": self.manual_enable_required,
            "injected_executor_only": self.injected_executor_only,
            "review_required": self.review_required,
            "fail_closed": self.fail_closed,
            "immutable_runtime_truth": self.immutable_runtime_truth,
            "runtime_truth_mutated": self.runtime_truth_mutated,
            "autonomous_execution_enabled": self.autonomous_execution_enabled,
            "automatic_updates_enabled": self.automatic_updates_enabled,
            "proof_only": self.proof_only,
        }


def _governance(extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    payload = {
        "review_required": True,
        "runtime_truth_mutated": False,
        "autonomous_execution": False,
        "automatic_updates": False,
        "fail_closed": True,
        "real_internet_calls": False,
        "operator_review_required": True,
    }
    if extra:
        payload.update(extra)
    return payload


def inspect_active_dashboard_google_search_surface(
    dashboard_path: Path | str = DEFAULT_DASHBOARD_PATH,
    js_path: Path | str = DEFAULT_JS_PATH,
) -> Dict[str, Any]:
    policy = FirstActiveDashboardGoogleResultProofPolicy()
    dashboard = Path(dashboard_path)
    js_file = Path(js_path)

    dashboard_exists = dashboard.exists()
    js_exists = js_file.exists()

    dashboard_text = dashboard.read_text(encoding="utf-8") if dashboard_exists else ""
    js_text = js_file.read_text(encoding="utf-8") if js_exists else ""

    missing_ids: List[str] = [item for item in REQUIRED_DASHBOARD_IDS if item not in dashboard_text]
    missing_dashboard_text: List[str] = [item for item in REQUIRED_DASHBOARD_TEXT if item not in dashboard_text]
    missing_js_text: List[str] = [item for item in REQUIRED_JS_TEXT if item not in js_text]

    html_ready = dashboard_exists and not missing_ids and not missing_dashboard_text
    js_ready = js_exists and not missing_js_text
    ready = html_ready and js_ready

    return {
        "contract_version": CONTRACT_VERSION,
        "status": "dashboard_google_surface_ready" if ready else "dashboard_google_surface_incomplete",
        "reason": "" if ready else "missing_dashboard_or_js_requirements",
        "created_at": _utc_now(),
        "dashboard_path": str(dashboard),
        "js_path": str(js_file),
        "dashboard_exists": dashboard_exists,
        "js_exists": js_exists,
        "html_ready": html_ready,
        "js_ready": js_ready,
        "missing_ids": missing_ids,
        "missing_dashboard_text": missing_dashboard_text,
        "missing_js_text": missing_js_text,
        "required_dashboard_ids": list(REQUIRED_DASHBOARD_IDS),
        "required_js_text": list(REQUIRED_JS_TEXT),
        "policy": policy.to_dict(),
        "governance": _governance({"surface_inspection_only": True}),
    }


def run_first_active_dashboard_google_result_proof(
    *,
    dashboard_path: Path | str = DEFAULT_DASHBOARD_PATH,
    js_path: Path | str = DEFAULT_JS_PATH,
) -> Dict[str, Any]:
    policy = FirstActiveDashboardGoogleResultProofPolicy()
    surface = inspect_active_dashboard_google_search_surface(dashboard_path, js_path)

    try:
        from .dashboard_to_endpoint_fetch_proof import (
            run_dashboard_to_endpoint_google_fetch_proof,
            run_dashboard_to_endpoint_manual_enable_block_proof,
        )
    except Exception as exc:
        return {
            "contract_version": CONTRACT_VERSION,
            "status": "blocked",
            "reason": "dashboard_to_endpoint_fetch_proof_unavailable",
            "created_at": _utc_now(),
            "surface": surface,
            "google_fetch_proof": {},
            "manual_enable_block_proof": {},
            "visible_result_ready": False,
            "error_type": type(exc).__name__,
            "policy": policy.to_dict(),
            "governance": _governance(),
        }

    google_fetch_proof = run_dashboard_to_endpoint_google_fetch_proof()
    manual_enable_block_proof = run_dashboard_to_endpoint_manual_enable_block_proof()

    google_ready = (
        google_fetch_proof.get("status") == "passed"
        and google_fetch_proof.get("first_result_title") == "Google"
        and google_fetch_proof.get("first_result_url") == GOOGLE_URL
        and int(google_fetch_proof.get("visible_result_count") or 0) >= 1
    )
    manual_block_ready = (
        manual_enable_block_proof.get("status") == "passed"
        and manual_enable_block_proof.get("manual_enable_block_confirmed") is True
    )
    surface_ready = surface.get("status") == "dashboard_google_surface_ready"

    passed = surface_ready and google_ready and manual_block_ready

    return {
        "contract_version": CONTRACT_VERSION,
        "status": "passed" if passed else "failed",
        "reason": "" if passed else "active_dashboard_google_result_proof_failed",
        "created_at": _utc_now(),
        "query": "google",
        "expected_title": "Google",
        "expected_url": GOOGLE_URL,
        "surface": surface,
        "google_fetch_proof": google_fetch_proof,
        "manual_enable_block_proof": manual_enable_block_proof,
        "surface_ready": surface_ready,
        "google_ready": google_ready,
        "manual_block_ready": manual_block_ready,
        "visible_result_ready": passed,
        "first_result_title": google_fetch_proof.get("first_result_title", ""),
        "first_result_url": google_fetch_proof.get("first_result_url", ""),
        "visible_result_count": google_fetch_proof.get("visible_result_count", 0),
        "operator_instruction": "Open the active dashboard, check Manual governed live-search enable, type google, then press Search.",
        "policy": policy.to_dict(),
        "governance": _governance({"proof_executor": "v18.64.dashboard_to_endpoint_fetch_proof"}),
    }


def build_first_active_dashboard_google_operator_checklist() -> Dict[str, Any]:
    policy = FirstActiveDashboardGoogleResultProofPolicy()
    return {
        "contract_version": CONTRACT_VERSION,
        "status": "operator_checklist_ready",
        "created_at": _utc_now(),
        "steps": [
            "Start the Claire app normally.",
            "Open the active dashboard.",
            "Confirm the Governed Live Web Search panel is visible.",
            "Check Manual governed live-search enable.",
            "Type google into the governed live-search input.",
            "Press Search.",
            "Expected first result: Google / https://www.google.com.",
        ],
        "expected_result": {
            "query": "google",
            "title": "Google",
            "url": GOOGLE_URL,
            "manual_enable_required": True,
            "review_required": True,
        },
        "policy": policy.to_dict(),
        "governance": _governance({"operator_visible": True}),
    }


__all__ = [
    "CONTRACT_VERSION",
    "DEFAULT_DASHBOARD_PATH",
    "DEFAULT_JS_PATH",
    "GOOGLE_URL",
    "FirstActiveDashboardGoogleResultProofPolicy",
    "build_first_active_dashboard_google_operator_checklist",
    "inspect_active_dashboard_google_search_surface",
    "run_first_active_dashboard_google_result_proof",
]
