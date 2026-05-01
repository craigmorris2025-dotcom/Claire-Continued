"""
Market Universe Feeds — feed descriptors for Claire market universes.

v5.41:
- Declares feed coverage for public-company, private-sector, government, and defense universes.
- Does not scrape, call APIs, or ingest external data yet.
"""

from __future__ import annotations

from typing import Dict, List

from claire.feeds.feed_result_contracts import FeedCoverage


def market_universe_feed_coverage() -> List[FeedCoverage]:
    return [
        FeedCoverage(
            market_universe="sp500_public",
            display_name="S&P 500 public-company universe",
            coverage_label="S&P 500 coverage universe",
            coverage_target="503 companies / securities coverage target",
            category="public_markets",
            notes=[
                "Future connected feed target: public filings, company news, market pressure, acquisition logic.",
                "Current scaffold: deterministic fallback only.",
            ],
        ),
        FeedCoverage(
            market_universe="djia_public",
            display_name="Dow Jones Industrial Average blue-chip universe",
            coverage_label="DJIA coverage universe",
            coverage_target="30 companies",
            category="public_markets",
            notes=[
                "Future connected feed target: blue-chip strategic movement, modernization pressure, capability gaps.",
                "Current scaffold: deterministic fallback only.",
            ],
        ),
        FeedCoverage(
            market_universe="nasdaq_composite",
            display_name="NASDAQ Composite public-growth universe",
            coverage_label="NASDAQ Composite coverage universe",
            coverage_target="3,300 companies coverage target",
            category="public_markets",
            notes=[
                "Future connected feed target: software, AI, biotech, technology adoption and disruption signals.",
                "Current scaffold: deterministic fallback only.",
            ],
        ),
        FeedCoverage(
            market_universe="private_sector_establishments",
            display_name="Private-sector establishments universe",
            coverage_label="Private-sector establishment coverage",
            coverage_target="7.88 million establishments coverage target",
            category="private_markets",
            notes=[
                "Future connected feed target: private-market segmentation, regional clusters, NAICS-style coverage.",
                "Current scaffold: deterministic fallback only.",
            ],
        ),
        FeedCoverage(
            market_universe="federal_government",
            display_name="Federal / government buyer universe",
            coverage_label="Federal and public-sector buyer coverage",
            coverage_target="agency and program coverage target",
            category="government",
            notes=[
                "Future connected feed target: procurement, agency needs, public-sector compliance pressure.",
                "Current scaffold: deterministic fallback only.",
            ],
        ),
        FeedCoverage(
            market_universe="defense_industrial_base",
            display_name="Defense industrial base universe",
            coverage_label="Defense and critical mission ecosystem",
            coverage_target="prime, integrator, supplier, and program coverage target",
            category="defense_critical",
            notes=[
                "Future connected feed target: mission gaps, program pressure, supplier readiness, secure systems.",
                "Current scaffold: deterministic fallback only.",
            ],
        ),
        FeedCoverage(
            market_universe="custom_universe",
            display_name="Custom user-defined universe",
            coverage_label="Custom coverage",
            coverage_target="user-defined",
            category="custom",
            notes=[
                "Future connected feed target: user-provided source list or curated strategic portfolio.",
                "Current scaffold: deterministic fallback only.",
            ],
        ),
    ]


def coverage_by_universe() -> Dict[str, FeedCoverage]:
    return {item.market_universe: item for item in market_universe_feed_coverage()}
