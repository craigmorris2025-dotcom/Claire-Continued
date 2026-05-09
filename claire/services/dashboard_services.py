from typing import List
from ..models.dashboard import *

def get_live_discoveries():
    return DiscoveryResponse(data=[
        DiscoveryItem(id='disc-001', title='Next-gen battery materials', domain='Energy', signal_strength=0.87, confidence=0.82, summary='Emerging materials.'),
        DiscoveryItem(id='disc-002', title='AI-driven supply chain', domain='Logistics', signal_strength=0.79, confidence=0.80, summary='Autonomous routing.'),
    ])

def get_market_overview():
    return MarketOverviewResponse(data=MarketOverview(sector='Semiconductors', trend='Bullish', confidence=0.83, notes='Strong demand.'))

def search_innovations():
    return InnovationResponse(data=[
        InnovationResult(id='inv-001', category='Manufacturing', novelty_score=0.91, manufacturability_score=0.78, description='Micro-factories.'),
        InnovationResult(id='inv-002', category='Healthcare', novelty_score=0.88, manufacturability_score=0.81, description='Wearable diagnostics.'),
    ])

def get_financial_markets():
    return FinancialResponse(data=[
        FinancialSnapshot(symbol='^SPX', price=5200.0, change=12.5, change_pct=0.24, sentiment='Positive'),
        FinancialSnapshot(symbol='^NDX', price=18000.0, change=45.2, change_pct=0.25, sentiment='Positive'),
    ])

def get_news_intel():
    return NewsResponse(data=[
        NewsItem(id='news-001', headline='Major acquisition', source='Reuters', impact='High', summary='Battery IP consolidation.'),
        NewsItem(id='news-002', headline='AI procurement framework', source='Bloomberg', impact='Medium', summary='Regulatory clarity.'),
    ])

def search_patents():
    return PatentResponse(data=[
        PatentItem(id='US-1234567', title='Solid-state battery', assignee='FutureEnergy', status='Granted', relevance=0.92),
        PatentItem(id='US-9876543', title='Autonomous routing', assignee='LogiAI', status='Pending', relevance=0.88),
    ])

def get_company_intel():
    return CompanyResponse(data=CompanyProfile(name='Syntalion Labs', sector='AI', stage='Growth', score=0.89, summary='Autonomous innovation engine.'))

def get_active_portfolios():
    return PortfolioResponse(data=[
        PortfolioItem(id='port-001', name='Energy Transition', value=125000000.0, risk_level='Moderate', status='Active'),
        PortfolioItem(id='port-002', name='Defense Innovation', value=210000000.0, risk_level='Balanced', status='Active'),
    ])

def get_buyer_matches():
    return BuyerResponse(data=[
        BuyerMatch(buyer='Global Energy OEM', fit_score=0.91, strategic_rationale='Battery modernization.'),
        BuyerMatch(buyer='Defense Prime', fit_score=0.88, strategic_rationale='Dual-use AI.'),
    ])

def get_deal_pipeline():
    return DealsResponse(data=[
        DealStage(id='deal-001', name='EV Battery IP', stage='Negotiation', value=45000000.0, probability=0.7),
        DealStage(id='deal-002', name='Defense AI Suite', stage='Proposal', value=80000000.0, probability=0.5),
    ])

def get_system_settings():
    return SettingsResponse(data=SystemSettings(mode='deterministic', audit_trail=True, deterministic=True, connected_intel=False))
