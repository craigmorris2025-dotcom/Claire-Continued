from pathlib import Path

ROOT = Path.cwd()

def write(path, content):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print(f"Wrote {path}")

write("src/claire/pilot/pilot_offer_definition.py", r"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


PILOT_OFFER_PATH = Path("data/pilot/governed_opportunity_intelligence_pilot.json")


def build_pilot_offer_definition() -> Dict[str, Any]:
    offer = {
        "version": "16.71",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "offer_name": "Governed Opportunity Intelligence Pilot",
        "positioning": (
            "Claire ingests a domain, detects weak signals, forms opportunity theses, "
            "builds evidence packets, identifies portfolio implications, and produces "
            "acquisition/productization recommendations."
        ),
        "target_buyers": [
            "strategy teams",
            "corporate development teams",
            "innovation groups",
            "R&D organizations",
            "market intelligence teams",
            "defense and critical infrastructure strategy groups",
        ],
        "pilot_scope": {
            "duration": "bounded pilot",
            "inputs": ["domain", "strategic question", "known constraints", "approved sources"],
            "outputs": [
                "opportunity thesis report",
                "evidence binder",
                "source lineage report",
                "benchmark replay summary",
                "portfolio recommendation",
                "acquirer or partner map",
                "go/no-go decision memo",
            ],
        },
        "guardrails": [
            "No unrestricted source scoring.",
            "Live evidence must pass source approval, lineage, rights, and review gates.",
            "Pilot claims must distinguish proven outputs from roadmap capabilities.",
            "Claire is positioned as governed strategic intelligence infrastructure, not AGI.",
        ],
        "status": "defined",
    }

    PILOT_OFFER_PATH.parent.mkdir(parents=True, exist_ok=True)
    PILOT_OFFER_PATH.write_text(json.dumps(offer, indent=2), encoding="utf-8")
    return offer
""")

print("v16.71 pilot offer definition installed.")
