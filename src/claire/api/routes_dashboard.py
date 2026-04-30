from fastapi import APIRouter
from ..services.dashboard_services import *

router = APIRouter(prefix='/dashboard', tags=['dashboard'])

@router.get('/discovery/live')
def discovery_live(): return get_live_discoveries()

@router.get('/market/overview')
def market_overview(): return get_market_overview()

@router.get('/innovation/search')
def innovation_search(): return search_innovations()

@router.get('/financial/markets')
def financial_markets(): return get_financial_markets()

@router.get('/news/intel')
def news_intel(): return get_news_intel()

@router.get('/patents/search')
def patents_search(): return search_patents()

@router.get('/company/intel')
def company_intel(): return get_company_intel()

@router.get('/portfolio/active')
def portfolio_active(): return get_active_portfolios()

@router.get('/buyer/matching')
def buyer_matching(): return get_buyer_matches()

@router.get('/deals/pipeline')
def deals_pipeline(): return get_deal_pipeline()

@router.get('/system/settings')
def system_settings(): return get_system_settings()
