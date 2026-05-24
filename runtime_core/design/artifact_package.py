from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "claire_design_artifact_package_v1"
INDEX_PATH = Path("data/design_portal/design_artifact_index.json")
PACKAGE_ROOT = Path("data/design_portal/packages")
ACTION_LOG_PATH = Path("data/design_portal/action_log.json")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _slug(value: Any, fallback: str = "design-candidate") -> str:
    text = str(value or fallback).strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text[:80] or fallback


def _write_json(path: Path, payload: Any) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, indent=2, sort_keys=True, default=str)
    path.write_text(text, encoding="utf-8")
    return _file_record(path, "json")


def _read_json(path: Path, fallback: Any) -> Any:
    if not path.exists():
        return fallback
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback


def _promoted_live_evidence_summary(root: Path) -> dict[str, Any]:
    path = root / "data" / "internet_evidence" / "promoted_metadata_evidence_store.json"
    store = _read_json(path, {})
    items = store.get("items", []) if isinstance(store, dict) else []
    metadata_items = [
        item
        for item in items
        if isinstance(item, dict)
        and item.get("metadata_only") is True
        and item.get("body_read_performed") is False
    ]
    providers = sorted({str(item.get("provider") or "unknown") for item in metadata_items})
    return {
        "status": "promoted_live_metadata_evidence_present" if metadata_items else "missing_promoted_live_metadata_evidence",
        "evidence_store": path.as_posix(),
        "metadata_evidence_count": len(metadata_items),
        "providers": providers,
        "body_read_performed": False,
        "runtime_truth_mutation": False,
    }


def _write_text(path: Path, text: str) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return _file_record(path, "markdown" if path.suffix.lower() == ".md" else "text")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _file_record(path: Path, file_format: str) -> dict[str, Any]:
    return {
        "filename": path.name,
        "path": path.as_posix(),
        "format": file_format,
        "size_bytes": path.stat().st_size,
        "sha256": _sha256(path),
    }


def _cad_registry(workbench: dict[str, Any]) -> dict[str, Any]:
    candidate = workbench.get("candidate", {}) if isinstance(workbench, dict) else {}
    return {
        "schema_version": "claire_cad_artifact_registry_v1",
        "status": "registry_ready_no_cad_files_attached",
        "candidate_title": candidate.get("title"),
        "viewer_required": True,
        "accepted_extensions": [".step", ".stp", ".iges", ".igs", ".stl", ".obj", ".glb", ".gltf", ".dxf"],
        "artifact_states": ["missing", "imported", "generated", "needs_engineer_review", "ready_for_blueprint_package"],
        "artifacts": [],
        "viewer": {
            "status": "ready_empty",
            "viewer_type": "cad_3d_viewer",
            "primary_formats": [".glb", ".gltf", ".obj", ".stl"],
            "engineering_formats": [".step", ".stp", ".iges", ".igs", ".dxf"],
            "empty_state": "No CAD asset attached yet. Import or generate an asset after design review.",
        },
        "generation_policy": {
            "cad_generated_from_runtime": False,
            "reason": "CAD files require physical/mechanical/electrical design detail or imported engineer/operator assets.",
            "next_required_action": "attach or generate candidate-specific CAD once the design is promoted beyond blueprint draft",
        },
    }


def _video_registry(workbench: dict[str, Any]) -> dict[str, Any]:
    candidate = workbench.get("candidate", {}) if isinstance(workbench, dict) else {}
    return {
        "schema_version": "claire_video_simulation_registry_v1",
        "status": "registry_ready_no_video_files_attached",
        "candidate_title": candidate.get("title"),
        "viewer_required": True,
        "accepted_extensions": [".mp4", ".webm", ".mov", ".mkv"],
        "artifact_states": ["missing", "imported", "generated", "needs_operator_review", "ready_for_package"],
        "artifacts": [],
        "viewer": {
            "status": "ready_empty",
            "viewer_type": "video_simulation_viewer",
            "primary_formats": [".mp4", ".webm"],
            "secondary_formats": [".mov", ".mkv"],
            "empty_state": "No video or simulation asset attached yet. Generate a demo, simulation, or workflow recording after design review.",
        },
        "simulation_slots": [
            {
                "id": "function_walkthrough",
                "label": "Function walkthrough",
                "purpose": "show how the designed technology/system works",
                "status": "missing",
            },
            {
                "id": "runtime_demo",
                "label": "Runtime demo",
                "purpose": "show candidate behavior through the Claire pipeline or product workflow",
                "status": "missing",
            },
            {
                "id": "assembly_or_architecture_animation",
                "label": "Assembly or architecture animation",
                "purpose": "show construction, architecture, data flow, or mechanism sequence",
                "status": "missing",
            },
        ],
        "generation_policy": {
            "video_generated_from_runtime": False,
            "reason": "Video/simulation assets require a promoted design scenario, CAD/model asset, or UI workflow recording.",
            "next_required_action": "generate or attach simulation media after blueprint draft review",
        },
    }


def _component_map(workbench: dict[str, Any]) -> dict[str, Any]:
    components = workbench.get("required_components", []) if isinstance(workbench, dict) else []
    systems = workbench.get("required_systems", []) if isinstance(workbench, dict) else []
    return {
        "schema_version": "claire_design_component_map_v1",
        "status": "component_map_ready",
        "component_count": len(components) if isinstance(components, list) else 0,
        "system_count": len(systems) if isinstance(systems, list) else 0,
        "components": components if isinstance(components, list) else [],
        "systems": systems if isinstance(systems, list) else [],
        "mapping_notes": [
            "Every component is treated as needed-to-function until operator review removes or downgrades it.",
            "Physical/hardware candidates require CAD and engineering review before final package promotion.",
            "Software/system candidates require code/module/API mapping before final package promotion.",
        ],
    }


def _handoff(workbench: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "claire_design_downstream_handoff_v1",
        "status": "handoff_ready_for_review",
        "candidate": workbench.get("candidate", {}),
        "invention_commitment": workbench.get("invention_commitment", {}),
        "downstream_route_contract": workbench.get("downstream_route_contract", {}),
        "promotion_gates": workbench.get("promotion_gates", []),
        "portfolio_input": {
            "design_candidate": workbench.get("candidate", {}),
            "materials_manifest": "materials_manifest.json",
            "blueprint_package": "blueprint_package.json",
            "component_map": "component_map.json",
        },
        "acquirer_input": {
            "strategic_fit_basis": workbench.get("buildability", {}),
            "technical_diligence_basis": workbench.get("feasibility", {}),
            "artifact_evidence": ["blueprint_package.json", "materials_manifest.json", "cad_artifact_registry.json", "video_simulation_registry.json"],
        },
        "package_input": {
            "required_documents": [
                "blueprint_package.json",
                "materials_manifest.json",
                "component_map.json",
                "cad_artifact_registry.json",
                "video_simulation_registry.json",
                "downstream_route_handoff.json",
            ],
            "manual_review_required": True,
        },
        "validation_chain": workbench.get("validation_chain", {}),
    }


def _readme(workbench: dict[str, Any], manifest: dict[str, Any]) -> str:
    candidate = workbench.get("candidate", {})
    return "\n".join(
        [
            "# Claire Design Portal Artifact Package",
            "",
            f"Generated: {manifest.get('generated_at')}",
            f"Candidate: {candidate.get('title')}",
            f"Route: {candidate.get('route')}",
            f"Status: {manifest.get('status')}",
            "",
            "## Files",
            "",
            *[f"- `{item['filename']}` - {item['format']}" for item in manifest.get("files", [])],
            "",
            "## Review Order",
            "",
            "1. `blueprint_package.json`",
            "2. `materials_manifest.json`",
            "3. `component_map.json`",
            "4. `cad_artifact_registry.json`",
            "5. `video_simulation_registry.json`",
            "6. `downstream_route_handoff.json`",
            "",
            "CAD/video registries are first-class package slots. They may be empty until assets are generated or attached.",
        ]
    )


def build_design_artifact_package(workbench: dict[str, Any], project_root: Path | str | None = None) -> dict[str, Any]:
    root = Path(project_root or Path.cwd()).resolve()
    candidate = workbench.get("candidate", {}) if isinstance(workbench, dict) else {}
    run_id = candidate.get("source_run_id") or "latest"
    folder_name = f"{_slug(run_id, 'latest')}_{_slug(candidate.get('title'))}"
    package_dir = root / PACKAGE_ROOT / folder_name
    package_dir.mkdir(parents=True, exist_ok=True)

    files: list[dict[str, Any]] = []
    files.append(_write_json(package_dir / "blueprint_package.json", workbench.get("blueprint_package", {})))
    files.append(_write_json(package_dir / "materials_manifest.json", workbench.get("materials_manifest", {})))
    files.append(_write_json(package_dir / "component_map.json", _component_map(workbench)))
    files.append(_write_json(package_dir / "cad_artifact_registry.json", _cad_registry(workbench)))
    files.append(_write_json(package_dir / "video_simulation_registry.json", _video_registry(workbench)))
    files.append(_write_json(package_dir / "downstream_route_handoff.json", _handoff(workbench)))

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "status": "design_artifact_package_ready",
        "generated_at": _now(),
        "package_dir": package_dir.as_posix(),
        "folder_name": folder_name,
        "candidate": candidate,
        "artifact_count": len(files),
        "cad_viewer_required": True,
        "video_viewer_required": True,
        "manual_review_required": True,
        "runtime_truth_mutation": False,
        "files": files,
    }
    manifest_record = _write_json(package_dir / "manifest.json", manifest)
    manifest["files"].append(manifest_record)
    readme_record = _write_text(package_dir / "README.md", _readme(workbench, manifest))
    manifest["files"].append(readme_record)
    _write_json(package_dir / "manifest.json", manifest)

    index = {
        "schema_version": "claire_design_artifact_index_v1",
        "status": "ready",
        "latest_package_dir": package_dir.as_posix(),
        "latest_folder_name": folder_name,
        "latest_candidate": candidate,
        "latest_manifest": (package_dir / "manifest.json").as_posix(),
        "cad_viewer_required": True,
        "video_viewer_required": True,
    }
    _write_json(root / INDEX_PATH, index)

    return {
        "status": "design_artifact_package_ready",
        "schema_version": SCHEMA_VERSION,
        "package_dir": package_dir.as_posix(),
        "folder_name": folder_name,
        "manifest_path": (package_dir / "manifest.json").as_posix(),
        "index_path": (root / INDEX_PATH).as_posix(),
        "artifact_count": manifest["artifact_count"],
        "file_count": len(manifest["files"]),
        "files": manifest["files"],
        "cad_viewer_required": True,
        "video_viewer_required": True,
        "manual_review_required": True,
        "runtime_truth_mutation": False,
    }


def execute_design_portal_action(action_id: str, project_root: Path | str | None = None, operator_note: str = "") -> dict[str, Any]:
    root = Path(project_root or Path.cwd()).resolve()
    action_id = str(action_id or "").strip()
    index = _read_json(root / INDEX_PATH, {})
    package_dir = Path(index.get("latest_package_dir") or "")
    if not package_dir.is_absolute():
        package_dir = root / package_dir
    if not action_id or not package_dir.exists():
        return {
            "status": "blocked",
            "reason": "missing_action_or_design_package",
            "action_id": action_id,
            "runtime_truth_mutation": False,
        }

    allowed_actions = {
        "prepare_cad_viewer",
        "prepare_video_viewer",
        "prepare_asset_import_slots",
        "hold_design_package",
        "approve_design_package",
        "validate_design_route",
        "promote_design_package",
    }
    if action_id not in allowed_actions:
        return {"status": "blocked", "reason": "unknown_design_portal_action", "action_id": action_id, "runtime_truth_mutation": False}

    status = "recorded"
    blocked = False
    result: dict[str, Any] = {}
    if action_id == "prepare_cad_viewer":
        registry = _read_json(package_dir / "cad_artifact_registry.json", {})
        registry["status"] = "cad_viewer_ready_waiting_for_asset"
        registry["viewer"] = {**registry.get("viewer", {}), "status": "ready_waiting_for_asset"}
        _write_json(package_dir / "cad_artifact_registry.json", registry)
        result = {"viewer": registry.get("viewer", {}), "registry": (package_dir / "cad_artifact_registry.json").as_posix()}
    elif action_id == "prepare_video_viewer":
        registry = _read_json(package_dir / "video_simulation_registry.json", {})
        registry["status"] = "video_viewer_ready_waiting_for_asset"
        registry["viewer"] = {**registry.get("viewer", {}), "status": "ready_waiting_for_asset"}
        _write_json(package_dir / "video_simulation_registry.json", registry)
        result = {"viewer": registry.get("viewer", {}), "registry": (package_dir / "video_simulation_registry.json").as_posix()}
    elif action_id == "prepare_asset_import_slots":
        for filename in ("cad_artifact_registry.json", "video_simulation_registry.json"):
            registry = _read_json(package_dir / filename, {})
            registry["import_slots_ready"] = True
            registry["import_policy"] = "operator_attached_or_generated_assets_only"
            _write_json(package_dir / filename, registry)
        result = {"cad_import_slots_ready": True, "video_import_slots_ready": True}
    elif action_id == "hold_design_package":
        status = "held_for_review"
        result = {"review_state": "hold", "operator_note": operator_note}
    elif action_id == "approve_design_package":
        status = "approved_for_downstream_validation"
        result = {"review_state": "approved_for_downstream_validation", "operator_note": operator_note}
    elif action_id == "validate_design_route":
        handoff = _read_json(package_dir / "downstream_route_handoff.json", {})
        validation = handoff.get("validation_chain", {})
        status = "route_validated" if validation.get("status") == "validated" else "route_validation_partial"
        result = {"validation_chain": validation}
    elif action_id == "promote_design_package":
        evidence = _promoted_live_evidence_summary(root)
        if evidence["metadata_evidence_count"] <= 0:
            status = "blocked"
            blocked = True
            result = {
                "reason": "promotion_requires_live_evidence_and_explicit_operator_promotion_gate",
                "review_recorded": True,
                "live_evidence": evidence,
            }
        else:
            status = "promoted_for_downstream_review"
            result = {
                "review_state": "promoted_for_downstream_review",
                "operator_note": operator_note,
                "live_evidence": evidence,
                "manual_promotion_required": True,
                "body_read_performed": False,
                "runtime_truth_mutation": False,
            }

    event = {
        "action_id": action_id,
        "status": status,
        "blocked": blocked,
        "operator_note": operator_note,
        "package_dir": package_dir.as_posix(),
        "generated_at": _now(),
        "runtime_truth_mutation": False,
        "result": result,
    }
    log_path = root / ACTION_LOG_PATH
    log = _read_json(log_path, {"schema_version": "claire_design_portal_action_log_v1", "events": []})
    events = log.get("events") if isinstance(log, dict) else []
    if not isinstance(events, list):
        events = []
    events.append(event)
    log = {
        "schema_version": "claire_design_portal_action_log_v1",
        "status": "ready",
        "latest_action": event,
        "event_count": len(events),
        "events": events[-100:],
    }
    _write_json(log_path, log)
    return event
