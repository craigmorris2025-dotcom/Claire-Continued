from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from .models import InternetEvidenceLink, utc_now


class InternetEvidenceContinuityStore:
    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path("data") / "internet_runtime_integration"
        self.links_dir = self.root / "evidence_links"
        self.index_path = self.root / "internet_evidence_index.json"
        self.links_dir.mkdir(parents=True, exist_ok=True)

    def link_evidence(self, run_id: str, query: str, evidence: Dict[str, Any], lifecycle_stage: str = "research") -> InternetEvidenceLink:
        link = InternetEvidenceLink(
            evidence_id=str(evidence.get("evidence_id")),
            run_id=run_id,
            query=query,
            source_url=str(evidence.get("source_url", "")),
            source_domain=str(evidence.get("source_domain", "")),
            confidence=float(evidence.get("confidence", 0.0)),
            source_reliability=float(evidence.get("source_reliability", 0.0)),
            lifecycle_stage=lifecycle_stage,
        )
        self.save_link(link)
        return link

    def save_link(self, link: InternetEvidenceLink) -> Path:
        path = self.links_dir / f"{link.run_id}_{link.evidence_id}.json"
        path.write_text(json.dumps(link.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
        self._update_index(link)
        return path

    def _update_index(self, link: InternetEvidenceLink) -> None:
        index = self.load_index()
        index.setdefault("runs", {})
        bucket = index["runs"].setdefault(link.run_id, {"evidence_ids": [], "queries": []})
        if link.evidence_id not in bucket["evidence_ids"]:
            bucket["evidence_ids"].append(link.evidence_id)
        if link.query not in bucket["queries"]:
            bucket["queries"].append(link.query)
        index["updated_at"] = utc_now()
        self.index_path.write_text(json.dumps(index, indent=2, sort_keys=True), encoding="utf-8")

    def load_index(self) -> Dict[str, Any]:
        if not self.index_path.exists():
            return {"created_at": utc_now(), "runs": {}}
        return json.loads(self.index_path.read_text(encoding="utf-8"))

    def links_for_run(self, run_id: str) -> List[Dict[str, Any]]:
        links: List[Dict[str, Any]] = []
        for path in sorted(self.links_dir.glob(f"{run_id}_*.json")):
            try:
                links.append(json.loads(path.read_text(encoding="utf-8")))
            except Exception:
                continue
        return links
