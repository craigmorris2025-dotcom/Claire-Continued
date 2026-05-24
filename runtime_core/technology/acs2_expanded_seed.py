from __future__ import annotations

from typing import Any


PRIMARY_DOMAINS: dict[str, list[str]] = {
    "technology": ["computing", "mobile", "wearables", "robotics", "ai_agents", "networking", "sensors_iot", "ar_vr_xr"],
    "automotive_transportation": ["cars", "evs", "autonomous_vehicles", "bicycles_ebikes", "public_transit", "drones", "logistics", "aviation"],
    "clothing_apparel": ["everyday_wear", "sportswear", "workwear", "footwear", "smart_clothing", "outdoor_gear", "luxury", "accessories"],
    "home_living": ["appliances", "smart_home", "cleaning_tools", "home_energy", "security", "home_fitness", "furniture", "kitchenware"],
    "health_wellness": ["medical_devices", "telehealth", "wearable_health", "diagnostics", "mental_health", "personal_care", "fitness", "supplements"],
    "finance_commerce": ["banking", "payments", "insurance", "investing", "fintech", "ecommerce", "subscriptions", "loyalty"],
    "entertainment_media": ["movies_tv", "streaming", "music", "gaming", "books", "social_media", "podcasts", "creator_tools"],
    "industrial_infrastructure": ["energy", "manufacturing", "construction", "agriculture", "logistics", "defense", "utilities", "materials"],
}


STAGES: list[tuple[str, int, list[str], str]] = [
    ("manual_or_analog_origin", 1600, ["manual_use", "local_context"], "manual or analog origin became specialized tool use"),
    ("mechanized_tool", 1850, ["mechanization", "repeatability"], "manual tool became mechanized or standardized"),
    ("electrified_device", 1920, ["electrification", "powered_operation"], "mechanical function became powered operation"),
    ("mass_market_product", 1950, ["manufacturing_scale", "consumer_access"], "powered device became mass-market product"),
    ("portable_variant", 1980, ["miniaturization", "portability"], "fixed product became portable or personally carried"),
    ("digital_version", 1995, ["digitization", "storage_shift"], "analog workflow became digital record or device"),
    ("networked_platform", 2005, ["network_access", "software_platform"], "digital product became connected platform"),
    ("sensorized_feedback", 2015, ["sensorization", "feedback_loop"], "connected product became measurable live system"),
    ("ai_assisted", 2022, ["ai_analysis", "prediction"], "measured system became AI-assisted decision loop"),
    ("autonomous_or_agentic", 2028, ["automation", "agentic_interface"], "AI-assisted loop trends toward autonomous or agentic operation"),
]


def generated_expanded_acs2_edges() -> list[dict[str, Any]]:
    """Generate 576+ scalable ACS2 edges from category/stage templates.

    This supplies the mass needed for graph traversal and analogy scoring while
    keeping the seed maintainable. Each edge is still explicit in the generated
    graph and can later be replaced or enriched by JSON/DB source packs.
    """

    edges: list[dict[str, Any]] = []
    for domain, subdomains in PRIMARY_DOMAINS.items():
        for subdomain in subdomains:
            previous_node = None
            previous_year = None
            previous_stage = None
            for index, (stage, year, patterns, reason) in enumerate(STAGES):
                node_id = f"{domain}_{subdomain}_{stage}"
                if previous_node is not None and previous_year is not None and previous_stage is not None:
                    edges.append(
                        {
                            "from_id": previous_node,
                            "to_id": node_id,
                            "family": f"{domain}.{subdomain}",
                            "relationship": f"{previous_stage}_became_{stage}",
                            "logic_shift": reason,
                            "approx_from_year": previous_year,
                            "approx_to_year": year,
                            "capability_delta": patterns,
                            "transformation_pattern": patterns,
                            "evidence_status": "generated_expanded_acs2_seed_requires_future_evidence_enrichment",
                        }
                    )
                previous_node = node_id
                previous_year = year
                previous_stage = stage
            edges.append(
                {
                    "from_id": f"{domain}_{subdomain}_autonomous_or_agentic",
                    "to_id": f"{domain}_{subdomain}_predictive_market_signal",
                    "family": f"{domain}.{subdomain}",
                    "relationship": "agentic_operation_became_predictive_market_signal",
                    "logic_shift": "autonomous operation produces live signals that can be compared against historical emergence patterns",
                    "approx_from_year": 2028,
                    "approx_to_year": 2032,
                    "capability_delta": ["prediction", "market_signal_generation", "recursive_learning"],
                    "transformation_pattern": ["prediction", "recursive_learning", "market_signal_generation"],
                    "evidence_status": "generated_expanded_acs2_seed_requires_future_evidence_enrichment",
                }
            )
    return edges


def generated_expanded_acs2_nodes() -> dict[str, dict[str, Any]]:
    nodes: dict[str, dict[str, Any]] = {}
    for domain, subdomains in PRIMARY_DOMAINS.items():
        for subdomain in subdomains:
            for stage, year, patterns, _reason in STAGES:
                node_id = f"{domain}_{subdomain}_{stage}"
                nodes[node_id] = {
                    "id": node_id,
                    "name": f"{subdomain.replace('_', ' ').title()} {stage.replace('_', ' ').title()}",
                    "year": year,
                    "domains": [domain, subdomain],
                    "capabilities": patterns,
                    "source": "generated_expanded_acs2_seed",
                }
            signal_id = f"{domain}_{subdomain}_predictive_market_signal"
            nodes[signal_id] = {
                "id": signal_id,
                "name": f"{subdomain.replace('_', ' ').title()} Predictive Market Signal",
                "year": 2032,
                "domains": [domain, subdomain, "prediction"],
                "capabilities": ["prediction", "market_signal_generation", "recursive_learning"],
                "source": "generated_expanded_acs2_seed",
            }
    return nodes


__all__ = ["PRIMARY_DOMAINS", "STAGES", "generated_expanded_acs2_edges", "generated_expanded_acs2_nodes"]
