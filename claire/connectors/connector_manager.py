from claire.connectors.market import MarketConnector
from claire.connectors.patent import PatentConnector
from claire.connectors.financial import FinancialConnector


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
