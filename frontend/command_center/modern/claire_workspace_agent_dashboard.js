const stateEndpoints = [
  "http://127.0.0.1:8000/operator/dashboard/state",
  "http://localhost:8000/operator/dashboard/state",
  "/operator/dashboard/state",
  "/dashboard/state"
];

const searchEndpoints = [
  "http://127.0.0.1:8000/operator/search/query",
  "http://localhost:8000/operator/search/query",
  "/operator/search/query"
];

const capabilityEndpoints = [
  "http://127.0.0.1:8000/operator/search/capabilities",
  "http://localhost:8000/operator/search/capabilities",
  "/operator/search/capabilities"
];

let currentState = null;
let currentCapabilities = null;

const $ = id => document.getElementById(id);

function statusClass(status) {
  const s = String(status || "not_loaded").toLowerCase().replace(/[^a-z0-9]+/g, "_");
  if (s.includes("present") || s.includes("passed") || s.includes("ready") || s.includes("online") || s.includes("completed")) return "status-present";
  if (s.includes("missing") || s.includes("blocked") || s.includes("failed") || s.includes("stop")) return "status-missing";
  if (s.includes("warning") || s.includes("prepared")) return "status-warning";
  return "status-warning";
}
function safe(value, fallback = "Not loaded") {
  if (value === null || value === undefined || value === "" || value === "not_loaded") return fallback;
  if (typeof value === "object") return JSON.stringify(value, null, 2).slice(0, 1200);
  return String(value);
}
function simpleCard(label, status, value) {
  return `<article class="card">
    <h4>${label} <span class="${statusClass(status)}">${safe(status)}</span></h4>
    <p>${safe(value)}</p>
  </article>`;
}
function surfaceCard(surface) {
  return simpleCard(surface?.label || surface?.key || "Surface", surface?.status || "missing", surface?.value || "Not loaded");
}
async function fetchFirst(urls, options = {}) {
  let lastErr = null;
  for (const url of urls) {
    try {
      const res = await fetch(url, { cache: "no-store", ...options });
      if (!res.ok) throw new Error(`${url} returned ${res.status}`);
      const data = await res.json();
      data.__endpoint = url;
      return data;
    } catch (err) {
      lastErr = err;
    }
  }
  throw lastErr || new Error("No endpoint responded");
}

function switchWorkspace(id) {
  document.querySelectorAll("[data-workspace]").forEach(b => b.classList.toggle("active", b.dataset.workspace === id));
  document.querySelectorAll(".panel").forEach(p => p.classList.toggle("visible", p.id === id));
  $("contextBody").innerHTML = `<p>Workspace: <strong>${id}</strong></p><p>Use the command/search bar to search local proof, runtime truth, or prepared web/agent modes.</p>`;
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

function renderState(state) {
  currentState = state;
  $("backendStatus").textContent = `Backend Online`;
  $("backendStatus").className = "status-pill online";
  $("missionTitle").textContent = safe(state.mission?.title, "Claire Syntalion");
  $("missionSummary").textContent = safe(state.mission?.summary, "No mission summary loaded");
  $("stopGoStatus").textContent = safe(state.proof?.status || state.mission?.status, "not loaded");
  $("routeFamily").textContent = safe(state.route_gate?.route_family, "not loaded");
  $("autodesignStatus").textContent = safe(state.autodesign?.status, "not loaded");
  $("designPortalStatus").textContent = safe(state.design_portal?.status, "not loaded");
  $("internetStatus").textContent = safe(state.internet?.status, "not loaded");
  $("updatesStatus").textContent = safe(state.updates?.status, "guarded");
  $("proofStatus").textContent = safe(state.proof?.status, "not loaded");
  renderScorecards(state);

  const s = state.surfaces || {};
  $("missionCards").innerHTML = [
    simpleCard("Selected Route", state.route_gate?.status, state.route_gate?.selected_route),
    simpleCard("Route Family", state.route_gate?.status, state.route_gate?.route_family),
    simpleCard("Terminal State", state.route_gate?.status, state.route_gate?.terminal_state),
    simpleCard("Stop/Go", state.proof?.status, state.proof?.stop_go?.recommendation),
  ].join("");

  $("routeCards").innerHTML = ["signal_basis","trend_discovery","thesis","discovery","breakthrough","advancement_path"].map(k => surfaceCard(s[k])).join("");
  $("discoveryCards").innerHTML = ["signal_basis","trend_discovery","thesis","discovery","breakthrough","advancement_path"].map(k => surfaceCard(s[k])).join("");

  $("autodesignCards").innerHTML = [
    simpleCard("Status", state.autodesign?.status, state.autodesign?.required ? "Required by current route" : "Conditional / not required by every route"),
    simpleCard("Problem Statement", state.autodesign?.status, state.autodesign?.problem_statement),
    simpleCard("Invention Need", state.autodesign?.status, state.autodesign?.invention_need),
    simpleCard("Design Portal Required", state.autodesign?.design_portal_required ? "present" : "not_required", state.autodesign?.design_portal_required),
  ].join("");

  $("designPortalCards").innerHTML = [
    simpleCard("Architecture", state.design_portal?.status, state.design_portal?.architecture_summary),
    simpleCard("Blueprint", state.design_portal?.status, state.design_portal?.blueprint_summary),
    simpleCard("Component Map", state.design_portal?.status, state.design_portal?.component_map),
    simpleCard("Technology Stack", state.design_portal?.status, state.design_portal?.technology_stack),
  ].join("");

  $("portfolioCards").innerHTML = [surfaceCard(s.portfolio), surfaceCard(s.strategy), surfaceCard(s.next_actions)].join("");
  $("acquisitionCards").innerHTML = [surfaceCard(s.acquisition), surfaceCard(s.final_package), simpleCard("Proof Recommendation", state.proof?.status, state.proof?.stop_go?.recommendation)].join("");

  $("internetCards").innerHTML = [
    simpleCard("Internet Mode", state.internet?.status, state.internet?.mode),
    simpleCard("Search Bar Web Mode", currentCapabilities?.modes?.normal_web_search?.enabled ? "present" : "prepared_not_executed", currentCapabilities?.modes?.normal_web_search?.reason),
    simpleCard("Governed Research", currentCapabilities?.modes?.governed_research_search?.enabled ? "present" : "prepared_not_executed", currentCapabilities?.modes?.governed_research_search?.reason),
    simpleCard("Warnings", state.internet?.warnings?.length ? "warning" : "present", (state.internet?.warnings || []).join("\\n") || "No warnings loaded"),
  ].join("");

  $("updatesCards").innerHTML = [
    simpleCard("Staged Packs", state.updates?.staged_pack_count ? "present" : "missing", state.updates?.staged_pack_count),
    simpleCard("Rollback Plans", state.updates?.rollback_plan_count ? "present" : "missing", state.updates?.rollback_plan_count),
    simpleCard("Runner Gate", state.updates?.runner_gate, state.updates?.runner_gate),
    simpleCard("Regression Lock", state.updates?.regression_lock_active ? "present" : "missing", state.updates?.regression_lock_active),
    simpleCard("Automatic Updates", state.updates?.automatic_updates_enabled ? "blocked" : "present", "Disabled / guarded"),
  ].join("");

  const domains = state.proof?.domain_status || {};
  $("proofCards").innerHTML = Object.entries(domains).map(([k,v]) => simpleCard(k, v, v)).join("") || simpleCard("Proof", state.proof?.status, state.proof?.stop_go?.recommendation);

  $("diagnosticsStatus").textContent = "loaded";
  $("diagnosticsJson").textContent = JSON.stringify({ state, capabilities: currentCapabilities }, null, 2);
}

function renderOffline(err) {
  $("backendStatus").textContent = "Backend Offline";
  $("backendStatus").className = "status-pill offline";
  $("missionSummary").textContent = "Run LAUNCH_CLAIRE.bat and press Refresh. The search bar remains visible, but backend search waits for /operator/search/query.";
  $("diagnosticsStatus").textContent = "offline";
  $("diagnosticsJson").textContent = String(err?.message || err);
}

async function refresh() {
  try {
    currentCapabilities = await fetchFirst(capabilityEndpoints).catch(() => null);
    const state = await fetchFirst(stateEndpoints);
    renderState(state);
  } catch (err) {
    renderOffline(err);
  }
}

function renderSearchResults(data) {
  $("searchResultsPanel").classList.remove("hidden");
  const mode = data.mode || "unknown";
  const status = data.status || data?.command?.plan?.status || "completed";
  let rows = `<div class="result-row"><strong>${mode}</strong> <span class="${statusClass(status)}">${status}</span><p>${safe(data.reason || data.query || "")}</p></div>`;
  const results = data.results || (data.command ? [data.command] : []);
  rows += results.map(r => {
    if (r.type === "runtime_system_result") {
      return `<div class="result-row"><code>${r.path}</code><p>${safe(r.snippet)}</p></div>`;
    }
    const plan = r.plan || r;
    const workspace = plan.workspace || plan?.plan?.workspace;
    return `<div class="result-row"><strong>${safe(r.intent || plan.action || "Result")}</strong><p>${safe(plan)}</p>${workspace ? `<button data-workspace-jump="${workspace}">Open ${workspace}</button>` : ""}</div>`;
  }).join("");
  $("searchResults").innerHTML = rows;
  document.querySelectorAll("[data-workspace-jump]").forEach(btn => btn.onclick = () => switchWorkspace(btn.dataset.workspaceJump));
}

async function runSearch() {
  const query = $("commandSearch").value.trim();
  const mode = $("modeSelect").value;
  if (!query) return;
  try {
    const data = await fetchFirst(searchEndpoints, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ query, mode, limit: 12 })
    });
    renderSearchResults(data);
  } catch (err) {
    $("searchResultsPanel").classList.remove("hidden");
    $("searchResults").innerHTML = `<div class="result-row"><strong class="status-missing">Backend search unavailable</strong><p>${safe(err.message)}</p><p>Visible dashboard filtering is still available.</p></div>`;
    const q = query.toLowerCase();
    document.querySelectorAll(".card,.score").forEach(el => el.style.display = !q || el.innerText.toLowerCase().includes(q) ? "" : "none");
  }
}

document.querySelectorAll("[data-workspace]").forEach(btn => btn.addEventListener("click", () => switchWorkspace(btn.dataset.workspace)));
document.querySelectorAll("[data-workspace-jump]").forEach(btn => btn.addEventListener("click", () => switchWorkspace(btn.dataset.workspaceJump)));
document.querySelector("[data-action='refresh']").addEventListener("click", refresh);
$("runSearch").addEventListener("click", runSearch);
$("commandSearch").addEventListener("keydown", e => { if (e.key === "Enter") runSearch(); });
$("closeSearch").addEventListener("click", () => $("searchResultsPanel").classList.add("hidden"));
$("drawerToggle").addEventListener("click", () => document.getElementById("contextDrawer").style.display = "none");

refresh();
setInterval(refresh, 15000);
