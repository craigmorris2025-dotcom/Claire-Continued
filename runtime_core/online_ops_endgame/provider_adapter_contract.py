from __future__ import annotations
from typing import Any, Dict, List

class ProviderAdapterContract:
    def build_contract(self, provider_name: str, capabilities: List[str]) -> Dict[str, Any]:
        return {
            "record_type": "provider_adapter_contract",
            "provider_name": provider_name,
            "capabilities": capabilities,
            "required_controls": ["timeouts", "rate_limits", "source_policy", "audit_log", "quarantine"],
            "status": "contract_defined",
        }
