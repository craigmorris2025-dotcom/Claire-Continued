
from __future__ import annotations

from fastapi import APIRouter

from claire.runtime_truth.runtime_truth_contract_repair import (
    build_runtime_truth_artifacts,
    load_runtime_truth,
    runtime_truth_summary,
)

router = APIRouter(tags=["Runtime Truth"])


@router.get("/runtime/truth")
def get_runtime_truth():
    return load_runtime_truth()


@router.get("/runtime/state")
def get_runtime_state():
    return runtime_truth_summary()


@router.post("/runtime/truth/rebuild")
def rebuild_runtime_truth():
    return build_runtime_truth_artifacts()


@router.get("/dashboard/runtime-truth")
def get_dashboard_runtime_truth():
    return load_runtime_truth()
