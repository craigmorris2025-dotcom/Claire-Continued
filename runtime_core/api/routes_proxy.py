"""
History Routes — GET /history, /history/{run_id}, /stats
"""

from fastapi import APIRouter, HTTPException, Query

# ✅ FIXED IMPORTS
from runtime_core.api.schemas import HistoryResponse, RunSummary, StatsResponse
from runtime_core.persistence.database import Database


router = APIRouter(tags=["history"])
db = Database()


@router.get("/history", response_model=HistoryResponse)
async def get_history(
    limit: int = Query(default=25, le=100),
    offset: int = Query(default=0, ge=0),
):
    """Retrieve pipeline run history."""

    runs = db.get_runs(limit=limit, offset=offset)
    summaries = []

    for run in runs:
        summaries.append(
            RunSummary(
                run_id=run.get("run_id", ""),
                mode=run.get("mode", "deterministic"),
                decision_score=run.get("decision_score", 0),
                decision_class=run.get("decision_class", ""),
                breakthrough_score=run.get("breakthrough_score", 0),
                portfolio_score=run.get("portfolio_score", 0),
                confidence=run.get("confidence", 0),
                started_at=run.get("started_at", ""),
                input_preview=run.get("input_text", "")[:120],
            )
        )

    return HistoryResponse(
        runs=summaries,
        total=len(summaries)
    )


@router.get("/history/{run_id}")
async def get_run_detail(run_id: str):
    """Retrieve full details for a single run."""

    run = db.get_run(run_id)

    if not run:
        raise HTTPException(
            status_code=404,
            detail=f"Run {run_id} not found"
        )

    return run


@router.get("/stats", response_model=StatsResponse)
async def get_stats():
    """Aggregate statistics across all pipeline runs."""

    stats = db.get_stats()

    return StatsResponse(
        total_runs=stats.get("total_runs", 0),
        avg_decision_score=stats.get("avg_decision_score", 0),
        avg_breakthrough=stats.get("avg_breakthrough", 0),
        avg_portfolio=stats.get("avg_portfolio", 0),
        avg_confidence=stats.get("avg_confidence", 0),
        go_count=stats.get("go_count", 0),
        caution_count=stats.get("caution_count", 0),
        no_go_count=stats.get("no_go_count", 0),
    )
