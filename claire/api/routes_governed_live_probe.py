
from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter

from claire.internet.governed_live_probe import (
    build_probe_contract,
    live_probe_summary,
    run_governed_live_probe,
)
from claire.internet.live_probe_request_adapter import adapter_status, normalize_live_probe_payload, run_adapter_payload

router = APIRouter(tags=["Internet Provider"])


@router.get("/internet/live-probe/status")
def get_live_probe_status():
    return live_probe_summary()


@router.get("/internet/live-probe/contract")
def get_live_probe_contract():
    return build_probe_contract()


@router.post("/internet/live-probe/run")
def post_live_probe_run(payload: Dict[str, Any]):
    normalized = normalize_live_probe_payload(payload)
    return run_governed_live_probe(
        query=normalized["query"],
        confirm_text=normalized["confirm_text"],
    )


@router.post("/internet/live-probe/run-confirmed")
def post_live_probe_run_confirmed(payload: Dict[str, Any]):
    return run_adapter_payload(payload)


@router.post("/internet/live-probe/run-adapter")
def post_live_probe_run_adapter(payload: Dict[str, Any]):
    return run_adapter_payload(payload)


@router.post("/operator/search/web/run-governed-probe")
def post_operator_search_web_run_governed_probe(payload: Dict[str, Any]):
    return run_adapter_payload(payload)


@router.get("/internet/live-probe/adapter/status")
def get_live_probe_adapter_status():
    return adapter_status()


@router.get("/internet/live-probe/last")
def get_live_probe_last():
    return live_probe_summary()
