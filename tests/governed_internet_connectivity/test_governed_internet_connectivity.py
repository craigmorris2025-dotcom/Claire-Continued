from claire.governed_internet_connectivity import GovernedInternetRuntime, SourcePolicyEngine


def test_allowed_source_stub_research_passes_regression():
    runtime = GovernedInternetRuntime()
    result = runtime.run_research_stub(
        query="AI disclosure rules",
        source_url="https://www.sec.gov/newsroom",
        query_terms=["AI", "disclosure"],
    )

    assert result["layer"] == "governed_internet_connectivity"
    assert result["source_policy"]["decision"] == "allowed"
    assert result["fetch"]["status"] == "stubbed_success"
    assert result["regression"]["regression_status"] == "passed"
    assert result["governance_boundary"] == "no_unreviewed_external_action"


def test_unknown_source_requires_review():
    runtime = GovernedInternetRuntime()
    result = runtime.run_research_stub(
        query="unknown source test",
        source_url="https://example-random-site.invalid/report",
    )

    assert result["source_policy"]["decision"] == "review_required"
    assert result["fetch"]["status"] == "review_required"
    assert result["regression"]["regression_status"] == "passed"


def test_watchlist_schedule_contract():
    runtime = GovernedInternetRuntime()
    result = runtime.build_watchlist_schedule(
        [
            {
                "topic": "governed autonomous research systems",
                "thesis": "Demand is rising for auditable AI research infrastructure.",
                "confidence": 0.71,
                "cadence": "daily",
            }
        ]
    )

    assert len(result["watchlist"]) == 1
    assert result["schedule"]["status"] == "schedule_ready"
    assert result["governance_boundary"] == "no_unreviewed_external_action"


def test_policy_blocks_explicit_blocked_domain():
    engine = SourcePolicyEngine()
    engine.policy.blocked_domains.append("bad.example")
    decision = engine.evaluate("https://bad.example/a")
    assert decision["decision"] == "blocked"
