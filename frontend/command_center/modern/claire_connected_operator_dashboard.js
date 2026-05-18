const endpoints = [
  "http://127.0.0.1:8000/operator/dashboard/state",
  "http://localhost:8000/operator/dashboard/state",
  "/operator/dashboard/state",
  "/dashboard/state"
];

let currentState = null;

const $ = (id) => document.getElementById(id);

function statusClass(status) {
  const s = String(status || "not_loaded").toLowerCase().replace(/[^a-z0-9]+/g, "_");
  if (s.includes("present") || s.includes("passed") || s.includes("ready") || s.includes("loaded") || s.includes("online")) return "status-present";
  if (s.includes("missing") || s.includes("blocked") || s.includes("failed") || s.includes("stop")) return "status-missing";
  return "status-not_loaded";
}

function safe(value, fallback = "Not loaded") {
  if (value === null || value === undefined || value === "" || value === "not_loaded") return fallback;
  if (typeof value === "object") return JSON.stringify(value, null, 2).slice(0, 900);
  return String(value);
}

function card(item) {
  const status = item.status || "missing";
  return `<article class="card">
    <h4>${item.label || item.key || "Surface"} <span class="${statusClass(status)}">${status}</span></h4>
    <p>${safe(item.value)}</p>
    ${item.description ? `<p>${item.description}</p>` : ""}
  </article>`;
}

function simpleCard(label, status, value) {
  return card({ label, status, value });
}

async function fetchState() {
  let lastError = null;
  for (const url of endpoints) {
    try {
      const res = await fetch(url, { cache: "no-store" });
      if (!res.ok) throw new Error(`${url} returned ${res.status}`);
      const data = await res.json();
      data.__endpoint = url;
      return data;
    } catch (err) {
      lastError = err;
    }
  }
  throw lastError || new Error("No dashboard state endpoint responded.");
}

function renderScorecards(state) {
  const cards = Object.values(state.scorecards || {});
  $("scorecards").innerHTML = cards.map(s => `
    <article class="score">
      <span>${s.label}</span>
      <strong class="${statusClass(s.status)}">${safe(s.value)}</strong>
    </article>
  `).join("");
}

function renderRouteCards(state) {
  const surfaces = state.surfaces || {};
  const keys = ["signal_basis", "trend_discovery", "thesis", "discovery", "breakthrough", "advancement_path"];
  $("routeCards").innerHTML = keys.map(k => card(surfaces[k] || { key: k, label: k, status: "missing", value: "Not loaded" })).join("");
  $("discoveryCards").innerHTML = keys.map(k => card(surfaces[k] || { key: k, label: k, status: "missing", value: "Not loaded" })).join("");
}

function renderDesign(state) {
  const auto = state.autodesign || {};
  const portal = state.design_portal || {};
  $("autodesignStatus").textContent = safe(auto.status, "missing");
  $("designCards").innerHTML = [
    simpleCard("AutoDesign", auto.status || "missing", auto.problem_statement),
    simpleCard("Invention Need", auto.required ? "present" : "not_required", auto.invention_need),
    simpleCard("Architecture Summary", portal.status || "missing", portal.architecture_summary),
    simpleCard("Blueprint Summary", portal.status || "missing", portal.blueprint_summary),
    simpleCard("Component Map", portal.status || "missing", portal.component_map),
    simpleCard("Technology Stack", portal.status || "missing", portal.technology_stack),
  ].join("");
}

function renderPortfolio(state) {
  const s = state.surfaces || {};
  $("portfolioCards").innerHTML = [
    card(s.portfolio || { label: "Portfolio", status: "missing", value: "Not loaded" }),
    card(s.strategy || { label: "Strategy", status: "missing", value: "Not loaded" }),
    card(s.next_actions || { label: "Next Actions", status: "missing", value: "Not loaded" }),
  ].join("");
}

function renderAcquisition(state) {
  const s = state.surfaces || {};
  $("acquisitionCards").innerHTML = [
    card(s.acquisition || { label: "Acquisition", status: "missing", value: "Not loaded" }),
    card(s.final_package || { label: "Final Package", status: "missing", value: "Not loaded" }),
    simpleCard("User-Facing Result", state.proof?.status || "missing", state.proof?.stop_go?.recommendation || "Not loaded"),
  ].join("");
}

function renderInternet(state) {
  const internet = state.internet || {};
  $("internetStatus").textContent = safe(internet.status, "not_loaded");
  $("internetCards").innerHTML = [
    simpleCard("Internet Status", internet.status || "missing", internet.mode),
    simpleCard("Static Readiness", internet.readiness?.static_internet_readiness ? "present" : "missing", JSON.stringify(internet.readiness || {}, null, 2)),
    simpleCard("Blockers", internet.blockers?.length ? "blocked" : "present", (internet.blockers || []).join("\n") || "No blockers loaded"),
    simpleCard("Warnings", internet.warnings?.length ? "warning" : "present", (internet.warnings || []).join("\n") || "No warnings loaded"),
  ].join("");
}

function renderUpdates(state) {
  const updates = state.updates || {};
  $("updateStatus").textContent = safe(updates.status, "Guarded");
  $("updateCards").innerHTML = [
    simpleCard("Staged Packs", updates.staged_pack_count ? "present" : "missing", updates.staged_pack_count),
    simpleCard("Rollback Plans", updates.rollback_plan_count ? "present" : "missing", updates.rollback_plan_count),
    simpleCard("Runner Gate", updates.runner_gate || "missing", updates.runner_gate),
    simpleCard("Regression Lock", updates.regression_lock_active ? "present" : "missing", updates.regression_lock_active ? "Active" : "Missing"),
    simpleCard("Automatic Updates", updates.automatic_updates_enabled ? "blocked" : "present", "Disabled / guarded"),
  ].join("");
}

function renderState(state) {
  currentState = state;
  $("connectionStatus").textContent = `Backend Online — ${state.__endpoint || "operator state"}`;
  $("connectionStatus").className = "connection online";
  $("truthState").textContent = state.source?.runtime_truth_loaded ? "runtime truth loaded" : "runtime truth missing";
  $("missionTitle").textContent = safe(state.mission?.title, "Claire route decision");
  $("missionSummary").textContent = safe(state.mission?.summary, "No mission summary loaded");
  $("stopGoStatus").textContent = safe(state.proof?.status || state.mission?.status, "not_loaded");
  $("routeStatus").textContent = safe(state.route_gate?.status, "not_loaded");
  $("routeFamily").textContent = safe(state.route_gate?.route_family, "not_loaded");
  $("routeSummary").textContent = safe(state.route_gate?.summary, "The dashboard shows actual route surfaces from runtime truth.");
  $("routePortfolio").textContent = safe(state.surfaces?.portfolio?.status === "present" ? "Loaded" : "Trend to action");
  $("routeBreakthrough").textContent = safe(state.surfaces?.breakthrough?.status === "present" ? "Loaded" : "Conditional escalation");
  $("routeDesign").textContent = state.autodesign?.required ? "Required by route" : "Conditional";
  $("routePackage").textContent = safe(state.surfaces?.final_package?.status === "present" ? "Loaded" : "Strategic output");

  renderScorecards(state);
  renderRouteCards(state);
  renderDesign(state);
  renderPortfolio(state);
  renderAcquisition(state);
  renderInternet(state);
  renderUpdates(state);

  $("diagnosticStatus").textContent = "loaded";
  $("diagnosticsJson").textContent = JSON.stringify(state, null, 2);
}

function renderOffline(error) {
  $("connectionStatus").textContent = "Backend Offline — run LAUNCH_CLAIRE.bat";
  $("connectionStatus").className = "connection offline";
  $("truthState").textContent = "no backend state loaded";
  $("missionSummary").textContent = "Start the backend to load /operator/dashboard/state. Missing data stays missing.";
  $("diagnosticStatus").textContent = "offline";
  $("diagnosticsJson").textContent = String(error?.message || error || "Backend offline");
}

async function refresh() {
  try {
    renderState(await fetchState());
  } catch (err) {
    renderOffline(err);
  }
}

document.querySelectorAll("nav button").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll("nav button").forEach(b => b.classList.remove("active"));
    document.querySelectorAll(".panel").forEach(p => p.classList.remove("visible"));
    btn.classList.add("active");
    const target = document.getElementById(btn.dataset.section);
    if (target) target.classList.add("visible");
  });
});

$("refreshButton").addEventListener("click", refresh);
$("searchBox").addEventListener("input", (event) => {
  const q = event.target.value.toLowerCase().trim();
  document.querySelectorAll(".card,.mini,.score").forEach(el => {
    el.style.display = !q || el.innerText.toLowerCase().includes(q) ? "" : "none";
  });
});

refresh();
setInterval(refresh, 15000);
