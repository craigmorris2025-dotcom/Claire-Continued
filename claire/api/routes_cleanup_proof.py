
from __future__ import annotations

from fastapi import APIRouter

from claire.cleanup.cleanup_proof import build_cleanup_proof, cleanup_proof_summary

router = APIRouter(tags=["Cleanup Proof"])


@router.get("/cleanup/proof")
def get_cleanup_proof():
    return build_cleanup_proof()


@router.get("/cleanup/proof/summary")
def get_cleanup_proof_summary():
    return cleanup_proof_summary()


@router.post("/cleanup/proof/rebuild")
def rebuild_cleanup_proof():
    return build_cleanup_proof()


@router.get("/cleanup/archive-plan")
def get_cleanup_archive_plan():
    return build_cleanup_proof().get("archive_plan_path")


@router.get("/cleanup/status")
def get_cleanup_status():
    return cleanup_proof_summary()
