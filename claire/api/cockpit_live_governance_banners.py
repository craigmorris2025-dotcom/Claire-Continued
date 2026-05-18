from __future__ import annotations

from typing import Dict, List


def get_live_governance_banners() -> Dict[str, object]:
    banners: List[Dict[str, object]] = [
        {
            "banner_id": "backend_owns_truth",
            "severity": "info",
            "text": "Backend owns truth. Cockpit is presentation and governed control only.",
            "always_visible": True,
        },
        {
            "banner_id": "manual_promotion_required",
            "severity": "warning",
            "text": "Manual promotion is mandatory before evidence can influence runtime truth.",
            "always_visible": True,
        },
        {
            "banner_id": "quarantine_required",
            "severity": "warning",
            "text": "External evidence remains quarantined until operator review.",
            "always_visible": True,
        },
        {
            "banner_id": "automatic_updates_blocked",
            "severity": "critical",
            "text": "Automatic updates are blocked. Only update proposals are allowed.",
            "always_visible": True,
        },
        {
            "banner_id": "runtime_mutation_blocked",
            "severity": "critical",
            "text": "Runtime mutation is blocked. Only mutation proposals may be reviewed.",
            "always_visible": True,
        },
    ]
    return {
        "version": "v19.89.8-S254-S260",
        "banners": banners,
        "unsafe_actions_redirected": True,
    }
