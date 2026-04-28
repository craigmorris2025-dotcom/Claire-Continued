from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class Signals:
    raw: Dict[str, Any]
    engineered: Dict[str, Any]
