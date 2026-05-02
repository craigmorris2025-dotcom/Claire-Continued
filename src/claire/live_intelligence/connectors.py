"""Starter source-specific connectors for Claire live intelligence."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from claire.live_intelligence.entity_registry import SourceEntityRegistry


class BaseConnector:
    connector_id = "base_connector"
    source_family = "base"
    source_type = "public_metadata"
    signal_terms: List[str] = []

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        self.registry = SourceEntityRegistry(project_root)

    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        entities = self.registry.entities(
            market_universe=payload.get("market_universe", "sp500_public"),
            industry_domain=payload.get("industry_domain", ""),
            limit=int(payload.get("entity_limit", 4) or 4),
        )
        outputs = [self._entity_output(entity, payload) for entity in entities]
        return {
            "status": "success",
            "connector": self.connector_id,
            "source_family": self.source_family,
            "source_type": self.source_type,
            "record_count": len(outputs),
            "records": outputs,
            "safe_metadata_only": True,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    def _entity_output(self, entity: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
        title = f"{entity.get('name')} {self.source_family.replace('_', ' ')} signal"
        snippet = self._snippet(entity, payload)
        return {
            "record_id": f"{self.connector_id}_{entity.get('entity_id')}",
            "entity_id": entity.get("entity_id"),
            "entity_name": entity.get("name"),
            "ticker": entity.get("ticker"),
            "market_universe": entity.get("market_universe"),
            "industry_domain": entity.get("industry_domain"),
            "source_family": self.source_family,
            "source_type": self.source_type,
            "source_url": self._source_url(entity),
            "title": title,
            "snippet": snippet,
            "terms": self.signal_terms,
            "status": "metadata_only",
            "metadata": {
                "connector": self.connector_id,
                "sector": entity.get("sector"),
                "tags": entity.get("tags", []),
                "objective": payload.get("objective", "discover_market_gaps"),
            },
        }

    def _source_url(self, entity: Dict[str, Any]) -> str:
        urls = entity.get("source_urls") or []
        return urls[0] if urls else ""

    def _snippet(self, entity: Dict[str, Any], payload: Dict[str, Any]) -> str:
        tags = ", ".join(entity.get("tags", []))
        return f"Public metadata context for {entity.get('name')} covering {tags}."


class SecPublicFilingConnector(BaseConnector):
    connector_id = "sec_public_filing_connector_v1"
    source_family = "sec_public_filings"
    source_type = "public_regulatory"
    signal_terms = ["filing", "risk", "regulation", "compliance", "market pressure"]

    def _source_url(self, entity: Dict[str, Any]) -> str:
        return "https://www.sec.gov/edgar/search/"

    def _snippet(self, entity: Dict[str, Any], payload: Dict[str, Any]) -> str:
        return f"Public filing lens for {entity.get('name')}: risk, compliance, segment pressure, AI governance, and operating disclosures."


class InvestorRelationsConnector(BaseConnector):
    connector_id = "investor_relations_connector_v1"
    source_family = "investor_relations"
    source_type = "public_web"
    signal_terms = ["strategy", "earnings", "investor", "growth", "infrastructure"]


class PublicNewsMetadataConnector(BaseConnector):
    connector_id = "public_news_metadata_connector_v1"
    source_family = "public_news_metadata"
    source_type = "public_news"
    signal_terms = ["market", "pressure", "launch", "demand", "competition"]

    def _source_url(self, entity: Dict[str, Any]) -> str:
        return "https://www.reuters.com/markets/"

    def _snippet(self, entity: Dict[str, Any], payload: Dict[str, Any]) -> str:
        return f"Public news metadata lens for {entity.get('name')}: market movement, product shifts, demand pressure, and competitive activity."


class UsptoPatentMetadataConnector(BaseConnector):
    connector_id = "uspto_patent_metadata_connector_v1"
    source_family = "public_patent_metadata"
    source_type = "public_patent"
    signal_terms = ["patent", "innovation", "technical feasibility", "defensibility", "moat"]

    def _source_url(self, entity: Dict[str, Any]) -> str:
        return "https://ppubs.uspto.gov/pubwebapp/"

    def _snippet(self, entity: Dict[str, Any], payload: Dict[str, Any]) -> str:
        return f"Public patent metadata lens for {entity.get('name')}: innovation direction, technical feasibility, defensibility, and whitespace."


class ConnectorRunner:
    """Run installed source connectors as a governed starter connector set."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        self.connectors = [
            SecPublicFilingConnector(project_root),
            InvestorRelationsConnector(project_root),
            PublicNewsMetadataConnector(project_root),
            UsptoPatentMetadataConnector(project_root),
        ]

    def status(self) -> Dict[str, Any]:
        return {
            "status": "success",
            "connector_count": len(self.connectors),
            "connectors": [
                {
                    "connector": connector.connector_id,
                    "source_family": connector.source_family,
                    "source_type": connector.source_type,
                    "safe_metadata_only": True,
                }
                for connector in self.connectors
            ],
        }

    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        requested = set(payload.get("connectors") or [])
        selected = [
            connector for connector in self.connectors
            if not requested or connector.connector_id in requested or connector.source_family in requested
        ]
        results = [connector.run(payload) for connector in selected]
        records: List[Dict[str, Any]] = []
        for result in results:
            records.extend(result.get("records", []))
        return {
            "status": "success",
            "connector_count": len(selected),
            "record_count": len(records),
            "results": results,
            "records": records,
            "safe_metadata_only": True,
        }
