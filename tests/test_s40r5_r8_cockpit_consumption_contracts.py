
from __future__ import annotations

import importlib
import json
from pathlib import Path


def make_truth_surfaces(root: Path) -> None:
    out = root / "output" / "backend_truth_surfaces"
    out.mkdir(parents=True)
    status = {
        "available": True,
        "surfaces": {
            "system_inventory": {"available": True, "path": "output/system_inventory"},
            "web_needs": {"available": False, "path": "output/governed_web_needs", "reason": "missing"},
            "research_queue": {"available": True, "path": "output/governed_research_queue"},
            "source_policy": {"available": True, "path": "output/source_policy"},
            "approved_fetch_plans": {"available": True, "path": "output/approved_fetch_plans"},
            "quarantined_evidence": {"available": True, "path": "output/quarantined_evidence", "json_count": 2},
            "extraction_reports": {"available": True, "path": "output/structured_knowledge", "json_count": 1},
            "manual_promotion_status": {"available": True, "path": "output/manual_promotion_plateau/s39_manual_promotion_plateau_report.json"},
            "update_proposal_status": {"available": True, "path": "output/manual_promotion_plateau/manual_promotion_package_index.json"},
        },
    }
    payload = {
        "available": True,
        "manual_promotion": {
            "plateau_report": {
                "available": True,
                "record_type": "s39_manual_promotion_plateau_report",
                "candidate_count": 1,
                "blocked_count": 0,
                "runtime_truth_mutation_allowed": False,
                "promotion_effect": "none",
            },
            "package_index": {
                "available": True,
                "record_type": "manual_promotion_package_index",
                "candidate_count": 1,
                "runtime_truth_mutation_allowed": False,
                "promotion_effect": "none",
            },
        },
    }
    (out / "backend_truth_surface_status.json").write_text(json.dumps(status), encoding="utf-8")
    (out / "backend_truth_surface_payload.json").write_text(json.dumps(payload), encoding="utf-8")


def test_s40r5_builds_panel_contracts(tmp_path: Path):
    module = importlib.import_module("runtime_core.api.governed_cockpit_consumption_contracts")
    make_truth_surfaces(tmp_path)
    contracts = module.build_cockpit_panel_contracts(tmp_path)

    assert contracts["backend_owns_truth"] is True
    assert contracts["cockpit_presentation_only"] is True
    assert contracts["panel_count"] == 9
    assert contracts["runtime_truth_mutation_allowed"] is False
    assert contracts["automatic_update_allowed"] is False
    assert len(contracts["contracts_sha256"]) == 64


def test_s40r6_panel_index_is_read_only(tmp_path: Path):
    module = importlib.import_module("runtime_core.api.governed_cockpit_consumption_contracts")
    make_truth_surfaces(tmp_path)
    contracts = module.build_cockpit_panel_contracts(tmp_path)
    index = module.build_cockpit_panel_index(contracts)

    assert index["panel_count"] == 9
    assert index["runtime_truth_mutation_allowed"] is False
    assert index["automatic_update_allowed"] is False
    assert index["panels"][0]["panel"] == "system_inventory"
    assert len(index["panel_index_sha256"]) == 64


def test_s40r7_verification_passes_safe_contracts(tmp_path: Path):
    module = importlib.import_module("runtime_core.api.governed_cockpit_consumption_contracts")
    make_truth_surfaces(tmp_path)
    contracts = module.build_cockpit_panel_contracts(tmp_path)
    report = module.verify_cockpit_contracts(contracts)

    assert report["verification_ok"] is True
    assert report["failures"] == []
    assert report["runtime_truth_mutation_allowed"] is False
    assert report["automatic_update_allowed"] is False


def test_s40r8_writes_contract_artifacts(tmp_path: Path):
    module = importlib.import_module("runtime_core.api.governed_cockpit_consumption_contracts")
    make_truth_surfaces(tmp_path)
    result = module.write_cockpit_consumption_contracts(tmp_path, tmp_path / "out")

    assert set(result) == {"contracts", "panel_index", "verification"}
    for value in result.values():
        assert Path(value).exists()

    verification = json.loads(Path(result["verification"]).read_text(encoding="utf-8"))
    assert verification["verification_ok"] is True
