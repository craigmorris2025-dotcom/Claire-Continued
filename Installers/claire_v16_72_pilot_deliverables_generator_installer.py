from pathlib import Path

ROOT = Path.cwd()

def write(path, content):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print(f"Wrote {path}")

write("src/claire/pilot/pilot_deliverables_generator.py", r"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from claire.pilot.pilot_offer_definition import build_pilot_offer_definition


PILOT_DELIVERABLES_PATH = Path("data/pilot/pilot_deliverables_package.json")


def build_pilot_deliverables_package(domain: str = "enterprise AI strategy") -> Dict[str, Any]:
    offer = build_pilot_offer_definition()

    package = {
        "version": "16.72",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "ready",
        "domain": domain,
        "offer": offer,
        "deliverables": {
            "opportunity_thesis_report": {
                "purpose": "Summarize weak signals, opportunity thesis, implications, and confidence.",
                "sections": ["domain context", "weak signals", "thesis", "evidence", "confidence", "risks"],
            },
            "evidence_binder": {
                "purpose": "Collect replayable evidence records and proof artifacts.",
                "sections": ["record summary", "source lineage", "operator review", "benchmark replay"],
            },
            "source_lineage_report": {
                "purpose": "Show source status, approval state, rights status, and quarantine decisions.",
                "sections": ["allowed sources", "pending sources", "quarantined sources", "review gaps"],
            },
            "portfolio_recommendation": {
                "purpose": "Translate thesis into portfolio, productization, or strategic action.",
                "sections": ["recommendation", "rationale", "risk", "timing", "watchlist"],
            },
            "acquirer_partner_map": {
                "purpose": "Identify likely strategic buyers, partners, or integration paths.",
                "sections": ["buyer categories", "fit rationale", "integration map", "open diligence questions"],
            },
            "go_no_go_memo": {
                "purpose": "Provide a concise pilot decision memo.",
                "sections": ["decision", "supporting evidence", "missing evidence", "falsification triggers"],
            },
        },
    }

    PILOT_DELIVERABLES_PATH.parent.mkdir(parents=True, exist_ok=True)
    PILOT_DELIVERABLES_PATH.write_text(json.dumps(package, indent=2), encoding="utf-8")
    return package
""")

print("v16.72 pilot deliverables generator installed.")
