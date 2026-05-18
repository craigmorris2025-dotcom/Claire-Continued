from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


PUBLIC_COMPANY_SOURCES = [
    {
        "id": "sec_company_filings",
        "name": "SEC Company Filings",
        "category": "public_company",
        "status": "success",
        "governed": True,
        "live_execution": False,
    },
    {
        "id": "company_investor_relations",
        "name": "Company Investor Relations",
        "category": "public_company",
        "status": "success",
        "governed": True,
        "live_execution": False,
    },
    {
        "id": "exchange_public_company_profiles",
        "name": "Exchange Public Company Profiles",
        "category": "public_company",
        "status": "success",
        "governed": True,
        "live_execution": False,
    },
]


def resolve_public_company_sources() -> dict:
    return {
        "status": "success",
        "count": len(PUBLIC_COMPANY_SOURCES),
        "sources": PUBLIC_COMPANY_SOURCES,
        "governed": True,
        "live_execution": False,
        "truth": "catalog resolution only; does not perform uncontrolled web execution",
    }


def health_catalog_only_check() -> dict:
    return {
        "status": "success",
        "count": len(PUBLIC_COMPANY_SOURCES),
        "catalog_only": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    path = root / "data" / "runtime" / "live_source_catalog.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = resolve_public_company_sources()
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
