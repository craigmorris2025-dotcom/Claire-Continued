from __future__ import annotations

import importlib
from pathlib import Path


def test_s149_s155_import_origin_and_exact_assertions(tmp_path):
    module = importlib.import_module("claire.api.governed_cockpit_payload_visibility_s149_s155")
    origin = Path(module.__file__).as_posix()

    assert origin.endswith("governed_cockpit_payload_visibility_s149_s155.py")

    contract = module.build_cockpit_payload_read_contract()
    assert contract["stage_version"] == "S149"
    assert contract["status"] == "cockpit_payload_read_contract_ready"

    probe = module.build_live_payload_visibility_probe()
    assert probe["stage_version"] == "S150"
    assert probe["ok"] is True

    nonbreak = module.build_existing_payload_nonbreak_probe()
    assert nonbreak["stage_version"] == "S151"
    assert nonbreak["ok"] is True

    repeated = module.build_repeated_payload_fetch_stability_probe(fetch_count=3)
    assert repeated["stage_version"] == "S152"
    assert repeated["ok"] is True
    assert repeated["fetch_count"] == 3

    manifest = module.build_cockpit_payload_manifest()
    assert manifest["stage_version"] == "S153"
    assert manifest["status"] == "cockpit_payload_manifest_ready"

    readiness = module.build_cockpit_live_visibility_readiness()
    assert readiness["stage_version"] == "S154"
    assert readiness["ok"] is True

    stop_gate = module.build_s149_s155_stop_gate(report_dir=tmp_path / "reports")
    assert stop_gate["stage_version"] == "S155"
    assert stop_gate["ok"] is True
    assert stop_gate["stop_go"] == "GO"
    assert "report_path" in stop_gate
