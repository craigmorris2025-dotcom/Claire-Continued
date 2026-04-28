"""
24 Domain Engines — Auto-discovery registry.
Imports all engines and builds DOMAIN_REGISTRY + PHASE_SEQUENCE.
"""
from backend.engines.ingestion import IngestionEngine
from backend.engines.semantic import SemanticEngine
from backend.engines.fusion import FusionEngine
from backend.engines.company import CompanyEngine
from backend.engines.engineering import EngineeringEngine
from backend.engines.product import ProductEngine
from backend.engines.customer import CustomerEngine
from backend.engines.competitive import CompetitiveEngine
from backend.engines.operational import OperationalEngine
from backend.engines.financial import FinancialEngine
from backend.engines.synergy import SynergyEngine
from backend.engines.strategy import StrategyEngine
from backend.engines.risk import RiskEngine
from backend.engines.market import MarketEngine
from backend.engines.innovation import InnovationEngine
from backend.engines.breakthrough import BreakthroughEngine
from backend.engines.predictive import PredictiveEngine
from backend.engines.forecasting import ForecastingEngine
from backend.engines.deal import DealEngine
from backend.engines.decision import DecisionEngine
from backend.engines.discovery import DiscoveryEngine
from backend.engines.acquirer_matching import AcquirermatchingEngine
from backend.engines.portfolio import PortfolioEngine
from backend.engines.compliance import ComplianceEngine

# Ordered engine instances
_ALL_ENGINES = [
    IngestionEngine(), SemanticEngine(), FusionEngine(),
    CompanyEngine(), EngineeringEngine(), ProductEngine(),
    CustomerEngine(), CompetitiveEngine(), OperationalEngine(), FinancialEngine(),
    SynergyEngine(), StrategyEngine(), RiskEngine(), MarketEngine(),
    InnovationEngine(), BreakthroughEngine(), PredictiveEngine(), ForecastingEngine(),
    DealEngine(), DecisionEngine(), DiscoveryEngine(), AcquirermatchingEngine(),
    PortfolioEngine(), ComplianceEngine(),
]

# Key → engine instance
DOMAIN_REGISTRY = {e.get_key(): e for e in _ALL_ENGINES}

# Phase → [engine_keys] in execution order
PHASE_SEQUENCE = [
    ("ingestion_semantic", ["ingestion", "semantic", "fusion"]),
    ("intel_scoring", ["company", "engineering", "product", "customer",
                       "competitive", "operational", "financial"]),
    ("strategic_analysis", ["synergy", "strategy", "risk", "market"]),
    ("innovation_breakthrough", ["innovation", "breakthrough", "predictive", "forecasting"]),
    ("deal_construction", ["deal", "decision", "discovery", "acquirer_matching"]),
    ("portfolio_compliance", ["portfolio", "compliance"]),
]
