from claire.live_connectivity.source_allowlist import SourceAllowlist
from claire.live_connectivity.live_ingestion_gate import LiveIngestionGate

def test_allowlist_allows_domain():
    policy = SourceAllowlist().build_policy(["example.com"])
    assert SourceAllowlist().is_allowed("https://www.example.com/page", policy)

def test_live_gate_blocks_empty():
    assert LiveIngestionGate().evaluate({})["status"] == "blocked"
