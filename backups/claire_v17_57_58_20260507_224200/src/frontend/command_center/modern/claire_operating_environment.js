
/* Claire Syntalion v17.56 — Operating Environment Redesign Foundation */
/* This file renders architecture truth and runtime truth. It does not generate fake run results. */

const CLAIRE_BUILD = {"version": "v17.56", "name": "Claire Operating Environment Redesign Foundation"};
const FALLBACK_ARCHITECTURE_MAP = {
  "version": "v17.56",
  "source_reference": "(7)Claire-Complete-Systems-Flow HTML",
  "build_name": "Claire Operating Environment Redesign Foundation",
  "principle": "The dashboard is the Claire operating environment, not a dev dashboard.",
  "sections": [
    {
      "id": "command",
      "label": "Command",
      "html_reference": "Master Header",
      "purpose": "Launch, inspect, and govern live/local Claire runs."
    },
    {
      "id": "sources",
      "label": "Sources",
      "html_reference": "External Data Sources",
      "purpose": "Display configured source domains, trust state, freshness, and intake readiness."
    },
    {
      "id": "acs2",
      "label": "ACS2 Loops",
      "html_reference": "ACS2 Intelligence Loops",
      "purpose": "Show the external sensing loops that feed governed signals into the lifecycle."
    },
    {
      "id": "governance",
      "label": "Signal Governance",
      "html_reference": "Signal Governance",
      "purpose": "Render stages 1-5 and the governance stamp."
    },
    {
      "id": "entity",
      "label": "Entity Intelligence",
      "html_reference": "Entity Intelligence",
      "purpose": "Render stages 6-7, entities, and relationship mapping."
    },
    {
      "id": "trend",
      "label": "Trend Discovery",
      "html_reference": "Trend Discovery",
      "purpose": "Render stages 8-10, thesis formation, clusters, and route gate inputs."
    },
    {
      "id": "route-gate",
      "label": "Route Gate",
      "html_reference": "Route Branches",
      "purpose": "Show selected route, rejected routes, confidence, and reasons."
    },
    {
      "id": "portfolio",
      "label": "Portfolio",
      "html_reference": "Route Branches / Portfolio Route",
      "purpose": "Render market positioning, competitor analysis, and portfolio creation or optimization."
    },
    {
      "id": "breakthrough",
      "label": "Breakthrough",
      "html_reference": "Route Branches / Breakthrough Route",
      "purpose": "Render gap detection, discovery generation, breakthrough classification, and advancement path."
    },
    {
      "id": "autodesign",
      "label": "AutoDesign",
      "html_reference": "Stages 16-22 / Auto Invention & Design Pipeline",
      "purpose": "Expose stages 16-22 as first-class route execution."
    },
    {
      "id": "technology",
      "label": "Technology Intelligence",
      "html_reference": "Technology Intelligence",
      "purpose": "Support design/software/system routes with catalog, matching, dependencies, and buildability context."
    },
    {
      "id": "acquisition",
      "label": "Acquisition",
      "html_reference": "Acquisition Route",
      "purpose": "Render moat, business model, acquirer identification, fit, and final package readiness."
    },
    {
      "id": "validation",
      "label": "Validation",
      "html_reference": "Output & Validation",
      "purpose": "Make validation the final authority for any output."
    },
    {
      "id": "evidence",
      "label": "Evidence",
      "html_reference": "Output & Validation / Lifecycle Contracts",
      "purpose": "Provide evidence chain, traceability, contract compliance, and proof readiness."
    },
    {
      "id": "memory",
      "label": "Memory",
      "html_reference": "Memory & Recursion",
      "purpose": "Show verified memory eligibility and recursive feedback only after validation pass."
    },
    {
      "id": "runtime",
      "label": "Runtime",
      "html_reference": "Runtime Infrastructure / Implementation Status",
      "purpose": "Show runtime health, protected spine, isolation, launch continuity, and rollback state."
    },
    {
      "id": "update-packs",
      "label": "Update Packs",
      "html_reference": "Forward Roadmap",
      "purpose": "Draft dashboard and system update packs from architecture-map gaps."
    }
  ],
  "non_negotiables": [
    "No fake runtime data.",
    "No random UI feature expansion.",
    "Stages 16-22 remain a dedicated route surface.",
    "Dashboard renders runtime truth from output artifacts when available.",
    "Validation is the final authority.",
    "Only validated outputs can be marked memory eligible.",
    "Rollback safety is preserved before replacing files."
  ]
};
const FALLBACK_STAGE_REGISTRY = {
  "version": "v17.56",
  "canonical_stage_count": 30,
  "stages": [
    {
      "stage": 1,
      "name": "Signal Ingestion",
      "group": "Signal Governance",
      "dashboard_surface": "governance",
      "required_state": [
        "completed",
        "skipped_by_route",
        "blocked",
        "failed"
      ],
      "requires_evidence": true,
      "route_notes": "Always execute before route gate."
    },
    {
      "stage": 2,
      "name": "Signal Normalization",
      "group": "Signal Governance",
      "dashboard_surface": "governance",
      "required_state": [
        "completed",
        "skipped_by_route",
        "blocked",
        "failed"
      ],
      "requires_evidence": true,
      "route_notes": "Always execute before route gate."
    },
    {
      "stage": 3,
      "name": "Source Validation & Weighting",
      "group": "Signal Governance",
      "dashboard_surface": "governance",
      "required_state": [
        "completed",
        "skipped_by_route",
        "blocked",
        "failed"
      ],
      "requires_evidence": true,
      "route_notes": "Always execute before route gate."
    },
    {
      "stage": 4,
      "name": "Context Expansion",
      "group": "Signal Governance",
      "dashboard_surface": "governance",
      "required_state": [
        "completed",
        "skipped_by_route",
        "blocked",
        "failed"
      ],
      "requires_evidence": true,
      "route_notes": "Always execute before route gate."
    },
    {
      "stage": 5,
      "name": "Signal Consolidation",
      "group": "Signal Governance",
      "dashboard_surface": "governance",
      "required_state": [
        "completed",
        "skipped_by_route",
        "blocked",
        "failed"
      ],
      "requires_evidence": true,
      "route_notes": "Always execute before route gate."
    },
    {
      "stage": 6,
      "name": "Entity Extraction",
      "group": "Entity Intelligence",
      "dashboard_surface": "entity",
      "required_state": [
        "completed",
        "skipped_by_route",
        "blocked",
        "failed"
      ],
      "requires_evidence": true,
      "route_notes": "Always execute before route gate."
    },
    {
      "stage": 7,
      "name": "Relationship Mapping",
      "group": "Entity Intelligence",
      "dashboard_surface": "entity",
      "required_state": [
        "completed",
        "skipped_by_route",
        "blocked",
        "failed"
      ],
      "requires_evidence": true,
      "route_notes": "Always execute before route gate."
    },
    {
      "stage": 8,
      "name": "Trend Discovery",
      "group": "Trend Discovery / Route Gate",
      "dashboard_surface": "trend",
      "required_state": [
        "completed",
        "skipped_by_route",
        "blocked",
        "failed"
      ],
      "requires_evidence": true,
      "route_notes": "Always execute before route gate."
    },
    {
      "stage": 9,
      "name": "Cluster Formation",
      "group": "Trend Discovery / Route Gate",
      "dashboard_surface": "trend",
      "required_state": [
        "completed",
        "skipped_by_route",
        "blocked",
        "failed"
      ],
      "requires_evidence": true,
      "route_notes": "Always execute before route gate."
    },
    {
      "stage": 10,
      "name": "Insight / Thesis Structuring + Route Gate",
      "group": "Trend Discovery / Route Gate",
      "dashboard_surface": "trend",
      "required_state": [
        "completed",
        "skipped_by_route",
        "blocked",
        "failed"
      ],
      "requires_evidence": true,
      "route_notes": "Always execute before route gate."
    },
    {
      "stage": 11,
      "name": "Gap Detection",
      "group": "Breakthrough / Advancement Selection",
      "dashboard_surface": "breakthrough",
      "required_state": [
        "completed",
        "skipped_by_route",
        "blocked",
        "failed"
      ],
      "requires_evidence": true,
      "route_notes": "Breakthrough/design route only unless route contract explicitly requires it."
    },
    {
      "stage": 12,
      "name": "Gap Qualification",
      "group": "Breakthrough / Advancement Selection",
      "dashboard_surface": "breakthrough",
      "required_state": [
        "completed",
        "skipped_by_route",
        "blocked",
        "failed"
      ],
      "requires_evidence": true,
      "route_notes": "Breakthrough/design route only unless route contract explicitly requires it."
    },
    {
      "stage": 13,
      "name": "Discovery Generation",
      "group": "Breakthrough / Advancement Selection",
      "dashboard_surface": "breakthrough",
      "required_state": [
        "completed",
        "skipped_by_route",
        "blocked",
        "failed"
      ],
      "requires_evidence": true,
      "route_notes": "Breakthrough/design route only unless route contract explicitly requires it."
    },
    {
      "stage": 14,
      "name": "Breakthrough Identification / Classification",
      "group": "Breakthrough / Advancement Selection",
      "dashboard_surface": "breakthrough",
      "required_state": [
        "completed",
        "skipped_by_route",
        "blocked",
        "failed"
      ],
      "requires_evidence": true,
      "route_notes": "Breakthrough/design route only unless route contract explicitly requires it."
    },
    {
      "stage": 15,
      "name": "Advancement Path Selection",
      "group": "Breakthrough / Advancement Selection",
      "dashboard_surface": "breakthrough",
      "required_state": [
        "completed",
        "skipped_by_route",
        "blocked",
        "failed"
      ],
      "requires_evidence": true,
      "route_notes": "Breakthrough/design route only unless route contract explicitly requires it."
    },
    {
      "stage": 16,
      "name": "Auto Invention / Solution Generation",
      "group": "AutoDesign / Design Portal",
      "dashboard_surface": "autodesign",
      "required_state": [
        "completed",
        "skipped_by_route",
        "blocked",
        "failed"
      ],
      "requires_evidence": true,
      "route_notes": "Breakthrough/design route only unless route contract explicitly requires it."
    },
    {
      "stage": 17,
      "name": "Solution Structuring",
      "group": "AutoDesign / Design Portal",
      "dashboard_surface": "autodesign",
      "required_state": [
        "completed",
        "skipped_by_route",
        "blocked",
        "failed"
      ],
      "requires_evidence": true,
      "route_notes": "Breakthrough/design route only unless route contract explicitly requires it."
    },
    {
      "stage": 18,
      "name": "Buildability Assessment",
      "group": "AutoDesign / Design Portal",
      "dashboard_surface": "autodesign",
      "required_state": [
        "completed",
        "skipped_by_route",
        "blocked",
        "failed"
      ],
      "requires_evidence": true,
      "route_notes": "Breakthrough/design route only unless route contract explicitly requires it."
    },
    {
      "stage": 19,
      "name": "Viability Assessment",
      "group": "AutoDesign / Design Portal",
      "dashboard_surface": "autodesign",
      "required_state": [
        "completed",
        "skipped_by_route",
        "blocked",
        "failed"
      ],
      "requires_evidence": true,
      "route_notes": "Breakthrough/design route only unless route contract explicitly requires it."
    },
    {
      "stage": 20,
      "name": "Manufacturability / Deployability Assessment",
      "group": "AutoDesign / Design Portal",
      "dashboard_surface": "autodesign",
      "required_state": [
        "completed",
        "skipped_by_route",
        "blocked",
        "failed"
      ],
      "requires_evidence": true,
      "route_notes": "Breakthrough/design route only unless route contract explicitly requires it."
    },
    {
      "stage": 21,
      "name": "Feasibility Validation",
      "group": "AutoDesign / Design Portal",
      "dashboard_surface": "autodesign",
      "required_state": [
        "completed",
        "skipped_by_route",
        "blocked",
        "failed"
      ],
      "requires_evidence": true,
      "route_notes": "Breakthrough/design route only unless route contract explicitly requires it."
    },
    {
      "stage": 22,
      "name": "Design Portal Output / Blueprints / Specs",
      "group": "AutoDesign / Design Portal",
      "dashboard_surface": "autodesign",
      "required_state": [
        "completed",
        "skipped_by_route",
        "blocked",
        "failed"
      ],
      "requires_evidence": true,
      "route_notes": "Breakthrough/design route only unless route contract explicitly requires it."
    },
    {
      "stage": 23,
      "name": "Market Positioning",
      "group": "Strategy / Portfolio / Acquisition",
      "dashboard_surface": "portfolio",
      "required_state": [
        "completed",
        "skipped_by_route",
        "blocked",
        "failed"
      ],
      "requires_evidence": true,
      "route_notes": "Route-specific strategy, portfolio, or acquisition execution."
    },
    {
      "stage": 24,
      "name": "Moat & Differentiation",
      "group": "Strategy / Portfolio / Acquisition",
      "dashboard_surface": "acquisition",
      "required_state": [
        "completed",
        "skipped_by_route",
        "blocked",
        "failed"
      ],
      "requires_evidence": true,
      "route_notes": "Route-specific strategy, portfolio, or acquisition execution."
    },
    {
      "stage": 25,
      "name": "Business Model & Value Capture",
      "group": "Strategy / Portfolio / Acquisition",
      "dashboard_surface": "acquisition",
      "required_state": [
        "completed",
        "skipped_by_route",
        "blocked",
        "failed"
      ],
      "requires_evidence": true,
      "route_notes": "Route-specific strategy, portfolio, or acquisition execution."
    },
    {
      "stage": 26,
      "name": "Competitor Analysis",
      "group": "Strategy / Portfolio / Acquisition",
      "dashboard_surface": "portfolio",
      "required_state": [
        "completed",
        "skipped_by_route",
        "blocked",
        "failed"
      ],
      "requires_evidence": true,
      "route_notes": "Route-specific strategy, portfolio, or acquisition execution."
    },
    {
      "stage": 27,
      "name": "Portfolio Creation / Optimization",
      "group": "Strategy / Portfolio / Acquisition",
      "dashboard_surface": "portfolio",
      "required_state": [
        "completed",
        "skipped_by_route",
        "blocked",
        "failed"
      ],
      "requires_evidence": true,
      "route_notes": "Route-specific strategy, portfolio, or acquisition execution."
    },
    {
      "stage": 28,
      "name": "Acquirer Identification",
      "group": "Strategy / Portfolio / Acquisition",
      "dashboard_surface": "acquisition",
      "required_state": [
        "completed",
        "skipped_by_route",
        "blocked",
        "failed"
      ],
      "requires_evidence": true,
      "route_notes": "Route-specific strategy, portfolio, or acquisition execution."
    },
    {
      "stage": 29,
      "name": "Acquisition Fit & Rationale",
      "group": "Strategy / Portfolio / Acquisition",
      "dashboard_surface": "acquisition",
      "required_state": [
        "completed",
        "skipped_by_route",
        "blocked",
        "failed"
      ],
      "requires_evidence": true,
      "route_notes": "Route-specific strategy, portfolio, or acquisition execution."
    },
    {
      "stage": 30,
      "name": "Final Package Construction",
      "group": "Strategy / Portfolio / Acquisition",
      "dashboard_surface": "acquisition",
      "required_state": [
        "completed",
        "skipped_by_route",
        "blocked",
        "failed"
      ],
      "requires_evidence": true,
      "route_notes": "Route-specific strategy, portfolio, or acquisition execution."
    }
  ]
};
const FALLBACK_ROUTE_REGISTRY = {
  "version": "v17.56",
  "routes": {
    "portfolio": {
      "label": "Portfolio Route",
      "default_when": "Signals form a viable market/thesis or optimization action without qualifying for breakthrough/design escalation.",
      "required_stages": [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        23,
        26,
        27
      ],
      "optional_stages": [
        24,
        25
      ],
      "terminal_states": [
        "portfolio_action_ready",
        "portfolio_optimization_ready",
        "insufficient_data",
        "blocked",
        "failed"
      ],
      "dashboard_surface": "portfolio"
    },
    "breakthrough": {
      "label": "Breakthrough / AutoDesign Route",
      "default_when": "A qualified gap or non-obvious structural advancement is detected and advancement path selection requires solution/design execution.",
      "required_stages": [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18,
        19,
        20,
        21,
        22
      ],
      "optional_stages": [
        23,
        24,
        25,
        26,
        28,
        29,
        30
      ],
      "terminal_states": [
        "breakthrough_classified",
        "advancement_path_selected",
        "design_output_ready",
        "final_package_ready",
        "insufficient_data",
        "blocked",
        "failed"
      ],
      "dashboard_surface": "breakthrough/autodesign"
    },
    "acquisition": {
      "label": "Acquisition Route",
      "default_when": "The run has enough strategy, moat, target, and fit evidence to prepare acquisition-facing rationale or package.",
      "required_stages": [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        24,
        25,
        28,
        29,
        30
      ],
      "optional_stages": [
        23,
        26,
        27
      ],
      "terminal_states": [
        "acquisition_ready",
        "final_package_ready",
        "insufficient_data",
        "blocked",
        "failed"
      ],
      "dashboard_surface": "acquisition"
    },
    "research_discovery": {
      "label": "Discovery / Research Route",
      "default_when": "The system has enough governed signals to produce a discovery or thesis but not enough to route into portfolio, design, or acquisition execution.",
      "required_stages": [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13
      ],
      "optional_stages": [],
      "terminal_states": [
        "discovery_ready",
        "insufficient_data",
        "blocked",
        "failed"
      ],
      "dashboard_surface": "trend/breakthrough"
    }
  }
};
const FALLBACK_RUNTIME_SURFACE_REGISTRY = {
  "version": "v17.56",
  "runtime_inputs": [
    "exports/index.json",
    "exports/latest/core_run_output.json",
    "output/core_run_output.json",
    "core_run_output.json"
  ],
  "required_runtime_fields": [
    "run_id",
    "timestamp",
    "route_selected",
    "route_decision",
    "stages_completed",
    "stages_skipped",
    "evidence_chain",
    "confidence_scores",
    "governance_stamp",
    "terminal_state",
    "validation_result",
    "validated_output_path",
    "memory_eligibility"
  ],
  "surface_field_map": {
    "command": [
      "run_id",
      "mode",
      "terminal_state",
      "validation_result"
    ],
    "sources": [
      "sources",
      "source_validation",
      "governance_stamp"
    ],
    "acs2": [
      "aie_loops",
      "acs2_loops",
      "live_intelligence_feed"
    ],
    "governance": [
      "core_lifecycle_stages",
      "source_validation",
      "normalized_signals",
      "governance_stamp"
    ],
    "entity": [
      "entities",
      "relationships",
      "core_lifecycle_stages"
    ],
    "trend": [
      "trend_clusters",
      "thesis",
      "route_gate_inputs",
      "core_lifecycle_stages"
    ],
    "route-gate": [
      "route_selected",
      "route_decision",
      "routes_rejected",
      "route_confidence"
    ],
    "portfolio": [
      "market_positioning",
      "competitor_analysis",
      "portfolio_output",
      "portfolio_actions"
    ],
    "breakthrough": [
      "gap_detection",
      "gap_qualification",
      "discovery_generation",
      "breakthrough_classification",
      "advancement_path"
    ],
    "autodesign": [
      "stage_16_output",
      "stage_17_output",
      "stage_18_buildability",
      "stage_19_viability",
      "stage_20_deployability",
      "stage_21_feasibility",
      "stage_22_design_portal"
    ],
    "technology": [
      "technology_intelligence",
      "technology_catalog",
      "technology_matches",
      "dependency_notes"
    ],
    "acquisition": [
      "moat",
      "business_model",
      "acquirer_identification",
      "acquisition_fit",
      "final_package"
    ],
    "validation": [
      "validation_result",
      "validation_checks",
      "contract_compliance",
      "route_integrity",
      "confidence_thresholds"
    ],
    "evidence": [
      "evidence_chain",
      "source_traceability",
      "claim_traceability"
    ],
    "memory": [
      "memory_eligibility",
      "verified_memory_record",
      "recursive_feedback"
    ],
    "runtime": [
      "runtime_health",
      "protected_spine",
      "rollback_state",
      "launch_continuity"
    ],
    "update-packs": [
      "update_pack_plan",
      "architecture_gap_report"
    ]
  }
};
const FALLBACK_UPDATE_PACK_REGISTRY = {
  "version": "v17.56",
  "next_packs": [
    {
      "version": "v17.57",
      "name": "Architecture Navigation + Runtime Surface Registry",
      "purpose": "Harden architecture navigation and connect dashboard surfaces to runtime truth fields."
    },
    {
      "version": "v17.58",
      "name": "30-Stage Lifecycle Execution Workspace",
      "purpose": "Make the full lifecycle visible with per-stage statuses, evidence, and route-skip reasons."
    },
    {
      "version": "v17.59",
      "name": "Route Gate + Route Branch Pack",
      "purpose": "Render selected route, rejected routes, route confidence, and route execution panels."
    },
    {
      "version": "v17.60",
      "name": "AutoDesign + Stages 16-22 Design Portal Surface",
      "purpose": "Preserve and surface stages 16-22 as a first-class operating zone."
    },
    {
      "version": "v17.61",
      "name": "Validation Authority + Evidence Traceability",
      "purpose": "Make validation, evidence chain, and contract compliance the final proof layer."
    },
    {
      "version": "v17.62",
      "name": "Verified Memory + Recursive Feedback Surface",
      "purpose": "Allow only validated outputs to be memory eligible and recursively reused."
    },
    {
      "version": "v17.63",
      "name": "Dashboard/System Update Pack Generator",
      "purpose": "Generate dashboard and runtime release packs from architecture-map gaps."
    }
  ]
};

const state = {
  surface: "command",
  architecture: FALLBACK_ARCHITECTURE_MAP,
  stages: FALLBACK_STAGE_REGISTRY,
  routes: FALLBACK_ROUTE_REGISTRY,
  runtimeSurfaces: FALLBACK_RUNTIME_SURFACE_REGISTRY,
  updatePacks: FALLBACK_UPDATE_PACK_REGISTRY,
  runtime: null,
  runtimeSource: null,
  runtimeLoadError: null
};

const qs = (selector, root = document) => root.querySelector(selector);
const qsa = (selector, root = document) => Array.from(root.querySelectorAll(selector));

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function asArray(value) {
  if (!value) return [];
  if (Array.isArray(value)) return value;
  if (typeof value === "object") return Object.entries(value).map(([key, val]) => {
    if (val && typeof val === "object" && !Array.isArray(val)) return { id: key, ...val };
    return { id: key, value: val };
  });
  return [value];
}

function pick(...values) {
  for (const value of values) {
    if (value !== undefined && value !== null && value !== "") return value;
  }
  return null;
}

function stringifyBrief(value) {
  if (value === null || value === undefined || value === "") return "Not present in latest runtime output";
  if (typeof value === "string" || typeof value === "number" || typeof value === "boolean") return String(value);
  if (Array.isArray(value)) return value.length ? value.map(v => typeof v === "object" ? JSON.stringify(v) : String(v)).slice(0, 5).join(" • ") : "Empty";
  if (typeof value === "object") return Object.keys(value).length ? JSON.stringify(value, null, 2) : "Empty";
  return String(value);
}

function normalizeStatus(raw) {
  const value = String(raw || "").toLowerCase().replaceAll(" ", "_");
  if (["completed", "complete", "executed", "done", "passed", "success"].includes(value)) return "completed";
  if (["skipped", "skipped_by_route", "not_applicable", "not_applicable_by_route"].includes(value)) return "skipped_by_route";
  if (["blocked", "failed", "error", "validation_failed"].includes(value)) return value === "error" ? "failed" : value;
  return "pending";
}

function runtimeStages() {
  const rt = state.runtime || {};
  return pick(rt.core_lifecycle_stages, rt.lifecycle_stages, rt.stage_outputs, rt.stages, rt.core_lifecycle?.stages) || [];
}

function findRuntimeStage(stageNumber) {
  const stages = runtimeStages();
  if (Array.isArray(stages)) {
    return stages.find(item => Number(item.stage || item.stage_number || item.id || item.number) === Number(stageNumber)) || null;
  }
  if (typeof stages === "object") {
    return stages[String(stageNumber)] || stages[`stage_${stageNumber}`] || stages[`stage${stageNumber}`] || null;
  }
  return null;
}

function getStageStatus(stageNumber) {
  const rt = state.runtime || {};
  const stage = findRuntimeStage(stageNumber);
  if (stage) return normalizeStatus(stage.status || stage.state || stage.result || stage.completion_state);
  const completed = asArray(pick(rt.stages_completed, rt.completed_stages, rt.core_lifecycle?.stages_completed));
  const skipped = asArray(pick(rt.stages_skipped, rt.skipped_stages, rt.skipped_by_route, rt.core_lifecycle?.stages_skipped));
  const failed = asArray(pick(rt.stages_failed, rt.failed_stages));
  const blocked = asArray(pick(rt.stages_blocked, rt.blocked_stages));
  if (completed.some(x => Number(x.stage || x.stage_number || x.id || x) === Number(stageNumber))) return "completed";
  if (skipped.some(x => Number(x.stage || x.stage_number || x.id || x) === Number(stageNumber))) return "skipped_by_route";
  if (failed.some(x => Number(x.stage || x.stage_number || x.id || x) === Number(stageNumber))) return "failed";
  if (blocked.some(x => Number(x.stage || x.stage_number || x.id || x) === Number(stageNumber))) return "blocked";
  return state.runtime ? "pending" : "pending";
}

async function fetchJson(path) {
  const response = await fetch(path, { cache: "no-store" });
  if (!response.ok) throw new Error(`${path} returned ${response.status}`);
  return await response.json();
}

async function fetchFirstJson(paths) {
  const errors = [];
  for (const path of paths) {
    try {
      const data = await fetchJson(path);
      return { data, path };
    } catch (error) {
      errors.push(`${path}: ${error.message}`);
    }
  }
  throw new Error(errors.join(" | "));
}

async function loadRegistries() {
  const registryLoads = [
    ["architecture", "./dashboard_architecture_map.json", FALLBACK_ARCHITECTURE_MAP],
    ["stages", "./lifecycle_stage_registry.json", FALLBACK_STAGE_REGISTRY],
    ["routes", "./route_surface_registry.json", FALLBACK_ROUTE_REGISTRY],
    ["runtimeSurfaces", "./runtime_surface_registry.json", FALLBACK_RUNTIME_SURFACE_REGISTRY],
    ["updatePacks", "./update_pack_registry.json", FALLBACK_UPDATE_PACK_REGISTRY]
  ];
  await Promise.all(registryLoads.map(async ([key, path, fallback]) => {
    try { state[key] = await fetchJson(path); }
    catch { state[key] = fallback; }
  }));
}

async function loadRuntimeTruth() {
  const directCandidates = [
    "/exports/latest/core_run_output.json",
    "/output/core_run_output.json",
    "/core_run_output.json",
    "../../../exports/latest/core_run_output.json",
    "../../../../exports/latest/core_run_output.json",
    "../../../output/core_run_output.json",
    "../../../../output/core_run_output.json"
  ];

  try {
    const index = await fetchFirstJson(["/exports/index.json", "../../../exports/index.json", "../../../../exports/index.json"]);
    const runs = asArray(index.data.runs || index.data.items || index.data);
    const latest = runs[0] || null;
    const path = latest?.core_run_output_path || latest?.output_path || latest?.path || latest?.file;
    if (path) {
      const normalized = String(path).startsWith("/") ? path : "/" + String(path).replaceAll("\\", "/");
      const loaded = await fetchFirstJson([normalized, normalized.replace(/^\//, "../../../"), normalized.replace(/^\//, "../../../../")]);
      state.runtime = loaded.data;
      state.runtimeSource = loaded.path;
      state.runtimeLoadError = null;
      return;
    }
  } catch (error) {
    // Continue to direct candidates.
  }

  try {
    const loaded = await fetchFirstJson(directCandidates);
    state.runtime = loaded.data;
    state.runtimeSource = loaded.path;
    state.runtimeLoadError = null;
  } catch (error) {
    state.runtime = null;
    state.runtimeSource = null;
    state.runtimeLoadError = error.message;
  }
}

function renderNav() {
  const nav = qs("#main-nav");
  nav.innerHTML = state.architecture.sections.map((section, index) => `
    <button type="button" data-surface="${escapeHtml(section.id)}" class="${section.id === state.surface ? "active" : ""}">
      <span class="nav-num">${String(index + 1).padStart(2, "0")}</span>
      <span class="nav-label">${escapeHtml(section.label)}</span>
      <span class="nav-dot"></span>
    </button>
  `).join("");
  qsa("button[data-surface]", nav).forEach(button => {
    button.addEventListener("click", () => activateSurface(button.dataset.surface));
  });
}

function activateSurface(surfaceId) {
  state.surface = surfaceId;
  qsa(".surface").forEach(surface => surface.classList.remove("active"));
  const target = qs(`#surface-${CSS.escape(surfaceId)}`);
  if (target) target.classList.add("active");
  qsa("#main-nav button").forEach(button => button.classList.toggle("active", button.dataset.surface === surfaceId));
  const meta = state.architecture.sections.find(section => section.id === surfaceId) || state.architecture.sections[0];
  qs("#surface-kicker").textContent = meta.html_reference || meta.label;
  qs("#surface-title").textContent = meta.label;
  qs("#surface-description").textContent = meta.purpose;
}

function card(title, body, kicker = "") {
  return `<article class="card">${kicker ? `<div class="card-kicker">${escapeHtml(kicker)}</div>` : ""}<h4>${escapeHtml(title)}</h4>${body}</article>`;
}

function emptyRuntimeNote(surfaceName) {
  return `<div class="empty">No verified runtime output is currently loaded for ${escapeHtml(surfaceName)}. This is an honest no-data state, not sample data. Expected runtime sources: <span class="code-path">exports/latest/core_run_output.json</span>, <span class="code-path">output/core_run_output.json</span>, or <span class="code-path">exports/index.json</span>.</div>`;
}

function renderCommand() {
  const rt = state.runtime || {};
  const body = `
    <div class="grid-4">
      ${card("Run ID", `<div class="metric">${escapeHtml(pick(rt.run_id, rt.id, "None"))}</div><div class="metric-label">Latest loaded run</div>`, "Runtime")}
      ${card("Route", `<div class="metric">${escapeHtml(pick(rt.route_selected, rt.route, "None"))}</div><div class="metric-label">Selected route</div>`, "Route gate")}
      ${card("Terminal State", `<div class="metric">${escapeHtml(pick(rt.terminal_state, rt.status, "None"))}</div><div class="metric-label">Final outcome</div>`, "Proof")}
      ${card("Validation", `<div class="metric">${escapeHtml(pick(rt.validation_result?.status, rt.validation_result, rt.validation_status, "Unverified"))}</div><div class="metric-label">Final authority</div>`, "Validation")}
    </div>
    <div style="height:14px"></div>
    <div class="grid-2">
      ${card("Operating Model", `<p>Claire is rendered as a governed operating environment: sources → ACS2 loops → 30-stage lifecycle → route gate → route execution → validation → evidence → verified memory.</p><ul><li>No random UI expansion.</li><li>No fake run data.</li><li>Stages 16-22 remain first-class.</li></ul>`, "Architecture map")}
      ${card("Runtime Source", `<p>${state.runtimeSource ? `Loaded from <span class="code-path">${escapeHtml(state.runtimeSource)}</span>` : "No runtime output file was reachable from the dashboard context."}</p>${state.runtimeLoadError ? `<p>${escapeHtml(state.runtimeLoadError)}</p>` : ""}`, "Truth loading")}
    </div>
  `;
  qs("#surface-command").innerHTML = body;
}

function renderSources() {
  const rt = state.runtime || {};
  const sources = asArray(pick(rt.sources, rt.source_validation?.sources, rt.external_sources));
  const sourceNames = ["Market Data Feeds", "Company Intelligence", "Technology Sources", "News / Media", "Regulatory Sources", "Research Sources", "Existing Systems", "Internal Runtime Outputs"];
  const cards = sourceNames.map((name, index) => {
    const runtime = sources[index] || sources.find(s => String(s.name || s.id || "").toLowerCase().includes(name.toLowerCase().split(" ")[0])) || null;
    return card(name, `<p>${runtime ? escapeHtml(stringifyBrief(runtime)) : "Configured in the architecture map; runtime trust/freshness data will appear when source registry output is present."}</p>`, "Source lane");
  }).join("");
  qs("#surface-sources").innerHTML = `<div class="grid-4">${cards}</div>`;
}

function renderAcs2() {
  const rt = state.runtime || {};
  const loops = asArray(pick(rt.aie_loops, rt.acs2_loops, rt.intelligence_loops));
  const names = ["Discovery", "Analysis", "Synthesis", "Validation", "Regulatory", "Market", "Execution", "Decision"];
  qs("#surface-acs2").innerHTML = `<div class="grid-4">${names.map((name, index) => card(`${name} Loop`, `<p>${loops[index] ? escapeHtml(stringifyBrief(loops[index])) : "Loop surface reserved for live sensing output and lifecycle handoff proof."}</p>`, "ACS2 / AIE")).join("")}</div>`;
}

function renderLifecycleRange(surface, start, end, intro) {
  const stages = state.stages.stages.filter(stage => stage.stage >= start && stage.stage <= end);
  qs(`#surface-${surface}`).innerHTML = `
    <div class="card" style="margin-bottom:14px"><p>${escapeHtml(intro)}</p></div>
    <div class="stage-grid">
      ${stages.map(stage => {
        const status = getStageStatus(stage.stage);
        const rtStage = findRuntimeStage(stage.stage);
        return `<div class="stage ${status}">
          <span class="num">${stage.stage}</span>
          <b>${escapeHtml(stage.name)}</b>
          <small>${escapeHtml(status)}</small>
          ${rtStage?.reason ? `<p>${escapeHtml(rtStage.reason)}</p>` : ""}
        </div>`;
      }).join("")}
    </div>
  `;
}

function renderRouteGate() {
  const rt = state.runtime || {};
  const selected = String(pick(rt.route_selected, rt.route, "")).toLowerCase();
  const routes = Object.entries(state.routes.routes);
  qs("#surface-route-gate").innerHTML = `
    <div class="route-map">
      ${routes.map(([key, route]) => `<div class="route-card ${selected.includes(key) ? "selected" : ""}">
        <h4>${escapeHtml(route.label)}</h4>
        <p>${escapeHtml(route.default_when)}</p>
        <p><b>Required stages:</b> ${route.required_stages.join(", ")}</p>
        <p><b>Terminal states:</b> ${route.terminal_states.join(", ")}</p>
      </div>`).join("")}
    </div>
    <div style="height:14px"></div>
    ${card("Runtime Route Decision", `<p><b>Selected:</b> ${escapeHtml(pick(rt.route_selected, rt.route, "No route loaded"))}</p><p><b>Reason:</b> ${escapeHtml(stringifyBrief(pick(rt.route_decision?.reason, rt.route_reason, rt.route_decision)))}</p><p><b>Rejected routes:</b> ${escapeHtml(stringifyBrief(pick(rt.routes_rejected, rt.rejected_routes)))}</p>`, "Route gate truth")}
  `;
}

function renderPortfolio() {
  const rt = state.runtime || {};
  qs("#surface-portfolio").innerHTML = `
    <div class="grid-3">
      ${card("Market Positioning", `<p>${escapeHtml(stringifyBrief(pick(rt.market_positioning, rt.stage_23_output)))}</p>`, "Stage 23")}
      ${card("Competitor Analysis", `<p>${escapeHtml(stringifyBrief(pick(rt.competitor_analysis, rt.stage_26_output)))}</p>`, "Stage 26")}
      ${card("Portfolio Creation / Optimization", `<p>${escapeHtml(stringifyBrief(pick(rt.portfolio_output, rt.portfolio_actions, rt.stage_27_output)))}</p>`, "Stage 27")}
    </div>
    <div style="height:14px"></div>
    ${!state.runtime ? emptyRuntimeNote("portfolio route") : ""}
  `;
}

function renderBreakthrough() {
  const rt = state.runtime || {};
  qs("#surface-breakthrough").innerHTML = `
    <div class="grid-3">
      ${card("Gap Detection", `<p>${escapeHtml(stringifyBrief(pick(rt.gap_detection, rt.stage_11_output)))}</p>`, "Stage 11")}
      ${card("Gap Qualification", `<p>${escapeHtml(stringifyBrief(pick(rt.gap_qualification, rt.stage_12_output)))}</p>`, "Stage 12")}
      ${card("Discovery Generation", `<p>${escapeHtml(stringifyBrief(pick(rt.discovery_generation, rt.stage_13_output)))}</p>`, "Stage 13")}
      ${card("Breakthrough Classification", `<p>${escapeHtml(stringifyBrief(pick(rt.breakthrough_classification, rt.stage_14_output)))}</p>`, "Stage 14")}
      ${card("Advancement Path", `<p>${escapeHtml(stringifyBrief(pick(rt.advancement_path, rt.stage_15_output)))}</p>`, "Stage 15")}
      ${card("Route Status", `<p>${escapeHtml(stringifyBrief(pick(rt.route_selected, rt.terminal_state)))}</p>`, "Route")}
    </div>
  `;
}

function renderAutoDesign() {
  const rt = state.runtime || {};
  const designStages = state.stages.stages.filter(stage => stage.stage >= 16 && stage.stage <= 22);
  const fieldMap = {
    16: ["stage_16_output", "auto_invention", "solution_generation"],
    17: ["stage_17_output", "solution_structuring"],
    18: ["stage_18_buildability", "buildability_assessment"],
    19: ["stage_19_viability", "viability_assessment"],
    20: ["stage_20_deployability", "manufacturability_assessment", "deployability_assessment"],
    21: ["stage_21_feasibility", "feasibility_validation"],
    22: ["stage_22_design_portal", "design_portal_output", "blueprints", "specs"]
  };
  qs("#surface-autodesign").innerHTML = `
    <div class="empty" style="margin-bottom:14px">Stages 16-22 are preserved as a dedicated AutoDesign / Design Portal execution block. They are not collapsed into a generic design card.</div>
    <div class="design-spine">
      ${designStages.map(stage => {
        const keys = fieldMap[stage.stage] || [];
        const value = pick(...keys.map(key => rt[key]), findRuntimeStage(stage.stage)?.output);
        const status = getStageStatus(stage.stage);
        return `<div class="design-stage stage ${status}">
          <span class="num">${stage.stage}</span>
          <b>${escapeHtml(stage.name)}</b>
          <small>${escapeHtml(status)}</small>
          <p>${escapeHtml(stringifyBrief(value))}</p>
        </div>`;
      }).join("")}
    </div>
  `;
}

function renderTechnology() {
  const rt = state.runtime || {};
  qs("#surface-technology").innerHTML = `
    <div class="grid-3">
      ${card("Technology Catalog", `<p>${escapeHtml(stringifyBrief(pick(rt.technology_catalog, rt.technology_intelligence?.catalog)))}</p>`, "Conditional")}
      ${card("Compatibility / Component Matching", `<p>${escapeHtml(stringifyBrief(pick(rt.technology_matches, rt.component_matching, rt.technology_intelligence?.matches)))}</p>`, "Route support")}
      ${card("Dependency / Integration Notes", `<p>${escapeHtml(stringifyBrief(pick(rt.dependency_notes, rt.integration_complexity, rt.technology_intelligence?.dependencies)))}</p>`, "Buildability support")}
    </div>
  `;
}

function renderAcquisition() {
  const rt = state.runtime || {};
  qs("#surface-acquisition").innerHTML = `
    <div class="grid-3">
      ${card("Moat & Differentiation", `<p>${escapeHtml(stringifyBrief(pick(rt.moat, rt.moat_differentiation, rt.stage_24_output)))}</p>`, "Stage 24")}
      ${card("Business Model & Value Capture", `<p>${escapeHtml(stringifyBrief(pick(rt.business_model, rt.value_capture, rt.stage_25_output)))}</p>`, "Stage 25")}
      ${card("Acquirer Identification", `<p>${escapeHtml(stringifyBrief(pick(rt.acquirer_identification, rt.stage_28_output)))}</p>`, "Stage 28")}
      ${card("Acquisition Fit", `<p>${escapeHtml(stringifyBrief(pick(rt.acquisition_fit, rt.acquisition_rationale, rt.stage_29_output)))}</p>`, "Stage 29")}
      ${card("Final Package", `<p>${escapeHtml(stringifyBrief(pick(rt.final_package, rt.stage_30_output)))}</p>`, "Stage 30")}
    </div>
  `;
}

function renderValidation() {
  const rt = state.runtime || {};
  const checks = asArray(pick(rt.validation_checks, rt.validation_result?.checks, rt.contract_compliance));
  qs("#surface-validation").innerHTML = `
    <div class="grid-3">
      ${card("Validation Result", `<p>${escapeHtml(stringifyBrief(pick(rt.validation_result, rt.validation_status)))}</p>`, "Final authority")}
      ${card("Route Integrity", `<p>${escapeHtml(stringifyBrief(pick(rt.route_integrity, rt.validation_result?.route_integrity)))}</p>`, "Route proof")}
      ${card("Confidence Thresholds", `<p>${escapeHtml(stringifyBrief(pick(rt.confidence_scores, rt.confidence_thresholds)))}</p>`, "Confidence")}
    </div>
    <div style="height:14px"></div>
    <table class="table"><thead><tr><th>Check</th><th>Status</th><th>Details</th></tr></thead><tbody>
      ${checks.length ? checks.map((check, index) => `<tr><td>${escapeHtml(check.name || check.id || `Check ${index+1}`)}</td><td>${escapeHtml(check.status || check.result || "unknown")}</td><td>${escapeHtml(stringifyBrief(check.details || check.reason || check))}</td></tr>`).join("") : `<tr><td colspan="3">No validation check list found in latest runtime output.</td></tr>`}
    </tbody></table>
  `;
}

function renderEvidence() {
  const rt = state.runtime || {};
  const evidence = asArray(pick(rt.evidence_chain, rt.evidence, rt.source_traceability));
  qs("#surface-evidence").innerHTML = `
    <table class="table"><thead><tr><th>#</th><th>Evidence / Source</th><th>Claim / Stage</th></tr></thead><tbody>
      ${evidence.length ? evidence.map((item, index) => `<tr><td>${index+1}</td><td>${escapeHtml(stringifyBrief(item.source || item.url || item.reference || item))}</td><td>${escapeHtml(stringifyBrief(item.claim || item.stage || item.reason || item.summary))}</td></tr>`).join("") : `<tr><td colspan="3">No evidence chain found in latest runtime output.</td></tr>`}
    </tbody></table>
  `;
}

function renderMemory() {
  const rt = state.runtime || {};
  qs("#surface-memory").innerHTML = `
    <div class="grid-3">
      ${card("Memory Eligibility", `<p>${escapeHtml(stringifyBrief(pick(rt.memory_eligibility, rt.verified_memory_eligible)))}</p>`, "Verified only")}
      ${card("Verified Memory Record", `<p>${escapeHtml(stringifyBrief(pick(rt.verified_memory_record, rt.memory_record)))}</p>`, "Memory")}
      ${card("Recursive Feedback", `<p>${escapeHtml(stringifyBrief(pick(rt.recursive_feedback, rt.self_ingestion, rt.recursion_status)))}</p>`, "Recursion")}
    </div>
  `;
}

function renderRuntime() {
  const rt = state.runtime || {};
  qs("#surface-runtime").innerHTML = `
    <div class="grid-3">
      ${card("Runtime Health", `<p>${escapeHtml(stringifyBrief(pick(rt.runtime_health, rt.health, "Dashboard loaded. Runtime output not yet loaded.")))}</p>`, "Health")}
      ${card("Rollback Safety", `<p>The v17.56 installer backs up overwritten files to <span class="code-path">backups/claire_v17_56_*</span> before writing replacements.</p>`, "Installer")}
      ${card("Launch Continuity", `<p>Launcher remains wired to <span class="code-path">src/frontend/command_center/modern/index.html</span>.</p>`, "Path")}
      ${card("Required Runtime Fields", `<p>${state.runtimeSurfaces.required_runtime_fields.map(field => `<span class="code-path">${escapeHtml(field)}</span>`).join(" ")}</p>`, "Contract")}
      ${card("Runtime Source", `<p>${state.runtimeSource ? escapeHtml(state.runtimeSource) : "No runtime source loaded."}</p>`, "Truth")}
      ${card("Architecture Compliance", `<p>Current dashboard surfaces are generated from architecture sections and runtime surface registries.</p>`, "Compliance")}
    </div>
  `;
}

function renderUpdatePacks() {
  qs("#surface-update-packs").innerHTML = `
    <div class="grid-2">
      ${state.updatePacks.next_packs.map(pack => card(`${pack.version} — ${pack.name}`, `<p>${escapeHtml(pack.purpose)}</p>`, "Next pack")).join("")}
    </div>
  `;
}

function renderProofbar() {
  const rt = state.runtime || {};
  const completed = state.stages.stages.filter(stage => getStageStatus(stage.stage) === "completed").length;
  const skipped = state.stages.stages.filter(stage => getStageStatus(stage.stage) === "skipped_by_route").length;
  const evidence = asArray(pick(rt.evidence_chain, rt.evidence)).length;
  const validation = pick(rt.validation_result?.status, rt.validation_result, rt.validation_status, "unverified");
  const items = [
    ["Run", pick(rt.run_id, rt.id, "none")],
    ["Route", pick(rt.route_selected, rt.route, "none")],
    ["Terminal", pick(rt.terminal_state, rt.status, "none")],
    ["Completed", completed],
    ["Skipped", skipped],
    ["Evidence", evidence],
    ["Validation", validation],
    ["Memory", pick(rt.memory_eligibility, "not eligible")]
  ];
  qs("#proofbar").innerHTML = items.map(([label, value]) => `<div class="proof-item"><b>${escapeHtml(value)}</b><span>${escapeHtml(label)}</span></div>`).join("");
  qs("#chip-route").textContent = pick(rt.route_selected, rt.route, "No run loaded");
  qs("#chip-validation").textContent = String(validation).slice(0, 28);
}

function renderEventRail() {
  const rt = state.runtime || {};
  const events = asArray(pick(rt.live_intelligence_feed, rt.events, rt.stage_events, rt.runtime_events));
  const architectureEvents = [
    ["Architecture map loaded", "17 operating surfaces are available."],
    ["Runtime truth policy", "No fake data is generated for missing run output."],
    ["Stages 16-22 preserved", "AutoDesign has a dedicated operating surface."],
    ["Validation authority", "Outputs remain unverified until runtime validation passes."]
  ];
  const runtimeEvents = events.map((event, index) => [
    event.title || event.name || `Runtime event ${index+1}`,
    stringifyBrief(event.message || event.summary || event.details || event)
  ]);
  qs("#event-rail").innerHTML = [...runtimeEvents, ...architectureEvents].slice(0, 12).map(([title, msg]) => `<div class="event"><b>${escapeHtml(title)}</b><span>${escapeHtml(msg)}</span></div>`).join("");
}

function renderAll() {
  renderNav();
  renderCommand();
  renderSources();
  renderAcs2();
  renderLifecycleRange("governance", 1, 5, "Stages 1-5 convert raw external intake into governed, normalized, weighted, context-expanded, consolidated signals.");
  renderLifecycleRange("entity", 6, 7, "Stages 6-7 extract entities and map relationships before trend discovery begins.");
  renderLifecycleRange("trend", 8, 10, "Stages 8-10 discover trends, form clusters, structure thesis, and prepare route gate input.");
  renderRouteGate();
  renderPortfolio();
  renderBreakthrough();
  renderAutoDesign();
  renderTechnology();
  renderAcquisition();
  renderValidation();
  renderEvidence();
  renderMemory();
  renderRuntime();
  renderUpdatePacks();
  renderProofbar();
  renderEventRail();
  activateSurface(state.surface);
}

async function boot() {
  await loadRegistries();
  await loadRuntimeTruth();
  renderAll();
  qs("#refresh-runtime").addEventListener("click", async () => {
    await loadRuntimeTruth();
    renderAll();
  });
}

boot().catch(error => {
  state.runtimeLoadError = error.message;
  renderAll();
});
