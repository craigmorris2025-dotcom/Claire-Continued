from pathlib import Path

ROOT = Path.cwd()

def write(path, content):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print(f"Wrote {path}")

write("src/claire/buyer/buyer_readiness_checklist.py", r"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


BUYER_READINESS_PATH = Path("data/buyer/buyer_readiness_checklist.json")

CHECKS = {
    "demo": [
        "one launcher",
        "one dashboard",
        "three demo scenarios",
        "guided demo flow",
        "operator-readable README",
    ],
    "proof": [
        "benchmark replay records",
        "operator review records",
        "outcome labels",
        "false-positive examples",
        "source lineage records",
        "evidence binder",
    ],
    "governance": [
        "source allowlist",
        "quarantine layer",
        "audit logs",
        "runtime command contracts",
        "rollback awareness",
    ],
    "technical": [
        "pytest proof",
        "dependency snapshot",
        "runtime manifest",
        "health checks",
        "no duplicate launch paths",
    ],
    "buyer_materials": [
        "category thesis",
        "architecture memo",
        "competitive landscape memo",
        "pilot offer",
        "buyer integration map",
    ],
}


def build_buyer_readiness_checklist() -> Dict[str, Any]:
    checklist = {
        "version": "16.73",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "checklist_ready",
        "readiness_categories": CHECKS,
        "current_assessment": {
            "demo": "foundation_ready_needs_polish",
            "proof": "foundation_ready_needs_real_records",
            "governance": "strong_foundation",
            "technical": "needs_full_project_wide_validation",
            "buyer_materials": "now_being_generated",
        },
        "decision_rule": (
            "Claire should not be described as acquisition-ready until demo, proof, "
            "governance, technical, and buyer materials all have external-review quality artifacts."
        ),
    }

    BUYER_READINESS_PATH.parent.mkdir(parents=True, exist_ok=True)
    BUYER_READINESS_PATH.write_text(json.dumps(checklist, indent=2), encoding="utf-8")
    return checklist
""")

print("v16.73 buyer readiness checklist installed.")
