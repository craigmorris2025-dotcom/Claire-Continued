from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class Clusters:
    segments: Dict[str, Any]
    labels: Dict[str, str]
