"""FastAPI routes for S646-S652 governed metadata-only result contract."""
from __future__ import annotations

from fastapi import APIRouter

from runtime_core.governance.governed_metadata_result_contract import (
    build_metadata_actions,
    build_metadata_cards,
    build_metadata_payload,
    build_metadata_status,
    build_metadata_stop_gate,
    get_metadata_result_contract,
    get_sample_metadata_results,
    validate_metadata_result,
)

router = APIRouter(tags=["governed-metadata-result-contract"])


@router.get("/api/search/metadata/contract")
def search_metadata_contract():
    return get_metadata_result_contract()


@router.get("/api/search/metadata/results/sample")
def search_metadata_sample_results():
    return {"results": get_sample_metadata_results()}


@router.get("/api/search/metadata/cards")
def search_metadata_cards():
    return {"cards": build_metadata_cards()}


@router.get("/api/search/metadata/actions")
def search_metadata_actions():
    return {"actions": build_metadata_actions()}


@router.get("/api/search/metadata/policy")
def search_metadata_policy():
    return get_metadata_result_contract()


@router.get("/api/search/metadata/status")
def search_metadata_status():
    return build_metadata_status()


@router.get("/api/search/metadata/payload")
def search_metadata_payload():
    return build_metadata_payload()


@router.get("/api/search/metadata/stop-gate")
def search_metadata_stop_gate():
    return build_metadata_stop_gate()


@router.post("/api/search/metadata/validate")
def search_metadata_validate(result: dict):
    return validate_metadata_result(result)


@router.get("/api/internet/metadata/result-contract")
def internet_metadata_result_contract():
    return get_metadata_result_contract()


@router.get("/api/internet/metadata/payload")
def internet_metadata_payload():
    return build_metadata_payload()
