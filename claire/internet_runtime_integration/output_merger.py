from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


class CoreRunOutputInternetMerger:
    def merge_dict(self, core_output: Dict[str, Any], internet_output: Dict[str, Any]) -> Dict[str, Any]:
        merged = dict(core_output)
        internet_summary = internet_output.get("internet_summary", {})
        evidence_links = internet_output.get("evidence_links", [])
        merged["internet_research"] = {
            "status": internet_summary.get("internet_status"),
            "summary": internet_summary,
            "evidence_links": evidence_links,
            "activation_result": internet_output.get("internet_activation_result", {}),
        }
        merged.setdefault("evidence", {})
        if isinstance(merged["evidence"], dict):
            merged["evidence"].setdefault("internet", []).extend(evidence_links)
        merged.setdefault("runtime_capabilities", {})
        if isinstance(merged["runtime_capabilities"], dict):
            merged["runtime_capabilities"]["internet_research"] = True
        return merged

    def merge_file(self, core_output_path: Path, internet_output: Dict[str, Any], write_back: bool = True) -> Dict[str, Any]:
        if core_output_path.exists():
            core_output = json.loads(core_output_path.read_text(encoding="utf-8"))
        else:
            core_output = {"status": "created_by_internet_runtime_integration", "note": "core_run_output file did not exist before merge"}
        merged = self.merge_dict(core_output, internet_output)
        if write_back:
            core_output_path.parent.mkdir(parents=True, exist_ok=True)
            core_output_path.write_text(json.dumps(merged, indent=2, sort_keys=True), encoding="utf-8")
        return merged
