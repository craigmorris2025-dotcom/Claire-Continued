
from __future__ import annotations

from fastapi import APIRouter

from claire.proof.full_e2e_proof_pack import (
    build_full_e2e_proof_pack,
    full_e2e_proof_pack_summary,
)

router = APIRouter(tags=["Proof Pack"])


@router.get("/proof/e2e")
def get_full_e2e_proof_pack():
    return build_full_e2e_proof_pack()


@router.get("/proof/e2e/summary")
def get_full_e2e_proof_pack_summary():
    return full_e2e_proof_pack_summary()


@router.post("/proof/e2e/rebuild")
def rebuild_full_e2e_proof_pack():
    return build_full_e2e_proof_pack()


@router.get("/system/stop-go")
def get_stop_go_report():
    return full_e2e_proof_pack_summary()
