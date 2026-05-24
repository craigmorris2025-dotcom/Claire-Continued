
from __future__ import annotations

from fastapi import APIRouter

from runtime_core.validation_stack.buildability_validation_stack import (
    build_validation_stack,
    validation_stack_summary,
)

router = APIRouter(tags=["Buildability Validation"])


@router.get("/validation/buildability")
def get_buildability_validation():
    return build_validation_stack()


@router.get("/validation/buildability/summary")
def get_buildability_validation_summary():
    return validation_stack_summary()


@router.post("/validation/buildability/rebuild")
def rebuild_buildability_validation():
    return build_validation_stack()


@router.get("/design-portal/validation")
def get_design_portal_validation():
    return build_validation_stack()
