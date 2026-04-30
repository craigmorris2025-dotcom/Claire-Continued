from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
import uuid
import inspect

from claire.orchestrator.pipeline_v4 import PipelineOrchestrator
from claire.domain.contract import ClaireIntent

router = APIRouter(tags=["pipeline"])

orchestrator = PipelineOrchestrator()


class EvaluateRequest(BaseModel):
    raw_input: str
    mode: Optional[str] = "deterministic"


@router.post("/pipeline/evaluate")
async def evaluate(req: EvaluateRequest):
    """
    Main pipeline execution endpoint
    """

    # 🚨 HARD GUARD
    if not req.raw_input or len(req.raw_input.strip()) < 5:
        return {
            "status": "error",
            "message": "raw_input is empty or too short"
        }

    # ✅ CLEAN INPUT
    clean_input = req.raw_input.strip()

    # ✅ BUILD INTENT
    intent = ClaireIntent(
        intent_id=f"intent-{uuid.uuid4().hex[:8]}",
        raw_input=clean_input,
        mode=req.mode or "deterministic"
    )

    # ✅ DEBUG — INPUT
    print(">>> INPUT RECEIVED:", clean_input)

    # ✅ DEBUG — WHICH FILE IS ACTUALLY RUNNING
    print(">>> ORCHESTRATOR FILE:", inspect.getfile(PipelineOrchestrator))

    # 🚀 EXECUTE
    result = orchestrator.execute(intent)

    return result.to_dict()
