from __future__ import annotations
from typing import Any, Dict, List

class ResumeDocBuilder:
    def build_resume_doc(self, version: str, next_steps: List[str]) -> Dict[str, Any]:
        return {
            "record_type": "resume_doc",
            "version": version,
            "next_steps": next_steps,
            "do_not_do": ["new architecture expansion", "ungated live activation", "runtime rewrites without tests"],
        }
