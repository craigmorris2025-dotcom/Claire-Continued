
from __future__ import annotations

from fastapi import APIRouter

from claire.design_portal.output_contract import (
    build_design_portal_output,
    design_portal_output_summary,
)

router = APIRouter(tags=["Design Portal"])


@router.get("/design-portal/output")
def get_design_portal_output():
    return build_design_portal_output()


@router.get("/design-portal/output/summary")
def get_design_portal_output_summary():
    return design_portal_output_summary()


@router.post("/design-portal/output/rebuild")
def rebuild_design_portal_output():
    return build_design_portal_output()


@router.get("/design/portal/output")
def get_design_portal_output_alias():
    return build_design_portal_output()
