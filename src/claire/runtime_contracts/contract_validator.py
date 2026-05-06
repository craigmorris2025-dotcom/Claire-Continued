"""
Contract Validator
==================
ACS2-Claire / Syntalion — v10.3.2

Master validator that checks all runtime output against every contract
before allowing the output to reach the UI, export system, or proof binder.

This is the single gate between runtime execution and downstream consumers.
Nothing passes without contract validation.
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from claire.runtime_contracts.core_run_contract import CoreRunContract
from claire.runtime_contracts.lifecycle_output_contract import LifecycleOutputContract
from claire.runtime_contracts.route_contract import RouteContract
from claire.runtime_contracts.dashboard_contract import DashboardContract
from claire.runtime_contracts.export_contract import ExportContract
from claire.runtime_contracts.proof_contract import ProofContract


class ContractValidator:
    """
    Master contract validator for all Claire runtime output.

    Validates core run output, lifecycle stages, route selection,
    dashboard data, export packages, and proof binders.
    """

    VERSION = "10.3.2"

    def __init__(self, audit_dir: Optional[str] = None):
        self.core_contract = CoreRunContract()
        self.lifecycle_contract = LifecycleOutputContract()
        self.route_contract = RouteContract()
        self.dashboard_contract = DashboardContract()
        self.export_contract = ExportContract()
        self.proof_contract = ProofContract()
        self.audit_dir = Path(audit_dir) if audit_dir else None
        self.validation_history = []

    def validate_runtime_output(
        self, output: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Full validation of runtime output against all applicable contracts.

        Returns a comprehensive validation report.
        """
        report = {
            "validation_id": self._generate_id(output),
            "timestamp": datetime.utcnow().isoformat(),
            "overall_valid": True,
            "contracts_checked": [],
            "total_errors": 0,
            "total_warnings": 0,
            "details": {},
        }

        core_valid, core_errors, core_warnings = self.core_contract.validate(output)
        report["details"]["core_run"] = {
            "valid": core_valid,
            "errors": core_errors,
            "warnings": core_warnings,
        }
        report["contracts_checked"].append("core_run")
        if not core_valid:
            report["overall_valid"] = False

        stages = output.get("stages_completed", [])
        if isinstance(stages, list) and stages and isinstance(stages[0], dict):
            lc_valid, lc_errors, lc_warnings = (
                self.lifecycle_contract.validate_full_lifecycle(stages)
            )
            report["details"]["lifecycle"] = {
                "valid": lc_valid,
                "errors": lc_errors,
                "warnings": lc_warnings,
            }
            report["contracts_checked"].append("lifecycle")
            if not lc_valid:
                report["overall_valid"] = False

        route_data = {
            "route_selected": output.get("route_selected", ""),
            "confidence": output.get("confidence", 0),
            "terminal_state": output.get("terminal_state", ""),
            "skipped_stages": output.get("stages_skipped", []),
            "route_rationale": output.get("metadata", {}).get("route_rationale", ""),
            "alternative_routes": output.get("metadata", {}).get("alternative_routes", []),
            "selection_timestamp": output.get("timestamp", ""),
        }
        rt_valid, rt_errors, rt_warnings = self.route_contract.validate(route_data)
        report["details"]["route"] = {
            "valid": rt_valid,
            "errors": rt_errors,
            "warnings": rt_warnings,
        }
        report["contracts_checked"].append("route")
        if not rt_valid:
            report["overall_valid"] = False

        for section_name, section_data in report["details"].items():
            report["total_errors"] += len(section_data.get("errors", []))
            report["total_warnings"] += len(section_data.get("warnings", []))

        self.validation_history.append(report)

        if self.audit_dir:
            self._write_audit(report)

        return report

    def validate_export_package(
        self, package: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate an export package against the export contract."""
        valid, errors, warnings = self.export_contract.validate(package)
        report = {
            "validation_id": self._generate_id(package),
            "timestamp": datetime.utcnow().isoformat(),
            "contract": "export_package",
            "valid": valid,
            "errors": errors,
            "warnings": warnings,
        }
        self.validation_history.append(report)
        if self.audit_dir:
            self._write_audit(report)
        return report

    def validate_proof_binder(
        self, binder: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate a proof binder against the proof contract."""
        valid, errors, warnings = self.proof_contract.validate(binder)
        report = {
            "validation_id": self._generate_id(binder),
            "timestamp": datetime.utcnow().isoformat(),
            "contract": "proof_binder",
            "valid": valid,
            "errors": errors,
            "warnings": warnings,
        }
        self.validation_history.append(report)
        if self.audit_dir:
            self._write_audit(report)
        return report

    def get_dashboard_data(
        self, runtime_output: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Transform validated runtime output into dashboard-ready data."""
        validation = self.validate_runtime_output(runtime_output)
        if not validation["overall_valid"]:
            return {
                "valid": False,
                "validation_errors": validation["total_errors"],
                "panels": {},
            }
        return {
            "valid": True,
            "panels": self.dashboard_contract.transform_all_panels(runtime_output),
        }

    def get_contract_summary(self) -> Dict[str, Any]:
        """Return a summary of all contracts and their definitions."""
        return {
            "validator_version": self.VERSION,
            "contracts": {
                "core_run": self.core_contract.to_dict(),
                "lifecycle": self.lifecycle_contract.to_dict(),
                "route": self.route_contract.to_dict(),
                "dashboard": self.dashboard_contract.to_dict(),
                "export": self.export_contract.to_dict(),
                "proof": self.proof_contract.to_dict(),
            },
            "total_validations": len(self.validation_history),
        }

    def _generate_id(self, data: Dict) -> str:
        raw = json.dumps(data, sort_keys=True, default=str)[:500]
        return f"val_{hashlib.md5(raw.encode()).hexdigest()[:10]}"

    def _write_audit(self, report: Dict[str, Any]):
        """Write validation report to audit directory."""
        if not self.audit_dir:
            return
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        vid = report.get("validation_id", "unknown")
        path = self.audit_dir / f"validation_{ts}_{vid}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, default=str)
