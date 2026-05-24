from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Dict, List

from .models import NormalizedContent, PersistentEvidenceRecord


class EvidencePersistence:
    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path("data") / "real_governed_live_connectivity" / "evidence_records"
        self.root.mkdir(parents=True, exist_ok=True)

    def create_record(self, normalized: NormalizedContent, reliability_score: float = 0.5) -> PersistentEvidenceRecord:
        claim = normalized.summary or normalized.title
        evidence_id = "persistent_evidence_" + hashlib.sha256(
            f"{normalized.source_url}|{claim}".encode("utf-8")
        ).hexdigest()[:12]
        confidence = round(max(0.0, min(1.0, reliability_score * 0.8 + 0.1)), 4)
        return PersistentEvidenceRecord(
            evidence_id=evidence_id,
            source_url=normalized.source_url,
            claim=claim,
            reliability_score=round(reliability_score, 4),
            confidence=confidence,
            lineage={
                "normalization_status": normalized.normalization_status,
                "content_type": normalized.content_type,
                "extracted_terms": normalized.extracted_terms,
            },
        )

    def save(self, record: PersistentEvidenceRecord) -> Path:
        path = self.root / f"{record.evidence_id}.json"
        path.write_text(json.dumps(record.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
        return path

    def list_records(self) -> List[Dict[str, object]]:
        records = []
        for path in sorted(self.root.glob("*.json")):
            try:
                records.append(json.loads(path.read_text(encoding="utf-8")))
            except Exception:
                continue
        return records
