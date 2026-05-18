
from __future__ import annotations

import importlib
import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient


def make_payload(root: Path) -> None:
    target = root / "output" / "unified_operator_payload" / "unified_backend_operator_payload.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps({
        "record_type": "unified_backend_operator_payload",
        "runtime_truth_mutation_allowed": False,
        "operator_payload_sha256": "p" * 64,
    }), encoding="utf-8")


def test_s42r13_discovery_is_non_invasive():
    module = importlib.import_module("claire.api.operator_router_include_adapter")
    report = module.discover_app_factory()

    assert report["app_py_patch_required"] is False
    assert report["non_invasive"] is True
    assert report["runtime_truth_mutation_allowed"] is False
    assert report["automatic_update_allowed"] is False
    assert len(report["discovery_sha256"]) == 64


def test_s42r14_include_adapter_mounts_routes_without_patch(tmp_path: Path):
    module = importlib.import_module("claire.api.operator_router_include_adapter")
    make_payload(tmp_path)

    app = FastAPI()
    returned = module.include_operator_router_non_invasive(app, root=tmp_path)

    assert returned is app
    paths = {route.path for route in app.routes}
    assert "/operator/payload" in paths
    assert "/operator/alerts" in paths

    client = TestClient(app)
    response = client.get("/operator/payload")
    assert response.status_code == 200
    body = response.json()
    assert body["available"] is True
    assert body["runtime_truth_mutation_allowed"] is False
    assert body["automatic_update_allowed"] is False


def test_s42r15_include_adapter_is_idempotent(tmp_path: Path):
    module = importlib.import_module("claire.api.operator_router_include_adapter")
    app = FastAPI()

    module.include_operator_router_non_invasive(app, root=tmp_path)
    module.include_operator_router_non_invasive(app, root=tmp_path)

    paths = [route.path for route in app.routes if route.path == "/operator/payload"]
    assert len(paths) == 1


def test_s42r16_to_r20_manifest_and_verification(tmp_path: Path):
    module = importlib.import_module("claire.api.operator_router_include_adapter")
    discovery = module.discover_app_factory()
    manifest = module.build_router_include_adapter_manifest(discovery)
    verification = module.verify_router_include_adapter(discovery, manifest)

    assert manifest["app_py_patch_required"] is False
    assert manifest["include_strategy"] == "external_include_router_call"
    assert manifest["runtime_truth_mutation_allowed"] is False
    assert verification["verification_ok"] is True
    assert verification["failures"] == []

    result = module.write_router_include_adapter_artifacts(tmp_path / "out")
    assert set(result) == {"discovery", "manifest", "verification"}
    for value in result.values():
        assert Path(value).exists()
