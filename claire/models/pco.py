from dataclasses import dataclass
from datetime import datetime
from typing import Dict
from uuid import UUID

@dataclass
class PortfolioCandidateObject:
    id: UUID
    breakthrough_id: UUID
    promoted_at: datetime
    rationale: Dict[str, str]
    scores: Dict[str, float]
    safety: Dict[str, float]
    status: str
