from claire.feeds.source_catalogs.live_source_catalog import LiveSourceCatalog
from claire.feeds.source_catalogs.source_health import LiveSourceHealthChecker


def test_live_source_catalog_resolves_public_company_sources():
    catalog = LiveSourceCatalog()
    status = catalog.status()
    assert status["status"] == "success"
    assert status["source_pack_count"] >= 1
    assert status["active_source_count"] >= 5

    resolved = catalog.resolve(market_universe="sp500_public", limit=5)
    assert resolved["status"] == "success"
    assert resolved["source_count"] == 5
    assert all(url.startswith("https://") for url in resolved["source_urls"])


def test_live_source_health_catalog_only_check():
    payload = LiveSourceHealthChecker().check(market_universe="sp500_public", limit=3, fetch_live=False)
    assert payload["status"] == "success"
    assert payload["source_count"] == 3
    assert payload["healthy_count"] == 3
    assert payload["live_fetch_performed"] is False
