
from __future__ import annotations

import importlib
import json
from pathlib import Path


def make_inputs(root: Path) -> None:
    bt = root / "output" / "backend_truth_surfaces"
    cc = root / "output" / "cockpit_consumption_contracts"
    mp = root / "output" / "manual_promotion_plateau"
    bt.mkdir(parents=True)
    cc.mkdir(parents=True)
    mp.mkdir(parents=True)

    status = {
        "available": True,
        "record_type": "backend_truth_surface_status",
        "status_sha256": "s" * 64,
        "surfaces": {
            "web_needs": {"available": True, "path": "output/governed_web_needs"},
            "research_queue": {"available": True, "path": "output/governed_research_queue"},
            "source_policy": {"available": True, "path": "output/source_policy"},
            "approved_fetch_plans": {"available": True, "path": "output/approved_fetch_plans"},
            "quarantined_evidence": {"available": True, "path": "output/quarantined_evidence", "json_count": 2},
            "extraction_reports": {"available": True, "path": "output/structured_knowledge", "json_count": 1},
        },
    }
    payload = {"available": True, "payload_sha256": "p" * 64}
    contracts = {"available": True, "contracts_sha256": "c" * 64}
    contract_verification = {"available": True, "verification_ok": True, "verification_sha256": "v" * 64}
    package_index = {"available": True, "record_type": "manual_promotion_package_index", "candidate_count": 1, "package_index_sha256": "i" * 64}
    blocked = {"available": True, "record_type": "blocked_promotion_candidate_registry", "blocked_count": 0, "blocked_registry_sha256": "b" * 64}
    replay = {"available": True, "record_type": "promotion_package_replay_verification", "replay_ok": True, "replay_report_sha256": "r" * 64}
    plateau = {"available": True, "record_type": "s39_manual_promotion_plateau_report", "status": "plateau_ready", "plateau_report_sha256": "t" * 64}

    (bt / "backend_truth_surface_status.json").write_text(json.dumps(status), encoding="utf-8")
    (bt / "backend_truth_surface_payload.json").write_text(json.dumps(payload), encoding="utf-8")
    (cc / "cockpit_consumption_contracts.json").write_text(json.dumps(contracts), encoding="utf-8")
    (cc / "cockpit_consumption_contract_verification.json").write_text(json.dumps(contract_verification), encoding="utf-8")
    (mp / "manual_promotion_package_index.json").write_text(json.dumps(package_index), encoding="utf-8")
    (mp / "blocked_promotion_candidate_registry.json").write_text(json.dumps(blocked), encoding="utf-8")
    (mp / "promotion_package_replay_verification.json").write_text(json.dumps(replay), encoding="utf-8")
    (mp / "s39_manual_promotion_plateau_report.json").write_text(json.dumps(plateau), encoding="utf-8")


def test_s40r9_builds_unified_payload(tmp_path: Path):
    module = importlib.import_module("claire.api.governed_unified_operator_payload")
    make_inputs(tmp_path)
    payload = module.build_unified_operator_payload(tmp_path)

    assert payload["backend_owns_truth"] is True
    assert payload["cockpit_presentation_only"] is True
    assert payload["section_count"] == 11
    assert payload["runtime_truth_mutation_allowed"] is False
    assert payload["automatic_update_allowed"] is False
    assert len(payload["operator_payload_sha256"]) == 64


def test_s40r10_sections_are_locked_and_ordered(tmp_path: Path):
    module = importlib.import_module("claire.api.governed_unified_operator_payload")
    make_inputs(tmp_path)
    payload = module.build_unified_operator_payload(tmp_path)

    assert [section["section"] for section in payload["sections"]] == module.SECTION_ORDER
    for section in payload["sections"]:
        assert section["runtime_truth_mutation_allowed"] is False
        assert section["automatic_update_allowed"] is False
        assert section["promotion_effect"] == "none"
        assert len(section["section_sha256"]) == 64


def test_s40r11_verification_passes(tmp_path: Path):
    module = importlib.import_module("claire.api.governed_unified_operator_payload")
    make_inputs(tmp_path)
    payload = module.build_unified_operator_payload(tmp_path)
    report = module.verify_unified_operator_payload(payload)

    assert report["verification_ok"] is True
    assert report["failures"] == []
    assert report["runtime_truth_mutation_allowed"] is False
    assert report["automatic_update_allowed"] is False


def test_s40r12_writes_unified_operator_artifacts(tmp_path: Path):
    module = importlib.import_module("claire.api.governed_unified_operator_payload")
    make_inputs(tmp_path)
    result = module.write_unified_operator_payload(tmp_path, tmp_path / "out")

    assert set(result) == {"payload", "verification"}
    for value in result.values():
        assert Path(value).exists()

    verification = json.loads(Path(result["verification"]).read_text(encoding="utf-8"))
    assert verification["verification_ok"] is True
