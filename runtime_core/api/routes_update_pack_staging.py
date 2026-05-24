
from __future__ import annotations

from fastapi import APIRouter

from runtime_core.update_governance.update_pack_staging import (
    build_update_pack_staging,
    update_pack_staging_summary,
)

router = APIRouter(tags=["Update Governance"])


@router.get("/updates/staging")
def get_update_pack_staging():
    return build_update_pack_staging()


@router.get("/updates/staging/summary")
def get_update_pack_staging_summary():
    return update_pack_staging_summary()


@router.post("/updates/staging/create")
def create_update_pack_staging():
    return build_update_pack_staging()


@router.get("/updates/governance/status")
def get_update_governance_status():
    return update_pack_staging_summary()
