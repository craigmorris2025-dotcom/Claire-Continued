"""
Pipeline Routes — POST /evaluate, GET /scorecard/{run_id}
"""
from fastapi import APIRouter, HTTPException
from backend.api.schemas import EvaluateRequest, EvaluateResponse
from backend.claire.contract import ContractValidator
from backend.orchestrator.pipeline import PipelineOrchestrator
from backend.scoring.scorecard import ScoreCard
from backend.persistence.database import Database

router = APIRouter(tags=["Pipeline"])
pipeline = PipelineOrchestrator()
db = Database()


@router.post("/evaluate", response_model=EvaluateResponse)
async def evaluate(req: EvaluateRequest):
    """Run the full 24-engine evaluation pipeline."""
    validator = ContractValidator()
    intent, errors = validator.validate_input({
        "raw_input": req.input_text,
        "mode": req.mode,
        "source": req.source,
        "priority": req.priority,
    })

    if errors or intent is None:
        raise HTTPException(status_code=422, detail={"validation_errors": errors})

    result = pipeline.execute(intent)

    return EvaluateResponse(
        run_id=result.data.get("run_id", ""),
        status=result.status,
        mode=result.mode,
        decision_classification=result.decision_classification or "UNKNOWN",
        breakthrough_classification=result.breakthrough_classification or "UNKNOWN",
        scores=result.scores or {},
        acquirer_matches=result.acquirer_matches or [],
        domain=result.data.get("domain", "general"),
        keywords=result.data.get("keywords", []),
        domain_scores=result.data.get("domain_scores", {}),
        engine_details=result.data.get("engine_details", {}),
        connector_sources=result.data.get("connector_sources", {}),
        syntalion_ready=result.ready_for_syntalion,
        confidence=result.scores.get("_confidence", 0) if result.scores else 0,
    )


@router.get("/scorecard/{run_id}")
async def get_scorecard(run_id: str):
    """Get a formatted scorecard for a completed run."""
    run = db.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")
    return {"run_id": run_id, "scores": run.get("full_result", {}).get("scores", {})}
