from fastapi import APIRouter
from ..claire.orchestrator.pipeline import ClairePipeline

def register_endpoints(router: APIRouter):
    pipeline = ClairePipeline()

    @router.post("/run")
    def run_pipeline(payload: dict):
        return pipeline.run(payload)
