from __future__ import annotations


class LiveSourceCatalog:
    def __init__(self) -> None:
        self.urls = [
            "https://www.sec.gov/edgar/search/",
            "https://www.nasdaq.com/market-activity/stocks",
            "https://www.nyse.com/listings_directory/stock",
            "https://www.spglobal.com/spdji/en/indices/equity/sp-500/",
            "https://finance.yahoo.com/",
        ]

    def status(self) -> dict:
        return {
            "status": "success",
            "source_pack_count": 1,
            "active_source_count": len(self.urls),
        }

    def resolve(self, market_universe: str = "sp500_public", limit: int = 5) -> dict:
        return {
            "status": "success",
            "market_universe": market_universe,
            "source_count": limit,
            "source_urls": self.urls[:limit],
        }
