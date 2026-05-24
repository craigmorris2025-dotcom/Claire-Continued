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

router = APIRouter()
pipeline = RuntimePipelineAdapter()


@router.post("/command")
def command_interface(payload: dict):
    """
    Receives search bar input and routes it into the Claire pipeline.

    SAFETY:
    - Preserves existing command route behavior.
    - Does not add updater/install behavior here.
    - Updater commands must be added later through a validated route with
      explicit updater dependency wiring.
    """
    user_input = payload.get("query", "")
    return pipeline.run({"command": user_input})
