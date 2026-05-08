from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .models import SourceTrustEvent, SourceTrustProfile
from .models import utc_now


class SourceTrustStore:
    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path("data") / "dynamic_source_trust"
        self.profile_dir = self.root / "profiles"
        self.event_dir = self.root / "events"
        self.audit_dir = self.root / "audit"
        for path in [self.profile_dir, self.event_dir, self.audit_dir]:
            path.mkdir(parents=True, exist_ok=True)

    def profile_path(self, domain: str) -> Path:
        safe = self.safe_domain(domain)
        return self.profile_dir / f"{safe}.json"

    def save_profile(self, profile: SourceTrustProfile) -> Path:
        profile.last_updated_at = utc_now()
        path = self.profile_path(profile.domain)
        path.write_text(json.dumps(profile.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
        return path

    def load_profile(self, domain: str) -> Optional[SourceTrustProfile]:
        path = self.profile_path(domain)
        if not path.exists():
            return None
        return SourceTrustProfile(**json.loads(path.read_text(encoding="utf-8")))

    def list_profiles(self) -> List[Dict[str, Any]]:
        profiles = []
        for path in sorted(self.profile_dir.glob("*.json")):
            try:
                profiles.append(json.loads(path.read_text(encoding="utf-8")))
            except Exception:
                continue
        return profiles

    def save_event(self, event: SourceTrustEvent) -> Path:
        safe_domain = self.safe_domain(event.domain)
        path = self.event_dir / f"{safe_domain}_{event.event_id}.json"
        path.write_text(json.dumps(event.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
        return path

    def list_events(self, domain: str | None = None, limit: int = 100) -> List[Dict[str, Any]]:
        pattern = "*.json" if domain is None else f"{self.safe_domain(domain)}_*.json"
        events = []
        for path in sorted(self.event_dir.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)[:limit]:
            try:
                events.append(json.loads(path.read_text(encoding="utf-8")))
            except Exception:
                continue
        return events

    def audit(self, event_type: str, payload: Dict[str, Any]) -> Path:
        safe = "".join(ch if ch.isalnum() or ch in "_-" else "_" for ch in event_type)
        path = self.audit_dir / f"{utc_now().replace(':', '').replace('.', '_')}_{safe}.json"
        path.write_text(json.dumps({
            "event_type": event_type,
            "created_at": utc_now(),
            "payload": payload,
        }, indent=2, sort_keys=True), encoding="utf-8")
        return path

    def safe_domain(self, domain: str) -> str:
        return "".join(ch if ch.isalnum() or ch in ".-" else "_" for ch in domain.lower()).strip(".")
