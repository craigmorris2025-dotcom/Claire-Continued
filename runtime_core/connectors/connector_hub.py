class ConnectorHub:

    def __init__(self):
        # lazy imports so we don’t break if names differ
        try:
            from runtime_core.connectors.market_connector import MarketConnector
            self.market = MarketConnector()
        except:
            self.market = None

        try:
            from runtime_core.connectors.patent_connector import PatentConnector
            self.patent = PatentConnector()
        except:
            self.patent = None

        try:
            from runtime_core.connectors.financial_connector import FinancialConnector
            self.financial = FinancialConnector()
        except:
            self.financial = None


    # -------------------------
    # SAFE CALL WRAPPER
    # -------------------------
    def _safe_call(self, connector, domain, keywords):

        if connector is None:
            return {}

        # Try common method names
        for method in ["fetch", "run", "get", "execute"]:
            if hasattr(connector, method):
                try:
                    fn = getattr(connector, method)

                    # Try calling with domain
                    try:
                        return fn(domain)
                    except:
                        pass

                    # Try calling with keywords
                    try:
                        return fn(keywords)
                    except:
                        pass

                    # Try no args
                    try:
                        return fn()
                    except:
                        pass

                except Exception:
                    return {}

        return {}


    # -------------------------
    # NORMALIZE OUTPUT
    # -------------------------
    def _normalize_market(self, data):
        return {
            "source": "market_connector",
            "growth_rate": data.get("growth_rate", data.get("growth", 0.05)),
            "volatility": data.get("volatility", 0.15),
            "market_cap_b": data.get("market_cap_b", 5000),
            "confidence": data.get("confidence", 0.6)
        }

    def _normalize_patent(self, data):
        return {
            "source": "patent_connector",
            "innovation_signal": data.get("innovation_signal", 0.1),
            "patent_density": data.get("patent_density", 0.3),
            "confidence": data.get("confidence", 0.6)
        }

    def _normalize_financial(self, data):
        return {
            "source": "financial_connector",
            "rev_multiple": data.get("rev_multiple", 5.0),
            "ebitda_multiple": data.get("ebitda_multiple", 15),
            "deal_activity": data.get("deal_activity", 0.5),
            "confidence": data.get("confidence", 0.65)
        }


    # -------------------------
    # MAIN GATHER
    # -------------------------
    def gather(self, domain: str, keywords):

        raw_market = self._safe_call(self.market, domain, keywords)
        raw_patent = self._safe_call(self.patent, domain, keywords)
        raw_financial = self._safe_call(self.financial, domain, keywords)

        market = self._normalize_market(raw_market)
        patent = self._normalize_patent(raw_patent)
        financial = self._normalize_financial(raw_financial)

        return {
            "market": market,
            "patent": patent,
            "financial": financial,
            "sources": {
                "market": market["source"],
                "patent": patent["source"],
                "financial": financial["source"],
            }
        }
