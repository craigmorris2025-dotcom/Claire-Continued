from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from .config import InternetActivationConfig
from .models import EvidenceRecord, ResearchRun, utc_now


class InternetResearchStore:
    def __init__(self, config: InternetActivationConfig) -> None:
        self.config=config; self.root=config.resolved_data_dir()
        self.evidence_dir=self.root/"evidence"; self.runs_dir=self.root/"runs"; self.audit_dir=self.root/"audit"; self.cache_dir=self.root/"cache"
        for p in [self.evidence_dir,self.runs_dir,self.audit_dir,self.cache_dir]: p.mkdir(parents=True, exist_ok=True)
    def save_evidence(self, record: EvidenceRecord) -> Path:
        path=self.evidence_dir/f"{record.evidence_id}.json"; path.write_text(json.dumps(record.to_dict(), indent=2, sort_keys=True), encoding="utf-8"); return path
    def save_run(self, run: ResearchRun, output: Dict[str, Any]) -> Path:
        path=self.runs_dir/f"{run.run_id}.json"; path.write_text(json.dumps(output, indent=2, sort_keys=True), encoding="utf-8"); return path
    def audit(self, event_type: str, payload: Dict[str, Any]) -> Path:
        safe="".join(ch if ch.isalnum() or ch in "_-" else "_" for ch in event_type)
        path=self.audit_dir/f"{utc_now().replace(':','').replace('.','_')}_{safe}.json"
        path.write_text(json.dumps({"event_type":event_type,"created_at":utc_now(),"payload":payload}, indent=2, sort_keys=True), encoding="utf-8"); return path
    def get_evidence(self, evidence_id: str) -> Dict[str, Any] | None:
        path=self.evidence_dir/f"{evidence_id}.json"
        return None if not path.exists() else json.loads(path.read_text(encoding="utf-8"))
    def list_evidence(self, limit: int = 50) -> List[Dict[str, Any]]:
        out=[]
        for path in sorted(self.evidence_dir.glob("*.json"), key=lambda p:p.stat().st_mtime, reverse=True)[:limit]:
            try: out.append(json.loads(path.read_text(encoding="utf-8")))
            except Exception: pass
        return out
