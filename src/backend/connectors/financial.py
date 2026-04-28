"""
Financial Data Connector — valuation benchmarks, deal metrics, financial health.
API-ready: override _live_fetch() for Alpha Vantage, FRED, SEC EDGAR.
"""
import logging
from typing import Any, Dict
from backend.connectors.base import BaseConnector

logger = logging.getLogger("claire.connectors.financial")

FINANCIAL_DATA = {
    "defense": {
        "avg_revenue_multiple": 3.2, "avg_ebitda_multiple": 14.0,
        "median_gross_margin": 0.28, "avg_rd_spend_pct": 0.05,
        "avg_debt_equity": 0.65, "typical_deal_premium_pct": 0.25,
        "cost_of_capital_pct": 0.085,
        "comparable_transactions": [
            {"name": "L3Harris/Aerojet", "ev_revenue": 3.8, "ev_ebitda": 16.2, "premium_pct": 0.30},
            {"name": "Raytheon/UTC", "ev_revenue": 2.1, "ev_ebitda": 12.5, "premium_pct": 0.18},
            {"name": "Northrop/Orbital ATK", "ev_revenue": 2.4, "ev_ebitda": 13.8, "premium_pct": 0.22},
        ],
        "risk_factors": {"customer_concentration": 0.75, "contract_visibility_years": 3.5,
                        "backlog_ratio": 2.8, "book_to_bill": 1.15},
        "valuation_signal": 0.72,
    },
    "technology": {
        "avg_revenue_multiple": 8.5, "avg_ebitda_multiple": 22.0,
        "median_gross_margin": 0.72, "avg_rd_spend_pct": 0.18,
        "avg_debt_equity": 0.35, "typical_deal_premium_pct": 0.32,
        "cost_of_capital_pct": 0.095,
        "comparable_transactions": [
            {"name": "Broadcom/VMware", "ev_revenue": 6.8, "ev_ebitda": 25.0, "premium_pct": 0.44},
            {"name": "Cisco/Splunk", "ev_revenue": 7.2, "ev_ebitda": 35.0, "premium_pct": 0.31},
            {"name": "Microsoft/Nuance", "ev_revenue": 12.5, "ev_ebitda": 45.0, "premium_pct": 0.23},
        ],
        "risk_factors": {"customer_concentration": 0.35, "contract_visibility_years": 1.2,
                        "backlog_ratio": 0.8, "book_to_bill": 1.05},
        "valuation_signal": 0.65,
    },
    "healthcare": {
        "avg_revenue_multiple": 5.8, "avg_ebitda_multiple": 18.0,
        "median_gross_margin": 0.65, "avg_rd_spend_pct": 0.22,
        "avg_debt_equity": 0.42, "typical_deal_premium_pct": 0.38,
        "cost_of_capital_pct": 0.090,
        "comparable_transactions": [
            {"name": "Pfizer/Seagen", "ev_revenue": 9.8, "ev_ebitda": 42.0, "premium_pct": 0.33},
            {"name": "Amgen/Horizon", "ev_revenue": 7.5, "ev_ebitda": 28.0, "premium_pct": 0.48},
        ],
        "risk_factors": {"customer_concentration": 0.25, "contract_visibility_years": 2.0,
                        "backlog_ratio": 1.5, "book_to_bill": 1.10},
        "valuation_signal": 0.68,
    },
    "energy": {
        "avg_revenue_multiple": 2.8, "avg_ebitda_multiple": 10.0,
        "median_gross_margin": 0.35, "avg_rd_spend_pct": 0.03,
        "avg_debt_equity": 0.85, "typical_deal_premium_pct": 0.20,
        "cost_of_capital_pct": 0.080,
        "comparable_transactions": [
            {"name": "Brookfield/Origin", "ev_revenue": 2.5, "ev_ebitda": 9.0, "premium_pct": 0.18},
        ],
        "risk_factors": {"customer_concentration": 0.40, "contract_visibility_years": 5.0,
                        "backlog_ratio": 3.2, "book_to_bill": 1.08},
        "valuation_signal": 0.60,
    },
}


class FinancialConnector(BaseConnector):
    def get_name(self) -> str:
        return "financial"

    def fetch(self, query: Dict[str, Any], mode: str = "connected") -> Dict[str, Any]:
        return self._safe_fetch(query, mode)

    def _live_fetch(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Wire to real financial API here:
          - Alpha Vantage (free tier: sector performance, fundamentals)
          - FRED API (free: macro indicators, rates, GDP)
          - SEC EDGAR (free: company filings, 10-K/10-Q)
          - PitchBook (licensed: deal comps, valuations)
        """
        return None

    def fallback(self, query: Dict[str, Any]) -> Dict[str, Any]:
        sector = query.get("sector", query.get("domain", "technology")).lower()
        if sector not in FINANCIAL_DATA:
            sector = "technology"
        data = dict(FINANCIAL_DATA[sector])
        data["sector"] = sector

        # Compute deal attractiveness signal
        margin = data["median_gross_margin"]
        rd = data["avg_rd_spend_pct"]
        leverage = data["avg_debt_equity"]
        data["deal_attractiveness"] = round(
            margin * 0.35 + (1.0 - leverage) * 0.25 + rd * 0.20 + data["valuation_signal"] * 0.20, 4
        )

        logger.info(f"Financial fallback: sector={sector}, deal_attractiveness={data['deal_attractiveness']:.3f}")
        return {"connector": "financial", "sector": sector, "data": data}
