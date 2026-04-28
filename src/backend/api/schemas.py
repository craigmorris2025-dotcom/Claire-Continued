"""
Pydantic request/response models for all API endpoints.
"""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class EvaluateRequest(BaseModel):
    input_text: str = Field(..., min_length=3, max_length=50000,
                            description="Target text to evaluate")
    mode: str = Field("deterministic",
                      pattern="^(deterministic|connected|hybrid)$",
                      description="Operating mode")
    request_type: str = Field("evaluate",
                              pattern="^(plan|analyze|evaluate|construct)$",
                              description="Request type")
    source: str = Field("api", description="Request source: api, ui, cli")
    priority: str = Field("medium", description="Priority: low, medium, high")


class EvaluateResponse(BaseModel):
    run_id: str = ""
    status: str = "success"
    mode: str = "deterministic"
    decision_classification: str = "UNKNOWN"
    breakthrough_classification: str = "UNKNOWN"
    scores: Dict[str, float] = Field(default_factory=dict)
    acquirer_matches: List[Dict[str, Any]] = Field(default_factory=list)
    domain: str = "general"
    keywords: List[str] = Field(default_factory=list)
    domain_scores: Dict[str, float] = Field(default_factory=dict)
    engine_details: Dict[str, Any] = Field(default_factory=dict)
    connector_sources: Dict[str, str] = Field(default_factory=dict)
    syntalion_ready: bool = False
    confidence: float = 0.0


class HealthResponse(BaseModel):
    status: str
    version: str
    checks: Dict[str, Any] = Field(default_factory=dict)
    passed: int = 0
    total: int = 0


class RunSummary(BaseModel):
    run_id: str = ""
    mode: str = "deterministic"
    decision_score: float = 0.0
    decision_class: str = ""
    breakthrough_score: float = 0.0
    portfolio_score: float = 0.0
    confidence: float = 0.0
    started_at: str = ""
    input_preview: str = ""


class HistoryResponse(BaseModel):
    runs: List[RunSummary] = Field(default_factory=list)
    total: int = 0


class StatsResponse(BaseModel):
    total_runs: int = 0
    avg_decision_score: float = 0.0
    avg_breakthrough: float = 0.0
    avg_portfolio: float = 0.0
    avg_confidence: float = 0.0
    go_count: int = 0
    caution_count: int = 0
    no_go_count: int = 0


class AcquirerProfile(BaseModel):
    name: str = ""
    ticker: str = ""
    sector: str = ""
    fit: float = 0.0
    capacity: float = 0.0
    strategy_alignment: float = 0.0
    tech_alignment: float = 0.0
    focus: List[str] = Field(default_factory=list)


class AcquirersResponse(BaseModel):
    acquirers: List[AcquirerProfile] = Field(default_factory=list)
    count: int = 0


class ConnectorRequest(BaseModel):
    connector: Optional[str] = Field(None, description="Connector: market, patent, financial")
    mode: str = Field("connected", description="Operating mode")
    sector: str = Field("technology", description="Query sector")
    domain: Optional[str] = Field(None, description="Domain filter")
