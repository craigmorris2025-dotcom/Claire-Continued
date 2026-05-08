from claire.distributed_production_runtime import DistributedProductionRuntime


def test_distributed_runtime_cycle_passes_regression():
    runtime = DistributedProductionRuntime()
    result = runtime.run_cycle(
        topic="governed research systems",
        payload={"confidence": 0.72, "signal": "demand increasing"},
        campaigns=[
            {"name": "campaign a", "topics": ["governed research systems"], "confidence": 0.7},
            {"name": "campaign b", "topics": ["governed research systems", "ai infra"], "confidence": 0.8},
        ],
    )

    assert result["layer"] == "distributed_production_runtime"
    assert result["regression"]["regression_status"] == "passed"
    assert result["workload_assignment"]["status"] == "assigned"
    assert result["health"]["status"] == "healthy"
    assert result["governance_boundary"] == "production_contract_no_unreviewed_external_action"


def test_bootstrap_creates_workers_and_shards():
    runtime = DistributedProductionRuntime()
    runtime.bootstrap(shard_count=3, workers_per_shard=2)

    assert len(runtime.shards.snapshot()) == 3
    assert len(runtime.workers.snapshot()) == 6


def test_cross_campaign_fusion_detects_repeated_topic():
    runtime = DistributedProductionRuntime()
    result = runtime.run_cycle(
        topic="market structure",
        payload={"confidence": 0.6},
        campaigns=[
            {"topics": ["market structure"], "confidence": 0.5},
            {"topics": ["market structure"], "confidence": 0.7},
        ],
    )

    assert "market structure" in result["cross_campaign_fusion"]["repeated_topics"]
