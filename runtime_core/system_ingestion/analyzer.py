"""
System analyzer — decompose external systems into signal components

Version: 7.0.0
Module: src.claire.system_ingestion.analyzer
Architecture: LOCKED at v5.90.2
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from runtime_core.system_ingestion.component_extractor import extract_component_graph
from runtime_core.system_ingestion.intake_graph import build_system_intake_graph

logger = logging.getLogger("claire.system_ingestion")

class Analyzer:
    """System analyzer — decompose external systems into signal components"""

    def __init__(self):
        self.logger = logging.getLogger(
            f"claire.system_ingestion.{type(self).__name__}"
        )

    def _validate_input(self, stage_input: dict):
        """Validate input matches the I/O contract."""
        required = ['stage_id', 'source_stage', 'payload', 'metadata', 'timestamp']
        missing = [f for f in required if f not in stage_input]
        if missing:
            raise ValueError(f"Input contract violation — missing fields: {missing}")

    def _build_output(self, status='completed', confidence=0.0, evidence=None, failure_reasons=None, payload=None, metadata=None) -> dict:
        """Build a contract-compliant output dict."""
        return {
            "stage_id": None,
            "status": status,
            "confidence": max(0.0, min(1.0, confidence)),
            "evidence": evidence or [],
            "failure_reasons": failure_reasons or [],
            "payload": payload or {},
            "metadata": metadata or {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def analyze(self, system_payload: dict[str, Any] | str | None) -> dict[str, Any]:
        """Decompose a supplied system description into deterministic review signals."""
        text = self._payload_text(system_payload)
        intake_graph = build_system_intake_graph(system_payload)
        component_graph = extract_component_graph(intake_graph)
        components = self._extract_terms(
            text,
            {
                "ingestion": ["ingestion", "source", "upload", "connector", "intake"],
                "processing": ["processing", "analysis", "semantic", "model", "pipeline"],
                "storage": ["storage", "database", "memory", "warehouse", "index"],
                "routing": ["routing", "orchestrator", "workflow", "stage", "queue"],
                "interface": ["dashboard", "api", "portal", "ui", "report"],
                "governance": ["governance", "approval", "audit", "policy", "validation"],
            },
        )
        gaps = self._extract_terms(
            text,
            {
                "missing_lineage": ["missing lineage", "untraced", "no trace", "unverified"],
                "manual_bottleneck": ["manual", "spreadsheet", "handoff", "copy paste"],
                "weak_validation": ["weak validation", "no validation", "untested", "unknown quality"],
                "integration_gap": ["silo", "fragmented", "disconnected", "integration gap"],
                "governance_gap": ["ungoverned", "no approval", "unsafe", "uncontrolled"],
            },
        )
        component_count = len(components)
        gap_count = len(gaps)
        confidence = min(0.95, 0.35 + component_count * 0.07 + gap_count * 0.04)
        return {
            "status": "success" if text else "insufficient_data",
            "analysis_type": "system_ingestion_decomposition",
            "components": components,
            "gaps": gaps,
            "component_count": component_count,
            "gap_count": gap_count,
            "intake_graph": intake_graph,
            "component_graph": component_graph,
            "source_type_count": intake_graph.get("source_type_count", 0),
            "source_types": intake_graph.get("source_types", []),
            "extracted_component_count": component_graph.get("component_count", 0),
            "extracted_component_types": component_graph.get("component_types", []),
            "redesign_required": gap_count > 0 or component_count >= 4,
            "confidence": round(confidence if text else 0.0, 4),
        }

    def _payload_text(self, payload: dict[str, Any] | str | None) -> str:
        if payload is None:
            return ""
        if isinstance(payload, str):
            return payload.lower()
        parts: list[str] = []
        for value in payload.values():
            if isinstance(value, (str, int, float)):
                parts.append(str(value))
            elif isinstance(value, list):
                parts.extend(str(item) for item in value)
            elif isinstance(value, dict):
                parts.extend(str(item) for item in value.values())
        return " ".join(parts).lower()

    def _extract_terms(self, text: str, taxonomy: dict[str, list[str]]) -> list[dict[str, Any]]:
        findings: list[dict[str, Any]] = []
        for key, terms in taxonomy.items():
            matched = [term for term in terms if term in text]
            if matched:
                findings.append({"id": key, "matched_terms": matched, "score": round(min(1.0, 0.4 + len(matched) * 0.15), 4)})
        return findings
