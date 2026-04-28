from pydantic import BaseModel
from typing import List
from datetime import datetime

class BaseResponse(BaseModel):
    status: str = 'ok'
    source: str = 'claire-syntalion'
    timestamp: datetime = datetime.utcnow()

class DiscoveryItem(BaseModel):
    id: str
    title: str
    domain: str
    signal_strength: float
    confidence: float
    summary: str

class MarketOverview(BaseModel):
    sector: str
    trend: str
    confidence: float
    notes: str

class InnovationResult(BaseModel):
    id: str
    category: str
    novelty_score: float
    manufacturability_score: float
    description: str

class FinancialSnapshot(BaseModel):
    symbol: str
    price: float
    change: float
    change_pct: float
    sentiment: str

class NewsItem(BaseModel):
    id: str
    headline: str
    source: str
    impact: str
    summary: str

class PatentItem(BaseModel):
    id: str
    title: str
    assignee: str
    status: str
    relevance: float

class CompanyProfile(BaseModel):
    name: str
    sector: str
    stage: str
    score: float
    summary: str

class PortfolioItem(BaseModel):
    id: str
    name: str
    value: float
    risk_level: str
    status: str

class BuyerMatch(BaseModel):
    buyer: str
    fit_score: float
    strategic_rationale: str

class DealStage(BaseModel):
    id: str
    name: str
    stage: str
    value: float
    probability: float

class SystemSettings(BaseModel):
    mode: str
    audit_trail: bool
    deterministic: bool
    connected_intel: bool

class DiscoveryResponse(BaseResponse):
    data: List[DiscoveryItem]

class MarketOverviewResponse(BaseResponse):
    data: MarketOverview

class InnovationResponse(BaseResponse):
    data: List[InnovationResult]

class FinancialResponse(BaseResponse):
    data: List[FinancialSnapshot]

class NewsResponse(BaseResponse):
    data: List[NewsItem]

class PatentResponse(BaseResponse):
    data: List[PatentItem]

class CompanyResponse(BaseResponse):
    data: CompanyProfile

class PortfolioResponse(BaseResponse):
    data: List[PortfolioItem]

class BuyerResponse(BaseResponse):
    data: List[BuyerMatch]

class DealsResponse(BaseResponse):
    data: List[DealStage]

class SettingsResponse(BaseResponse):
    data: SystemSettings
