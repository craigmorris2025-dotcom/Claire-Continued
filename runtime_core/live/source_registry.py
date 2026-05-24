
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from urllib.parse import urlparse


SOURCE_REGISTRY_PATH = Path("data/live/source_registry.json")

DEFAULT_ALLOWED_DOMAINS = {
    "sec.gov": {
        "rights_status": "public_government_source",
        "confidence_tier": "high",
        "use_allowed": True,
    },
    "federalreserve.gov": {
        "rights_status": "public_government_source",
        "confidence_tier": "high",
        "use_allowed": True,
    },
    "bls.gov": {
        "rights_status": "public_government_source",
        "confidence_tier": "high",
        "use_allowed": True,
    },
    "census.gov": {
        "rights_status": "public_government_source",
        "confidence_tier": "high",
        "use_allowed": True,
    },
}


def seed_source_registry() -> Dict[str, Any]:
    SOURCE_REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": "16.62",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "policy": "Only approved sources may enter high-confidence scoring.",
        "allowed_domains": DEFAULT_ALLOWED_DOMAINS,
        "blocked_domains": {},
        "pending_review_domains": {},
    }
    SOURCE_REGISTRY_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def load_source_registry() -> Dict[str, Any]:
    if not SOURCE_REGISTRY_PATH.exists():
        return seed_source_registry()
    return json.loads(SOURCE_REGISTRY_PATH.read_text(encoding="utf-8"))


def normalize_domain(url_or_domain: str) -> str:
    parsed = urlparse(url_or_domain)
    domain = parsed.netloc or parsed.path
    domain = domain.lower().strip()
    if domain.startswith("www."):
        domain = domain[4:]
    return domain


def evaluate_source(url_or_domain: str) -> Dict[str, Any]:
    registry = load_source_registry()
    domain = normalize_domain(url_or_domain)

    if domain in registry.get("blocked_domains", {}):
        return {
            "domain": domain,
            "status": "blocked",
            "may_score": False,
            "reason": "Domain is explicitly blocked.",
        }

    if domain in registry.get("allowed_domains", {}):
        meta = registry["allowed_domains"][domain]
        return {
            "domain": domain,
            "status": "allowed",
            "may_score": bool(meta.get("use_allowed")),
            "metadata": meta,
            "reason": "Domain is approved in source registry.",
        }

    return {
        "domain": domain,
        "status": "pending_review",
        "may_score": False,
        "reason": "Domain is not approved. Send to quarantine until reviewed.",
    }
