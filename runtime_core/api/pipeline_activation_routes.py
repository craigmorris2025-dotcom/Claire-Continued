from __future__ import annotations

from runtime_core.pipeline.activation_registry import build_pipeline_activation_registry


from fastapi import APIRouter


router = APIRouter(tags=["Pipeline Activation"])


@router.get("/api/pipelines/activation")
def pipeline_activation():
    return build_pipeline_activation_registry()
