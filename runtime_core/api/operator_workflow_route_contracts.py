from __future__ import annotations

from typing import Dict, List


LOCKS = {
    "runtime_truth_write_enabled": False,
    "runtime_mutation_enabled": False,
    "automatic_updates_enabled": False,
    "autonomous_execution_enabled": False,
    "continuous_crawling_enabled": False,
}


def get_operator_workflow_route_contracts() -> Dict[str, object]:
    routes: List[Dict[str, object]] = [
        {
            "route_id": "workflow_counts",
            "method": "GET",
            "path": "/api/operator/workflows/counts",
            "purpose": "Read dashboard queue counts.",
            "authority": "read_only",
            "writes_runtime_truth": False,
        },
        {
            "route_id": "review_queue_list",
            "method": "GET",
            "path": "/api/operator/workflows/review-queue",
            "purpose": "Read operator review queue.",
            "authority": "read_only",
            "writes_runtime_truth": False,
        },
        {
            "route_id": "bounded_jobs_list",
            "method": "GET",
            "path": "/api/operator/workflows/bounded-jobs",
            "purpose": "Read bounded web job records.",
            "authority": "read_only",
            "writes_runtime_truth": False,
        },
        {
            "route_id": "exports_list",
            "method": "GET",
            "path": "/api/operator/workflows/exports",
            "purpose": "Read export artifact records.",
            "authority": "read_only",
            "writes_runtime_truth": False,
        },
        {
            "route_id": "audit_trail_list",
            "method": "GET",
            "path": "/api/operator/workflows/audit-trail",
            "purpose": "Read append-only operator audit trail.",
            "authority": "read_only",
            "writes_runtime_truth": False,
        },
        {
            "route_id": "review_decision_proposal",
            "method": "POST",
            "path": "/api/operator/workflows/review-decision",
            "purpose": "Record an operator review decision proposal only.",
            "authority": "operator_review_proposal_only",
            "writes_runtime_truth": False,
        },
        {
            "route_id": "bounded_job_request_proposal",
            "method": "POST",
            "path": "/api/operator/workflows/bounded-job-request",
            "purpose": "Record a bounded web job request proposal only.",
            "authority": "operator_request_proposal_only",
            "writes_runtime_truth": False,
        },
    ]

    return {
        "version": "v19.89.8-S275-S281",
        "route_contracts": routes,
        "route_count": len(routes),
        "safe_methods": ["GET", "POST"],
        "post_routes_are_proposal_only": True,
        "runtime_truth_write_enabled": False,
        **LOCKS,
    }
