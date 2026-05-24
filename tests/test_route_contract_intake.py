from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient


def test_center_route_contract_selects_operator_route_families():
    from runtime_core.lifecycle.canonical_paths import (
        ACQUISITION_ROUTE,
        BREAKTHROUGH_DESIGN_ROUTE,
        BREAKTHROUGH_ESCALATION_ROUTE,
        EXISTING_SYSTEM_REPLACEMENT_ROUTE,
        PORTFOLIO_ROUTE,
    )
    from runtime_core.lifecycle.route_contracts import select_route_by_center_contract

    assert select_route_by_center_contract({})["selected_route"] == PORTFOLIO_ROUTE
    assert (
        select_route_by_center_contract({"breakthrough": {"primary": "market", "breakthrough_threshold": 0.80}})[
            "selected_route"
        ]
        == PORTFOLIO_ROUTE
    )
    assert (
        select_route_by_center_contract({"breakthrough": {"primary": "acquirer_fit", "breakthrough_threshold": 0.80}})[
            "selected_route"
        ]
        == ACQUISITION_ROUTE
    )
    assert (
        select_route_by_center_contract({"breakthrough": {"primary": "ai_native", "breakthrough_threshold": 0.80}})[
            "selected_route"
        ]
        == BREAKTHROUGH_DESIGN_ROUTE
    )
    assert (
        select_route_by_center_contract({"breakthrough": {"primary": "system_replacement", "breakthrough_threshold": 0.80}})[
            "selected_route"
        ]
        == EXISTING_SYSTEM_REPLACEMENT_ROUTE
    )
    assert (
        select_route_by_center_contract({"breakthrough": {"primary": "novel_category", "breakthrough_threshold": 0.80}})[
            "selected_route"
        ]
        == BREAKTHROUGH_ESCALATION_ROUTE
    )


def test_route_contracts_capture_all_operator_route_blocks():
    from runtime_core.lifecycle.route_contracts import build_route_contracts

    payload = build_route_contracts()

    assert payload["status"] == "ready"
    assert payload["route_count"] == 5
    assert payload["routes"]["portfolio"]["sequence"] == [23, 26, 27]
    assert payload["routes"]["breakthrough"]["sequence"] == [11, 12, 13, 14, 15]
    assert payload["routes"]["tech_design_build"]["sequence"] == [15, 16, 17, 18, 19, 20, 21, 22]
    assert payload["routes"]["acquisition"]["sequence"] == [24, 25, 28, 29, 30]
    assert payload["routes"]["recursive_memory"]["sequence"] == ["output", "memory", "replay"]
    assert payload["causal_intake_status"]["status"] == "deferred_until_route_and_emergence_contracts_are_clean"
    for contract in payload["routes"].values():
        assert Path(contract["source_file"]).exists()
    for source_file in payload["causal_intake_status"]["received_causal_contract_files"]:
        assert Path(source_file).exists()


def test_lifecycle_runner_uses_center_route_contract_when_breakthrough_present():
    from runtime_core.lifecycle.canonical_paths import ACQUISITION_ROUTE, BREAKTHROUGH_DESIGN_ROUTE, PORTFOLIO_ROUTE
    from runtime_core.lifecycle.lifecycle_runner import CoreLifecycleRunner

    runner = CoreLifecycleRunner()

    assert runner.detect_route({"breakthrough": {"primary": "market", "breakthrough_threshold": 0.70}}) == PORTFOLIO_ROUTE
    assert runner.detect_route({"breakthrough": {"primary": "technology", "breakthrough_threshold": 0.70}}) == BREAKTHROUGH_DESIGN_ROUTE
    assert runner.detect_route({"breakthrough": {"primary": "buyer", "breakthrough_threshold": 0.70}}) == ACQUISITION_ROUTE


def test_lifecycle_route_contract_routes_are_mounted():
    from runtime_core.app import create_app

    client = TestClient(create_app())

    center = client.get("/api/lifecycle/center-route-contract")
    contracts = client.get("/api/lifecycle/route-contracts")
    selected = client.post(
        "/api/lifecycle/select-route",
        json={"breakthrough": {"primary": "ai_native", "breakthrough_threshold": 0.80}},
    )

    assert center.status_code == 200
    assert contracts.status_code == 200
    assert contracts.json()["route_count"] == 5
    assert selected.status_code == 200
    assert selected.json()["selected_route"] == "breakthrough_design"
    assert selected.json()["selected_route_id"] == "tech_design_build"
