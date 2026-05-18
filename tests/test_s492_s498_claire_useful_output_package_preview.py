from __future__ import annotations

import importlib
from pathlib import Path


def test_s492_s493_package_schema_and_types_are_ready():
    module = importlib.import_module("claire.api.claire_useful_output_package_preview_s492_s498")

    schema = module.build_s492_output_package_schema()
    types = module.build_s493_package_type_contracts()

    assert "package_id" in schema["package_fields"]
    assert "review_status" in schema["package_fields"]
    assert "market_brief" in types["package_types"]
    assert "engineering_feasibility_preview" in types["package_types"]
    assert "governed_update_preview" in types["package_types"]

    for payload in [schema, types]:
        for flag in module.BLOCKED_AUTHORITY:
            assert payload[flag] is False


def test_useful_output_preview_builds_market_engineering_update_and_breakthrough_packages():
    module = importlib.import_module("claire.api.claire_useful_output_package_preview_s492_s498")

    market = module.build_useful_output_package_preview(
        "Can Claire build a market trend brief with portfolio implications?",
        preferred_package_type="market_brief",
        preferred_domain="market",
    )
    assert market["package_type"] == "market_brief"
    assert "portfolio_implication" in market["sections"]

    engineering = module.build_useful_output_package_preview(
        "Can Claire build an engineering feasibility preview for this system architecture?",
        preferred_package_type="engineering_feasibility_preview",
        preferred_domain="engineering",
    )
    assert engineering["package_type"] == "engineering_feasibility_preview"
    assert "buildability_read" in engineering["sections"]

    update = module.build_useful_output_package_preview(
        "Can Claire evaluate an online update package with rollback validation and approval?",
        preferred_package_type="governed_update_preview",
    )
    assert update["package_type"] == "governed_update_preview"
    assert update["export_manifest"]["export_ready"] is False
    assert "rollback_plan" in update["sections"]

    breakthrough = module.build_useful_output_package_preview(
        "Can Claire create a breakthrough candidate preview from this non-obvious market gap?",
        preferred_package_type="breakthrough_candidate_preview",
    )
    assert breakthrough["package_type"] == "breakthrough_candidate_preview"
    assert "route_candidate" in breakthrough

    for preview in [market, engineering, update, breakthrough]:
        assert preview["governance"]["review_only"] is True
        assert preview["governance"]["execution_allowed"] is False
        for flag in module.BLOCKED_AUTHORITY:
            assert preview[flag] is False


def test_s494_builder_and_s495_review_gate_contracts():
    module = importlib.import_module("claire.api.claire_useful_output_package_preview_s492_s498")

    builder = module.build_s494_preview_builder_contract()
    assert builder["sample_preview"]["section_count"] >= 1
    assert builder["sample_preview"]["review_status"] in {
        "review_ready",
        "operator_review_required",
        "needs_more_evidence",
        "insufficient_for_preview",
    }

    gate = module.build_s495_review_gate_contract()
    assert "operator_review_required" in gate["review_statuses"]
    assert "No preview can execute runtime actions." in gate["review_rules"]


def test_s496_export_manifest_is_stub_only_no_export_performed():
    module = importlib.import_module("claire.api.claire_useful_output_package_preview_s492_s498")

    manifest = module.build_export_manifest_stub("market_brief")
    assert manifest["export_ready"] is False
    assert manifest["export_performed"] is False
    assert manifest["requires_operator_review"] is True

    contract = module.build_s496_export_manifest_contract()
    assert contract["manifests"]["market_brief"]["export_ready"] is False
    assert contract["package_export_performed"] is False


def test_s497_assets_exist_and_preserve_authority_flags():
    root = Path.cwd()
    js = root / "frontend/cockpit/shell/assets/claire_useful_output_package_preview.js"
    css = root / "frontend/cockpit/shell/assets/claire_useful_output_package_preview.css"

    assert js.exists()
    assert css.exists()

    text = js.read_text(encoding="utf-8")
    assert "ClaireUsefulOutputPackagePreviewVersion" in text
    assert "runtimeTruthMutationAllowed: false" in text
    assert "automaticUpdatesEnabled: false" in text
    assert "packageExecutionEnabled: false" in text
    assert "packageExportPerformed: false" in text


def test_s498_stop_gate_allows_forward_motion(tmp_path):
    module = importlib.import_module("claire.api.claire_useful_output_package_preview_s492_s498")

    gate = module.build_s498_stop_gate(report_dir=tmp_path, project_root=Path.cwd())
    assert gate["ok"] is True
    assert gate["ready"] is True
    assert gate["forward_motion_allowed"] is True
    assert gate["checks"]["update_preview_blocks_export"] is True
    assert gate["checks"]["all_previews_review_only"] is True
    assert (tmp_path / "s498_claire_useful_output_package_preview_stop_gate.json").exists()


def test_s492_s498_rollup_ready():
    module = importlib.import_module("claire.api.claire_useful_output_package_preview_s492_s498")

    rollup = module.build_claire_useful_output_package_preview_s492_s498(project_root=Path.cwd())
    assert rollup["ready"] is True
    assert rollup["contracts"]["s492"]["ready"] is True
    assert rollup["stop_gate"]["forward_motion_allowed"] is True
    assert rollup["runtime_truth_mutation_allowed"] is False
    assert rollup["automatic_updates_enabled"] is False
    assert rollup["package_export_performed"] is False
