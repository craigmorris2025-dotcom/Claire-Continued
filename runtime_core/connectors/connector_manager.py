from runtime_core.connectors.market import MarketConnector
from runtime_core.connectors.patent import PatentConnector
from runtime_core.connectors.financial import FinancialConnector


class ConnectorManager:

    def __init__(self):
        self.market = MarketConnector()
        self.patent = PatentConnector()
        self.financial = FinancialConnector()

    def fetch_all(self, query: str):
        return {
            "market": self.market.fetch(query),
            "patent": self.patent.fetch(query),
            "financial": self.financial.fetch(query),
        }
