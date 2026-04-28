"""
Core — Gateway: External communication and output formatting.
Exports pipeline results to files, formats summaries, delivers to external systems.
"""
import json
import logging
import os
from datetime import datetime
from typing import Any, Dict
from backend.claire.contract import ClaireResult

logger = logging.getLogger("claire.core.gateway")


class Gateway:
    """Formats and delivers pipeline results."""

    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def format_json(self, result: ClaireResult) -> str:
        return json.dumps(result.to_dict(), indent=2, default=str)

    def format_summary(self, result: ClaireResult) -> str:
        lines = [
            "=" * 60,
            "  CLAIRE SYNTALION — Pipeline Result",
            f"  Intent: {result.intent_id}  |  Status: {result.status}",
            "=" * 60, "",
        ]
        if result.scores:
            lines.append("  Scores:")
            for name, value in sorted(result.scores.items()):
                bar = "#" * int(value * 20)
                lines.append(f"    {name:25s} {value:.4f}  [{bar}]")
        if result.acquirer_matches:
            lines.append(f"\n  Top Acquirers ({len(result.acquirer_matches)}):")
            for a in result.acquirer_matches[:5]:
                lines.append(f"    {a.get('name','?'):20s}  fit={a.get('fit',0):.2f}")
        lines.append(f"\n  Decision: {result.decision_classification}")
        lines.append(f"  Breakthrough: {result.breakthrough_classification}")
        lines.append(f"  Syntalion Ready: {result.ready_for_syntalion}")
        lines.append("=" * 60)
        return "\n".join(lines)

    def export(self, result: ClaireResult, filename: str = None) -> str:
        if not filename:
            ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"claire_{result.intent_id}_{ts}.json"
        path = os.path.join(self.output_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.format_json(result))
        logger.info(f"Exported result to {path}")
        return path

    def get_status(self) -> Dict[str, Any]:
        return {"component": "Gateway", "status": "active", "output_dir": self.output_dir}
