
from pathlib import Path

from claire.live.live_connectivity_probe import probe_live_connectivity
from claire.live.source_registry import evaluate_source, seed_source_registry
from claire.live.live_ingestion_quarantine import ingest_live_candidate
from claire.live.governed_async_ingestion_queue import LiveIngestionJob, run_governed_ingestion_queue


def test_connectivity_probe_is_safe():
    result = probe_live_connectivity(timeout_seconds=0.5)
    assert result["version"] == "16.61"
    assert "No unrestricted fetching" in result["note"]


def test_source_registry_allows_known_government_source():
    seed_source_registry()
    result = evaluate_source("https://www.sec.gov")
    assert result["status"] == "allowed"
    assert result["may_score"] is True


def test_source_registry_quarantines_unknown_source():
    seed_source_registry()
    result = evaluate_source("https://unknown-example-source.invalid")
    assert result["status"] == "pending_review"
    assert result["may_score"] is False


def test_live_candidate_unknown_source_goes_to_quarantine():
    result = ingest_live_candidate(
        "https://unknown-example-source.invalid/article",
        "Unknown source test",
        {"summary": "test"},
    )
    assert result["status"] == "quarantined"
    assert Path("data/live/live_ingestion_quarantine.json").exists()


def test_governed_async_queue_completes():
    result = run_governed_ingestion_queue([
        LiveIngestionJob(
            source_url="https://www.sec.gov",
            title="Allowed source test",
            payload={"summary": "test"},
        )
    ])
    assert result["status"] == "completed"
    assert Path("data/live/governed_async_ingestion_queue.json").exists()
