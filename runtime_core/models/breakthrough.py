from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any
from uuid import UUID

@dataclass
class Breakthrough:
    id: UUID
    title: str
    description: str
    domain: str
    created_at: datetime
    signals: Dict[str, Any]
    scores: Dict[str, float]
    safety: Dict[str, Any]
    status: str
