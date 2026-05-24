from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class SafetyProfile:
    redlines: Dict[str, Any]
    compliance: Dict[str, Any]
    audit_trail: Dict[str, Any]
