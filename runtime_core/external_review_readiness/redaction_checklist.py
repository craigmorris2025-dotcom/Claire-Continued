from __future__ import annotations
from typing import Dict, Any

class RedactionChecklist:
    REQUIRED = ["secrets_removed", "private_keys_removed", "personal_files_removed", "license_notes_present"]
    def evaluate(self, checks: Dict[str, bool]) -> Dict[str, Any]:
        missing = [x for x in self.REQUIRED if not checks.get(x, False)]
        return {"status": "clear" if not missing else "blocked", "missing": missing}
