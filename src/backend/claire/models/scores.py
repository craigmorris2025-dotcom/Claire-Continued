from dataclasses import dataclass
from typing import Dict

@dataclass
class Scores:
    buildability: Dict[str, float]
    demand: Dict[str, float]
    differentiation: Dict[str, float]
    composite: Dict[str, float]
