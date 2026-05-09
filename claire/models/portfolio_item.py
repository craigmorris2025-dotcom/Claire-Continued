from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any
from uuid import UUID

@dataclass
class PortfolioItem:
    id: UUID
    breakthrough_id: UUID
    pco_id: UUID
    title: str
    abstract: str
    created_at: datetime
    technical: Dict[str, Any]
    market: Dict[str, Any]
    strategic: Dict[str, Any]
    risk: Dict[str, float]
    status: str
