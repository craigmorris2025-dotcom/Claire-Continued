from __future__ import annotations

from typing import Dict, List


def get_disabled_button_behavior_contract() -> Dict[str, object]:
    buttons: List[Dict[str, object]] = [
        {
            "button_id": "run_autonomous_update",
            "enabled": False,
            "visible": True,
            "reason": "automatic_updates_blocked",
            "safe_redirect": "create_update_proposal",
        },
        {
            "button_id": "execute_runtime_mutation",
            "enabled": False,
            "visible": True,
            "reason": "runtime_mutation_blocked",
            "safe_redirect": "request_mutation_proposal",
        },
        {
            "button_id": "start_continuous_crawl",
            "enabled": False,
            "visible": True,
            "reason": "continuous_crawling_blocked",
            "safe_redirect": "request_bounded_web_job",
        },
        {
            "button_id": "promote_without_review",
            "enabled": False,
            "visible": True,
            "reason": "manual_promotion_mandatory",
            "safe_redirect": "open_review_queue",
        },
    ]
    return {
        "version": "v19.89.8-S233-S239",
        "buttons": buttons,
        "disabled_buttons_must_explain_reason": True,
        "frontend_may_enable_blocked_buttons": False,
    }
