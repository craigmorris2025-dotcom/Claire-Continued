from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Dict

class EvidenceTemplateBuilder:
    def build_template(self, evidence_type: str) -> Dict[str, Any]:
        return {
            "record_type": "evidence_template",
            "evidence_type": evidence_type,
            "required_fields": ["id", "source", "summary", "lineage", "review_status"],
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
        }
