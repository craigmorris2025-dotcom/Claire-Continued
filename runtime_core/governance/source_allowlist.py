"""
Source Allowlist — source category control for connected/hybrid feeds.

v5.43:
- Defines allowed source categories by type.
- Does not perform ingestion.
"""

from __future__ import annotations

from typing import Any, Dict, List


class SourceAllowlist:
    """Simple allowlist for source categories used by future connectors."""

    def catalog(self) -> Dict[str, Any]:
        return {
            "status": "success",
            "allowed_categories": self.allowed_categories(),
            "review_categories": self.review_categories(),
            "blocked_categories": self.blocked_categories(),
        }

    def allowed_categories(self) -> List[Dict[str, str]]:
        return [
            {
                "id": "public_company_market_data",
                "name": "Public company market data",
                "examples": "public filings, issuer websites, public news, public market metadata",
            },
            {
                "id": "public_statistical_establishment_data",
                "name": "Public statistical establishment data",
                "examples": "public labor/economic/establishment statistics and aggregated industry data",
            },
            {
                "id": "public_government_procurement_data",
                "name": "Public government procurement data",
                "examples": "public solicitations, award notices, agency pages, public procurement metadata",
            },
            {
                "id": "public_regulatory_data",
                "name": "Public regulatory data",
                "examples": "public rulemaking, regulatory updates, compliance notices, official agency releases",
            },
            {
                "id": "user_supplied_or_custom_sources",
                "name": "User-supplied or custom sources",
                "examples": "user-provided lists, uploaded documents, curated URLs, internal customer lists",
            },
        ]

    def review_categories(self) -> List[Dict[str, str]]:
        return [
            {
                "id": "restricted_defense_technical_data",
                "name": "Restricted defense technical data",
                "reason": "May involve export-control, classified-adjacent, or restricted technical information.",
            },
            {
                "id": "non_public_company_data",
                "name": "Non-public company data",
                "reason": "May involve confidentiality, licensing, insider information, or improper access.",
            },
            {
                "id": "personal_or_sensitive_data",
                "name": "Personal or sensitive data",
                "reason": "May involve privacy, employment, health, or protected data requirements.",
            },
        ]

    def blocked_categories(self) -> List[Dict[str, str]]:
        return [
            {
                "id": "classified_data",
                "name": "Classified data",
                "reason": "Not permitted without authorized classified environment and governance.",
            },
            {
                "id": "stolen_or_unlawfully_accessed_data",
                "name": "Stolen or unlawfully accessed data",
                "reason": "Illegal or improper source category.",
            },
            {
                "id": "autonomous_weaponization_enablement",
                "name": "Autonomous weaponization enablement",
                "reason": "Hard stop category.",
            },
        ]

    def check(self, source_category: str) -> Dict[str, Any]:
        source_category = source_category or "user_supplied_or_custom_sources"
        for item in self.allowed_categories():
            if item["id"] == source_category:
                return {"status": "success", "source_category": source_category, "allowed": True, "requires_review": False, "blocked": False, "details": item}
        for item in self.review_categories():
            if item["id"] == source_category:
                return {"status": "success", "source_category": source_category, "allowed": False, "requires_review": True, "blocked": False, "details": item}
        for item in self.blocked_categories():
            if item["id"] == source_category:
                return {"status": "success", "source_category": source_category, "allowed": False, "requires_review": False, "blocked": True, "details": item}
        return {"status": "unknown", "source_category": source_category, "allowed": False, "requires_review": True, "blocked": False, "details": {"reason": "Unknown source category requires review."}}
