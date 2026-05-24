"""
Claire Runtime Contract Layer
==============================
ACS2-Claire / Syntalion — v10.3.2

Canonical truth contracts between runtime output, dashboard rendering,
export packaging, proof binders, and update governance validation.

Every runtime output must pass contract validation before reaching
the UI, export system, or proof binder.
"""

from runtime_core.runtime_contracts.core_run_contract import CoreRunContract
from runtime_core.runtime_contracts.lifecycle_output_contract import LifecycleOutputContract
from runtime_core.runtime_contracts.route_contract import RouteContract
from runtime_core.runtime_contracts.dashboard_contract import DashboardContract
from runtime_core.runtime_contracts.export_contract import ExportContract
from runtime_core.runtime_contracts.proof_contract import ProofContract
from runtime_core.runtime_contracts.contract_validator import ContractValidator

__all__ = [
    "CoreRunContract",
    "LifecycleOutputContract",
    "RouteContract",
    "DashboardContract",
    "ExportContract",
    "ProofContract",
    "ContractValidator",
]

CONTRACT_VERSION = "10.3.2"
