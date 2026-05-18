
from __future__ import annotations

from fastapi import APIRouter

from claire.proof.manual_browser_swagger_proof import (
    build_manual_browser_swagger_proof_binder,
    manual_browser_swagger_proof_summary,
)

router = APIRouter(tags=["Manual Proof"])


@router.get("/proof/manual-browser-swagger")
def get_manual_browser_swagger_proof_binder():
    return build_manual_browser_swagger_proof_binder()


@router.get("/proof/manual-browser-swagger/summary")
def get_manual_browser_swagger_proof_summary():
    return manual_browser_swagger_proof_summary()


@router.post("/proof/manual-browser-swagger/rebuild")
def rebuild_manual_browser_swagger_proof_binder():
    return build_manual_browser_swagger_proof_binder()


@router.get("/proof/manual-browser-swagger/checklist")
def get_manual_browser_swagger_checklist():
    return manual_browser_swagger_proof_summary()
