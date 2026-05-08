
/* Claire Syntalion v17.57-v17.58 — Runtime Execution Mirror + Route Gate Branch Execution */
/* Runtime truth only. This dashboard never invents run results. */
const CLAIRE_BUILD = {"version": "v17.57-v17.58", "name": "Runtime Execution Mirror + Route Gate Branch Execution"};
const STAGE_REGISTRY = [
  {
    "number": 1,
    "id": "stage_01",
    "name": "Signal Ingestion",
    "domain": "governance",
    "purpose": "Capture raw signals from approved live/local sources.",
    "routes": [
      "all"
    ],
    "required_status_fields": [
      "status",
      "evidence",
      "confidence",
      "summary",
      "reason_if_skipped"
    ],
    "valid_statuses": [
      "completed",
      "skipped_by_route",
      "blocked",
      "failed",
      "waiting",
      "not_started",
      "running"
    ]
  },
  {
    "number": 2,
    "id": "stage_02",
    "name": "Signal Normalization",
    "domain": "governance",
    "purpose": "Normalize signals into a consistent runtime format.",
    "routes": [
      "all"
    ],
    "required_status_fields": [
      "status",
      "evidence",
      "confidence",
      "summary",
      "reason_if_skipped"
    ],
    "valid_statuses": [
      "completed",
      "skipped_by_route",
      "blocked",
      "failed",
      "waiting",
      "not_started",
      "running"
    ]
  },
  {
    "number": 3,
    "id": "stage_03",
    "name": "Source Validation & Weighting",
    "domain": "governance",
    "purpose": "Validate source quality, freshness, and trust weight.",
    "routes": [
      "all"
    ],
    "required_status_fields": [
      "status",
      "evidence",
      "confidence",
      "summary",
      "reason_if_skipped"
    ],
    "valid_statuses": [
      "completed",
      "skipped_by_route",
      "blocked",
      "failed",
      "waiting",
      "not_started",
      "running"
    ]
  },
  {
    "number": 4,
    "id": "stage_04",
    "name": "Context Expansion",
    "domain": "governance",
    "purpose": "Expand signal context with related source/evidence material.",
    "routes": [
      "all"
    ],
    "required_status_fields": [
      "status",
      "evidence",
      "confidence",
      "summary",
      "reason_if_skipped"
    ],
    "valid_statuses": [
      "completed",
      "skipped_by_route",
      "blocked",
      "failed",
      "waiting",
      "not_started",
      "running"
    ]
  },
  {
    "number": 5,
    "id": "stage_05",
    "name": "Signal Consolidation",
    "domain": "governance",
    "purpose": "Consolidate duplicate/conflicting signals into governed evidence baskets.",
    "routes": [
      "all"
    ],
    "required_status_fields": [
      "status",
      "evidence",
      "confidence",
      "summary",
      "reason_if_skipped"
    ],
    "valid_statuses": [
      "completed",
      "skipped_by_route",
      "blocked",
      "failed",
      "waiting",
      "not_started",
      "running"
    ]
  },
  {
    "number": 6,
    "id": "stage_06",
    "name": "Entity Extraction",
    "domain": "entity",
    "purpose": "Extract organizations, technologies, markets, people, risks, and assets.",
    "routes": [
      "all"
    ],
    "required_status_fields": [
      "status",
      "evidence",
      "confidence",
      "summary",
      "reason_if_skipped"
    ],
    "valid_statuses": [
      "completed",
      "skipped_by_route",
      "blocked",
      "failed",
      "waiting",
      "not_started",
      "running"
    ]
  },
  {
    "number": 7,
    "id": "stage_07",
    "name": "Relationship Mapping",
    "domain": "entity",
    "purpose": "Map relationships between entities, evidence, opportunities, and constraints.",
    "routes": [
      "all"
    ],
    "required_status_fields": [
      "status",
      "evidence",
      "confidence",
      "summary",
      "reason_if_skipped"
    ],
    "valid_statuses": [
      "completed",
      "skipped_by_route",
      "blocked",
      "failed",
      "waiting",
      "not_started",
      "running"
    ]
  },
  {
    "number": 8,
    "id": "stage_08",
    "name": "Trend Discovery",
    "domain": "trend",
    "purpose": "Detect emerging trends, clusters, weak signals, and anomalies.",
    "routes": [
      "all"
    ],
    "required_status_fields": [
      "status",
      "evidence",
      "confidence",
      "summary",
      "reason_if_skipped"
    ],
    "valid_statuses": [
      "completed",
      "skipped_by_route",
      "blocked",
      "failed",
      "waiting",
      "not_started",
      "running"
    ]
  },
  {
    "number": 9,
    "id": "stage_09",
    "name": "Cluster Formation",
    "domain": "trend",
    "purpose": "Form durable clusters from related signals and entities.",
    "routes": [
      "all"
    ],
    "required_status_fields": [
      "status",
      "evidence",
      "confidence",
      "summary",
      "reason_if_skipped"
    ],
    "valid_statuses": [
      "completed",
      "skipped_by_route",
      "blocked",
      "failed",
      "waiting",
      "not_started",
      "running"
    ]
  },
  {
    "number": 10,
    "id": "stage_10",
    "name": "Insight / Thesis Structuring + Route Gate",
    "domain": "route_gate",
    "purpose": "Structure the thesis and select the route.",
    "routes": [
      "all"
    ],
    "required_status_fields": [
      "status",
      "evidence",
      "confidence",
      "summary",
      "reason_if_skipped"
    ],
    "valid_statuses": [
      "completed",
      "skipped_by_route",
      "blocked",
      "failed",
      "waiting",
      "not_started",
      "running"
    ]
  },
  {
    "number": 11,
    "id": "stage_11",
    "name": "Gap Detection",
    "domain": "breakthrough",
    "purpose": "Identify market, technical, operational, portfolio, or system gaps.",
    "routes": [
      "breakthrough",
      "design"
    ],
    "required_status_fields": [
      "status",
      "evidence",
      "confidence",
      "summary",
      "reason_if_skipped"
    ],
    "valid_statuses": [
      "completed",
      "skipped_by_route",
      "blocked",
      "failed",
      "waiting",
      "not_started",
      "running"
    ]
  },
  {
    "number": 12,
    "id": "stage_12",
    "name": "Gap Qualification",
    "domain": "breakthrough",
    "purpose": "Qualify whether a gap deserves discovery or breakthrough escalation.",
    "routes": [
      "breakthrough",
      "design"
    ],
    "required_status_fields": [
      "status",
      "evidence",
      "confidence",
      "summary",
      "reason_if_skipped"
    ],
    "valid_statuses": [
      "completed",
      "skipped_by_route",
      "blocked",
      "failed",
      "waiting",
      "not_started",
      "running"
    ]
  },
  {
    "number": 13,
    "id": "stage_13",
    "name": "Discovery Generation",
    "domain": "breakthrough",
    "purpose": "Generate discovery candidates and route them for classification.",
    "routes": [
      "breakthrough",
      "design"
    ],
    "required_status_fields": [
      "status",
      "evidence",
      "confidence",
      "summary",
      "reason_if_skipped"
    ],
    "valid_statuses": [
      "completed",
      "skipped_by_route",
      "blocked",
      "failed",
      "waiting",
      "not_started",
      "running"
    ]
  },
  {
    "number": 14,
    "id": "stage_14",
    "name": "Breakthrough Identification / Classification",
    "domain": "breakthrough",
    "purpose": "Classify breakthrough type and strength.",
    "routes": [
      "breakthrough",
      "design"
    ],
    "required_status_fields": [
      "status",
      "evidence",
      "confidence",
      "summary",
      "reason_if_skipped"
    ],
    "valid_statuses": [
      "completed",
      "skipped_by_route",
      "blocked",
      "failed",
      "waiting",
      "not_started",
      "running"
    ]
  },
  {
    "number": 15,
    "id": "stage_15",
    "name": "Advancement Path Selection",
    "domain": "breakthrough",
    "purpose": "Select advancement path: technology, business model, portfolio, system, acquisition, or other route.",
    "routes": [
      "breakthrough",
      "design"
    ],
    "required_status_fields": [
      "status",
      "evidence",
      "confidence",
      "summary",
      "reason_if_skipped"
    ],
    "valid_statuses": [
      "completed",
      "skipped_by_route",
      "blocked",
      "failed",
      "waiting",
      "not_started",
      "running"
    ]
  },
  {
    "number": 16,
    "id": "stage_16",
    "name": "Auto Invention / Solution Generation",
    "domain": "autodesign",
    "purpose": "Generate solution candidates under constraints.",
    "routes": [
      "design"
    ],
    "required_status_fields": [
      "status",
      "evidence",
      "confidence",
      "summary",
      "reason_if_skipped"
    ],
    "valid_statuses": [
      "completed",
      "skipped_by_route",
      "blocked",
      "failed",
      "waiting",
      "not_started",
      "running"
    ]
  },
  {
    "number": 17,
    "id": "stage_17",
    "name": "Solution Structuring",
    "domain": "autodesign",
    "purpose": "Structure solution concept, components, dependencies, constraints, and implementation phases.",
    "routes": [
      "design"
    ],
    "required_status_fields": [
      "status",
      "evidence",
      "confidence",
      "summary",
      "reason_if_skipped"
    ],
    "valid_statuses": [
      "completed",
      "skipped_by_route",
      "blocked",
      "failed",
      "waiting",
      "not_started",
      "running"
    ]
  },
  {
    "number": 18,
    "id": "stage_18",
    "name": "Buildability Assessment",
    "domain": "autodesign",
    "purpose": "Assess engineering buildability, complexity, dependencies, and failure modes.",
    "routes": [
      "design"
    ],
    "required_status_fields": [
      "status",
      "evidence",
      "confidence",
      "summary",
      "reason_if_skipped"
    ],
    "valid_statuses": [
      "completed",
      "skipped_by_route",
      "blocked",
      "failed",
      "waiting",
      "not_started",
      "running"
    ]
  },
  {
    "number": 19,
    "id": "stage_19",
    "name": "Viability Assessment",
    "domain": "autodesign",
    "purpose": "Assess market, financial, operational, and strategic viability.",
    "routes": [
      "design"
    ],
    "required_status_fields": [
      "status",
      "evidence",
      "confidence",
      "summary",
      "reason_if_skipped"
    ],
    "valid_statuses": [
      "completed",
      "skipped_by_route",
      "blocked",
      "failed",
      "waiting",
      "not_started",
      "running"
    ]
  },
  {
    "number": 20,
    "id": "stage_20",
    "name": "Manufacturability / Deployability Assessment",
    "domain": "autodesign",
    "purpose": "Assess production, deployment, integration, and operating feasibility.",
    "routes": [
      "design"
    ],
    "required_status_fields": [
      "status",
      "evidence",
      "confidence",
      "summary",
      "reason_if_skipped"
    ],
    "valid_statuses": [
      "completed",
      "skipped_by_route",
      "blocked",
      "failed",
      "waiting",
      "not_started",
      "running"
    ]
  },
  {
    "number": 21,
    "id": "stage_21",
    "name": "Feasibility Validation",
    "domain": "autodesign",
    "purpose": "Validate combined technical, market, operational, and deployment feasibility.",
    "routes": [
      "design"
    ],
    "required_status_fields": [
      "status",
      "evidence",
      "confidence",
      "summary",
      "reason_if_skipped"
    ],
    "valid_statuses": [
      "completed",
      "skipped_by_route",
      "blocked",
      "failed",
      "waiting",
      "not_started",
      "running"
    ]
  },
  {
    "number": 22,
    "id": "stage_22",
    "name": "Design Portal Output / Blueprints / Specs",
    "domain": "autodesign",
    "purpose": "Produce blueprint/specification output for the design portal.",
    "routes": [
      "design"
    ],
    "required_status_fields": [
      "status",
      "evidence",
      "confidence",
      "summary",
      "reason_if_skipped"
    ],
    "valid_statuses": [
      "completed",
      "skipped_by_route",
      "blocked",
      "failed",
      "waiting",
      "not_started",
      "running"
    ]
  },
  {
    "number": 23,
    "id": "stage_23",
    "name": "Market Positioning",
    "domain": "strategy",
    "purpose": "Position thesis/product/company/portfolio in the market.",
    "routes": [
      "portfolio",
      "acquisition",
      "breakthrough",
      "design"
    ],
    "required_status_fields": [
      "status",
      "evidence",
      "confidence",
      "summary",
      "reason_if_skipped"
    ],
    "valid_statuses": [
      "completed",
      "skipped_by_route",
      "blocked",
      "failed",
      "waiting",
      "not_started",
      "running"
    ]
  },
  {
    "number": 24,
    "id": "stage_24",
    "name": "Moat & Differentiation",
    "domain": "strategy",
    "purpose": "Analyze defensibility, differentiation, lock-in, and advantage.",
    "routes": [
      "acquisition",
      "breakthrough",
      "design"
    ],
    "required_status_fields": [
      "status",
      "evidence",
      "confidence",
      "summary",
      "reason_if_skipped"
    ],
    "valid_statuses": [
      "completed",
      "skipped_by_route",
      "blocked",
      "failed",
      "waiting",
      "not_started",
      "running"
    ]
  },
  {
    "number": 25,
    "id": "stage_25",
    "name": "Business Model & Value Capture",
    "domain": "strategy",
    "purpose": "Define revenue, value capture, pricing, and operating model.",
    "routes": [
      "acquisition",
      "breakthrough",
      "design"
    ],
    "required_status_fields": [
      "status",
      "evidence",
      "confidence",
      "summary",
      "reason_if_skipped"
    ],
    "valid_statuses": [
      "completed",
      "skipped_by_route",
      "blocked",
      "failed",
      "waiting",
      "not_started",
      "running"
    ]
  },
  {
    "number": 26,
    "id": "stage_26",
    "name": "Competitor Analysis",
    "domain": "strategy",
    "purpose": "Assess competitors, substitute systems, threats, and gaps.",
    "routes": [
      "portfolio",
      "acquisition",
      "breakthrough",
      "design"
    ],
    "required_status_fields": [
      "status",
      "evidence",
      "confidence",
      "summary",
      "reason_if_skipped"
    ],
    "valid_statuses": [
      "completed",
      "skipped_by_route",
      "blocked",
      "failed",
      "waiting",
      "not_started",
      "running"
    ]
  },
  {
    "number": 27,
    "id": "stage_27",
    "name": "Portfolio Creation / Optimization",
    "domain": "portfolio",
    "purpose": "Create or optimize portfolio action from the thesis and evidence.",
    "routes": [
      "portfolio"
    ],
    "required_status_fields": [
      "status",
      "evidence",
      "confidence",
      "summary",
      "reason_if_skipped"
    ],
    "valid_statuses": [
      "completed",
      "skipped_by_route",
      "blocked",
      "failed",
      "waiting",
      "not_started",
      "running"
    ]
  },
  {
    "number": 28,
    "id": "stage_28",
    "name": "Acquirer Identification",
    "domain": "acquisition",
    "purpose": "Identify likely acquirers, sponsors, buyers, or strategic partners.",
    "routes": [
      "acquisition"
    ],
    "required_status_fields": [
      "status",
      "evidence",
      "confidence",
      "summary",
      "reason_if_skipped"
    ],
    "valid_statuses": [
      "completed",
      "skipped_by_route",
      "blocked",
      "failed",
      "waiting",
      "not_started",
      "running"
    ]
  },
  {
    "number": 29,
    "id": "stage_29",
    "name": "Acquisition Fit & Rationale",
    "domain": "acquisition",
    "purpose": "Explain strategic fit, synergies, integration complexity, and acquisition logic.",
    "routes": [
      "acquisition"
    ],
    "required_status_fields": [
      "status",
      "evidence",
      "confidence",
      "summary",
      "reason_if_skipped"
    ],
    "valid_statuses": [
      "completed",
      "skipped_by_route",
      "blocked",
      "failed",
      "waiting",
      "not_started",
      "running"
    ]
  },
  {
    "number": 30,
    "id": "stage_30",
    "name": "Final Package Construction",
    "domain": "package",
    "purpose": "Construct final package with proof, evidence, route outputs, and validation.",
    "routes": [
      "acquisition",
      "portfolio",
      "breakthrough",
      "design"
    ],
    "required_status_fields": [
      "status",
      "evidence",
      "confidence",
      "summary",
      "reason_if_skipped"
    ],
    "valid_statuses": [
      "completed",
      "skipped_by_route",
      "blocked",
      "failed",
      "waiting",
      "not_started",
      "running"
    ]
  }
];
const SURFACES = [
  {
    "id": "command",
    "label": "Command",
    "purpose": "Launch and inspect live/local Claire runs."
  },
  {
    "id": "sources",
    "label": "Sources",
    "purpose": "External source intake, source readiness, trust, and freshness."
  },
  {
    "id": "acs2",
    "label": "ACS2 Loops",
    "purpose": "Autonomous sensing loops feeding the lifecycle."
  },
  {
    "id": "lifecycle",
    "label": "Lifecycle",
    "purpose": "Full 30-stage execution mirror."
  },
  {
    "id": "route-gate",
    "label": "Route Gate",
    "purpose": "Selected route, rejected routes, confidence, and rationale."
  },
  {
    "id": "portfolio",
    "label": "Portfolio",
    "purpose": "Portfolio route execution and action readiness."
  },
  {
    "id": "breakthrough",
    "label": "Breakthrough",
    "purpose": "Gap, discovery, classification, and advancement path stages."
  },
  {
    "id": "autodesign",
    "label": "AutoDesign",
    "purpose": "Stages 16-22 Auto Invention / Design Portal execution."
  },
  {
    "id": "technology",
    "label": "Technology Intelligence",
    "purpose": "Technology layer activated only for design/system routes."
  },
  {
    "id": "acquisition",
    "label": "Acquisition",
    "purpose": "Moat, business model, acquirer fit, and final package route."
  },
  {
    "id": "validation",
    "label": "Validation",
    "purpose": "Final authority, contract compliance, route integrity, and PASS/FAIL proof."
  },
  {
    "id": "evidence",
    "label": "Evidence",
    "purpose": "Traceable evidence chain and source-backed claims."
  },
  {
    "id": "memory",
    "label": "Memory",
    "purpose": "Verified memory eligibility and recursive feedback."
  },
  {
    "id": "runtime",
    "label": "Runtime",
    "purpose": "Runtime files, endpoints, health, isolation, and rollback state."
  },
  {
    "id": "update-packs",
    "label": "Update Packs",
    "purpose": "Dashboard/system update packs mapped to architecture gaps."
  }
];
const ROUTE_REGISTRY = {
  "portfolio": {
    "label": "Portfolio Route",
    "description": "Default practical route for governed market/trend/portfolio thesis outputs.",
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
      27,
      30
    ],
    "terminal_states": [
      "portfolio_action_ready",
      "portfolio_optimization_ready",
      "final_package_ready"
    ],
    "dashboard_surfaces": [
      "route-gate",
      "portfolio",
      "validation",
      "evidence"
    ]
  },
  "breakthrough": {
    "label": "Breakthrough Route",
    "description": "Conditional escalation when gap/discovery signals justify breakthrough classification.",
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
      23,
      24,
      25,
      26,
      30
    ],
    "terminal_states": [
      "breakthrough_classified",
      "advancement_path_selected",
      "final_package_ready"
    ],
    "dashboard_surfaces": [
      "route-gate",
      "breakthrough",
      "validation",
      "evidence"
    ]
  },
  "design": {
    "label": "AutoDesign / System Design Route",
    "description": "Design route that must preserve stages 16-22 as a first-class execution block.",
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
      22,
      23,
      24,
      25,
      26,
      30
    ],
    "critical_stages": [
      16,
      17,
      18,
      19,
      20,
      21,
      22
    ],
    "terminal_states": [
      "design_output_ready",
      "advancement_path_selected",
      "final_package_ready"
    ],
    "dashboard_surfaces": [
      "route-gate",
      "breakthrough",
      "autodesign",
      "technology",
      "validation",
      "evidence"
    ]
  },
  "acquisition": {
    "label": "Acquisition Route",
    "description": "Strategic route for acquirer identification, acquisition fit, rationale, and final package.",
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
      24,
      25,
      26,
      28,
      29,
      30
    ],
    "terminal_states": [
      "acquisition_ready",
      "final_package_ready"
    ],
    "dashboard_surfaces": [
      "route-gate",
      "acquisition",
      "validation",
      "evidence"
    ]
  },
  "insufficient_data": {
    "label": "Insufficient Data Route",
    "description": "Safe terminal route when evidence quality, source coverage, or confidence is not adequate.",
    "required_stages": [
      1,
      2,
      3,
      4,
      5,
      10
    ],
    "terminal_states": [
      "insufficient_data",
      "blocked",
      "failed"
    ],
    "dashboard_surfaces": [
      "route-gate",
      "validation",
      "evidence"
    ]
  }
};
const RUNTIME_LOCATIONS = [
  "./dashboard_runtime_truth.json",
  "./core_run_output.json",
  "/exports/latest/dashboard_runtime_truth.json",
  "/exports/latest/core_run_output.json",
  "/output/core_run_output.json",
  "/core_run_output.json",
  "/api/runtime/latest",
  "/runtime/latest",
  "/api/core-run-output/latest",
  "/exports/index.json"
];

const state = { activeSurface: 'command', runtime: null, runtimeSource: null, loadError: null, registries: { stages: STAGE_REGISTRY, routes: ROUTE_REGISTRY } };
const $ = (id) => document.getElementById(id);
const safe = (v, fallback = 'not_reported') => (v === undefined || v === null || v === '' ? fallback : v);
const asArray = (v) => Array.isArray(v) ? v : (v === undefined || v === null ? [] : [v]);
const norm = (v) => String(v || '').trim().toLowerCase().replace(/[^a-z0-9]+/g, '_').replace(/^_|_$/g, '');

function textValue(v) {
  if (v === undefined || v === null || v === '') return 'not_reported';
  if (typeof v === 'string' || typeof v === 'number' || typeof v === 'boolean') return String(v);
  try { return JSON.stringify(v); } catch { return String(v); }
}

function titleCase(v) { return String(v || '').replace(/_/g, ' ').replace(/\w/g, c => c.toUpperCase()); }
function nowStamp() { return new Date().toLocaleTimeString([], {hour:'2-digit', minute:'2-digit', second:'2-digit'}); }

function addEvent(title, body, tone='info') {
  const rail = $('event-rail');
  if (!rail) return;
  const el = document.createElement('div');
  el.className = 'event ' + tone;
  el.innerHTML = `<b>${title}</b><p>${body}</p><span class="time">${nowStamp()}</span>`;
  rail.prepend(el);
  while (rail.children.length > 18) rail.removeChild(rail.lastChild);
}

async function fetchJson(url) {
  const response = await fetch(url, { cache: 'no-store' });
  if (!response.ok) throw new Error(`${response.status} ${response.statusText}`);
  return await response.json();
}

async function loadFirstAvailableRuntime() {
  const errors = [];
  for (const url of RUNTIME_LOCATIONS) {
    try {
      const data = await fetchJson(url);
      if (!data || (typeof data === 'object' && Object.keys(data).length === 0)) throw new Error('empty json');
      if (url.endsWith('/exports/index.json') || url.endsWith('exports/index.json')) {
        const candidate = selectLatestFromExportIndex(data);
        if (!candidate) throw new Error('exports index did not include readable latest run');
        return { data: candidate, source: url + ' → latest entry' };
      }
      return { data, source: url };
    } catch (error) { errors.push(`${url}: ${error.message}`); }
  }
  throw new Error(errors.join(' | '));
}

function selectLatestFromExportIndex(data) {
  const runs = asArray(data.runs || data.exports || data.items || data.history);
  if (!runs.length) return null;
  const latest = runs[0];
  if (latest.core_run_output) return latest.core_run_output;
  if (latest.output) return latest.output;
  if (latest.runtime_truth) return latest.runtime_truth;
  return latest;
}

function extractRuntime(raw) {
  const root = raw && raw.runtime_truth ? raw.runtime_truth : raw;
  const routeDecision = root.route_decision || root.route || root.routing || root.core_lifecycle_summary || {};
  const validation = root.validation_result || root.validation || root.output_validation || {};
  const stageMap = buildStageMap(root);
  const routeSelected = normalizeRoute(root.route_selected || root.selected_route || routeDecision.route_selected || routeDecision.selected_route || routeDecision.name || routeDecision.route || root.route_type);
  const terminalState = root.terminal_state || root.status_terminal || root.core_lifecycle_summary?.terminal_state || root.status;
  const evidence = asArray(root.evidence_chain || root.evidence || root.sources || root.source_evidence || root.validation_evidence);
  const completed = Object.values(stageMap).filter(s => s.status === 'completed').length;
  const skipped = Object.values(stageMap).filter(s => s.status === 'skipped_by_route').length;
  const failed = Object.values(stageMap).filter(s => ['failed','blocked'].includes(s.status)).length;
  return {
    raw: root,
    run_id: root.run_id || root.id || root.session_id || root.core_run_id || 'not_reported',
    timestamp: root.timestamp || root.created_at || root.completed_at || root.started_at || 'not_reported',
    route_selected: routeSelected,
    route_decision: routeDecision,
    routes_rejected: asArray(root.routes_rejected || routeDecision.routes_rejected || routeDecision.rejected_routes),
    terminal_state: terminalState || 'not_reported',
    validation_result: normalizeValidation(validation),
    validated_output_path: root.validated_output_path || root.output_path || root.export_path || root.core_run_output_path || 'not_reported',
    memory_eligibility: root.memory_eligibility || root.verified_memory_eligibility || root.memory?.eligibility || 'not_reported',
    evidence_chain: evidence,
    confidence_scores: root.confidence_scores || root.confidence || routeDecision.confidence_scores || {},
    governance_stamp: root.governance_stamp || root.governance || root.source_governance || 'not_reported',
    stage_map: stageMap,
    counts: { completed, skipped, failed, total: 30, reported: Object.keys(stageMap).length }
  };
}

function normalizeRoute(route) {
  const r = norm(route);
  if (!r) return 'not_reported';
  if (r.includes('portfolio')) return 'portfolio';
  if (r.includes('acquisition') || r.includes('acquirer')) return 'acquisition';
  if (r.includes('design') || r.includes('invention') || r.includes('autodesign') || r.includes('solution')) return 'design';
  if (r.includes('breakthrough') || r.includes('discovery')) return 'breakthrough';
  if (r.includes('insufficient')) return 'insufficient_data';
  if (r.includes('blocked')) return 'insufficient_data';
  return r;
}

function normalizeValidation(v) {
  const status = typeof v === 'string' ? v : (v.status || v.result || v.validation_status || v.passed || v.pass);
  let normalized = norm(status);
  if (status === true) normalized = 'pass';
  if (status === false) normalized = 'fail';
  if (normalized === 'passed') normalized = 'pass';
  if (normalized === 'failed') normalized = 'fail';
  return { status: normalized || 'not_reported', raw: v };
}

function buildStageMap(root) {
  const map = {};
  const candidates = [
    root.lifecycle_stages, root.core_lifecycle_stages, root.stage_statuses, root.stages, root.core_lifecycle?.stages,
    root.lifecycle?.stages, root.runtime?.stages, root.execution?.stages
  ];
  for (const candidate of candidates) readStageCandidate(candidate, map);
  for (const key of Object.keys(root || {})) {
    const match = key.match(/^stage[_-]?(\d{1,2})(?:_|$)/i) || key.match(/^stage_(\d{2})_/i);
    if (match) {
      const num = Number(match[1]);
      map[num] = mergeStage(map[num], { number:num, key, payload:root[key], status: inferStatusFromPayload(root[key]) });
    }
  }
  for (const n of asArray(root.stages_completed || root.completed_stages)) {
    const num = stageNumberFromAny(n); if (num) map[num] = mergeStage(map[num], { number:num, status:'completed', payload:n });
  }
  for (const n of asArray(root.stages_skipped || root.skipped_stages || root.skipped_by_route)) {
    const num = stageNumberFromAny(n); if (num) map[num] = mergeStage(map[num], { number:num, status:'skipped_by_route', payload:n, reason: n.reason || n.reason_if_skipped });
  }
  for (const n of asArray(root.stages_failed || root.failed_stages)) {
    const num = stageNumberFromAny(n); if (num) map[num] = mergeStage(map[num], { number:num, status:'failed', payload:n });
  }
  return map;
}

function readStageCandidate(candidate, map) {
  if (!candidate) return;
  if (Array.isArray(candidate)) {
    for (const item of candidate) { const num = stageNumberFromAny(item); if (num) map[num] = mergeStage(map[num], normalizeStageObject(num, item)); }
  } else if (typeof candidate === 'object') {
    for (const [key, value] of Object.entries(candidate)) { const num = stageNumberFromAny(value) || stageNumberFromAny(key); if (num) map[num] = mergeStage(map[num], normalizeStageObject(num, value)); }
  }
}

function stageNumberFromAny(v) {
  if (typeof v === 'number') return v >= 1 && v <= 30 ? v : null;
  if (typeof v === 'string') { const m = v.match(/(?:stage[_ -]?)?(\d{1,2})/i); if (m) { const n=Number(m[1]); return n>=1&&n<=30?n:null; } }
  if (v && typeof v === 'object') {
    return stageNumberFromAny(v.number || v.stage_number || v.stage || v.id || v.name || v.stage_id);
  }
  return null;
}

function normalizeStageObject(num, value) {
  const obj = value && typeof value === 'object' ? value : { value };
  const status = norm(obj.status || obj.state || obj.result || obj.outcome) || inferStatusFromPayload(obj);
  return { number:num, status, payload:value, evidence:obj.evidence || obj.evidence_chain, confidence:obj.confidence, summary:obj.summary || obj.output_summary || obj.result_summary, reason:obj.reason || obj.reason_if_skipped || obj.skip_reason };
}

function inferStatusFromPayload(payload) {
  if (payload === undefined || payload === null || payload === '') return 'not_reported';
  if (typeof payload === 'string') { const n = norm(payload); if (['completed','skipped_by_route','blocked','failed','waiting','running','not_started'].includes(n)) return n; }
  if (typeof payload === 'object') {
    const s = norm(payload.status || payload.state || payload.result || payload.outcome);
    if (s) return s;
    if (Object.keys(payload).length) return 'completed';
  }
  return 'completed';
}

function mergeStage(a, b) {
  const rank = { failed:8, blocked:8, running:7, completed:6, skipped_by_route:5, waiting:4, not_started:3, not_reported:1 };
  if (!a) return b;
  const keepB = (rank[b.status] || 0) >= (rank[a.status] || 0);
  return keepB ? {...a, ...b, payload:b.payload ?? a.payload} : {...b, ...a, payload:a.payload ?? b.payload};
}

function stageStatus(n) { return state.runtime?.stage_map?.[n]?.status || 'not_reported'; }
function stagePayload(n) { return state.runtime?.stage_map?.[n]?.payload || null; }
function routeObj() { return ROUTE_REGISTRY[state.runtime?.route_selected] || null; }
function validationStatusClass() { const s = state.runtime?.validation_result?.status || 'not_reported'; return ['pass','passed'].includes(s) ? 'pass' : ['fail','failed','blocked'].includes(s) ? 'fail' : s; }

function initNav() {
  const nav = $('main-nav'); nav.innerHTML = '';
  SURFACES.forEach((s, idx) => {
    const btn = document.createElement('button'); btn.type = 'button'; btn.dataset.surface = s.id; btn.className = s.id === state.activeSurface ? 'active' : '';
    btn.innerHTML = `<span class="nav-num">${String(idx+1).padStart(2,'0')}</span><span class="nav-label">${s.label}</span><span class="nav-dot"></span>`;
    btn.addEventListener('click', () => setSurface(s.id)); nav.appendChild(btn);
  });
}

function setSurface(id) { state.activeSurface = id; document.querySelectorAll('.nav button').forEach(b => b.classList.toggle('active', b.dataset.surface === id)); render(); }

async function refreshRuntime() {
  addEvent('Runtime refresh started', 'Scanning approved runtime truth locations for core_run_output or dashboard_runtime_truth data.');
  try {
    const {data, source} = await loadFirstAvailableRuntime();
    state.runtime = extractRuntime(data); state.runtimeSource = source; state.loadError = null;
    addEvent('Runtime truth loaded', `Loaded data from ${source}. Route: ${state.runtime.route_selected}. Terminal: ${state.runtime.terminal_state}.`, 'good');
  } catch (error) {
    state.runtime = null; state.runtimeSource = null; state.loadError = error.message;
    addEvent('No runtime truth loaded', 'Dashboard remains honest: no fake run output is displayed. ' + error.message.slice(0,220), 'warn');
  }
  render();
}

function render() {
  const surface = SURFACES.find(s => s.id === state.activeSurface) || SURFACES[0];
  $('surface-kicker').textContent = surface.id.replace(/-/g,' ').toUpperCase();
  $('surface-title').textContent = surface.label;
  $('surface-description').textContent = surface.purpose;
  $('chip-build').textContent = 'v17.58';
  $('chip-route').textContent = state.runtime?.route_selected || 'No run loaded';
  $('chip-validation').textContent = state.runtime?.validation_result?.status || 'Unverified';
  const body = $('workspace-body');
  body.innerHTML = `<section class="surface active">${renderSurface(surface.id)}</section>`;
  renderProofbar();
}

function renderSurface(id) {
  const map = {
    command: renderCommand, sources: renderSources, acs2: renderACS2, lifecycle: renderLifecycle, 'route-gate': renderRouteGate,
    portfolio: () => renderRouteSurface('portfolio'), breakthrough: () => renderRouteSurface('breakthrough'), autodesign: renderAutoDesign,
    technology: renderTechnology, acquisition: () => renderRouteSurface('acquisition'), validation: renderValidation, evidence: renderEvidence,
    memory: renderMemory, runtime: renderRuntime, 'update-packs': renderUpdatePacks
  };
  return (map[id] || renderCommand)();
}

function noRuntimeBlock() {
  return `<div class="empty"><h4>No runtime output loaded</h4><p>Claire is live-capable, but this surface will not invent run data. Generate or expose a real <b>core_run_output.json</b> or <b>dashboard_runtime_truth.json</b>, then refresh runtime truth.</p></div>`;
}

function renderCommand() {
  const rt = state.runtime;
  return `<div class="grid four">
    ${metricCard('Run ID', rt?.run_id || 'not_loaded', 'Current runtime identifier from loaded output.')}
    ${metricCard('Route', rt?.route_selected || 'not_loaded', 'Selected route from route gate.')}
    ${metricCard('Terminal', rt?.terminal_state || 'not_loaded', 'Explicit terminal state.')}
    ${metricCard('Validation', rt?.validation_result?.status || 'not_loaded', 'Final validation authority status.')}
  </div>
  <div class="section-title">Build Purpose</div>
  <div class="grid two">
    <div class="card"><div class="card-kicker">v17.57</div><h4>Runtime Execution Mirror</h4><p>Expose the full 30-stage lifecycle and status of every stage as completed, skipped_by_route, blocked, failed, running, waiting, not_started, or not_reported.</p></div>
    <div class="card"><div class="card-kicker">v17.58</div><h4>Route Gate + Route Branch Execution</h4><p>Expose route selection, rejected routes, route confidence, required route stages, terminal-state fit, and route execution integrity.</p></div>
  </div>
  <div class="section-title">Runtime Load State</div>
  ${rt ? renderRuntimeSummary() : noRuntimeBlock()}`;
}

function metricCard(label, value, help) { return `<div class="card"><div class="card-kicker">${label}</div><div class="metric">${textValue(value)}</div><p>${help}</p></div>`; }
function renderRuntimeSummary() {
  const rt = state.runtime;
  return `<div class="card"><h4>Loaded Runtime Truth</h4><table class="table"><tbody>
    <tr><th>Source</th><td>${textValue(state.runtimeSource)}</td></tr>
    <tr><th>Timestamp</th><td>${textValue(rt.timestamp)}</td></tr>
    <tr><th>Stages Completed</th><td>${rt.counts.completed} / 30</td></tr>
    <tr><th>Stages Skipped</th><td>${rt.counts.skipped}</td></tr>
    <tr><th>Failed / Blocked</th><td>${rt.counts.failed}</td></tr>
    <tr><th>Evidence Items</th><td>${rt.evidence_chain.length}</td></tr>
  </tbody></table></div>`;
}

function renderSources() {
  const sourceData = state.runtime?.raw?.sources || state.runtime?.raw?.external_sources || state.runtime?.raw?.source_status || null;
  return `<div class="grid four">
    ${sourceCard('Market Data Feeds','Stock, sector, economic, commodity, currency signals.')}
    ${sourceCard('Company Intelligence','SEC filings, earnings, leadership, M&A, announcements.')}
    ${sourceCard('Technology Sources','Patents, papers, GitHub, APIs, technical systems.')}
    ${sourceCard('Regulatory / Competitor / Systems','Regulatory databases, competitors, legacy systems, infrastructure.')}
  </div><div class="section-title">Loaded Source State</div>${sourceData ? objectCard('Runtime Source Status', sourceData) : noRuntimeBlock()}`;
}
function sourceCard(title, body) { return `<div class="card"><div class="card-kicker">Source Domain</div><h4>${title}</h4><p>${body}</p></div>`; }

function renderACS2() {
  const loops = ['Discovery Loop','Analysis Loop','Synthesis Loop','Validation Loop','Regulatory Loop','Marketing Loop','Execution Loop','Decision Loop'];
  const data = state.runtime?.raw?.acs2_loops || state.runtime?.raw?.aie_loops || state.runtime?.raw?.intelligence_loops;
  return `<div class="grid four">${loops.map(l => `<div class="card"><div class="card-kicker">ACS2</div><h4>${l}</h4><p>Loop events should hand governed signals into Stage 1 or enrich existing lifecycle evidence.</p></div>`).join('')}</div><div class="section-title">Loaded Loop Activity</div>${data ? objectCard('Runtime ACS2/AIE Loop Data', data) : noRuntimeBlock()}`;
}

function renderLifecycle() {
  return `<div class="grid four">
    ${metricCard('Completed', state.runtime?.counts.completed ?? 'not_loaded', 'Stages marked completed.')}
    ${metricCard('Skipped', state.runtime?.counts.skipped ?? 'not_loaded', 'Stages skipped by route.')}
    ${metricCard('Failed/Blocked', state.runtime?.counts.failed ?? 'not_loaded', 'Stages requiring intervention.')}
    ${metricCard('Reported', state.runtime?.counts.reported ?? 'not_loaded', 'Stage states found in runtime output.')}
  </div><div class="section-title">30-Stage Execution Mirror</div><div class="stage-grid">${STAGE_REGISTRY.map(renderStageCard).join('')}</div>`;
}

function renderStageCard(stage) {
  const s = stageStatus(stage.number); const loaded = state.runtime?.stage_map?.[stage.number];
  const classes = ['stage-card']; if ([16,17,18,19,20,21,22].includes(stage.number)) classes.push('critical');
  if (routeObj()?.required_stages?.includes(stage.number)) classes.push('selected-route');
  return `<div class="${classes.join(' ')}"><div class="stage-num">${String(stage.number).padStart(2,'0')}</div><div class="stage-name">${stage.name}</div><span class="status ${s}">${titleCase(s)}</span><p class="stage-purpose">${stage.purpose}</p>${loaded?.reason ? `<p class="small"><b>Reason:</b> ${textValue(loaded.reason)}</p>` : ''}${loaded?.summary ? `<p class="small"><b>Summary:</b> ${textValue(loaded.summary)}</p>` : ''}</div>`;
}

function renderRouteGate() {
  const rt = state.runtime;
  const selected = rt?.route_selected || 'not_loaded';
  return `<div class="route-board"><div>
    <div class="card"><div class="card-kicker">Selected Route</div><h4>${titleCase(selected)}</h4><p>${routeObj()?.description || 'No route selected from runtime output yet.'}</p><table class="table"><tbody>
      <tr><th>Route Confidence</th><td>${textValue(rt?.route_decision?.route_confidence || rt?.route_decision?.confidence || rt?.confidence_scores?.route_confidence)}</td></tr>
      <tr><th>Route Reason</th><td>${textValue(rt?.route_decision?.route_reason || rt?.route_decision?.reason || rt?.route_decision?.rationale)}</td></tr>
      <tr><th>Terminal State</th><td>${textValue(rt?.terminal_state || 'not_loaded')}</td></tr>
      <tr><th>Terminal Fit</th><td>${textValue(checkTerminalFit())}</td></tr>
    </tbody></table></div>
    <div class="section-title">Route Required Stages</div>${renderRouteStagePills(selected)}
  </div><div><div class="section-title">Route Branches</div><div class="route-list">${Object.entries(ROUTE_REGISTRY).map(([id,r]) => renderRouteCard(id,r,selected)).join('')}</div></div></div>`;
}

function renderRouteCard(id, r, selected) {
  const active = id === selected; const rejected = state.runtime?.routes_rejected?.some(x => normalizeRoute(x.route || x.name || x) === id);
  return `<div class="route-card ${active ? 'active' : rejected ? 'rejected' : ''}"><h4>${r.label}</h4><span class="status ${active ? 'completed' : rejected ? 'skipped_by_route' : 'not_reported'}">${active ? 'Selected' : rejected ? 'Rejected' : 'Not Selected'}</span><p>${r.description}</p>${renderRouteStagePills(id)}</div>`;
}

function renderRouteStagePills(routeId) {
  const r = ROUTE_REGISTRY[routeId]; if (!r) return '<div class="empty"><p>No route stage contract is available for this route.</p></div>';
  return `<div class="route-stages">${r.required_stages.map(n => { const s=stageStatus(n); const critical = r.critical_stages?.includes(n); return `<span class="stage-pill ${s === 'completed' ? 'done' : s === 'skipped_by_route' ? 'skip' : ['failed','blocked'].includes(s) ? 'fail' : ''} ${critical ? 'critical' : ''}">${n} ${titleCase(s)}</span>`; }).join('')}</div>`;
}
function checkTerminalFit() { const r = routeObj(); const t = state.runtime?.terminal_state; if (!r || !t) return 'not_reported'; return r.terminal_states.includes(t) ? 'terminal_matches_route' : 'terminal_not_listed_for_route'; }

function renderRouteSurface(routeId) {
  const r = ROUTE_REGISTRY[routeId]; const active = state.runtime?.route_selected === routeId;
  return `<div class="card"><div class="card-kicker">${active ? 'Active Route' : 'Route Surface'}</div><h4>${r.label}</h4><p>${r.description}</p><span class="status ${active ? 'completed' : 'not_reported'}">${active ? 'Selected' : 'Not Selected'}</span></div><div class="section-title">Route Stage Contract</div>${renderRouteStagePills(routeId)}<div class="section-title">Route Runtime Data</div>${active && state.runtime ? objectCard(r.label + ' Runtime Payload', collectRoutePayload(routeId)) : noRuntimeBlock()}`;
}

function collectRoutePayload(routeId) {
  const raw = state.runtime?.raw || {};
  const keys = Object.keys(raw).filter(k => norm(k).includes(routeId) || (routeId === 'design' && (norm(k).includes('design') || norm(k).includes('invention') || norm(k).includes('solution'))));
  const out = { route_selected: state.runtime?.route_selected, route_decision: state.runtime?.route_decision };
  for (const k of keys) out[k] = raw[k];
  return out;
}

function renderAutoDesign() {
  const active = state.runtime?.route_selected === 'design';
  return `<div class="card"><div class="card-kicker">Stages 16-22</div><h4>AutoDesign / Design Portal Execution</h4><p>This surface preserves the critical block from the architecture map. It activates only when the route is design/system/invention/solution. No simulation is shown until real stage outputs exist.</p><span class="status ${active ? 'completed' : 'not_reported'}">${active ? 'Active' : 'Inactive / Not Selected'}</span></div><div class="section-title">Critical Design Execution Stages</div><div class="stage-grid">${STAGE_REGISTRY.filter(s => s.number >= 16 && s.number <= 22).map(renderStageCard).join('')}</div><div class="section-title">Stage 16-22 Payloads</div>${renderDesignPayloadTable()}`;
}

function renderDesignPayloadTable() {
  if (!state.runtime) return noRuntimeBlock();
  const rows = STAGE_REGISTRY.filter(s => s.number>=16 && s.number<=22).map(s => `<tr><td>${s.number}</td><td>${s.name}</td><td><span class="status ${stageStatus(s.number)}">${titleCase(stageStatus(s.number))}</span></td><td class="code">${textValue(stagePayload(s.number)).slice(0,900)}</td></tr>`).join('');
  return `<table class="table"><thead><tr><th>#</th><th>Stage</th><th>Status</th><th>Runtime Payload</th></tr></thead><tbody>${rows}</tbody></table>`;
}

function renderTechnology() {
  const active = ['design','breakthrough'].includes(state.runtime?.route_selected);
  const data = state.runtime?.raw?.technology_intelligence || state.runtime?.raw?.technology_layer || state.runtime?.raw?.tech_stack;
  return `<div class="card"><div class="card-kicker">Route-Aware Layer</div><h4>Technology Intelligence</h4><p>Should activate for design/software/system construction routes and remain secondary for normal portfolio route execution.</p><span class="status ${active ? 'running' : 'not_reported'}">${active ? 'Eligible Route' : 'Not Route-Active'}</span></div><div class="section-title">Loaded Technology Payload</div>${data ? objectCard('Technology Intelligence Runtime Data', data) : noRuntimeBlock()}`;
}

function renderValidation() {
  if (!state.runtime) return noRuntimeBlock();
  const rt = state.runtime; const checks = [
    ['Route selected', rt.route_selected !== 'not_reported'], ['Terminal state present', rt.terminal_state !== 'not_reported'], ['Validation reported', rt.validation_result.status !== 'not_reported'], ['Evidence chain reported', rt.evidence_chain.length > 0], ['All 30 stage states reported', rt.counts.reported >= 30], ['Route terminal fit', checkTerminalFit() === 'terminal_matches_route']
  ];
  return `<div class="grid three">${metricCard('Validation', rt.validation_result.status, 'Final validation authority result.')}${metricCard('Terminal Fit', checkTerminalFit(), 'Whether terminal state matches selected route contract.')}${metricCard('Evidence', rt.evidence_chain.length, 'Evidence items loaded.')}</div><div class="section-title">Proof Checks</div><table class="table"><tbody>${checks.map(([name,ok]) => `<tr><th>${name}</th><td><span class="status ${ok ? 'pass':'fail'}">${ok ? 'PASS':'FAIL / PENDING'}</span></td></tr>`).join('')}</tbody></table><div class="section-title">Validation Payload</div>${objectCard('Raw Validation', rt.validation_result.raw)}`;
}

function renderEvidence() {
  if (!state.runtime) return noRuntimeBlock();
  const evidence = state.runtime.evidence_chain;
  if (!evidence.length) return `<div class="empty"><h4>No evidence chain reported</h4><p>The runtime output loaded, but no evidence chain was found. Future runs should include source references per stage and route decision.</p></div>`;
  return evidence.map((e, i) => `<div class="evidence-item"><b>Evidence ${i+1} — ${textValue(e.title || e.source || e.id || e.stage || 'source')}</b><p>${textValue(e.summary || e.description || e.claim || e).slice(0,700)}</p></div>`).join('');
}

function renderMemory() {
  if (!state.runtime) return noRuntimeBlock();
  return `<div class="grid two"><div class="card"><div class="card-kicker">Memory Eligibility</div><h4>${textValue(state.runtime.memory_eligibility)}</h4><p>Only validated outputs should become memory or recursive feedback candidates.</p></div>${objectCard('Memory Payload', state.runtime.raw.memory || state.runtime.raw.recursive_feedback || state.runtime.raw.lifecycle_memory || {})}</div>`;
}

function renderRuntime() {
  return `<div class="grid two"><div class="card"><div class="card-kicker">Runtime Source Search</div><h4>Approved Runtime Truth Locations</h4><p>The browser attempts to load only explicit runtime output locations.</p><div class="code">${RUNTIME_LOCATIONS.join('\n')}</div></div><div class="card"><div class="card-kicker">Load Result</div><h4>${state.runtimeSource ? 'Runtime Loaded' : 'No Runtime Loaded'}</h4><p>${state.runtimeSource || state.loadError || 'No refresh attempted yet.'}</p></div></div><div class="section-title">Raw Runtime Summary</div>${state.runtime ? objectCard('Runtime Truth Object', state.runtime.raw) : noRuntimeBlock()}`;
}

function renderUpdatePacks() {
  return `<div class="grid two"><div class="card"><div class="card-kicker">v17.57</div><h4>Runtime Execution Mirror Pack</h4><p>Closes the gap between current dashboard shell and actual 30-stage lifecycle proof.</p></div><div class="card"><div class="card-kicker">v17.58</div><h4>Route Gate + Route Branch Pack</h4><p>Closes the route ambiguity gap: selected route, rejected routes, confidence, reasons, and required stage execution.</p></div></div><div class="section-title">Next Builds</div><table class="table"><tbody><tr><th>v17.59</th><td>AutoDesign / Stages 16-22 Runtime Surface hardening</td></tr><tr><th>v17.60</th><td>Validation Authority + Evidence Traceability</td></tr><tr><th>v17.61</th><td>Cleanup / UI Stabilization after functionality proof</td></tr><tr><th>v17.62</th><td>Design Simulation Portal Foundation after real design-route data is reliable</td></tr></tbody></table>`;
}

function objectCard(title, obj) { return `<div class="card"><div class="card-kicker">Runtime Payload</div><h4>${title}</h4><pre class="code">${textValue(obj).slice(0,5000)}</pre></div>`; }

function renderProofbar() {
  const rt = state.runtime;
  const items = [['Run', rt?.run_id || 'not_loaded'], ['Route', rt?.route_selected || 'not_loaded'], ['Terminal', rt?.terminal_state || 'not_loaded'], ['Stages', rt ? `${rt.counts.completed}/30 complete` : 'not_loaded'], ['Validation', rt?.validation_result?.status || 'not_loaded'], ['Memory', rt?.memory_eligibility || 'not_loaded']];
  $('proofbar').innerHTML = items.map(([label,value]) => `<div class="proof-item"><div class="proof-label">${label}</div><div class="proof-value">${textValue(value)}</div></div>`).join('');
}

function boot() {
  initNav(); render(); addEvent('Dashboard booted', 'Claire Operating Environment v17.57-v17.58 loaded. Runtime data is not invented; refresh to load real output.', 'info');
  $('refresh-runtime')?.addEventListener('click', refreshRuntime);
  refreshRuntime();
}

document.addEventListener('DOMContentLoaded', boot);
