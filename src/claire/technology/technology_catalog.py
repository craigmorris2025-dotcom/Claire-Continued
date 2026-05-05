"""Minimum viable Claire-native technology catalog."""

from __future__ import annotations

from typing import Any, Dict, List


class TechnologyCatalog:
    """Small in-process technology catalog for design-route recommendations."""

    def __init__(self) -> None:
        self._items = self._seed_items()

    def all(self) -> List[Dict[str, Any]]:
        return [dict(item) for item in self._items]

    def by_id(self, technology_id: str) -> Dict[str, Any]:
        for item in self._items:
            if item["id"] == technology_id:
                return dict(item)
        return {}

    def categories(self) -> List[str]:
        return sorted({item["category"] for item in self._items})

    def _seed_items(self) -> List[Dict[str, Any]]:
        return [
            self._item(
                "react",
                "React",
                "frontend",
                "Component UI framework for interactive web workspaces.",
                tags=["frontend", "dashboard", "workspace", "portal"],
                languages=["javascript", "typescript"],
                platforms=["web", "desktop_shell"],
                use_cases=["dashboard", "command_center", "design_portal"],
                compatible=["fastapi", "postgresql", "prometheus"],
            ),
            self._item(
                "fastapi",
                "FastAPI",
                "backend",
                "Python API framework for typed local service routes.",
                tags=["api", "backend", "local_service", "contracts"],
                languages=["python"],
                platforms=["local", "cloud", "desktop_shell"],
                use_cases=["pipeline_api", "export_api", "lifecycle_service"],
                compatible=["react", "postgresql", "redis", "prometheus"],
            ),
            self._item(
                "postgresql",
                "PostgreSQL",
                "database",
                "Relational database for structured run, artifact, and catalog records.",
                tags=["database", "structured", "audit", "portfolio"],
                languages=["sql"],
                platforms=["local", "cloud"],
                use_cases=["run_history", "portfolio_records", "technology_catalog"],
                compatible=["fastapi", "redis"],
                integration_complexity="medium",
            ),
            self._item(
                "sqlite",
                "SQLite",
                "database",
                "Embedded database for portable desktop and local-first state.",
                tags=["database", "local_first", "portable", "desktop"],
                languages=["sql"],
                platforms=["local", "desktop_shell"],
                use_cases=["portable_state", "run_history", "catalog_cache"],
                compatible=["fastapi"],
                integration_complexity="low",
            ),
            self._item(
                "redis",
                "Redis",
                "backend",
                "In-memory queue/cache for scan jobs and execution state.",
                tags=["queue", "cache", "jobs", "monitoring"],
                languages=["python", "javascript"],
                platforms=["local", "cloud"],
                use_cases=["scan_queue", "job_state", "live_monitor"],
                compatible=["fastapi", "postgresql"],
                integration_complexity="medium",
            ),
            self._item(
                "docker",
                "Docker",
                "devops",
                "Container runtime for repeatable deployment and packaging.",
                tags=["devops", "deployment", "packaging"],
                languages=[],
                platforms=["local", "cloud"],
                use_cases=["deployment", "portable_runtime", "test_environment"],
                compatible=["fastapi", "postgresql", "redis"],
            ),
            self._item(
                "prometheus",
                "Prometheus",
                "monitoring",
                "Metrics collection for runtime and pipeline observability.",
                tags=["monitoring", "metrics", "health"],
                languages=[],
                platforms=["local", "cloud"],
                use_cases=["system_health", "pipeline_metrics", "scan_monitoring"],
                compatible=["fastapi"],
                integration_complexity="medium",
            ),
            self._item(
                "openapi",
                "OpenAPI",
                "api_contract",
                "Machine-readable API contract for service and connector boundaries.",
                tags=["api", "contract", "integration", "documentation"],
                languages=["json", "yaml"],
                platforms=["web", "local", "cloud"],
                use_cases=["service_contract", "export_contract", "connector_boundary"],
                compatible=["fastapi", "react"],
            ),
            self._item(
                "vector_index",
                "Vector Index",
                "search",
                "Semantic retrieval layer for evidence, technology, and design references.",
                tags=["search", "semantic", "retrieval", "evidence"],
                languages=["python"],
                platforms=["local", "cloud"],
                use_cases=["technology_search", "evidence_retrieval", "design_reference"],
                compatible=["fastapi", "postgresql"],
                integration_complexity="medium",
            ),
        ]

    def _item(
        self,
        technology_id: str,
        name: str,
        category: str,
        description: str,
        tags: List[str],
        languages: List[str],
        platforms: List[str],
        use_cases: List[str],
        compatible: List[str],
        integration_complexity: str = "low",
    ) -> Dict[str, Any]:
        return {
            "id": technology_id,
            "name": name,
            "category": category,
            "description": description,
            "maturity_level": "established",
            "license_type": "open_source_or_standard_commercial",
            "vendor": "community_or_multiple_vendors",
            "documentation": f"Use standard {name} documentation.",
            "dependencies": [],
            "compatible_with": compatible,
            "programming_languages": languages,
            "platforms": platforms,
            "use_cases": use_cases,
            "performance_metrics": {},
            "cost_model": "low_to_moderate_operational_cost",
            "security_features": ["role_based_access_possible", "audit_integration_possible"],
            "scalability_limits": "depends_on_deployment_topology",
            "integration_complexity": integration_complexity,
            "learning_curve": "moderate" if integration_complexity == "medium" else "low",
            "tags": tags,
        }
