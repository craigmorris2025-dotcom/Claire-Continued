
from __future__ import annotations

import importlib
import json
from pathlib import Path


EXPECTED_ROUTES = [
    "/operator/payload",
    "/operator/snapshot",
    "/operator/summary",
    "/operator/digest",
    "/operator/alerts",
    "/operator/readiness",
    "/operator/routes",
]


def router_manifest():
    return {
        "routes": [
            {
                "route": route,
                "method": "GET",
                "artifact": f"output/{route.strip('/').replace('/', '_')}.json",
                "mutating": False,
            }
            for route in EXPECTED_ROUTES
        ]
    }


def route_plateau():
    return {
        "routes": [
            {
                "route": route,
                "method": "GET",
                "artifact": f"output/{route.strip('/').replace('/', '_')}.json",
                "artifact_available": True,
                "mutating": False,
            }
            for route in EXPECTED_ROUTES
        ]
    }


def test_s42r5_mount_contract_is_read_only_and_ordered():
    module = importlib.import_module("claire.api.governed_operator_router_mount_contracts")
    contract = module.build_operator_mount_contract(router_manifest(), route_plateau())

    assert contract["route_count"] == 7
    assert contract["mount_allowed_count"] == 7
    assert contract["requires_app_py_patch"] is False
    assert contract["runtime_truth_mutation_allowed"] is False
    assert [route["route"] for route in contract["routes"]] == EXPECTED_ROUTES
    for route in contract["routes"]:
        assert route["method"] == "GET"
        assert route["mutating"] is False
        assert route["requires_app_py_patch"] is False


def test_s42r6_probe_plan_is_contract_only():
    module = importlib.import_module("claire.api.governed_operator_router_mount_contracts")
    contract = module.build_operator_mount_contract(router_manifest(), route_plateau())
    plan = module.build_operator_route_probe_plan(contract)

    assert plan["probe_count"] == 7
    assert plan["live_execution_allowed"] is False
    assert plan["contract_only"] is True
    for probe in plan["probes"]:
        assert probe["mutating"] is False
        assert probe["allowed_to_execute_live"] is False


def test_s42r7_readiness_and_verification_pass():
    module = importlib.import_module("claire.api.governed_operator_router_mount_contracts")
    contract = module.build_operator_mount_contract(router_manifest(), route_plateau())
    plan = module.build_operator_route_probe_plan(contract)
    readiness = module.build_operator_router_mount_readiness(contract, plan)
    verification = module.verify_operator_router_mount_contracts(contract, plan, readiness)

    assert readiness["status"] == "mount_contract_ready"
    assert readiness["requires_app_py_patch"] is False
    assert verification["verification_ok"] is True
    assert verification["failures"] == []


def test_s42r8_to_r12_writes_plateau_artifacts(tmp_path: Path):
    module = importlib.import_module("claire.api.governed_operator_router_mount_contracts")

    manifest_dir = tmp_path / "output" / "operator_read_only_router"
    plateau_dir = tmp_path / "output" / "operator_route_plateau"
    manifest_dir.mkdir(parents=True)
    plateau_dir.mkdir(parents=True)
    (manifest_dir / "operator_read_only_router_manifest.json").write_text(json.dumps(router_manifest()), encoding="utf-8")
    (plateau_dir / "operator_route_plateau_index.json").write_text(json.dumps(route_plateau()), encoding="utf-8")

    result = module.write_operator_router_mount_contracts(tmp_path, tmp_path / "out")
    assert set(result) == {"mount_contract", "probe_plan", "readiness", "verification", "report"}
    for value in result.values():
        assert Path(value).exists()

    report = json.loads(Path(result["report"]).read_text(encoding="utf-8"))
    assert report["status"] == "s42_mount_contract_plateau_ready"
    assert report["requires_app_py_patch"] is False
    assert report["next_phase"] == "S42R13-R16 app factory discovery and non-invasive router include adapter"
