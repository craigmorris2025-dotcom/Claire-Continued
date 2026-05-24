from __future__ import annotations

from typing import Dict, List


def get_cockpit_count_binding_metadata() -> Dict[str, object]:
    bindings: List[Dict[str, object]] = [
        {"card_id": "review_queue", "count_key": "review_queue", "label": "Review Queue", "action": "open_review_queue"},
        {"card_id": "bounded_web_jobs", "count_key": "bounded_web_jobs", "label": "Bounded Web Jobs", "action": "request_bounded_web_job"},
        {"card_id": "exports", "count_key": "exports", "label": "Exports", "action": "export_reviewed_package"},
        {"card_id": "audit_trail", "count_key": "audit_trail", "label": "Audit Trail", "action": "inspect_audit_trail"},
    ]
    return {
        "version": "v19.89.8-S282-S288",
        "stage_version": "S288",
        "status": "cockpit_count_binding_metadata_ready",
        "ok": True,
        "bindings": bindings,
        "binding_count": len(bindings),
        "safe_to_bind_frontend_counts": True,
        "runtime_truth_write_enabled": False,
        "automatic_updates_enabled": False,
    }
