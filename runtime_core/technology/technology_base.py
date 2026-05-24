from __future__ import annotations

import json
import math
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from runtime_core.technology.acs2_expanded_seed import generated_expanded_acs2_edges, generated_expanded_acs2_nodes
from runtime_core.technology.reemergence_pattern_engine import build_reemergence_pattern_engine
from runtime_core.technology.technology_graph import graph_from_lineage


VERSION = "v19.91_generated_technology_database"


SEED_TECHNOLOGY_RECORDS: list[dict[str, Any]] = [
    {
        "id": "transformer_architecture",
        "name": "Transformer Architecture",
        "era": "AI Renaissance",
        "year": 2017,
        "maturity": "production",
        "readiness_level": 9,
        "domains": ["ai", "software", "autonomous_systems"],
        "capabilities": ["sequence modeling", "reasoning substrate", "multimodal adaptation"],
        "buildability": "high",
        "manufacturability": "software_deployable",
        "deployment": "cloud_or_local_runtime",
        "gap_fit": ["enterprise reasoning", "workflow automation", "research synthesis"],
        "acquirer_fit": ["hyperscalers", "enterprise software", "data platforms"],
        "source": "seed_technology_base",
    },
    {
        "id": "retrieval_augmented_generation",
        "name": "Retrieval-Augmented Generation",
        "era": "AI Productization",
        "year": 2020,
        "maturity": "production",
        "readiness_level": 8,
        "domains": ["ai", "knowledge", "enterprise"],
        "capabilities": ["knowledge grounding", "document intelligence", "evidence-aware answers"],
        "buildability": "high",
        "manufacturability": "software_deployable",
        "deployment": "cloud_or_local_runtime",
        "gap_fit": ["trusted search", "enterprise knowledge access", "evidence traceability"],
        "acquirer_fit": ["enterprise search", "workflow platforms", "AI infrastructure"],
        "source": "seed_technology_base",
    },
    {
        "id": "autonomous_agent_orchestration",
        "name": "Autonomous Agent Orchestration",
        "era": "Autonomous Systems",
        "year": 2025,
        "maturity": "early_production",
        "readiness_level": 7,
        "domains": ["ai", "automation", "runtime_governance"],
        "capabilities": ["task planning", "tool use", "human approval gates", "governed execution"],
        "buildability": "medium_high",
        "manufacturability": "software_deployable_with_controls",
        "deployment": "gated_runtime",
        "gap_fit": ["operator-supervised automation", "research intake", "workflow execution"],
        "acquirer_fit": ["AI platforms", "RPA platforms", "enterprise operations"],
        "source": "seed_technology_base",
    },
    {
        "id": "digital_twin_simulation",
        "name": "Digital Twin Simulation",
        "era": "Cyber-Physical Intelligence",
        "year": 2015,
        "maturity": "production",
        "readiness_level": 8,
        "domains": ["industrial", "manufacturing", "simulation"],
        "capabilities": ["system modeling", "manufacturing validation", "scenario testing"],
        "buildability": "medium_high",
        "manufacturability": "manufacturing_integrable",
        "deployment": "enterprise_or_edge",
        "gap_fit": ["factory optimization", "supply-chain resilience", "pre-build validation"],
        "acquirer_fit": ["industrial automation", "PLM platforms", "manufacturing software"],
        "source": "seed_technology_base",
    },
    {
        "id": "edge_ai_inference",
        "name": "Edge AI Inference",
        "era": "Distributed AI",
        "year": 2020,
        "maturity": "production",
        "readiness_level": 8,
        "domains": ["hardware", "ai", "iot"],
        "capabilities": ["low-latency inference", "privacy-preserving deployment", "field autonomy"],
        "buildability": "medium",
        "manufacturability": "hardware_supply_chain_dependent",
        "deployment": "edge_device_or_hybrid",
        "gap_fit": ["industrial monitoring", "robotics", "field intelligence"],
        "acquirer_fit": ["semiconductor", "robotics", "industrial IoT"],
        "source": "seed_technology_base",
    },
    {
        "id": "knowledge_graph_reasoning",
        "name": "Knowledge Graph Reasoning",
        "era": "Enterprise Intelligence",
        "year": 2018,
        "maturity": "production",
        "readiness_level": 8,
        "domains": ["knowledge", "enterprise", "reasoning"],
        "capabilities": ["relationship mapping", "entity linking", "explainable inference"],
        "buildability": "high",
        "manufacturability": "software_deployable",
        "deployment": "database_plus_api",
        "gap_fit": ["decision intelligence", "compliance mapping", "acquisition diligence"],
        "acquirer_fit": ["data platforms", "compliance platforms", "enterprise AI"],
        "source": "seed_technology_base",
    },
]


DISCOVERY_LOOP_RECORDS: list[dict[str, Any]] = [
    {
        "id": "autonomous_invention_engine_loop",
        "name": "Autonomous Invention Engine Loop",
        "era": "ACS2 Autonomous Invention",
        "year": 2025,
        "maturity": "buildable_now_with_governance",
        "readiness_level": 7,
        "domains": ["ai", "invention", "workflow", "governance"],
        "capabilities": ["discovery loop", "analysis loop", "synthesis loop", "validation loop", "feedback loop"],
        "buildability": "medium_high",
        "manufacturability": "software_deployable_with_controls",
        "deployment": "local_or_cloud_governed_runtime",
        "gap_fit": ["automated technology scanning", "patent mining", "design generation", "feasibility validation"],
        "acquirer_fit": ["AI platforms", "engineering software", "innovation management", "R&D platforms"],
        "source": "operator_technology_database",
        "evidence_basis": [
            "Discovery Loop: web search, patent mining, tech scanning, code repositories, research databases",
            "Analysis Loop: pattern recognition, trend analysis, gap analysis, competitive intelligence",
            "Synthesis Loop: design generation, component combination, app stack assembly",
            "Validation Loop: feasibility, market test, prototype, performance, safety check",
        ],
    },
    {
        "id": "governed_technology_gap_engine",
        "name": "Governed Technology Gap Engine",
        "era": "ACS2 Autonomous Invention",
        "year": 2025,
        "maturity": "buildable_now",
        "readiness_level": 8,
        "domains": ["technology_intelligence", "research", "governance"],
        "capabilities": ["local source packs", "source trust scoring", "gap detection", "breakthrough gating"],
        "buildability": "high",
        "manufacturability": "software_deployable",
        "deployment": "local_runtime_dashboard",
        "gap_fit": ["weak local search results", "evidence-backed discovery", "dashboard-to-pipeline routing"],
        "acquirer_fit": ["enterprise search", "AI governance", "R&D intelligence"],
        "source": "operator_technology_database",
    },
]


TECHNOLOGY_LINEAGE_EDGES: list[dict[str, Any]] = [
    {
        "from_id": "mechanical_calculator",
        "to_id": "programmable_computation",
        "relationship": "mechanized_arithmetic_became_programmable_logic",
        "logic_shift": "fixed calculation moved toward general symbolic procedure execution",
        "approx_from_year": 1642,
        "approx_to_year": 1936,
        "capability_delta": ["manual arithmetic", "formal computation", "programmable procedure"],
    },
    {
        "from_id": "programmable_computation",
        "to_id": "electronic_computer",
        "relationship": "abstract_programming_became_electronic_execution",
        "logic_shift": "logical procedures became machine-speed electronic operations",
        "approx_from_year": 1936,
        "approx_to_year": 1946,
        "capability_delta": ["programmable logic", "stored program execution", "machine-speed computation"],
    },
    {
        "from_id": "electronic_computer",
        "to_id": "microprocessor",
        "relationship": "room_scale_computing_became_compact_manufacturable_compute",
        "logic_shift": "computation compressed from special-purpose systems into scalable manufactured chips",
        "approx_from_year": 1946,
        "approx_to_year": 1971,
        "capability_delta": ["electronic compute", "integrated circuits", "mass manufacturable processors"],
    },
    {
        "from_id": "microprocessor",
        "to_id": "personal_computer",
        "relationship": "component_compute_became_individual_tool",
        "logic_shift": "compute shifted from institution-owned infrastructure to user-facing productivity systems",
        "approx_from_year": 1971,
        "approx_to_year": 1981,
        "capability_delta": ["local compute", "interactive software", "individual productivity"],
    },
    {
        "from_id": "personal_computer",
        "to_id": "internet_web",
        "relationship": "isolated_compute_became_networked_knowledge_access",
        "logic_shift": "local processing connected into global information exchange",
        "approx_from_year": 1981,
        "approx_to_year": 1991,
        "capability_delta": ["personal compute", "network protocols", "web-scale information retrieval"],
    },
    {
        "from_id": "internet_web",
        "to_id": "search_knowledge_graph",
        "relationship": "networked_documents_became_indexed_relationship_memory",
        "logic_shift": "pages became searchable, ranked, and entity-linked knowledge structures",
        "approx_from_year": 1991,
        "approx_to_year": 2012,
        "capability_delta": ["web documents", "search ranking", "entity relationship mapping"],
    },
    {
        "from_id": "search_knowledge_graph",
        "to_id": "transformer_architecture",
        "relationship": "indexed_knowledge_became_learned_representation",
        "logic_shift": "retrieval and language patterns became a trainable reasoning substrate",
        "approx_from_year": 2012,
        "approx_to_year": 2017,
        "capability_delta": ["entity memory", "attention mechanisms", "general sequence modeling"],
    },
    {
        "from_id": "transformer_architecture",
        "to_id": "retrieval_augmented_generation",
        "relationship": "learned_representation_became_evidence_grounded_answering",
        "logic_shift": "generative reasoning gained source grounding and external memory",
        "approx_from_year": 2017,
        "approx_to_year": 2020,
        "capability_delta": ["generation", "retrieval grounding", "evidence traceability"],
    },
    {
        "from_id": "retrieval_augmented_generation",
        "to_id": "autonomous_agent_orchestration",
        "relationship": "evidence_grounded_answering_became_tool_using_runtime",
        "logic_shift": "answers became planned actions with tools, state, and operator gates",
        "approx_from_year": 2020,
        "approx_to_year": 2025,
        "capability_delta": ["grounded answers", "tool use", "governed action loops"],
    },
    {
        "from_id": "autonomous_agent_orchestration",
        "to_id": "autonomous_invention_engine_loop",
        "relationship": "tool_using_runtime_became_recursive_invention_loop",
        "logic_shift": "task execution became discovery, synthesis, validation, and feedback over technology history",
        "approx_from_year": 2025,
        "approx_to_year": 2026,
        "capability_delta": ["agent planning", "technology scanning", "recursive invention validation"],
    },
]


DEVICE_EVOLUTION_EDGES: list[dict[str, Any]] = [
    {
        "from_id": "postal_network",
        "to_id": "optical_telegraph",
        "family": "communications_portability",
        "relationship": "physical_message_delivery_became_line_of_sight_signal_network",
        "logic_shift": "messages began moving faster than the messenger through encoded relay infrastructure",
        "approx_from_year": 1639,
        "approx_to_year": 1792,
        "capability_delta": ["addressed messages", "relay networks", "encoded long-distance signaling"],
        "transformation_pattern": ["network_access", "latency_collapse", "symbolic_encoding"],
    },
    {
        "from_id": "optical_telegraph",
        "to_id": "electric_telegraph",
        "family": "communications_portability",
        "relationship": "visual_signal_network_became_electrical_long_distance_messaging",
        "logic_shift": "line-of-sight signaling moved into electrical infrastructure that collapsed distance and weather constraints",
        "approx_from_year": 1792,
        "approx_to_year": 1844,
        "capability_delta": ["electrical signal", "coded messages", "near-real-time distance communication"],
        "transformation_pattern": ["electrification", "latency_collapse", "infrastructure_catch_up"],
    },
    {
        "from_id": "electric_telegraph",
        "to_id": "telephone",
        "family": "communications_portability",
        "relationship": "coded_electrical_messages_became_live_voice_connection",
        "logic_shift": "communication shifted from encoded text pulses to real-time human voice over networks",
        "approx_from_year": 1844,
        "approx_to_year": 1876,
        "capability_delta": ["voice transmission", "real-time conversation", "personal communication endpoint"],
        "transformation_pattern": ["interface_shift", "latency_collapse", "personalization"],
    },
    {
        "from_id": "telephone",
        "to_id": "radio_telephone",
        "family": "communications_portability",
        "relationship": "wired_voice_network_became_wireless_radio_voice",
        "logic_shift": "voice communication detached from fixed wires and began moving through radio spectrum",
        "approx_from_year": 1876,
        "approx_to_year": 1920,
        "capability_delta": ["wireless voice", "radio spectrum", "mobile communication precursor"],
        "transformation_pattern": ["wireless_shift", "infrastructure_catch_up", "network_access"],
    },
    {
        "from_id": "radio_telephone",
        "to_id": "car_phone",
        "family": "communications_portability",
        "relationship": "wireless_voice_system_became_vehicle_bound_phone",
        "logic_shift": "radio voice became packaged into a mobile but vehicle-dependent personal communication tool",
        "approx_from_year": 1920,
        "approx_to_year": 1946,
        "capability_delta": ["vehicle radio telephone", "mobile endpoint", "cellular precursor"],
        "transformation_pattern": ["mobility", "personalization", "network_access"],
    },
    {
        "from_id": "car_phone",
        "to_id": "mobile_phone",
        "family": "communications_portability",
        "relationship": "vehicle_bound_phone_became_person_carried_mobile_phone",
        "logic_shift": "communication moved from mounted vehicle infrastructure to personal portable access",
        "approx_from_year": 1946,
        "approx_to_year": 1983,
        "capability_delta": ["cellular radio", "battery portability", "personal identity endpoint"],
        "transformation_pattern": ["miniaturization", "battery_power", "personalization", "network_access"],
    },
    {
        "from_id": "mobile_phone",
        "to_id": "smartphone",
        "family": "communications_portability",
        "relationship": "voice_mobile_phone_became_networked_pocket_computer",
        "logic_shift": "portable voice communication absorbed compute, internet, camera, sensors, and app ecosystems",
        "approx_from_year": 1983,
        "approx_to_year": 2007,
        "capability_delta": ["voice", "mobile internet", "touch interface", "apps", "sensors"],
        "transformation_pattern": ["convergence", "software_platform", "touch_interface", "network_access"],
    },
    {
        "from_id": "battery_portable_tv",
        "to_id": "portable_media_player",
        "family": "portable_visual_media",
        "relationship": "battery_powered_portable_tv_became_personal_digital_media_device",
        "logic_shift": "passive portable broadcast viewing became user-selected portable digital media",
        "approx_from_year": 1982,
        "approx_to_year": 2001,
        "capability_delta": ["battery screen", "personal media library", "digital storage"],
        "transformation_pattern": ["battery_power", "miniaturization", "digital_storage", "personalization"],
    },
    {
        "from_id": "portable_media_player",
        "to_id": "tablet",
        "family": "portable_visual_media",
        "relationship": "personal_media_device_became_touch_tablet_computer",
        "logic_shift": "portable media screens absorbed touch computing, apps, internet, and productivity workflows",
        "approx_from_year": 2001,
        "approx_to_year": 2010,
        "capability_delta": ["touch display", "apps", "web access", "portable productivity"],
        "transformation_pattern": ["convergence", "touch_interface", "software_platform", "portable_compute"],
    },
    {
        "from_id": "apple_ii",
        "to_id": "portable_computer",
        "family": "personal_compute_portability",
        "relationship": "desktop_personal_computer_became_portable_computer",
        "logic_shift": "personal computing moved from fixed desktop context toward transportable individual work",
        "approx_from_year": 1977,
        "approx_to_year": 1981,
        "capability_delta": ["personal software", "local storage", "transportable hardware"],
        "transformation_pattern": ["miniaturization", "portable_compute", "personalization"],
    },
    {
        "from_id": "portable_computer",
        "to_id": "laptop",
        "family": "personal_compute_portability",
        "relationship": "transportable_computer_became_battery_laptop",
        "logic_shift": "portable compute became lap-usable, battery-powered, and mainstream work-capable",
        "approx_from_year": 1981,
        "approx_to_year": 1989,
        "capability_delta": ["clamshell form factor", "battery operation", "mobile productivity"],
        "transformation_pattern": ["battery_power", "miniaturization", "ergonomic_form_factor", "portable_compute"],
    },
    {
        "from_id": "laptop",
        "to_id": "tablet",
        "family": "personal_compute_portability",
        "relationship": "battery_laptop_partly_became_touch_tablet",
        "logic_shift": "mobile productivity split into keyboard-first laptops and touch-first tablets",
        "approx_from_year": 1989,
        "approx_to_year": 2010,
        "capability_delta": ["battery productivity", "touch interface", "instant-on mobile apps"],
        "transformation_pattern": ["interface_shift", "touch_interface", "software_platform", "portable_compute"],
    },
    {
        "from_id": "smartphone",
        "to_id": "tablet",
        "family": "mobile_touch_compute_convergence",
        "relationship": "pocket_touch_computer_scaled_into_tablet",
        "logic_shift": "phone-sized mobile OS and touch interaction scaled into larger-screen portable computing",
        "approx_from_year": 2007,
        "approx_to_year": 2010,
        "capability_delta": ["mobile OS", "touch apps", "larger portable screen", "media and productivity"],
        "transformation_pattern": ["screen_scaling", "software_platform", "touch_interface", "convergence"],
    },
    {
        "from_id": "film_camera",
        "to_id": "digital_camera",
        "family": "imaging_digitization",
        "relationship": "chemical_film_camera_became_digital_image_sensor_camera",
        "logic_shift": "image capture moved from chemical storage to reusable electronic sensors and files",
        "approx_from_year": 1888,
        "approx_to_year": 1991,
        "capability_delta": ["optical capture", "digital sensor", "instant review", "file storage"],
        "transformation_pattern": ["digitization", "sensorization", "storage_shift", "instant_feedback"],
    },
    {
        "from_id": "digital_camera",
        "to_id": "smartphone_camera",
        "family": "imaging_digitization",
        "relationship": "standalone_digital_camera_became_phone_integrated_camera",
        "logic_shift": "image capture converged into networked pocket computing and social sharing",
        "approx_from_year": 1991,
        "approx_to_year": 2007,
        "capability_delta": ["digital images", "always-carried capture", "network sharing", "computational imaging"],
        "transformation_pattern": ["convergence", "network_access", "sensorization", "software_enhancement"],
    },
    {
        "from_id": "paper_map",
        "to_id": "gps_navigation_device",
        "family": "navigation_context_awareness",
        "relationship": "static_paper_map_became_satellite_navigation_device",
        "logic_shift": "navigation moved from preprinted reference to live position-aware guidance",
        "approx_from_year": 1890,
        "approx_to_year": 1995,
        "capability_delta": ["static geography", "satellite positioning", "turn-by-turn routing"],
        "transformation_pattern": ["sensorization", "real_time_context", "automation", "portable_compute"],
    },
    {
        "from_id": "gps_navigation_device",
        "to_id": "smartphone_navigation",
        "family": "navigation_context_awareness",
        "relationship": "standalone_gps_device_became_smartphone_navigation_app",
        "logic_shift": "navigation converged into app ecosystems with live traffic, search, and user data loops",
        "approx_from_year": 1995,
        "approx_to_year": 2008,
        "capability_delta": ["GPS routing", "live traffic", "local search", "adaptive rerouting"],
        "transformation_pattern": ["convergence", "network_access", "software_platform", "feedback_loop"],
    },
    {
        "from_id": "vinyl_record",
        "to_id": "compact_disc",
        "family": "music_storage_digitization",
        "relationship": "analog_record_became_digital_disc",
        "logic_shift": "music storage moved from analog grooves to optical digital encoding",
        "approx_from_year": 1948,
        "approx_to_year": 1982,
        "capability_delta": ["analog playback", "digital audio", "durable optical media"],
        "transformation_pattern": ["digitization", "storage_shift", "quality_improvement"],
    },
    {
        "from_id": "compact_disc",
        "to_id": "mp3_player",
        "family": "music_storage_digitization",
        "relationship": "digital_disc_became_file_based_portable_music",
        "logic_shift": "albums became compressed files carried in portable solid-state devices",
        "approx_from_year": 1982,
        "approx_to_year": 1998,
        "capability_delta": ["digital tracks", "compression", "portable library"],
        "transformation_pattern": ["compression", "miniaturization", "battery_power", "personalization"],
    },
    {
        "from_id": "mp3_player",
        "to_id": "streaming_music_app",
        "family": "music_storage_digitization",
        "relationship": "owned_file_library_became_cloud_streamed_music_access",
        "logic_shift": "personal storage shifted into network catalog access and recommendation systems",
        "approx_from_year": 1998,
        "approx_to_year": 2008,
        "capability_delta": ["portable files", "cloud catalog", "recommendations", "subscription access"],
        "transformation_pattern": ["network_access", "cloud_service", "recommendation_ai", "business_model_shift"],
    },
    {
        "from_id": "cash_register",
        "to_id": "point_of_sale_terminal",
        "family": "commerce_instrumentation",
        "relationship": "mechanical_cash_register_became_electronic_point_of_sale",
        "logic_shift": "transaction recording became digital inventory, payment, and analytics infrastructure",
        "approx_from_year": 1879,
        "approx_to_year": 1973,
        "capability_delta": ["cash tally", "electronic payments", "inventory data", "transaction analytics"],
        "transformation_pattern": ["digitization", "data_capture", "network_access", "workflow_integration"],
    },
    {
        "from_id": "point_of_sale_terminal",
        "to_id": "mobile_payment_wallet",
        "family": "commerce_instrumentation",
        "relationship": "fixed_checkout_terminal_became_mobile_payment_wallet",
        "logic_shift": "payment identity moved from cards and counters into networked personal devices",
        "approx_from_year": 1973,
        "approx_to_year": 2014,
        "capability_delta": ["card acceptance", "tokenized payment", "phone authentication", "portable checkout"],
        "transformation_pattern": ["convergence", "identity_layer", "network_access", "security_tokenization"],
    },
    {
        "from_id": "paper_book",
        "to_id": "ebook_reader",
        "family": "reading_media_digitization",
        "relationship": "printed_book_became_e_ink_digital_reader",
        "logic_shift": "static printed volumes became portable digital libraries",
        "approx_from_year": 1450,
        "approx_to_year": 2007,
        "capability_delta": ["printed pages", "digital library", "searchable text", "portable reading"],
        "transformation_pattern": ["digitization", "storage_shift", "portable_compute", "searchability"],
    },
    {
        "from_id": "ebook_reader",
        "to_id": "tablet",
        "family": "reading_media_digitization",
        "relationship": "dedicated_ebook_reader_partly_became_multifunction_tablet_reading",
        "logic_shift": "single-purpose digital reading converged into touch-screen app-based media and productivity",
        "approx_from_year": 2007,
        "approx_to_year": 2010,
        "capability_delta": ["digital reading", "color display", "apps", "interactive media"],
        "transformation_pattern": ["convergence", "touch_interface", "software_platform", "screen_scaling"],
    },
    {
        "from_id": "paper_calendar",
        "to_id": "pda",
        "family": "personal_organization",
        "relationship": "paper_planner_became_personal_digital_assistant",
        "logic_shift": "personal organization moved from static paper to editable pocket databases",
        "approx_from_year": 1900,
        "approx_to_year": 1993,
        "capability_delta": ["appointments", "contacts", "local database", "sync"],
        "transformation_pattern": ["digitization", "portable_compute", "personalization", "workflow_integration"],
    },
    {
        "from_id": "pda",
        "to_id": "smartphone",
        "family": "personal_organization",
        "relationship": "personal_digital_assistant_became_connected_smartphone",
        "logic_shift": "offline personal databases converged with cellular, internet, apps, and sensors",
        "approx_from_year": 1993,
        "approx_to_year": 2007,
        "capability_delta": ["contacts", "calendar", "mobile internet", "apps", "communications"],
        "transformation_pattern": ["convergence", "network_access", "software_platform", "sensorization"],
    },
    {
        "from_id": "typewriter",
        "to_id": "word_processor",
        "family": "writing_tool_evolution",
        "relationship": "mechanical_typewriter_became_editable_word_processor",
        "logic_shift": "writing shifted from irreversible mechanical imprinting to editable digital composition",
        "approx_from_year": 1868,
        "approx_to_year": 1976,
        "capability_delta": ["typed text", "editing", "storage", "printing"],
        "transformation_pattern": ["digitization", "editability", "storage_shift", "workflow_integration"],
    },
    {
        "from_id": "word_processor",
        "to_id": "collaborative_document_editor",
        "family": "writing_tool_evolution",
        "relationship": "local_word_processor_became_cloud_collaborative_document_editor",
        "logic_shift": "documents moved from local files to shared, real-time, networked workspaces",
        "approx_from_year": 1976,
        "approx_to_year": 2006,
        "capability_delta": ["digital text", "cloud sync", "real-time collaboration", "version history"],
        "transformation_pattern": ["network_access", "cloud_service", "collaboration", "versioned_memory"],
    },
    {
        "from_id": "paper_mail",
        "to_id": "email",
        "family": "messaging_latency_collapse",
        "relationship": "physical_mail_became_electronic_mail",
        "logic_shift": "message delivery collapsed from physical transport to network transmission",
        "approx_from_year": 1840,
        "approx_to_year": 1971,
        "capability_delta": ["addressed messages", "electronic delivery", "near-instant transmission"],
        "transformation_pattern": ["digitization", "network_access", "latency_collapse"],
    },
    {
        "from_id": "email",
        "to_id": "instant_messaging",
        "family": "messaging_latency_collapse",
        "relationship": "asynchronous_email_became_presence_aware_instant_messaging",
        "logic_shift": "messages moved from inbox batches to conversational presence and real-time reply loops",
        "approx_from_year": 1971,
        "approx_to_year": 1996,
        "capability_delta": ["electronic mail", "presence", "chat threads", "real-time messaging"],
        "transformation_pattern": ["latency_collapse", "presence_layer", "network_access", "conversation_interface"],
    },
    {
        "from_id": "instant_messaging",
        "to_id": "team_collaboration_platform",
        "family": "messaging_latency_collapse",
        "relationship": "instant_messaging_became_persistent_team_collaboration_platform",
        "logic_shift": "chat absorbed files, search, bots, workflows, and organizational memory",
        "approx_from_year": 1996,
        "approx_to_year": 2013,
        "capability_delta": ["chat", "channels", "files", "search", "workflow bots"],
        "transformation_pattern": ["workflow_integration", "searchability", "automation", "organizational_memory"],
    },
    {
        "from_id": "broadcast_radio",
        "to_id": "podcast",
        "family": "audio_distribution_shift",
        "relationship": "scheduled_broadcast_radio_became_on_demand_podcast",
        "logic_shift": "audio programming shifted from station schedules to subscription feeds and personal playback",
        "approx_from_year": 1920,
        "approx_to_year": 2004,
        "capability_delta": ["broadcast audio", "download feeds", "on-demand listening"],
        "transformation_pattern": ["time_shift", "network_access", "personalization", "subscription_feed"],
    },
    {
        "from_id": "broadcast_tv",
        "to_id": "streaming_video",
        "family": "video_distribution_shift",
        "relationship": "scheduled_broadcast_tv_became_on_demand_streaming_video",
        "logic_shift": "video distribution shifted from broadcast schedule to cloud catalog and recommendation loops",
        "approx_from_year": 1936,
        "approx_to_year": 2007,
        "capability_delta": ["scheduled video", "on-demand catalog", "adaptive streaming", "recommendations"],
        "transformation_pattern": ["time_shift", "cloud_service", "recommendation_ai", "network_access"],
    },
    {
        "from_id": "wristwatch",
        "to_id": "digital_watch",
        "family": "wearable_computing",
        "relationship": "mechanical_wristwatch_became_digital_timekeeping_device",
        "logic_shift": "wearable timekeeping became electronic, programmable, and display-driven",
        "approx_from_year": 1904,
        "approx_to_year": 1972,
        "capability_delta": ["wearable time", "digital display", "electronic timing"],
        "transformation_pattern": ["digitization", "miniaturization", "wearability"],
    },
    {
        "from_id": "digital_watch",
        "to_id": "smartwatch",
        "family": "wearable_computing",
        "relationship": "digital_watch_became_networked_sensor_wearable",
        "logic_shift": "timekeeping absorbed notifications, biometric sensors, apps, and phone-linked compute",
        "approx_from_year": 1972,
        "approx_to_year": 2015,
        "capability_delta": ["digital time", "biometric sensors", "notifications", "wearable apps"],
        "transformation_pattern": ["sensorization", "network_access", "software_platform", "health_context"],
    },
    {
        "from_id": "thermostat",
        "to_id": "programmable_thermostat",
        "family": "home_control_autonomy",
        "relationship": "manual_thermostat_became_programmable_environment_controller",
        "logic_shift": "manual control became scheduled local automation",
        "approx_from_year": 1885,
        "approx_to_year": 1986,
        "capability_delta": ["manual setpoint", "schedule", "local automation"],
        "transformation_pattern": ["automation", "programmability", "energy_optimization"],
    },
    {
        "from_id": "programmable_thermostat",
        "to_id": "smart_thermostat",
        "family": "home_control_autonomy",
        "relationship": "programmable_thermostat_became_learning_networked_home_controller",
        "logic_shift": "scheduled control gained sensors, cloud connection, optimization, and adaptive learning",
        "approx_from_year": 1986,
        "approx_to_year": 2011,
        "capability_delta": ["scheduling", "sensors", "remote control", "learning optimization"],
        "transformation_pattern": ["sensorization", "network_access", "learning_loop", "automation"],
    },
    {
        "from_id": "paper_ticket",
        "to_id": "magstripe_card",
        "family": "access_identity_digitization",
        "relationship": "paper_ticket_became_machine_readable_card",
        "logic_shift": "access rights moved from visible paper to encoded machine-readable identity",
        "approx_from_year": 1860,
        "approx_to_year": 1969,
        "capability_delta": ["paper proof", "encoded identity", "machine validation"],
        "transformation_pattern": ["digitization", "identity_layer", "machine_readability"],
    },
    {
        "from_id": "magstripe_card",
        "to_id": "mobile_credential",
        "family": "access_identity_digitization",
        "relationship": "machine_readable_card_became_mobile_credential",
        "logic_shift": "access identity converged into secure phone wallets and dynamic tokens",
        "approx_from_year": 1969,
        "approx_to_year": 2014,
        "capability_delta": ["card identity", "secure element", "dynamic token", "phone wallet"],
        "transformation_pattern": ["convergence", "security_tokenization", "identity_layer", "network_access"],
    },
    {
        "from_id": "arcade_game",
        "to_id": "home_game_console",
        "family": "interactive_entertainment_portability",
        "relationship": "venue_bound_arcade_game_became_home_game_console",
        "logic_shift": "interactive computing moved from public machines into living rooms",
        "approx_from_year": 1971,
        "approx_to_year": 1977,
        "capability_delta": ["coin-operated play", "home cartridges", "consumer interactive media"],
        "transformation_pattern": ["domestication", "consumerization", "software_platform"],
    },
    {
        "from_id": "home_game_console",
        "to_id": "mobile_game",
        "family": "interactive_entertainment_portability",
        "relationship": "home_console_play_became_mobile_app_game",
        "logic_shift": "games moved from dedicated living-room hardware to always-carried app platforms",
        "approx_from_year": 1977,
        "approx_to_year": 2008,
        "capability_delta": ["game console", "app store", "touch games", "mobile monetization"],
        "transformation_pattern": ["portable_compute", "software_platform", "touch_interface", "business_model_shift"],
    },
    {
        "from_id": "manual_vacuum_cleaner",
        "to_id": "robot_vacuum",
        "family": "domestic_robotics",
        "relationship": "manual_cleaning_appliance_became_autonomous_cleaning_robot",
        "logic_shift": "human-guided home appliance gained sensing, path planning, and autonomous task execution",
        "approx_from_year": 1908,
        "approx_to_year": 2002,
        "capability_delta": ["powered cleaning", "sensors", "path planning", "autonomous routine"],
        "transformation_pattern": ["sensorization", "autonomy", "task_planning", "domestication"],
    },
    {
        "from_id": "manual_car",
        "to_id": "driver_assistance_system",
        "family": "vehicle_autonomy",
        "relationship": "manual_vehicle_became_driver_assisted_vehicle",
        "logic_shift": "vehicle control began absorbing sensors, warning systems, and partial automation",
        "approx_from_year": 1908,
        "approx_to_year": 1995,
        "capability_delta": ["manual driving", "sensors", "lane/cruise assistance", "safety automation"],
        "transformation_pattern": ["sensorization", "automation", "safety_loop"],
    },
    {
        "from_id": "driver_assistance_system",
        "to_id": "autonomous_vehicle_stack",
        "family": "vehicle_autonomy",
        "relationship": "driver_assistance_became_autonomous_vehicle_stack",
        "logic_shift": "assistive safety features became perception, planning, control, and fleet-learning systems",
        "approx_from_year": 1995,
        "approx_to_year": 2020,
        "capability_delta": ["driver assistance", "perception", "planning", "fleet learning"],
        "transformation_pattern": ["autonomy", "sensor_fusion", "learning_loop", "real_time_context"],
    },
    {
        "from_id": "paper_medical_chart",
        "to_id": "electronic_health_record",
        "family": "health_record_digitization",
        "relationship": "paper_medical_chart_became_electronic_health_record",
        "logic_shift": "clinical memory moved from local paper files to searchable interoperable data systems",
        "approx_from_year": 1900,
        "approx_to_year": 2009,
        "capability_delta": ["paper chart", "structured data", "search", "interoperability"],
        "transformation_pattern": ["digitization", "searchability", "workflow_integration", "compliance"],
    },
    {
        "from_id": "electronic_health_record",
        "to_id": "clinical_decision_support",
        "family": "health_record_digitization",
        "relationship": "electronic_health_record_became_clinical_decision_support_layer",
        "logic_shift": "stored health data began producing alerts, recommendations, and workflow guidance",
        "approx_from_year": 2009,
        "approx_to_year": 2016,
        "capability_delta": ["clinical data", "rules", "alerts", "decision support"],
        "transformation_pattern": ["data_capture", "automation", "decision_support", "compliance"],
    },
]


DEVICE_EVOLUTION_CHAIN_SPECS: list[dict[str, Any]] = [
    {
        "family": "kitchen_heat_control",
        "nodes": [
            ("wood_stove", "Wood Stove", 1740, ["heat_source", "manual_control"]),
            ("gas_stove", "Gas Stove", 1826, ["metered_fuel", "finer_heat_control"]),
            ("electric_stove", "Electric Stove", 1892, ["electrified_heat", "safer_indoor_control"]),
            ("induction_cooktop", "Induction Cooktop", 1970, ["solid_state_power_control", "efficient_direct_heating"]),
            ("smart_induction_cooktop", "Smart Induction Cooktop", 2018, ["sensors", "software_recipes", "connected_control"]),
        ],
        "patterns": ["electrification", "sensorization", "software_control", "energy_efficiency"],
    },
    {
        "family": "food_preservation",
        "nodes": [
            ("icebox", "Icebox", 1802, ["passive_cooling", "food_preservation"]),
            ("electric_refrigerator", "Electric Refrigerator", 1913, ["compressor_cooling", "home_appliance"]),
            ("frost_free_refrigerator", "Frost-Free Refrigerator", 1950, ["automation", "maintenance_reduction"]),
            ("smart_refrigerator", "Smart Refrigerator", 2013, ["sensors", "inventory_awareness", "network_access"]),
        ],
        "patterns": ["electrification", "automation", "sensorization", "network_access"],
    },
    {
        "family": "laundry_automation",
        "nodes": [
            ("wash_board", "Wash Board", 1797, ["manual_labor", "cleaning_surface"]),
            ("electric_washing_machine", "Electric Washing Machine", 1908, ["motorized_cleaning", "home_appliance"]),
            ("automatic_washing_machine", "Automatic Washing Machine", 1937, ["timed_cycle", "water_control"]),
            ("smart_washing_machine", "Smart Washing Machine", 2015, ["sensors", "remote_status", "adaptive_cycle"]),
        ],
        "patterns": ["electrification", "automation", "sensorization", "remote_control"],
    },
    {
        "family": "lighting",
        "nodes": [
            ("candle", "Candle", 500, ["portable_light", "combustion"]),
            ("gas_lamp", "Gas Lamp", 1792, ["infrastructure_light", "fuel_distribution"]),
            ("incandescent_bulb", "Incandescent Bulb", 1879, ["electric_light", "mass_adoption"]),
            ("led_light", "LED Light", 1962, ["solid_state_light", "energy_efficiency"]),
            ("smart_light", "Smart Light", 2012, ["network_control", "automation", "contextual_scenes"]),
        ],
        "patterns": ["electrification", "solid_state", "energy_efficiency", "network_access", "automation"],
    },
    {
        "family": "heating_cooling",
        "nodes": [
            ("fireplace", "Fireplace", 1000, ["local_heat", "manual_fuel"]),
            ("central_heating", "Central Heating", 1855, ["distributed_heat", "building_infrastructure"]),
            ("air_conditioner", "Air Conditioner", 1902, ["active_cooling", "environment_control"]),
            ("heat_pump", "Heat Pump", 1948, ["reversible_thermal_control", "energy_efficiency"]),
            ("smart_hvac", "Smart HVAC", 2011, ["sensors", "optimization", "remote_control"]),
        ],
        "patterns": ["infrastructure", "automation", "sensorization", "energy_efficiency", "optimization"],
    },
    {
        "family": "farming_mechanization",
        "nodes": [
            ("hand_plow", "Hand Plow", 3000, ["manual_tilling", "agriculture"]),
            ("steel_plow", "Steel Plow", 1837, ["stronger_material", "soil_efficiency"]),
            ("tractor", "Tractor", 1892, ["engine_power", "mechanized_labor"]),
            ("gps_guided_tractor", "GPS-Guided Tractor", 1995, ["positioning", "precision_agriculture"]),
            ("autonomous_tractor", "Autonomous Tractor", 2022, ["autonomy", "sensor_fusion", "field_robotics"]),
        ],
        "patterns": ["mechanization", "sensorization", "real_time_context", "autonomy", "labor_leverage"],
    },
    {
        "family": "crop_monitoring",
        "nodes": [
            ("field_scouting", "Manual Field Scouting", 1800, ["human_observation", "crop_status"]),
            ("aerial_crop_photography", "Aerial Crop Photography", 1920, ["remote_observation", "visual_mapping"]),
            ("satellite_crop_imaging", "Satellite Crop Imaging", 1972, ["space_observation", "large_area_monitoring"]),
            ("drone_crop_monitoring", "Drone Crop Monitoring", 2010, ["low_altitude_sensors", "rapid_inspection"]),
            ("ai_crop_analytics", "AI Crop Analytics", 2018, ["computer_vision", "yield_prediction", "decision_support"]),
        ],
        "patterns": ["remote_sensing", "sensorization", "ai_analysis", "prediction", "decision_support"],
    },
    {
        "family": "manufacturing_control",
        "nodes": [
            ("manual_machine_tool", "Manual Machine Tool", 1800, ["manual_precision", "metalworking"]),
            ("assembly_line", "Assembly Line", 1913, ["process_standardization", "throughput"]),
            ("cnc_machine", "CNC Machine", 1952, ["programmable_motion", "precision_automation"]),
            ("industrial_robot", "Industrial Robot", 1961, ["robotic_manipulation", "repeatability"]),
            ("lights_out_factory", "Lights-Out Factory", 2000, ["autonomous_production", "sensor_feedback"]),
        ],
        "patterns": ["standardization", "programmability", "automation", "robotics", "closed_loop_control"],
    },
    {
        "family": "design_to_manufacture",
        "nodes": [
            ("drafting_board", "Drafting Board", 1900, ["manual_design", "technical_drawing"]),
            ("cad_software", "CAD Software", 1963, ["digital_design", "editable_geometry"]),
            ("cam_software", "CAM Software", 1970, ["machine_tool_pathing", "digital_fabrication"]),
            ("3d_printing", "3D Printing", 1984, ["additive_manufacturing", "rapid_prototyping"]),
            ("generative_design", "Generative Design", 2015, ["optimization", "algorithmic_geometry", "manufacturing_constraints"]),
        ],
        "patterns": ["digitization", "simulation", "automation", "optimization", "manufacturing_convergence"],
    },
    {
        "family": "medical_imaging",
        "nodes": [
            ("x_ray", "X-Ray Imaging", 1895, ["internal_visualization", "radiography"]),
            ("ct_scan", "CT Scan", 1971, ["computed_slices", "3d_medical_view"]),
            ("mri_scan", "MRI Scan", 1977, ["soft_tissue_imaging", "magnetic_resonance"]),
            ("digital_pacs", "Digital PACS", 1982, ["digital_storage", "networked_images"]),
            ("ai_radiology", "AI Radiology", 2016, ["pattern_detection", "triage", "decision_support"]),
        ],
        "patterns": ["sensorization", "digitization", "network_access", "ai_analysis", "decision_support"],
    },
    {
        "family": "patient_monitoring",
        "nodes": [
            ("manual_vitals", "Manual Vital Signs", 1800, ["periodic_measurement", "clinical_observation"]),
            ("bedside_monitor", "Bedside Monitor", 1960, ["continuous_measurement", "hospital_display"]),
            ("wearable_health_tracker", "Wearable Health Tracker", 2009, ["consumer_sensors", "continuous_tracking"]),
            ("remote_patient_monitoring", "Remote Patient Monitoring", 2015, ["cloud_connection", "alerting", "care_coordination"]),
            ("predictive_health_ai", "Predictive Health AI", 2020, ["risk_prediction", "personalized_intervention"]),
        ],
        "patterns": ["sensorization", "continuous_monitoring", "network_access", "prediction", "personalization"],
    },
    {
        "family": "finance_trading",
        "nodes": [
            ("open_outcry_trading", "Open Outcry Trading", 1870, ["human_market", "floor_signals"]),
            ("electronic_trading", "Electronic Trading", 1971, ["digital_order_book", "faster_execution"]),
            ("online_brokerage", "Online Brokerage", 1994, ["retail_access", "web_interface"]),
            ("algorithmic_trading", "Algorithmic Trading", 2000, ["automated_strategy", "low_latency"]),
            ("ai_portfolio_agent", "AI Portfolio Agent", 2024, ["signal_fusion", "risk_modeling", "governed_recommendations"]),
        ],
        "patterns": ["digitization", "latency_collapse", "automation", "ai_analysis", "risk_modeling"],
    },
    {
        "family": "banking_access",
        "nodes": [
            ("branch_banking", "Branch Banking", 1800, ["physical_service", "paper_records"]),
            ("atm", "ATM", 1967, ["self_service", "card_identity"]),
            ("online_banking", "Online Banking", 1995, ["web_access", "account_data"]),
            ("mobile_banking", "Mobile Banking", 2007, ["phone_access", "remote_deposit"]),
            ("embedded_finance", "Embedded Finance", 2016, ["api_banking", "in_context_payment"]),
        ],
        "patterns": ["self_service", "network_access", "mobile_access", "api_platform", "contextualization"],
    },
    {
        "family": "education_delivery",
        "nodes": [
            ("chalkboard_classroom", "Chalkboard Classroom", 1801, ["group_instruction", "local_presence"]),
            ("educational_film", "Educational Film", 1910, ["recorded_media", "visual_instruction"]),
            ("computer_based_training", "Computer-Based Training", 1960, ["interactive_lessons", "programmed_instruction"]),
            ("online_course", "Online Course", 1999, ["web_delivery", "asynchronous_learning"]),
            ("adaptive_ai_tutor", "Adaptive AI Tutor", 2023, ["personalized_feedback", "dialogue", "mastery_tracking"]),
        ],
        "patterns": ["media_shift", "interactivity", "network_access", "personalization", "ai_tutoring"],
    },
    {
        "family": "language_translation",
        "nodes": [
            ("human_translator", "Human Translator", 1000, ["language_expertise", "manual_translation"]),
            ("phrasebook", "Phrasebook", 1500, ["static_reference", "travel_language"]),
            ("statistical_machine_translation", "Statistical Machine Translation", 1990, ["corpus_patterns", "probabilistic_translation"]),
            ("neural_machine_translation", "Neural Machine Translation", 2016, ["sequence_modeling", "contextual_translation"]),
            ("real_time_speech_translation", "Real-Time Speech Translation", 2020, ["speech_recognition", "translation", "speech_synthesis"]),
        ],
        "patterns": ["digitization", "ai_analysis", "latency_collapse", "multimodal_interface", "contextualization"],
    },
    {
        "family": "retail_discovery",
        "nodes": [
            ("general_store", "General Store", 1800, ["local_inventory", "human_recommendation"]),
            ("catalog_shopping", "Catalog Shopping", 1872, ["remote_browsing", "mail_order"]),
            ("ecommerce_site", "E-Commerce Site", 1995, ["web_catalog", "online_checkout"]),
            ("marketplace_platform", "Marketplace Platform", 2000, ["third_party_sellers", "ratings", "search"]),
            ("personalized_commerce_ai", "Personalized Commerce AI", 2020, ["recommendations", "dynamic_pricing", "conversational_shopping"]),
        ],
        "patterns": ["network_access", "platformization", "searchability", "recommendation_ai", "personalization"],
    },
    {
        "family": "logistics_tracking",
        "nodes": [
            ("paper_manifest", "Paper Manifest", 1800, ["manual_record", "shipment_list"]),
            ("barcode_tracking", "Barcode Tracking", 1974, ["machine_readability", "inventory_scan"]),
            ("rfid_tracking", "RFID Tracking", 1999, ["wireless_identity", "bulk_scan"]),
            ("iot_asset_tracking", "IoT Asset Tracking", 2015, ["live_location", "sensors", "cloud_visibility"]),
            ("predictive_supply_chain_ai", "Predictive Supply Chain AI", 2020, ["forecasting", "risk_alerts", "optimization"]),
        ],
        "patterns": ["machine_readability", "sensorization", "network_access", "prediction", "optimization"],
    },
    {
        "family": "energy_grid",
        "nodes": [
            ("central_power_station", "Central Power Station", 1882, ["central_generation", "electric_distribution"]),
            ("regional_grid", "Regional Grid", 1920, ["interconnection", "load_balancing"]),
            ("smart_meter", "Smart Meter", 2005, ["digital_measurement", "remote_reading"]),
            ("distributed_energy_resource", "Distributed Energy Resource", 2010, ["solar", "storage", "edge_generation"]),
            ("ai_grid_orchestration", "AI Grid Orchestration", 2020, ["forecasting", "demand_response", "distributed_control"]),
        ],
        "patterns": ["infrastructure", "digitization", "edge_distribution", "prediction", "optimization"],
    },
    {
        "family": "battery_energy",
        "nodes": [
            ("lead_acid_battery", "Lead-Acid Battery", 1859, ["rechargeable_storage", "heavy_power"]),
            ("alkaline_battery", "Alkaline Battery", 1959, ["portable_power", "consumer_devices"]),
            ("lithium_ion_battery", "Lithium-Ion Battery", 1991, ["high_density_storage", "mobile_compute"]),
            ("battery_management_system", "Battery Management System", 2008, ["sensors", "charge_control", "safety"]),
            ("solid_state_battery", "Solid-State Battery", 2025, ["higher_density", "safety_potential", "manufacturing_challenge"]),
        ],
        "patterns": ["energy_density", "miniaturization", "sensorization", "safety_control", "manufacturing_breakthrough"],
    },
    {
        "family": "robotics_control",
        "nodes": [
            ("teleoperator", "Teleoperator", 1945, ["remote_manipulation", "human_control"]),
            ("industrial_robot", "Industrial Robot", 1961, ["programmable_motion", "repeatability"]),
            ("mobile_robot", "Mobile Robot", 1980, ["navigation", "mobile_sensing"]),
            ("collaborative_robot", "Collaborative Robot", 2008, ["human_safe_interaction", "flexible_tasking"]),
            ("embodied_ai_robot", "Embodied AI Robot", 2023, ["vision_language_action", "adaptive_planning"]),
        ],
        "patterns": ["programmability", "sensorization", "autonomy", "human_robot_collaboration", "ai_planning"],
    },
    {
        "family": "security_surveillance",
        "nodes": [
            ("human_guard", "Human Guard", 1000, ["human_observation", "physical_presence"]),
            ("cctv", "CCTV", 1942, ["remote_video", "monitoring"]),
            ("digital_video_recorder", "Digital Video Recorder", 1999, ["digital_storage", "searchable_video"]),
            ("ip_camera", "IP Camera", 2005, ["network_video", "remote_access"]),
            ("ai_video_analytics", "AI Video Analytics", 2015, ["object_detection", "alerts", "pattern_recognition"]),
        ],
        "patterns": ["remote_sensing", "digitization", "network_access", "ai_analysis", "automation"],
    },
    {
        "family": "law_research",
        "nodes": [
            ("law_library", "Law Library", 1800, ["physical_reference", "manual_search"]),
            ("legal_database", "Legal Database", 1973, ["digital_cases", "keyword_search"]),
            ("online_legal_research", "Online Legal Research", 1990, ["network_access", "full_text_search"]),
            ("e_discovery_platform", "E-Discovery Platform", 2000, ["document_processing", "review_workflow"]),
            ("legal_ai_research_agent", "Legal AI Research Agent", 2023, ["semantic_search", "drafting", "citation_checking"]),
        ],
        "patterns": ["digitization", "searchability", "workflow_integration", "ai_analysis", "evidence_traceability"],
    },
    {
        "family": "architecture_design",
        "nodes": [
            ("physical_model", "Physical Architectural Model", 1500, ["scale_representation", "spatial_reasoning"]),
            ("blueprint", "Blueprint", 1842, ["reproducible_plan", "construction_document"]),
            ("cad_architecture", "CAD Architecture", 1980, ["digital_drawing", "editable_plan"]),
            ("bim_model", "BIM Model", 2002, ["information_model", "coordination"]),
            ("generative_bim_ai", "Generative BIM AI", 2023, ["constraint_generation", "simulation", "code_checking"]),
        ],
        "patterns": ["digitization", "model_richness", "simulation", "optimization", "ai_generation"],
    },
    {
        "family": "news_distribution",
        "nodes": [
            ("printed_newspaper", "Printed Newspaper", 1605, ["periodic_news", "physical_distribution"]),
            ("radio_news", "Radio News", 1920, ["broadcast_audio", "faster_updates"]),
            ("television_news", "Television News", 1940, ["broadcast_video", "mass_attention"]),
            ("online_news", "Online News", 1995, ["web_updates", "hyperlinks"]),
            ("algorithmic_news_feed", "Algorithmic News Feed", 2006, ["personalization", "ranking", "engagement_loop"]),
        ],
        "patterns": ["latency_collapse", "media_shift", "network_access", "personalization", "recommendation_ai"],
    },
    {
        "family": "weather_prediction",
        "nodes": [
            ("barometer", "Barometer", 1643, ["pressure_measurement", "local_forecast"]),
            ("weather_station", "Weather Station", 1800, ["instrument_network", "observation"]),
            ("weather_satellite", "Weather Satellite", 1960, ["remote_sensing", "global_observation"]),
            ("numerical_weather_model", "Numerical Weather Model", 1950, ["simulation", "forecasting"]),
            ("ai_weather_model", "AI Weather Model", 2023, ["machine_learning", "fast_prediction", "pattern_inference"]),
        ],
        "patterns": ["sensorization", "networked_observation", "simulation", "prediction", "ai_analysis"],
    },
]


def generated_device_chain_edges() -> list[dict[str, Any]]:
    edges: list[dict[str, Any]] = []
    for spec in DEVICE_EVOLUTION_CHAIN_SPECS:
        nodes = spec.get("nodes", [])
        patterns = spec.get("patterns", [])
        family = str(spec.get("family") or "uncategorized_device_evolution")
        for left, right in zip(nodes, nodes[1:]):
            from_id, from_name, from_year, from_caps = left
            to_id, to_name, to_year, to_caps = right
            edges.append(
                {
                    "from_id": from_id,
                    "to_id": to_id,
                    "family": family,
                    "relationship": f"{from_id}_became_{to_id}",
                    "logic_shift": f"{from_name} became {to_name} by shifting from {', '.join(from_caps[:2])} toward {', '.join(to_caps[:2])}.",
                    "approx_from_year": from_year,
                    "approx_to_year": to_year,
                    "capability_delta": list(dict.fromkeys([*from_caps, *to_caps]))[:8],
                    "transformation_pattern": patterns,
                }
            )
    return edges


def generated_device_chain_nodes() -> dict[str, dict[str, Any]]:
    nodes: dict[str, dict[str, Any]] = {}
    for spec in DEVICE_EVOLUTION_CHAIN_SPECS:
        family = str(spec.get("family") or "uncategorized_device_evolution")
        for node_id, name, year, capabilities in spec.get("nodes", []):
            domains = sorted({family.split("_")[0], "technology"})
            nodes.setdefault(
                node_id,
                {
                    "id": node_id,
                    "name": name,
                    "year": year,
                    "domains": domains,
                    "capabilities": capabilities,
                    "source": "acs2_seed_transformation_chain",
                },
            )
    return nodes


CATEGORY_RULES: list[tuple[str, list[str], list[str]]] = [
    ("ai", ["ai", "artificial intelligence", "gpt", "chatgpt", "transformer", "deep learning", "perceptron", "agi"], ["reasoning", "prediction", "automation"]),
    ("compute", ["calculator", "computer", "microprocessor", "transistor", "chip", "processor"], ["computation", "programmable logic", "hardware acceleration"]),
    ("network", ["internet", "arpanet", "web", "tcp", "dns", "browser"], ["networked data exchange", "distributed access"]),
    ("mobile", ["mobile", "smartphone", "iphone", "android", "cellular"], ["field access", "edge interaction"]),
    ("knowledge", ["wikipedia", "search", "google", "database", "knowledge"], ["information retrieval", "knowledge organization"]),
    ("autonomous_systems", ["autonomous", "agent", "invention engine", "robot", "decision engine"], ["closed-loop autonomy", "tool use", "decision support"]),
    ("blockchain", ["bitcoin", "blockchain"], ["distributed ledger", "trustless record keeping"]),
    ("simulation", ["simulation", "digital twin", "prototype", "performance"], ["scenario testing", "pre-build validation"]),
    ("governance", ["safety", "regulatory", "standards", "compliance", "risk"], ["review gates", "auditability", "control policy"]),
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def project_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "main.py").exists() or (parent / "pyproject.toml").exists():
            return parent
    return Path.cwd()


def read_json(path: Path, fallback: Any) -> Any:
    if not path.exists():
        return fallback
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback


def technology_source_root() -> Path | None:
    manifest = read_json(project_root() / "data" / "source_packs" / "local_upload_source_packs.json", {})
    packs = manifest.get("packs", []) if isinstance(manifest, dict) else []
    for pack in packs if isinstance(packs, list) else []:
        if isinstance(pack, dict) and pack.get("pack_id") == "auto_invention_technology_database":
            root = Path(str(pack.get("root_path") or ""))
            return root if root.exists() else None
    fallback = Path("C:/Users/craig/OneDrive/Desktop/Docs Main/Tech database( auto invent)")
    return fallback if fallback.exists() else None


def slug(value: str) -> str:
    text = "".join(ch.lower() if ch.isalnum() else "_" for ch in value)
    text = re.sub(r"_+", "_", text).strip("_")
    return text[:80] or "technology_record"


def query_terms(query: str | None) -> set[str]:
    text = "".join(ch.lower() if ch.isalnum() else " " for ch in str(query or ""))
    return {part for part in text.split() if len(part) > 2}


def clean_text(value: str) -> str:
    return " ".join(str(value or "").replace("â†’", "->").replace("â€¢", "-").split())


def extract_year(value: str) -> int | None:
    match = re.search(r"(16|17|18|19|20)\d{2}", value)
    return int(match.group(0)) if match else None


def classify_domains(text: str) -> list[str]:
    lower = text.lower()
    domains = [domain for domain, hints, _ in CATEGORY_RULES if any(hint in lower for hint in hints)]
    return domains or ["technology"]


def capabilities_for(text: str, domains: list[str]) -> list[str]:
    lower = text.lower()
    capabilities: list[str] = []
    for domain, hints, caps in CATEGORY_RULES:
        if domain in domains or any(hint in lower for hint in hints):
            capabilities.extend(caps)
    if "invention" in lower or "autonomous" in lower:
        capabilities.extend(["technology scanning", "pattern recognition", "design generation", "feasibility validation"])
    return list(dict.fromkeys(capabilities))[:8] or ["technology evolution signal"]


def readiness_for(year: int | None, text: str) -> tuple[int, str, str, str]:
    lower = text.lower()
    if any(term in lower for term in ("predicted", "203", "post-singularity", "fully operational")):
        return 3, "future_speculative", "low_until_validated", "not_currently_manufacturable"
    if year and year >= 2022:
        return 8, "current_production_or_emerging", "medium_high", "software_deployable_with_controls"
    if year and year >= 2010:
        return 8, "production", "high", "software_deployable"
    if year and year >= 1990:
        return 9, "mature_foundation", "high", "widely_manufacturable_or_deployable"
    return 9, "historical_foundation", "high", "widely_manufacturable_or_deployable"


def parse_timeline_markdown(root: Path | None = None) -> list[dict[str, Any]]:
    root = root or technology_source_root()
    if not root:
        return []
    records: list[dict[str, Any]] = []
    seen: set[str] = set()
    for path in sorted(root.glob("*.md")):
        text = path.read_text(encoding="utf-8", errors="replace")
        era = "Technology Timeline"
        section = ""
        for line in text.splitlines():
            stripped = clean_text(line)
            if not stripped:
                continue
            if stripped.startswith("### "):
                era = stripped[4:].strip()
                continue
            if stripped.startswith("## "):
                section = stripped[3:].strip()
                continue
            if not stripped.startswith(("-", "1.", "2.", "3.")):
                continue
            normalized = re.sub(r"^\s*(?:-\s*|\d+\.\s*)", "", stripped)
            normalized = re.sub(r"\*\*", "", normalized)
            if ":" in normalized:
                date_part, description = normalized.split(":", 1)
            else:
                date_part, description = "", normalized
            description = clean_text(description or normalized)
            if len(description) < 20:
                continue
            dedupe_key = description.lower()
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)
            year = extract_year(date_part) or extract_year(description)
            domains = classify_domains(description)
            readiness, maturity, buildability, manufacturability = readiness_for(year, description)
            records.append(
                {
                    "id": "timeline_" + slug(description),
                    "name": description[:96],
                    "era": era,
                    "section": section,
                    "year": year,
                    "maturity": maturity,
                    "readiness_level": readiness,
                    "domains": domains,
                    "capabilities": capabilities_for(description, domains),
                    "buildability": buildability,
                    "manufacturability": manufacturability,
                    "deployment": "current_stack_or_historical_foundation" if readiness >= 7 else "future_requires_validation",
                    "gap_fit": ["technology evolution pattern", "component basis", "timeline evidence"],
                    "acquirer_fit": ["AI platforms", "R&D platforms", "industrial software"],
                    "source": str(path).replace("\\", "/"),
                    "source_type": "technology_timeline_markdown",
                    "evidence_basis": [description],
                }
            )
    return records


def configured_evidence_sources(root: Path | None = None) -> list[dict[str, Any]]:
    root = root or technology_source_root()
    if not root:
        return [
            {
                "name": "seeded_claire_technology_database",
                "path": "claire/technology/technology_base.py",
                "type": "embedded_seed_records",
                "status": "configured",
                "body_indexed": True,
            }
        ]
    return [
        {
            "name": path.name,
            "path": str(path).replace("\\", "/"),
            "type": path.suffix.lower().lstrip(".") or "file",
            "status": "configured",
            "body_indexed": path.suffix.lower() in {".md", ".txt", ".html"},
        }
        for path in sorted(root.iterdir())
        if path.is_file()
    ]


def generated_technology_records() -> list[dict[str, Any]]:
    records = [*SEED_TECHNOLOGY_RECORDS, *DISCOVERY_LOOP_RECORDS, *parse_timeline_markdown()]
    deduped: dict[str, dict[str, Any]] = {}
    for record in records:
        deduped.setdefault(str(record["id"]), record)
    return list(deduped.values())


def _record_lookup(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    lookup = {str(record.get("id")): record for record in records if record.get("id")}
    aliases = {
        "mechanical_calculator": {
            "id": "mechanical_calculator",
            "name": "Mechanical Calculator",
            "year": 1642,
            "domains": ["compute"],
            "capabilities": ["mechanized arithmetic"],
            "source": "lineage_anchor",
        },
        "programmable_computation": {
            "id": "programmable_computation",
            "name": "Programmable Computation",
            "year": 1936,
            "domains": ["compute"],
            "capabilities": ["formal computation", "programmable logic"],
            "source": "lineage_anchor",
        },
        "electronic_computer": {
            "id": "electronic_computer",
            "name": "Electronic Computer",
            "year": 1946,
            "domains": ["compute"],
            "capabilities": ["machine-speed computation"],
            "source": "lineage_anchor",
        },
        "microprocessor": {
            "id": "microprocessor",
            "name": "Microprocessor",
            "year": 1971,
            "domains": ["compute", "hardware"],
            "capabilities": ["mass manufacturable processors"],
            "source": "lineage_anchor",
        },
        "personal_computer": {
            "id": "personal_computer",
            "name": "Personal Computer",
            "year": 1981,
            "domains": ["compute", "software"],
            "capabilities": ["individual productivity", "interactive software"],
            "source": "lineage_anchor",
        },
        "internet_web": {
            "id": "internet_web",
            "name": "Internet and Web",
            "year": 1991,
            "domains": ["network", "knowledge"],
            "capabilities": ["networked data exchange", "web-scale information access"],
            "source": "lineage_anchor",
        },
        "search_knowledge_graph": {
            "id": "search_knowledge_graph",
            "name": "Search and Knowledge Graph",
            "year": 2012,
            "domains": ["knowledge", "ai"],
            "capabilities": ["search ranking", "entity relationship mapping"],
            "source": "lineage_anchor",
        },
        "car_phone": {
            "id": "car_phone",
            "name": "Car Phone",
            "year": 1946,
            "domains": ["mobile", "network"],
            "capabilities": ["vehicle-mounted radio telephone", "cellular precursor"],
            "source": "lineage_anchor",
        },
        "mobile_phone": {
            "id": "mobile_phone",
            "name": "Mobile Phone",
            "year": 1983,
            "domains": ["mobile", "network"],
            "capabilities": ["personal voice communication", "cellular mobility"],
            "source": "lineage_anchor",
        },
        "smartphone": {
            "id": "smartphone",
            "name": "Smartphone",
            "year": 2007,
            "domains": ["mobile", "compute", "network"],
            "capabilities": ["mobile internet", "touch apps", "sensors", "pocket computing"],
            "source": "lineage_anchor",
        },
        "battery_portable_tv": {
            "id": "battery_portable_tv",
            "name": "Battery Powered Portable TV",
            "year": 1982,
            "domains": ["mobile", "media", "hardware"],
            "capabilities": ["battery display", "portable broadcast viewing"],
            "source": "lineage_anchor",
        },
        "portable_media_player": {
            "id": "portable_media_player",
            "name": "Portable Digital Media Player",
            "year": 2001,
            "domains": ["mobile", "media", "storage"],
            "capabilities": ["digital media library", "portable playback"],
            "source": "lineage_anchor",
        },
        "tablet": {
            "id": "tablet",
            "name": "Tablet Computer",
            "year": 2010,
            "domains": ["mobile", "compute", "media"],
            "capabilities": ["touch computing", "portable media", "mobile productivity"],
            "source": "lineage_anchor",
        },
        "apple_ii": {
            "id": "apple_ii",
            "name": "Apple II",
            "year": 1977,
            "domains": ["compute", "software"],
            "capabilities": ["personal computing", "consumer software"],
            "source": "lineage_anchor",
        },
        "portable_computer": {
            "id": "portable_computer",
            "name": "Portable Computer",
            "year": 1981,
            "domains": ["compute", "hardware"],
            "capabilities": ["transportable personal computing"],
            "source": "lineage_anchor",
        },
        "laptop": {
            "id": "laptop",
            "name": "Laptop Computer",
            "year": 1989,
            "domains": ["compute", "mobile"],
            "capabilities": ["battery productivity", "portable work"],
            "source": "lineage_anchor",
        },
    }
    for key, value in aliases.items():
        lookup.setdefault(key, value)
    for key, value in generated_device_chain_nodes().items():
        lookup.setdefault(key, value)
    for key, value in generated_expanded_acs2_nodes().items():
        lookup.setdefault(key, value)
    return lookup


def build_technology_lineage(records: list[dict[str, Any]]) -> dict[str, Any]:
    lookup = _record_lookup(records)
    edges: list[dict[str, Any]] = []
    nodes: dict[str, dict[str, Any]] = {}
    intervals: list[int] = []
    all_edges = [
        *TECHNOLOGY_LINEAGE_EDGES,
        *DEVICE_EVOLUTION_EDGES,
        *generated_device_chain_edges(),
        *generated_expanded_acs2_edges(),
    ]
    for edge in all_edges:
        from_record = lookup.get(edge["from_id"], {"id": edge["from_id"], "name": edge["from_id"]})
        to_record = lookup.get(edge["to_id"], {"id": edge["to_id"], "name": edge["to_id"]})
        from_year = int(edge.get("approx_from_year") or from_record.get("year") or 0)
        to_year = int(edge.get("approx_to_year") or to_record.get("year") or from_year)
        if from_year and to_year and to_year >= from_year:
            intervals.append(max(1, to_year - from_year))
        for record in [from_record, to_record]:
            record_id = str(record.get("id"))
            nodes[record_id] = {
                "id": record_id,
                "name": record.get("name"),
                "year": record.get("year"),
                "domains": record.get("domains", []),
                "capabilities": record.get("capabilities", []),
                "source": record.get("source"),
            }
        edges.append(
            {
                **edge,
                "family": edge.get("family", "core_compute_to_autonomous_invention"),
                "from_name": from_record.get("name"),
                "to_name": to_record.get("name"),
                "interval_years": max(1, to_year - from_year) if from_year and to_year else None,
                "evidence_status": "lineage_anchor_or_record_match",
            }
        )
    family_counts = Counter(str(edge.get("family", "core_compute_to_autonomous_invention")) for edge in edges)
    pattern_counts: Counter[str] = Counter()
    for edge in edges:
        patterns = edge.get("transformation_pattern", [])
        if isinstance(patterns, list):
            pattern_counts.update(str(item) for item in patterns)
    return {
        "schema_version": "claire.technology_lineage.v1",
        "status": "ready",
        "purpose": "Track what became what so ACS2 trend reasoning can use an enormous transformation graph instead of isolated starting records.",
        "nodes": sorted(nodes.values(), key=lambda item: (int(item.get("year") or 9999), item.get("id", ""))),
        "edges": edges,
        "lineage_depth": len(edges),
        "family_count": len(family_counts),
        "families": dict(sorted(family_counts.items())),
        "transformation_patterns": [
            {"pattern": pattern, "count": count}
            for pattern, count in pattern_counts.most_common()
        ],
        "acs2_diagram": {
            "status": "graph_ready",
            "node_count": len(nodes),
            "edge_count": len(edges),
            "graph_type": "technology_object_transformation_graph",
            "reasoning_use": [
                "infer analogies across families",
                "detect convergence points",
                "measure interval compression",
                "identify repeated transformation patterns",
                "seed historical trend and singularity math",
            ],
        },
        "first_anchor_year": min([int(item.get("year") or 9999) for item in nodes.values()] or [0]),
        "latest_anchor_year": max([int(item.get("year") or 0) for item in nodes.values()] or [0]),
        "intervals_years": intervals,
    }


def get_acs2_graph(query: str | None = "") -> dict[str, Any]:
    database = build_technology_database(query)
    lineage = database.get("technology_lineage", {})
    graph = graph_from_lineage(lineage)
    return {
        "schema_version": "claire.acs2_graph.v1",
        "status": "ready",
        "query": str(query or ""),
        "node_count": len(graph.nodes),
        "edge_count": len(graph.edges),
        "nodes": [
            {
                "id": node.id,
                "name": node.name,
                "family": node.family,
                "year_start": node.year_start,
                "year_end": node.year_end,
                "source": node.metadata.get("source"),
            }
            for node in graph.nodes
        ],
        "edges": [
            {
                "from": edge.from_id,
                "to": edge.to_id,
                "reason": edge.reason,
                "patterns": edge.pattern_ids,
                "enabling_signals": edge.enabling_signals,
                "family": edge.metadata.get("family"),
            }
            for edge in graph.edges
        ],
    }


def build_historical_trend_math(lineage: dict[str, Any]) -> dict[str, Any]:
    edges = lineage.get("edges", []) if isinstance(lineage.get("edges"), list) else []
    core_intervals = [
        int(edge.get("interval_years"))
        for edge in edges
        if isinstance(edge, dict)
        and edge.get("family") == "core_compute_to_autonomous_invention"
        and edge.get("interval_years")
    ]
    intervals = core_intervals or [int(value) for value in lineage.get("intervals_years", []) if int(value) > 0]
    if not intervals:
        return {
            "schema_version": "claire.historical_trend_math.v1",
            "status": "insufficient_lineage",
            "singularity_math_ready": False,
        }
    early = intervals[: max(1, len(intervals) // 2)]
    late = intervals[max(1, len(intervals) // 2) :]
    average_interval = sum(intervals) / len(intervals)
    early_average = sum(early) / len(early)
    late_average = sum(late) / max(1, len(late))
    compression_ratio = round(early_average / max(1.0, late_average), 4)
    acceleration_score = round(min(1.0, max(0.0, (compression_ratio - 1.0) / 6.0)), 4)
    latest_year = int(lineage.get("latest_anchor_year") or 2026)
    projected_next_interval = max(1, int(round(late_average / max(1.0, compression_ratio))))
    return {
        "schema_version": "claire.historical_trend_math.v1",
        "status": "ready",
        "model": "interval_compression_over_core_compute_to_autonomy_lineage",
        "singularity_math_ready": True,
        "math_scope": "core_compute_to_autonomous_invention",
        "wider_graph_interval_count": len(lineage.get("intervals_years", [])) if isinstance(lineage.get("intervals_years"), list) else 0,
        "historical_linear_spine": [
            {
                "from": edge.get("from_name"),
                "to": edge.get("to_name"),
                "from_year": edge.get("approx_from_year"),
                "to_year": edge.get("approx_to_year"),
                "interval_years": edge.get("interval_years"),
                "logic_shift": edge.get("logic_shift"),
            }
            for edge in edges
            if isinstance(edge, dict) and edge.get("family") == "core_compute_to_autonomous_invention"
        ],
        "interval_statistics": {
            "average_interval_years": round(average_interval, 2),
            "early_average_interval_years": round(early_average, 2),
            "late_average_interval_years": round(late_average, 2),
            "compression_ratio": compression_ratio,
            "log2_compression": round(math.log(max(compression_ratio, 1.0), 2), 4),
            "acceleration_score": acceleration_score,
        },
        "projection": {
            "latest_anchor_year": latest_year,
            "projected_next_interval_years": projected_next_interval,
            "projected_next_inflection_year": latest_year + projected_next_interval,
            "caution": "Projection is a reasoning scaffold, not a prophecy; live evidence and validation must still govern route decisions.",
        },
    }


def build_acs2_transformation_diagram(lineage: dict[str, Any]) -> dict[str, Any]:
    edges = lineage.get("edges", []) if isinstance(lineage.get("edges"), list) else []
    families: dict[str, list[dict[str, Any]]] = {}
    convergence_targets: Counter[str] = Counter()
    for edge in edges:
        if not isinstance(edge, dict):
            continue
        family = str(edge.get("family") or "uncategorized")
        families.setdefault(family, []).append(edge)
        convergence_targets.update([str(edge.get("to_id"))])

    family_views: list[dict[str, Any]] = []
    for family, family_edges in sorted(families.items()):
        family_views.append(
            {
                "family": family,
                "edge_count": len(family_edges),
                "path": [
                    {
                        "from": edge.get("from_name"),
                        "to": edge.get("to_name"),
                        "relationship": edge.get("relationship"),
                        "logic_shift": edge.get("logic_shift"),
                        "patterns": edge.get("transformation_pattern", []),
                    }
                    for edge in family_edges
                ],
            }
        )

    convergence_points = [
        {
            "node_id": node_id,
            "incoming_edges": count,
            "meaning": "multiple older objects or branches converge into this later form",
        }
        for node_id, count in convergence_targets.most_common()
        if count >= 2
    ]
    return {
        "schema_version": "claire.acs2_transformation_diagram.v1",
        "status": "ready",
        "diagram_intent": "Represent the enormous ACS2 object-transformation map Craig described: many device families, their endings, and the patterns that explain how beginnings become later systems.",
        "family_views": family_views,
        "convergence_points": convergence_points,
        "pattern_summary": lineage.get("transformation_patterns", []),
        "operator_prompt": "Use this graph to ask: what older thing is this new thing becoming, which branches are converging, and which repeated pattern is compressing the timeline?",
    }


def _norm_node(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value or "").lower())


ROOT_TRACE_ALIASES: dict[str, list[str]] = {
    "cellphone": ["mobile_phone", "smartphone", "car_phone"],
    "cell": ["mobile_phone", "smartphone", "car_phone"],
    "phone": ["mobile_phone", "smartphone", "car_phone"],
    "mobilephone": ["mobile_phone", "smartphone", "car_phone"],
    "smartphone": ["smartphone", "mobile_phone"],
    "tablet": ["tablet", "portable_media_player", "battery_portable_tv"],
    "laptop": ["laptop", "portable_computer", "apple_ii"],
    "ev": ["electric_vehicle", "modern_electric_vehicle", "autonomous_electric_vehicle"],
    "electricvehicle": ["electric_vehicle", "modern_electric_vehicle", "autonomous_electric_vehicle"],
}


def build_root_to_current_timeline(lineage: dict[str, Any], query: str | None = "") -> dict[str, Any]:
    edges = [edge for edge in lineage.get("edges", []) if isinstance(edge, dict)]
    if not edges:
        return {
            "schema_version": "claire.root_to_current_timeline.v1",
            "status": "no_lineage_edges",
            "query": str(query or ""),
            "timelines": [],
        }

    query_text = str(query or "").lower()
    query_norm = _norm_node(query_text)
    targets: list[str] = []
    for alias, node_ids in ROOT_TRACE_ALIASES.items():
        if alias in query_norm:
            targets.extend(node_ids)

    node_text: dict[str, str] = {}
    reverse: dict[str, list[dict[str, Any]]] = {}
    forward: dict[str, list[dict[str, Any]]] = {}
    incoming: Counter[str] = Counter()
    outgoing: Counter[str] = Counter()
    for edge in edges:
        from_id = str(edge.get("from_id") or "")
        to_id = str(edge.get("to_id") or "")
        if not from_id or not to_id:
            continue
        node_text[from_id] = " ".join(
            [from_id, str(edge.get("from_name", "")), str(edge.get("family", "")), str(edge.get("relationship", ""))]
        ).lower()
        node_text[to_id] = " ".join(
            [to_id, str(edge.get("to_name", "")), str(edge.get("family", "")), str(edge.get("relationship", ""))]
        ).lower()
        reverse.setdefault(to_id, []).append(edge)
        forward.setdefault(from_id, []).append(edge)
        incoming[to_id] += 1
        outgoing[from_id] += 1

    terms = query_terms(query)
    for node_id, text in node_text.items():
        if terms and any(term in text for term in terms):
            targets.append(node_id)

    if not targets:
        convergence = lineage.get("convergence_targets", []) if isinstance(lineage.get("convergence_targets"), list) else []
        targets = [str(item.get("node_id")) for item in convergence[:3] if isinstance(item, dict) and item.get("node_id")]

    seen_targets: set[str] = set()
    ordered_targets = []
    for target in targets:
        if target and target not in seen_targets and target in node_text:
            ordered_targets.append(target)
            seen_targets.add(target)
    ordered_targets.sort(key=lambda node_id: (0 if _norm_node(node_id) in query_norm else 1, node_id))
    ordered_targets = ordered_targets[:5]

    def back_paths(node_id: str, path_edges: list[dict[str, Any]], visited: set[str]) -> list[list[dict[str, Any]]]:
        parents = reverse.get(node_id, [])
        if not parents or len(path_edges) >= 14:
            return [path_edges]
        paths: list[list[dict[str, Any]]] = []
        for edge in parents[:5]:
            parent = str(edge.get("from_id") or "")
            if not parent or parent in visited:
                continue
            paths.extend(back_paths(parent, [edge, *path_edges], visited | {parent}))
        return paths

    timelines: list[dict[str, Any]] = []
    for target in ordered_targets:
        paths = back_paths(target, [], {target})
        paths.sort(key=lambda path: (len(path), int(path[0].get("approx_from_year") or 999999) if path else 999999))
        best_path = paths[-1] if paths else []
        dots = []
        for edge in best_path:
            dots.append(
                {
                    "from_id": edge.get("from_id"),
                    "to_id": edge.get("to_id"),
                    "from_year": edge.get("approx_from_year"),
                    "to_year": edge.get("approx_to_year"),
                    "relationship": edge.get("relationship"),
                    "why_it_happened": edge.get("logic_shift"),
                    "capability_delta": edge.get("capability_delta", []),
                    "patterns": edge.get("transformation_pattern", []),
                    "family": edge.get("family"),
                }
            )
        all_patterns = Counter(
            str(pattern)
            for dot in dots
            for pattern in (dot.get("patterns") if isinstance(dot.get("patterns"), list) else [])
        )
        years = [
            int(year)
            for dot in dots
            for year in [dot.get("from_year"), dot.get("to_year")]
            if isinstance(year, int)
        ]
        recent_patterns = [pattern for pattern, _ in all_patterns.most_common(6)]
        repeat_score = round(min(0.96, 0.34 + len(dots) * 0.035 + len(recent_patterns) * 0.045 + (0.12 if incoming.get(target, 0) >= 2 else 0)), 3)
        next_patterns = [
            "agentic_interface",
            "ambient_computing",
            "autonomous_workflow",
            "predictive_assistance",
        ]
        if "battery_power" in all_patterns or "miniaturization" in all_patterns:
            next_patterns.append("smaller_embedded_form_factor")
        if "sensorization" in all_patterns or "ai_analysis" in all_patterns:
            next_patterns.append("self_measuring_autonomous_object")
        if "network_access" in all_patterns or "software_platform" in all_patterns:
            next_patterns.append("platform_native_service_layer")
        timelines.append(
            {
                "target_node": target,
                "root_node": dots[0]["from_id"] if dots else target,
                "root_year": min(years) if years else None,
                "current_year": max(years) if years else None,
                "dot_count": len(dots),
                "dots": dots,
                "dominant_transformation_patterns": recent_patterns,
                "why_it_happened_summary": (
                    "Each dot shows a capability compression: older physical/manual functions become portable, networked, software-defined, instrumented, and eventually predictive or autonomous."
                    if dots
                    else "No traceable dot chain found for target."
                ),
                "happening_now_assessment": (
                    "Active: the same pattern family is currently visible in AI, sensorization, platform convergence, and autonomy signals."
                    if {"ai_analysis", "prediction", "automation", "network_access", "software_platform"} & set(recent_patterns)
                    else "Watch: lineage exists, but current signal evidence should be strengthened before promotion."
                ),
                "likelihood_it_repeats": repeat_score,
                "likely_next_forms": next_patterns[:6],
            }
        )

    return {
        "schema_version": "claire.root_to_current_timeline.v1",
        "status": "ready" if timelines else "no_target_match",
        "query": str(query or ""),
        "intent": "Start at a current object or market signal, trace back to its root, then explain every relevant dot forward into the likely next transformation.",
        "timelines": timelines,
        "operator_question": "What old thing is this current thing becoming next, and which old failure conditions are now becoming ready?",
    }


def build_predictive_trend_engine(lineage: dict[str, Any], query: str | None = "") -> dict[str, Any]:
    edges = lineage.get("edges", []) if isinstance(lineage.get("edges"), list) else []
    terms = query_terms(query)
    pattern_counts: Counter[str] = Counter()
    family_counts: Counter[str] = Counter()
    recent_pattern_counts: Counter[str] = Counter()
    convergence_targets: Counter[str] = Counter()
    for edge in edges:
        if not isinstance(edge, dict):
            continue
        family = str(edge.get("family") or "uncategorized")
        family_counts[family] += 1
        convergence_targets[str(edge.get("to_id"))] += 1
        patterns = edge.get("transformation_pattern", [])
        if isinstance(patterns, list):
            pattern_counts.update(str(item) for item in patterns)
            if int(edge.get("approx_to_year") or 0) >= 2000:
                recent_pattern_counts.update(str(item) for item in patterns)

    pattern_priorities = []
    for pattern, count in pattern_counts.most_common(24):
        recent = recent_pattern_counts.get(pattern, 0)
        pattern_priorities.append(
            {
                "pattern": pattern,
                "historical_count": count,
                "recent_count": recent,
                "predictive_weight": round((count * 0.55) + (recent * 0.45), 3),
            }
        )

    query_matches = []
    for edge in edges:
        if not isinstance(edge, dict) or not terms:
            continue
        haystack = " ".join(
            str(value)
            for value in [
                edge.get("family"),
                edge.get("from_id"),
                edge.get("to_id"),
                edge.get("relationship"),
                edge.get("logic_shift"),
                " ".join(edge.get("capability_delta", [])) if isinstance(edge.get("capability_delta"), list) else "",
                " ".join(edge.get("transformation_pattern", [])) if isinstance(edge.get("transformation_pattern"), list) else "",
            ]
        ).lower()
        hits = sorted(term for term in terms if term in haystack)
        if hits:
            query_matches.append(
                {
                    "edge": f"{edge.get('from_id')}->{edge.get('to_id')}",
                    "family": edge.get("family"),
                    "hits": hits,
                    "patterns": edge.get("transformation_pattern", []),
                    "logic_shift": edge.get("logic_shift"),
                }
            )

    hypotheses = [
        {
            "hypothesis": "Objects with repeated manual use tend to become instrumented, software-controlled, and then partially autonomous.",
            "signals_to_watch": ["sensorization", "software_control", "automation", "ai_analysis", "feedback_loop"],
            "source_patterns": [
                item["pattern"]
                for item in pattern_priorities
                if item["pattern"] in {"sensorization", "software_control", "automation", "ai_analysis", "feedback_loop"}
            ],
        },
        {
            "hypothesis": "Single-purpose devices tend to converge into software platforms when screen, battery, compute, and network layers become cheap enough.",
            "signals_to_watch": ["miniaturization", "battery_power", "network_access", "software_platform", "convergence"],
            "source_patterns": [
                item["pattern"]
                for item in pattern_priorities
                if item["pattern"] in {"miniaturization", "battery_power", "network_access", "software_platform", "convergence"}
            ],
        },
        {
            "hypothesis": "Fields that digitize records later gain search, workflow integration, decision support, and predictive AI.",
            "signals_to_watch": ["digitization", "searchability", "workflow_integration", "decision_support", "prediction"],
            "source_patterns": [
                item["pattern"]
                for item in pattern_priorities
                if item["pattern"] in {"digitization", "searchability", "workflow_integration", "decision_support", "prediction"}
            ],
        },
        {
            "hypothesis": "Infrastructure with live measurement tends to become optimized, distributed, and eventually orchestrated by AI.",
            "signals_to_watch": ["sensorization", "edge_distribution", "optimization", "prediction", "distributed_control"],
            "source_patterns": [
                item["pattern"]
                for item in pattern_priorities
                if item["pattern"] in {"sensorization", "edge_distribution", "optimization", "prediction", "distributed_control"}
            ],
        },
    ]
    return {
        "schema_version": "claire.predictive_trend_engine.v1",
        "status": "ready",
        "query": str(query or ""),
        "basis": "ACS2 transformation graph pattern frequencies, recent pattern recurrence, convergence points, and family analogies.",
        "prediction_readiness": "foundation_ready_for_operator_review",
        "pattern_priorities": sorted(pattern_priorities, key=lambda item: item["predictive_weight"], reverse=True),
        "top_families": [{"family": family, "edge_count": count} for family, count in family_counts.most_common(20)],
        "convergence_targets": [
            {"node_id": node_id, "incoming_edges": count}
            for node_id, count in convergence_targets.most_common(12)
            if count >= 2
        ],
        "query_matched_analogies": query_matches[:12],
        "predictive_hypotheses": hypotheses,
        "safety_note": "This is a pattern engine for trend spotting, not autonomous truth promotion. Live evidence must still validate predictions.",
    }


def is_currently_buildable(record: dict[str, Any]) -> bool:
    return (
        int(record.get("readiness_level", 0) or 0) >= 6
        and "future" not in str(record.get("maturity", "")).lower()
        and str(record.get("manufacturability")) != "not_currently_manufacturable"
    )


def score_record(record: dict[str, Any], query: str | None) -> float:
    terms = query_terms(query)
    haystack = " ".join(
        str(value)
        for value in [
            record.get("id"),
            record.get("name"),
            record.get("era"),
            record.get("section"),
            " ".join(record.get("domains", [])),
            " ".join(record.get("capabilities", [])),
            " ".join(record.get("gap_fit", [])),
            " ".join(record.get("acquirer_fit", [])),
            " ".join(record.get("evidence_basis", [])),
        ]
    ).lower()
    readiness = float(record.get("readiness_level", 0) or 0) / 10
    current_bonus = 0.08 if is_currently_buildable(record) else -0.08
    if not terms:
        return round(max(0.0, min(1.0, readiness + current_bonus)), 3)
    hits = sum(1 for term in terms if term in haystack)
    phrase_bonus = 0.12 if str(query or "").lower() in haystack else 0.0
    return round(max(0.0, min(1.0, hits / max(1, len(terms)) * 0.68 + readiness * 0.24 + current_bonus + phrase_bonus)), 3)


def synthesize_innovation_candidates(query: str | None, records: list[dict[str, Any]], limit: int = 6) -> list[dict[str, Any]]:
    terms = query_terms(query)
    current = [record for record in records if is_currently_buildable(record)]

    def has_any(record: dict[str, Any], values: set[str]) -> bool:
        text = " ".join(
            [
                str(record.get("name", "")),
                " ".join(record.get("domains", [])),
                " ".join(record.get("capabilities", [])),
                " ".join(record.get("gap_fit", [])),
            ]
        ).lower()
        return any(value in text for value in values)

    groups = {
        "reasoning": [r for r in current if has_any(r, {"reasoning", "ai", "transformer", "prediction"})],
        "knowledge": [r for r in current if has_any(r, {"knowledge", "retrieval", "search", "relationship", "database"})],
        "validation": [r for r in current if has_any(r, {"simulation", "prototype", "manufacturing", "validation", "performance"})],
        "governance": [r for r in current if has_any(r, {"governance", "safety", "risk", "compliance", "control"})],
        "network": [r for r in current if has_any(r, {"internet", "network", "web", "distributed", "repository"})],
    }
    blueprints = [
        (
            "buildable_autonomous_invention_intake_engine",
            "Buildable Autonomous Invention Intake Engine",
            ["reasoning", "knowledge", "governance"],
            "Software system that turns local/uploaded technical sources into governed discovery candidates, then routes them through validation and dashboard review.",
        ),
        (
            "manufacturability_precheck_design_portal",
            "Manufacturability Precheck Design Portal",
            ["reasoning", "validation", "governance"],
            "Design portal that combines technology matching, simulation/digital-twin style validation, and safety gates before a breakthrough is treated as buildable.",
        ),
        (
            "patent_mining_gap_discovery_layer",
            "Patent-Mining Gap Discovery Layer",
            ["knowledge", "network", "reasoning"],
            "Metadata-first discovery layer for patents, standards, repositories, and local source packs that identifies buildable gaps without uncontrolled web ingestion.",
        ),
        (
            "recursive_evidence_learning_database",
            "Recursive Evidence Learning Database",
            ["knowledge", "governance", "validation"],
            "Validated memory layer that feeds only proven outputs back into future technology scans and route scoring.",
        ),
    ]
    candidates: list[dict[str, Any]] = []
    for candidate_id, title, required, thesis in blueprints:
        components: list[dict[str, Any]] = []
        used_ids: set[str] = set()
        for key in required:
            for record in groups.get(key, []):
                record_id = str(record.get("id") or "")
                if record_id and record_id not in used_ids:
                    components.append(record)
                    used_ids.add(record_id)
                    break
        if len(components) < 2:
            continue
        component_score = sum(float(item.get("readiness_level", 0) or 0) for item in components) / (len(components) * 10)
        query_bonus = 0.08 if terms and any(term in title.lower() or term in thesis.lower() for term in terms) else 0.0
        buildability_score = round(min(0.95, component_score + 0.08 + query_bonus), 3)
        manufacturability_score = round(min(0.93, component_score + 0.05), 3)
        breakthrough_score = round((buildability_score * 0.42) + (manufacturability_score * 0.28) + (len(required) / 5 * 0.30), 3)
        candidates.append(
            {
                "candidate_id": candidate_id,
                "title": title,
                "candidate_type": "discovery_breakthrough_candidate" if breakthrough_score >= 0.72 else "discovery_candidate",
                "innovation_type": "applied_intelligence_breakthrough",
                "status": "buildable_now_review_required",
                "route_recommendation": "breakthrough_design" if breakthrough_score >= 0.78 else "portfolio_creation_optimization",
                "breakthrough_score": breakthrough_score,
                "buildability_score": buildability_score,
                "manufacturability_score": manufacturability_score,
                "thesis": thesis,
                "component_records": [item["id"] for item in components],
                "component_names": [item["name"] for item in components],
                "evidence_basis": [
                    "ACS2 discovery-analysis-synthesis-validation loop",
                    "Timeline-derived current technology records",
                    "Seeded Claire runtime/governance technology records",
                ],
                "blocked_actions": [
                    "no autonomous runtime mutation",
                    "no live body ingestion without review",
                    "no breakthrough promotion without validation",
                ],
            }
        )
    candidates.sort(key=lambda item: (item["breakthrough_score"], item["buildability_score"]), reverse=True)
    return candidates[: max(1, min(limit, 12))]


def build_technology_database(query: str | None = "") -> dict[str, Any]:
    records = generated_technology_records()
    current_records = [item for item in records if is_currently_buildable(item)]
    speculative_records = [item for item in records if not is_currently_buildable(item)]
    candidates = synthesize_innovation_candidates(query, records)
    lineage = build_technology_lineage(records)
    trend_math = build_historical_trend_math(lineage)
    transformation_diagram = build_acs2_transformation_diagram(lineage)
    root_timeline = build_root_to_current_timeline(lineage, query)
    predictive_engine = build_predictive_trend_engine(lineage, query)
    reemergence_engine = build_reemergence_pattern_engine(
        query,
        {
            "timeline": [*predictive_engine.get("query_matched_analogies", []), root_timeline],
            "categories": transformation_diagram.get("family_views", []),
            "signals": predictive_engine.get("pattern_priorities", []),
        },
    )
    return {
        "schema_version": VERSION,
        "status": "ready",
        "generated_at": utc_now(),
        "query": str(query or ""),
        "source": "local_generated_technology_database",
        "source_root": str(technology_source_root() or ""),
        "viewpoint_contract": {
            "source_of_truth": "operator_supplied_technology_database_and_timeline_docs",
            "interpretation_layer": "generated_local_technology_database",
            "candidate_layer": "discovery_breakthrough_candidate_synthesis",
            "route_handoff": "governed_pipeline_after_review",
            "runtime_output_echo_allowed": False,
            "latest_run_output_primary_source": False,
        },
        "evidence_sources": configured_evidence_sources(),
        "record_count": len(records),
        "current_buildable_count": len(current_records),
        "speculative_or_future_count": len(speculative_records),
        "records": records,
        "technology_lineage": lineage,
        "historical_trend_math": trend_math,
        "acs2_transformation_diagram": transformation_diagram,
        "root_to_current_timeline": root_timeline,
        "predictive_trend_engine": predictive_engine,
        "reemergence_pattern_engine": reemergence_engine,
        "innovation_candidates": candidates,
        "authority": {
            "network_request_performed": False,
            "body_read_performed": False,
            "runtime_truth_mutation": False,
            "manual_promotion_required": True,
        },
    }


def search_technology_base(query: str | None, limit: int = 8) -> dict[str, Any]:
    database = build_technology_database(query)
    scored = [{**record, "match_score": score_record(record, query)} for record in database["records"]]
    scored.sort(key=lambda item: (item["match_score"], is_currently_buildable(item), item.get("readiness_level", 0)), reverse=True)
    filtered = [item for item in scored if item["match_score"] > 0.12 and is_currently_buildable(item)]
    if not filtered:
        filtered = [item for item in scored if item["match_score"] > 0.12]
    filtered = filtered[: max(1, min(limit, 50))]
    return {
        "schema_version": VERSION,
        "status": "ready",
        "generated_at": utc_now(),
        "query": str(query or ""),
        "source": database["source"],
        "source_root": database["source_root"],
        "record_count": database["record_count"],
        "current_buildable_count": database["current_buildable_count"],
        "speculative_or_future_count": database["speculative_or_future_count"],
        "viewpoint_contract": database["viewpoint_contract"],
        "result_count": len(filtered),
        "results": filtered,
        "technology_lineage": database["technology_lineage"],
        "historical_trend_math": database["historical_trend_math"],
        "acs2_transformation_diagram": database["acs2_transformation_diagram"],
        "root_to_current_timeline": database["root_to_current_timeline"],
        "predictive_trend_engine": database["predictive_trend_engine"],
        "reemergence_pattern_engine": database["reemergence_pattern_engine"],
        "innovation_candidates": database["innovation_candidates"],
        "evidence_sources": database["evidence_sources"],
        "authority": database["authority"],
    }


def assess_technology_base(query: str | None = "") -> dict[str, Any]:
    search = search_technology_base(query, limit=12)
    results = search["results"]
    candidates = search["innovation_candidates"]
    readiness = round(sum(float(item.get("readiness_level", 0) or 0) for item in results) / max(1, len(results)), 2)
    deployable = [item for item in results if "deployable" in str(item.get("manufacturability", ""))]
    manufacturable = [item for item in results if item.get("manufacturability") not in {"science_fiction", "not_currently_manufacturable"}]
    breakthrough_ready = [item for item in candidates if float(item.get("breakthrough_score", 0) or 0) >= 0.72]
    lineage = search.get("technology_lineage", {})
    trend_math = search.get("historical_trend_math", {})
    transformation_diagram = search.get("acs2_transformation_diagram", {})
    root_timeline = search.get("root_to_current_timeline", {})
    predictive_engine = search.get("predictive_trend_engine", {})
    reemergence_engine = search.get("reemergence_pattern_engine", {})
    return {
        "schema_version": VERSION,
        "status": "operational",
        "generated_at": utc_now(),
        "query": str(query or ""),
        "technology_search": search,
        "technology_lineage": lineage,
        "historical_trend_math": trend_math,
        "acs2_transformation_diagram": transformation_diagram,
        "root_to_current_timeline": root_timeline,
        "predictive_trend_engine": predictive_engine,
        "reemergence_pattern_engine": reemergence_engine,
        "innovation_candidates": candidates,
        "viewpoint_contract": search.get("viewpoint_contract", {}),
        "readiness": {
            "average_readiness_level": readiness,
            "current_technology_grounded": True,
            "science_fiction_filtered": True,
            "buildability_basis": "local timeline data, ACS2 loop model, seeded Claire technology records, deployability, manufacturability, and governed evidence promotion",
        },
        "counts": {
            "records": search["record_count"],
            "current_buildable_records": search["current_buildable_count"],
            "speculative_or_future_records": search["speculative_or_future_count"],
            "deployable_matches": len(deployable),
            "manufacturable_matches": len(manufacturable),
            "innovation_candidates": len(candidates),
            "breakthrough_ready_candidates": len(breakthrough_ready),
            "evidence_sources": len(search["evidence_sources"]),
            "acquirer_categories": len({fit for item in results for fit in item.get("acquirer_fit", [])}),
            "lineage_edges": lineage.get("lineage_depth", 0) if isinstance(lineage, dict) else 0,
            "lineage_families": lineage.get("family_count", 0) if isinstance(lineage, dict) else 0,
            "predictive_patterns": len(predictive_engine.get("pattern_priorities", [])) if isinstance(predictive_engine, dict) else 0,
            "reemergence_patterns": reemergence_engine.get("pattern_count", 0) if isinstance(reemergence_engine, dict) else 0,
            "signal_families": reemergence_engine.get("signal_family_count", 0) if isinstance(reemergence_engine, dict) else 0,
            "root_to_current_timelines": len(root_timeline.get("timelines", [])) if isinstance(root_timeline, dict) else 0,
        },
        "reasoning_capabilities": {
            "beginning_to_end_lineage": bool(lineage.get("edges")) if isinstance(lineage, dict) else False,
            "what_became_what_logic": True,
            "historical_linear_spine": trend_math.get("status") == "ready" if isinstance(trend_math, dict) else False,
            "singularity_math_scaffold": trend_math.get("singularity_math_ready") is True if isinstance(trend_math, dict) else False,
            "acs2_transformation_diagram": transformation_diagram.get("status") == "ready" if isinstance(transformation_diagram, dict) else False,
            "root_to_current_timeline": root_timeline.get("status") == "ready" if isinstance(root_timeline, dict) else False,
            "cross_family_analogy_reasoning": bool(transformation_diagram.get("convergence_points")) if isinstance(transformation_diagram, dict) else False,
            "predictive_trend_engine": predictive_engine.get("status") == "ready" if isinstance(predictive_engine, dict) else False,
            "reemergence_pattern_classification": reemergence_engine.get("status") == "ready" if isinstance(reemergence_engine, dict) else False,
            "signal_family_readiness_scoring": reemergence_engine.get("signal_family_count") == 7 if isinstance(reemergence_engine, dict) else False,
            "cycle_stage_detection": bool(reemergence_engine.get("cycle_stage")) if isinstance(reemergence_engine, dict) else False,
        },
        "next_pipeline_bindings": [
            "knowledge_ingestion",
            "technology_intelligence",
            "signal_family_scoring",
            "reemergence_pattern_classification",
            "technical_feasibility",
            "system_design",
            "portfolio_optimization",
            "breakthrough_design",
            "acquirer_matching",
            "recursive_learning_after_validation",
        ],
    }
