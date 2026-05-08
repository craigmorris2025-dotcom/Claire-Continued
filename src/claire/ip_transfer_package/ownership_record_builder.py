from __future__ import annotations
from datetime import datetime, timezone
from typing import Dict, Any

class OwnershipRecordBuilder:
    def build_record(self, owner: str = "Craig Morris", project: str = "Claire Syntalion") -> Dict[str, Any]:
        return {"record_type": "ownership_record", "owner": owner, "project": project, "created_at_utc": datetime.now(timezone.utc).isoformat(), "note": "Draft record only; not legal advice."}
