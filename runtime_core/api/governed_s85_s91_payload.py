from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Mapping

from runtime_core.api.governed_demo_run import build_demo_readiness_proof

def build_s85_s91_payload(evidence_basket: Mapping[str, Any] | None = None, extraction: Mapping[str, Any] | None = None, *, store_path: Path | None = None, export_dir: Path | None = None) -> Dict[str, Any]:
    evidence_basket = evidence_basket or {
        "basket_id": "demo_basket_s85_s91",
        "trust_score": 0.72,
        "evidence_items": [
            {"evidence_id": "ev_demo_001", "title": "Governed market signal", "url": "https://example.invalid/governed-signal", "trust_score": 0.72}
        ],
    }
    extraction = extraction or {
        "extraction_id": "extract_demo_s85_s91",
        "signals": [
            {"label": "market structure signal", "type": "portfolio", "confidence": 0.8},
            {"label": "emerging design implication", "type": "design", "confidence": 0.62},
        ],
        "entities": [{"name": "Example Sector", "type": "market"}],
    }
    proof = build_demo_readiness_proof(evidence_basket, extraction, store_path=store_path, export_dir=export_dir)
    return {
        "version": "v19.89.8-S85-S91",
        "vertical_slice": "governed_web_evidence_to_reviewed_export",
        "status": proof["status"],
        "locked_path": [
            "real_governed_web_intake",
            "quarantined_evidence",
            "extraction",
            "useful_output",
            "review",
            "export",
            "end_to_end_demo",
        ],
        "proof": proof,
    }
