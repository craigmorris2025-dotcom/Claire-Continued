from fastapi import APIRouter

from runtime_core.domain.contract import ClaireIntent
from runtime_core.orchestrator.pipeline_v4 import PipelineOrchestrator


class RuntimePipelineAdapter:
    def __init__(self) -> None:
        self.orchestrator = PipelineOrchestrator()

    def run(self, payload: dict):
        raw_input = payload.get("command") or payload.get("query") or payload.get("raw_input") or ""
        result = self.orchestrator.execute(ClaireIntent(raw_input=raw_input, metadata={"source": "api"}))
        return result.to_dict() if hasattr(result, "to_dict") else result

def register_endpoints(router: APIRouter):
    pipeline = RuntimePipelineAdapter()

    @router.post("/run")
    def run_pipeline(payload: dict):
        return pipeline.run(payload)
