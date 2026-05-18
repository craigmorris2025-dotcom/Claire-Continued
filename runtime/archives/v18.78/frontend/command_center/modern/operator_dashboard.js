const state = {
  view: "overview",
  backend: null,
  lastUpdated: null,
};

const routes = {
  health: ["/health", "/"],
  internetDashboard: ["/internet/ops/dashboard", "/internet/operations/dashboard"],
  dashboardState: ["/dashboard/state", "/api/dashboard/state"],
  launchLock: ["/launch/regression-lock", "/api/launch/regression-lock"],
  sourceTrust: ["/internet/source-trust", "/api/internet/source-trust"],
  campaigns: ["/internet/campaigns", "/api/internet/campaigns"],
};

const views = {
  overview: {
    title: "Overview",
    subtitle: "A plain-language operational view of Claire readiness, blockers, live status, and next safe action.",
  },
  internet: {
    title: "Internet Operations",
    subtitle: "Governed search, external evidence, bounded online execution, and internet runtime state.",
  },
  campaigns: {
    title: "Campaigns",
    subtitle: "Persistent longitudinal intelligence campaigns, refresh cycles, and campaign lifecycle state.",
  },
  trust: {
    title: "Source Trust",
    subtitle: "Adaptive source reputation, evidence weighting, quarantine, release, and trust risk.",
  },
  runtime: {
    title: "Runtime Health",
    subtitle: "Runtime stability, degraded-mode status, recovery protection, and orchestration safety.",
  },
  deployment: {
    title: "Deployment",
    subtitle: "Production hardening, rollback continuity, manifest state, and deployment safety.",
  },
  launch: {
    title: "Launch Lock",
    subtitle: "Regression lock, invariant protection, governance boundary status, and release readiness.",
  },
  actions: {
    title: "Actions",
    subtitle: "Safe operator actions with visible availability and route checks.",
  },
};

function el(tag, attrs = {}, children = []) {
  const node = document.createElement(tag);
  Object.entries(attrs).forEach(([key, value]) => {
    if (key === "class") node.className = value;
    else if (key === "text") node.textContent = value;
    else node.setAttribute(key, value);
  });
  children.forEach((child) => node.append(child));
  return node;
}

async function firstJson(routeList) {
  for (const route of routeList) {
    try {
      const response = await fetch(route, { cache: "no-store" });
      if (!response.ok) continue;
      const text = await response.text();
      try {
        return { route, ok: true, data: JSON.parse(text) };
      } catch {
        return { route, ok: true, data: { raw: text.slice(0, 500) } };
      }
    } catch {
      continue;
    }
  }
  return { route: null, ok: false, data: null };
}

async function loadBackendState() {
  const checks = {};
  await Promise.all(Object.entries(routes).map(async ([name, routeList]) => {
    checks[name] = await firstJson(routeList);
  }));

  state.backend = {
    checks,
    health: checks.health.ok ? "online" : "unavailable",
    dashboardState: checks.dashboardState.data,
    internet: checks.internetDashboard.ok,
    campaigns: checks.campaigns.ok,
    trust: checks.sourceTrust.ok,
    launchLock: checks.launchLock.ok,
  };
  state.lastUpdated = new Date();
}

function badge(ok, goodText = "Available", badText = "Needs wiring") {
  return el("span", { class: `badge ${ok ? "good" : "warn"}`, text: ok ? goodText : badText });
}

function panel(title, body, options = {}) {
  return el("section", { class: `panel ${options.className || ""}` }, [
    el("h2", { text: title }),
    ...(Array.isArray(body) ? body : [body]),
  ]);
}

function metric(label, valueNode) {
  return el("div", { class: "metric" }, [
    el("span", { text: label }),
    typeof valueNode === "string" ? el("strong", { text: valueNode }) : valueNode,
  ]);
}

function renderStrip() {
  const strip = document.getElementById("status-strip");
  strip.innerHTML = "";

  const backend = state.backend || {};
  const items = [
    ["Backend", backend.health === "online" ? "Online" : "Unavailable"],
    ["Internet Ops", backend.internet ? "Route found" : "Needs wiring"],
    ["Campaigns", backend.campaigns ? "Route found" : "Needs wiring"],
    ["Launch Lock", backend.launchLock ? "Route found" : "Needs wiring"],
  ];

  for (const [label, value] of items) {
    strip.append(el("div", { class: "status-pill" }, [
      el("span", { text: label }),
      el("strong", { text: value }),
    ]));
  }
}

function overviewView() {
  const backend = state.backend || {};
  return [
    panel("Operational Readiness", [
      metric("Backend health", badge(backend.health === "online", "Online", "Unavailable")),
      metric("Dashboard state route", badge(backend.checks?.dashboardState?.ok, "Connected", "Missing")),
      metric("Internet ops route", badge(backend.internet, "Connected", "Missing")),
      metric("Launch lock route", badge(backend.launchLock, "Connected", "Missing")),
    ], { className: "wide" }),
    panel("What This Dashboard Is Now", el("p", { text: "This is the operator layer: it shows what Claire can actually use, what is missing, and what should be fixed before live operational work." })),
    panel("Current Safest Next Action", el("div", { class: "notice" }, [
      el("p", { text: "Use this dashboard to identify route gaps and stale backend/frontend assumptions before running a real live campaign." }),
    ]), { className: "full" }),
  ];
}

function internetView() {
  const backend = state.backend || {};
  return [
    panel("Internet Runtime", [
      metric("Operations dashboard route", badge(backend.internet, "Available", "Missing")),
      metric("Governed action script", el("span", { class: "badge info", text: "Dashboard-managed" })),
      el("p", { text: "This section should become the user-friendly surface for governed external search, evidence baskets, and online runtime status." }),
    ], { className: "wide" }),
    panel("Missing Data Rule", el("p", { text: "If live internet state is unavailable, the UI must say so. It must not pretend a campaign or source check succeeded." })),
  ];
}

function campaignsView() {
  const backend = state.backend || {};
  return [
    panel("Campaign Lifecycle", [
      metric("Campaign route", badge(backend.campaigns, "Available", "Missing")),
      metric("Refresh cycles", el("span", { class: "badge warn", text: "Awaiting live state" })),
      metric("Persistence", el("span", { class: "badge warn", text: "Awaiting proof" })),
    ], { className: "wide" }),
    panel("Operator Meaning", el("p", { text: "Campaigns should show objective, cadence, last run, evidence count, trust risk, next refresh, and final status." })),
  ];
}

function trustView() {
  const backend = state.backend || {};
  return [
    panel("Source Trust Intelligence", [
      metric("Source trust route", badge(backend.trust, "Available", "Missing")),
      metric("Quarantine state", el("span", { class: "badge warn", text: "Awaiting data" })),
      metric("Reputation memory", el("span", { class: "badge warn", text: "Awaiting data" })),
    ], { className: "wide" }),
    panel("Trust Principle", el("p", { text: "Trust should be visible before evidence is trusted. This dashboard should show why a source is weighted, quarantined, or released." })),
  ];
}

function runtimeView() {
  return [
    panel("Runtime Safety", [
      metric("Bounded orchestration", el("span", { class: "badge good", text: "Protected by architecture" })),
      metric("Degraded mode", el("span", { class: "badge warn", text: "Needs live signal" })),
      metric("Recovery", el("span", { class: "badge warn", text: "Needs live signal" })),
    ], { className: "wide" }),
    panel("No Fake Green", el("p", { text: "Runtime health should distinguish installed, reachable, executing, degraded, blocked, and failed states." })),
  ];
}

function deploymentView() {
  return [
    panel("Deployment Hardening", [
      metric("Rollback safety", el("span", { class: "badge good", text: "Installed" })),
      metric("Manifest state", el("span", { class: "badge good", text: "Installed" })),
      metric("Production config", el("span", { class: "badge warn", text: "Verify locally" })),
    ], { className: "wide" }),
    panel("Deployment View Goal", el("p", { text: "Show exact deploy readiness, blocked checks, rollback state, installed build chain, and manifest mismatches." })),
  ];
}

function launchView() {
  const backend = state.backend || {};
  return [
    panel("Launch Regression Lock", [
      metric("Launch route", badge(backend.launchLock, "Available", "Missing")),
      metric("Invariant lock", el("span", { class: "badge good", text: "Installed" })),
      metric("Real launch proof", el("span", { class: "badge warn", text: "Not yet proven" })),
    ], { className: "wide" }),
    panel("Honest Status", el("p", { text: "Launch lock means install/regression protection exists. It does not mean the platform has been used under real operational load." })),
  ];
}

function actionsView() {
  const actionList = [
    ["Refresh dashboard state", "Reload backend routes and visible readiness.", refresh],
    ["Check route availability", "Verify important backend routes are reachable.", refresh],
    ["Open use guide", "Show operator sequence and safety rules.", () => document.getElementById("guide-dialog").showModal()],
    ["Prepare live campaign", "Placeholder-free UI slot: disabled until route and schema are confirmed.", null],
  ];

  const buttons = actionList.map(([title, description, handler]) => {
    const button = el("button", { class: "action-button", type: "button" }, [
      el("strong", { text: title }),
      el("span", { text: description }),
    ]);
    if (handler) button.addEventListener("click", handler);
    else {
      button.disabled = true;
      button.style.opacity = "0.56";
      button.title = "Disabled until backend route and schema are verified.";
    }
    return button;
  });

  return [
    panel("Safe Operator Actions", el("div", { class: "action-grid" }, buttons), { className: "full" }),
  ];
}

const renderers = {
  overview: overviewView,
  internet: internetView,
  campaigns: campaignsView,
  trust: trustView,
  runtime: runtimeView,
  deployment: deploymentView,
  launch: launchView,
  actions: actionsView,
};

function render() {
  const meta = views[state.view];
  document.getElementById("view-title").textContent = meta.title;
  document.getElementById("view-subtitle").textContent = meta.subtitle;

  document.querySelectorAll(".nav-item").forEach((button) => {
    button.classList.toggle("active", button.dataset.view === state.view);
  });

  renderStrip();

  const content = document.getElementById("dashboard-content");
  content.innerHTML = "";
  const nodes = renderers[state.view]();
  nodes.forEach((node) => content.append(node));
}

async function refresh() {
  await loadBackendState();
  render();
}

document.querySelectorAll(".nav-item").forEach((button) => {
  button.addEventListener("click", () => {
    state.view = button.dataset.view;
    render();
  });
});

document.getElementById("refresh-state").addEventListener("click", refresh);
document.getElementById("open-guide").addEventListener("click", () => {
  document.getElementById("guide-dialog").showModal();
});

refresh();

// CLAIRE_V18_75_JS
window.ClaireDashboardPacks = window.ClaireDashboardPacks || {};
window.ClaireDashboardPacks["v18.75"] = {
  version: "v18.75",
  title: "Dashboard Search Result Card Renderer Lock",
  normalSearchEndpoint: "/api/dashboard/search/live",
  providerStatusEndpoint: "/api/dashboard/search/provider/status",
  providerProbeEndpoint: "/api/dashboard/search/smoke/google",
  dashboardCurrent: true,
  providerProbeManualOnly: true,
  explicitEnableRequired: true,
  proof: "result-card",
  expectedResult: { title: "Google", url: "https://www.google.com" }
};
window.ClaireDashboardLatestPack = "v18.75";
// /CLAIRE_V18_75_JS

// CLAIRE_V18_76_JS
window.ClaireDashboardPacks = window.ClaireDashboardPacks || {};
window.ClaireDashboardPacks["v18.76"] = {
  version: "v18.76",
  title: "Dashboard Current-State Banner and Smoke Report",
  normalSearchEndpoint: "/api/dashboard/search/live",
  providerStatusEndpoint: "/api/dashboard/search/provider/status",
  providerProbeEndpoint: "/api/dashboard/search/smoke/google",
  dashboardCurrent: true,
  providerProbeManualOnly: true,
  explicitEnableRequired: true,
  proof: "current-state",
  expectedResult: { title: "Google", url: "https://www.google.com" }
};
window.ClaireDashboardLatestPack = "v18.76";
// /CLAIRE_V18_76_JS

// CLAIRE_V18_77_JS
window.ClaireDashboardPacks = window.ClaireDashboardPacks || {};
window.ClaireDashboardPacks["v18.77"] = {
  version: "v18.77",
  title: "Normal Search vs Manual Probe Route Guard",
  normalSearchEndpoint: "/api/dashboard/search/live",
  providerStatusEndpoint: "/api/dashboard/search/provider/status",
  providerProbeEndpoint: "/api/dashboard/search/smoke/google",
  dashboardCurrent: true,
  providerProbeManualOnly: true,
  explicitEnableRequired: true,
  proof: "route-guard",
  expectedResult: { title: "Google", url: "https://www.google.com" }
};
window.ClaireDashboardLatestPack = "v18.77";
// /CLAIRE_V18_77_JS
