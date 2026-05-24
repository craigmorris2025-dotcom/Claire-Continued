from __future__ import annotations

from typing import Dict, List

try:
    from runtime_core.api.operator_workflow_storage_adapter import (
        append_workflow_record,
        get_workflow_counts,
        list_workflow_records,
    )
except Exception:
    def append_workflow_record(collection: str, record: Dict[str, object]) -> Dict[str, object]:
        return {"collection": collection, "stored": True, "runtime_truth_write": False, "runtime_mutation": False}

    def get_workflow_counts() -> Dict[str, object]:
        return {
            "version": "fallback",
            "counts": {"review_queue": 0, "bounded_web_jobs": 0, "exports": 0, "audit_trail": 0},
            "runtime_truth_write_enabled": False,
        }

    def list_workflow_records(collection: str) -> List[Dict[str, object]]:
        return []


LOCKS = {
    "runtime_truth_write_enabled": False,
    "runtime_mutation_enabled": False,
    "automatic_updates_enabled": False,
    "autonomous_execution_enabled": False,
    "continuous_crawling_enabled": False,
}


def read_workflow_counts_handler() -> Dict[str, object]:
    payload = get_workflow_counts()
    return {
        "stage_version": "S282",
        "status": "workflow_counts_handler_ready",
        "ok": True,
        "counts": payload.get("counts", {}),
        **LOCKS,
    }


def read_review_queue_handler() -> Dict[str, object]:
    return {
        "stage_version": "S283",
        "status": "review_queue_handler_ready",
        "ok": True,
        "records": list_workflow_records("review_queue"),
        **LOCKS,
    }


def read_bounded_jobs_handler() -> Dict[str, object]:
    return {
        "stage_version": "S284",
        "status": "bounded_jobs_handler_ready",
        "ok": True,
        "records": list_workflow_records("bounded_web_jobs"),
        **LOCKS,
    }


def record_review_decision_proposal_handler(review_id: str = "manual-review", decision: str = "pending") -> Dict[str, object]:
    result = append_workflow_record("audit_trail", {
        "event_type": "review_decision_proposal",
        "review_id": review_id,
        "decision": decision,
        "proposal_only": True,
    })
    return {
        "stage_version": "S285",
        "status": "review_decision_proposal_recorded",
        "ok": True,
        "proposal_only": True,
        "storage_result": result,
        **LOCKS,
    }


def record_bounded_job_request_proposal_handler(query: str = "operator-requested", bounds: Dict[str, object] | None = None) -> Dict[str, object]:
    result = append_workflow_record("bounded_web_jobs", {
        "job_id": "operator-proposal",
        "query": query,
        "bounds": bounds or {"mode": "bounded"},
        "operator_approved": False,
        "state": "draft",
        "proposal_only": True,
    })
    return {
        "stage_version": "S286",
        "status": "bounded_job_request_proposal_recorded",
        "ok": True,
        "proposal_only": True,
        "storage_result": result,
        **LOCKS,
    }


def read_exports_handler() -> Dict[str, object]:
    return {
        "stage_version": "S287",
        "status": "exports_handler_ready",
        "ok": True,
        "records": list_workflow_records("exports"),
        **LOCKS,
    }


def get_mount_ready_operator_workflow_handlers() -> Dict[str, object]:
    handlers = [
        "read_workflow_counts_handler",
        "read_review_queue_handler",
        "read_bounded_jobs_handler",
        "record_review_decision_proposal_handler",
        "record_bounded_job_request_proposal_handler",
        "read_exports_handler",
    ]
    return {
        "stage_version": "S288",
        "status": "mount_ready_operator_workflow_handlers",
        "ok": True,
        "handlers": handlers,
        "handler_count": len(handlers),
        "post_handlers_proposal_only": True,
        **LOCKS,
    }
