// Claire AI - Syntalion Intelligence Cockpit
// Canonical local dashboard controller. Presentation only; backend owns truth.

const NAV = [
  { id: "overview", icon: "O", label: "Overview" },
  { id: "lifecycle", icon: "L", label: "Lifecycle Pipeline" },
  { id: "signals", icon: "S", label: "Signal Feed" },
  { id: "breakthroughs", icon: "B", label: "Breakthroughs" },
  { id: "technology", icon: "T", label: "Tech Base" },
  { id: "design_portal", icon: "Y", label: "Design Portal" },
  { id: "portfolio", icon: "P", label: "Portfolio" },
  { id: "deals", icon: "D", label: "Deal Discovery" },
  { id: "acquirers", icon: "A", label: "Acquirer Match" },
  { id: "strategic_world", icon: "N", label: "Strategic World" },
  { id: "modes", icon: "M", label: "Mode Control" },
  { id: "active_controls", icon: "C", label: "Active Controls" },
  { id: "review_queue", icon: "Q", label: "Review Queue" },
  { id: "web_ops", icon: "W", label: "Web Ops" },
  { id: "first_run", icon: "F", label: "First Run" },
  { id: "internet", icon: "I", label: "Internet" },
  { id: "updates", icon: "U", label: "Updates" },
  { id: "accounts", icon: "A", label: "Accounts" },
  { id: "settings", icon: "S", label: "Settings" },
  { id: "admin", icon: "K", label: "Admin" },
  { id: "governance", icon: "G", label: "Governance" },
  { id: "learning", icon: "R", label: "Learning Loop" },
  { id: "subsystems", icon: "W", label: "Subsystems" },
];

const KPI_KEYS = {
  "Operational Readiness": "platform_completion",
  "Project Files": "project_files_bound",
  "Missing Files": "project_files_missing",
  "Route Wires": "system_wiring_routes",
  "Wire Gaps": "system_wiring_missing",
  "Breakthroughs": "breakthroughs",
  "Portfolio Items": "portfolio_items",
  "Active Signals": "active_signals",
  "Acquirer Matches": "acquirer_matches",
  "Strategic Options": "strategic_world_options",
  "Recommendations": "strategic_world_recommendations",
  "First Run": "first_run_readiness",
  "Provider Lanes": "provider_stack_ready",
  "Provider Blocks": "provider_blockers",
  "Update Blocks": "update_blockers",
  "Available Updates": "available_updates",
  "Source Universes": "source_universes",
  "Safety Events": "safety_events",
  "Pipeline Score": "pipeline_score",
  "Active Pipelines": "active_pipelines",
  "Pipeline Gaps": "pipeline_gaps",
  "Tech Records": "technology_records",
  "Tech Readiness": "technology_readiness",
  "Manufacturable": "manufacturable_matches",
  "Capability Gaps": "discovery_candidates",
  "Pending Review": "pending_reviews",
  "Blocked": "blocked_items",
  "Errors": "blocked_items",
  "API Endpoint": "api_endpoint",
  "Version": "version",
};

let activeSection = "overview";
let dashboardState = {};
let commandPlan = null;
let platformBrowser = { url: "", title: "", status: "empty" };
let activeControlResult = null;
let updateGovernanceResult = null;

async function fetchJson(url, options) {
  const response = await fetch(url, options);
  if (!response.ok) {
    throw new Error(`${url} returned ${response.status}`);
  }
  return response.json();
}

function escapeText(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function records(name) {
  const value = dashboardState.records && dashboardState.records[name];
  return Array.isArray(value) ? value : [];
}

function metricValue(label, fallback = "N/A") {
  const key = KPI_KEYS[label];
  const metric = key && dashboardState.metrics ? dashboardState.metrics[key] : null;
  if (metric && metric.value !== null && metric.value !== undefined && metric.value !== "") {
    return metric.value;
  }
  if (label === "API Endpoint") return window.location.host || "localhost:8000";
  if (label === "Version") return "v19.61";
  return fallback;
}

function emptyState(title, detail) {
  return `<div class="empty-state"><strong>${escapeText(title)}</strong><small>${escapeText(detail)}</small></div>`;
}

function statusTag(value) {
  const text = value === true ? "YES" : value === false ? "NO" : String(value || "unknown");
  const lower = text.toLowerCase();
  const cls = lower.includes("blocked") || lower.includes("missing") || lower.includes("failed") || lower === "no"
    ? "tag-red"
    : lower.includes("gated") || lower.includes("review") || lower.includes("pending") || lower.includes("placeholder")
      ? "tag-amber"
      : "tag-green";
  return `<span class="tag ${cls}">${escapeText(text)}</span>`;
}

function kpi(label, icon, colorClass = "kpi-blue") {
  const key = KPI_KEYS[label];
  const metric = key && dashboardState.metrics ? dashboardState.metrics[key] : null;
  const source = metric && metric.source ? metric.source : "Backend sync";
  return `<div class="kpi-card ${colorClass}">
    <div class="kpi-icon">${escapeText(icon)}</div>
    <div class="kpi-label">${escapeText(label)}</div>
    <div class="kpi-value">${escapeText(metricValue(label))}</div>
    <div class="kpi-delta neutral">${escapeText(source)}</div>
  </div>`;
}

function sourceRow(title, meta, status) {
  return `<div class="source-row">
    <div class="source-title">${escapeText(title)}</div>
    <div class="source-meta">${escapeText(meta)}</div>
    <div class="source-status">${statusTag(status)}</div>
  </div>`;
}

function renderProjectFileBindings(limit = 18) {
  const bindings = dashboardState.project_file_bindings || {};
  const rows = Array.isArray(bindings.bindings) ? bindings.bindings : records("project_files");
  return rows.length
    ? rows.slice(0, limit).map((entry) => sourceRow(
      entry.label || entry.key || "Project file",
      `${entry.path || ""} / ${entry.surface || "surface"} / records ${entry.record_count ?? 0}`,
      entry.status || (entry.exists ? "bound" : "missing"),
    )).join("")
    : emptyState("No project file bindings", "Dashboard state has not exposed project-file bindings yet.");
}

function renderSystemWiring(limit = 12) {
  const wiring = dashboardState.system_wiring || {};
  const routes = Array.isArray(wiring.routes) ? wiring.routes.slice(0, limit) : [];
  return routes.length
    ? routes.map((route) => sourceRow(
      route.route,
      `${route.activation || ""} / stages ${route.stage_count || 0} / ${(route.dashboard_fields || []).join(", ")}`,
      route.route === wiring.selected_route ? "selected" : "wired",
    )).join("")
    : emptyState("No route wiring map", "Dashboard state is not exposing canonical route wiring yet.");
}

function renderSystemOwners(limit = 16) {
  const groups = Array.isArray(dashboardState.system_wiring?.owner_groups)
    ? dashboardState.system_wiring.owner_groups.slice(0, limit)
    : [];
  return groups.length
    ? groups.map((group) => sourceRow(
      group.group,
      (group.files || []).map((item) => item.path).join(", "),
      group.status || "bound",
    )).join("")
    : emptyState("No owner map", "Project owner groups are not exposed by the dashboard state payload yet.");
}

function renderCommandPlan() {
  const plan = commandPlan || dashboardState.command_plan || {};
  if (!plan || !plan.query) {
    return emptyState("No command plan yet", "Use the cockpit search bar to create a governed research plan from local source universes and evidence.");
  }
  const knowledge = plan.local_knowledge_matches || {};
  const sourcePacks = plan.local_source_pack_matches || {};
  const results = Array.isArray(knowledge.results) ? knowledge.results : [];
  const packs = Array.isArray(sourcePacks.results) ? sourcePacks.results : [];
  return `<div class="command-plan">
    <div class="stat-inline"><span class="stat-inline-label">Research Intake</span>${statusTag(plan.status || "planned")}</div>
    <div class="stat-inline"><span class="stat-inline-label">Query</span><span class="stat-inline-val">${escapeText(plan.query)}</span></div>
    <div class="stat-inline"><span class="stat-inline-label">Knowledge hits</span><span class="stat-inline-val">${results.length}</span></div>
    <div class="stat-inline"><span class="stat-inline-label">Local source packs</span><span class="stat-inline-val">${packs.length}</span></div>
    <div class="divider"></div>
    ${results.slice(0, 6).map((item) => sourceRow(item.title || "Local Knowledge Base", item.path || item.summary || "local_knowledge_matches", item.status || "match")).join("")}
    ${packs.slice(0, 6).map((item) => sourceRow(item.title || "Source pack", item.path || item.summary || "local_source_pack", item.status || "match")).join("")}
  </div>`;
}

function renderCommandHistory() {
  const history = Array.isArray(dashboardState.command_history) ? dashboardState.command_history : [];
  return history.length
    ? history.slice(0, 8).map((item) => sourceRow(item.query || "Command", item.created_at || item.status || "RESEARCH INTAKE", item.status || "logged")).join("")
    : emptyState("No command history", "Command History will populate after governed searches are planned.");
}

function renderQueue() {
  return itemList("review_queue", "No review queue items", "Operator review queue is empty.");
}

function renderPostRunHandoff() {
  const handoff = dashboardState.post_run_handoff || {};
  if (!handoff.run_id) {
    return emptyState("No completed run handoff", handoff.operator_message || "Run the lifecycle to populate output locations and next actions.");
  }
  const locations = handoff.output_locations || {};
  const gates = handoff.route_gates || {};
  const happened = handoff.what_happened || {};
  const tech = handoff.if_technology_scores || {};
  const actions = Array.isArray(handoff.next_actions) ? handoff.next_actions : [];
  const linkRows = `${sourceRow("Portfolio view", locations.portfolio_view_url || "missing", locations.portfolio_view_url ? "ready" : "missing")}
    ${sourceRow("Portfolio download", locations.portfolio_download_url || "missing", locations.portfolio_download_url ? "ready" : "missing")}
    ${sourceRow("Portfolio JSON", locations.portfolio_json_path || "missing", locations.portfolio_json_path ? "written" : "missing")}
    ${sourceRow("Portfolio HTML", locations.portfolio_html_path || "missing", locations.portfolio_html_path ? "written" : "missing")}
    ${sourceRow("Review queue", locations.review_queue || "missing", "operator review")}
    ${sourceRow("Design package", locations.design_package_dir || "not generated", gates.design?.package_status || "preview")}`;
  const gateRows = `${sourceRow("Selected route", handoff.route_selected || "none", handoff.status || "review")}
    ${sourceRow("Signals consumed", happened.signals ?? 0, happened.signals ? "present" : "missing")}
    ${sourceRow("Discovery created", happened.discovery, happened.discovery ? "created" : "missing")}
    ${sourceRow("Portfolio created", happened.portfolio, happened.portfolio ? "created" : "missing")}
    ${sourceRow("Acquirer matches", happened.acquirer_matches ?? 0, happened.acquirer_matches ? "matched" : "missing")}
    ${sourceRow("Final package", happened.final_package || "missing", happened.final_package || "missing")}
    ${sourceRow("Breakthrough gate", gates.breakthrough?.reason || gates.breakthrough?.status || "not evaluated", gates.breakthrough?.threshold_met ? "threshold met" : gates.breakthrough?.status || "review")}
    ${sourceRow("Design gate", gates.design?.reason || gates.design?.status || "not evaluated", gates.design?.design_route_activated ? "design active" : gates.design?.status || "not selected")}
    ${sourceRow("Internet provider", gates.internet?.status || "unknown", gates.internet?.live_search_enabled ? "enabled" : "gated")}
    ${sourceRow("Market value", gates.market_value?.reason || "requires live evidence", gates.market_value?.status || "review")}`;
  const techRows = `${sourceRow("If technology scores", tech.condition || "waiting for scored technology signal", tech.current_run_result || "review")}
    ${sourceRow("Expected route", tech.expected_route || "breakthrough_design_or_solution_design", tech.dashboard_surface || "Design Portal")}
    ${sourceRow("Downstream after design", Array.isArray(tech.downstream_after_design) ? tech.downstream_after_design.join(" -> ") : "portfolio -> acquirer -> package", "wired")}`;
  const actionRows = actions.length
    ? actions.map((item, index) => sourceRow(`${index + 1}. ${item}`, "operator next action", index === 0 ? "next" : "queued")).join("")
    : emptyState("No next actions", "Backend did not expose next actions for this run.");
  const buttons = `<div class="handoff-actions">
    ${locations.portfolio_view_url ? `<button class="inline-open-btn" type="button" onclick="openPortfolioView('${escapeText(locations.portfolio_view_url)}')">Open Portfolio</button>` : ""}
    ${locations.portfolio_download_url ? `<button class="inline-external-btn" type="button" onclick="window.open('${escapeText(locations.portfolio_download_url)}','_blank','noopener,noreferrer')">Download Package</button>` : ""}
    ${locations.portfolio_latest_view_url ? `<button class="inline-external-btn" type="button" onclick="openPortfolioView('${escapeText(locations.portfolio_latest_view_url)}')">Latest Portfolio</button>` : ""}
  </div>`;
  return `<div class="handoff-grid">
    <div>${sourceRow("Current run", handoff.run_id, handoff.operator_review_required ? "review required" : "ready")}${buttons}${linkRows}</div>
    <div>${gateRows}</div>
    <div>${techRows}${actionRows}</div>
  </div>`;
}

function providerSearchUrl(query) {
  const clean = (query || "").trim();
  return clean ? `https://html.duckduckgo.com/html/?q=${encodeURIComponent(clean)}` : "https://html.duckduckgo.com/html/";
}

function platformRenderUrl(url) {
  return `/api/platform/browser/render?url=${encodeURIComponent(url || "")}`;
}

function openExternalSearch(query) {
  const clean = (query || "").trim();
  window.open(clean ? `https://www.google.com/search?q=${encodeURIComponent(clean)}` : "https://www.google.com/", "_blank", "noopener,noreferrer");
}

function openPlatformBrowser(url, title) {
  platformBrowser = { url, title: title || url, status: "opened" };
  activeSection = "overview";
  render();
}

function openPortfolioView(url) {
  const clean = String(url || "").trim();
  if (!clean) return;
  window.location.href = clean;
}

function renderPlatformBrowser() {
  if (!platformBrowser.url) {
    return emptyState("No platform page open", "Open Page results render through /api/platform/browser/render without mutating runtime truth.");
  }
  return `<div class="platform-browser">
    <div class="stat-inline"><span class="stat-inline-label">Open Page</span><span class="stat-inline-val">${escapeText(platformBrowser.title)}</span></div>
    <iframe class="platform-browser-frame" src="${platformRenderUrl(platformBrowser.url)}" title="Claire platform browser render"></iframe>
  </div>`;
}

function buildSearchOnlyPlan(query) {
  return fetchJson("/api/cockpit/command/plan", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, intent: "connected_search", source_mode: "local_source_pack" }),
  });
}

async function runProviderSearch(query) {
  const clean = (query || "").trim();
  if (!clean) return;
  commandPlan = await buildSearchOnlyPlan(clean);
  try {
    commandPlan.connected_search = await fetchJson("/api/search/provider/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: clean, mode: "metadata_only" }),
    });
  } catch (error) {
    commandPlan.connected_search = { status: "blocked", error: "Direct web results blocked", results: [] };
  }
  render();
}

async function runDesignPortalAction(actionId) {
  const clean = (actionId || "").trim();
  if (!clean) return;
  const result = await fetchJson("/api/cockpit/command/plan", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query: clean, intent: "design_portal_action", action_id: clean, operator_note: "dashboard operator action" }),
  });
  dashboardState.design_portal_last_action = result;
  dashboardState = await fetchJson("/api/dashboard/state");
  dashboardState.design_portal_last_action = result;
  render();
}

async function approveGovernedUpdate(updateId) {
  const input = document.getElementById(`update-approval-${updateId}`);
  const approvalPhrase = input ? input.value : "";
  updateGovernanceResult = await fetchJson("/api/update-governance/open-web/approve", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ update_id: updateId, approval_phrase: approvalPhrase, actor: "dashboard_owner" }),
  }).catch((error) => ({ status: "approval_failed", reason: error.message, update_id: updateId }));
  await refreshDashboardState();
  activeSection = "updates";
  render();
}

async function stageGovernedUpdate(updateId) {
  updateGovernanceResult = await fetchJson("/api/update-governance/open-web/install/stage", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ update_id: updateId, actor: "dashboard_owner" }),
  }).catch((error) => ({ status: "stage_failed", reason: error.message, update_id: updateId }));
  await refreshDashboardState();
  activeSection = "updates";
  render();
}

async function applyGovernedUpdate(updateId) {
  const input = document.getElementById(`update-approval-${updateId}`);
  const approvalPhrase = input ? input.value : "";
  updateGovernanceResult = await fetchJson("/api/update-governance/open-web/install/apply", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ update_id: updateId, approval_phrase: approvalPhrase, actor: "dashboard_owner" }),
  }).catch((error) => ({ status: "apply_failed", reason: error.message, update_id: updateId }));
  await refreshDashboardState();
  activeSection = "updates";
  render();
}

function renderConnectedSearch() {
  const connected = commandPlan?.connected_search || dashboardState.connected_search || {};
  const results = Array.isArray(connected.results) ? connected.results : [];
  if (!results.length) {
    return emptyState("No connected search results", "Direct web results blocked or waiting for a governed provider query.");
  }
  return results.slice(0, 8).map((item) => {
    const url = item.url || item.link || providerSearchUrl(item.title || "");
    return `<div class="source-row">
      <div>
        <div class="source-title">${escapeText(item.title || "Direct Web Results")}</div>
        <div class="source-meta">${escapeText(item.snippet || url)}</div>
      </div>
      <div class="source-status">
        <button class="inline-external-btn" type="button" onclick="openPlatformBrowser('${escapeText(url)}','${escapeText(item.title || "Result")}')">Open in platform</button>
        <button class="inline-external-btn" type="button" onclick="openExternalSearch('${escapeText(item.title || "")}')">Open site</button>
      </div>
    </div>`;
  }).join("");
}

function itemList(name, emptyTitle, emptyDetail, limit = 12) {
  const rows = records(name);
  return rows.length
    ? rows.slice(0, limit).map((item) => {
      const title = item.title || item.name || item.id || name;
      const meta = item.summary || item.domain || item.source || "backend";
      const status = item.status || item.mode || "ready";
      const viewUrl = item.view_url || (item.artifact && item.artifact.view_url);
      const downloadUrl = item.download_url || (item.artifact && item.artifact.download_url);
      if (!viewUrl && !downloadUrl) return sourceRow(title, meta, status);
      return `<div class="source-row source-row-action">
        <div class="source-title">${escapeText(title)}</div>
        <div class="source-meta">${escapeText(meta)}</div>
        <div class="source-status">${statusTag(status)}</div>
        ${viewUrl ? `<button class="inline-open-btn" type="button" onclick="window.open('${escapeText(viewUrl)}','_blank','noopener,noreferrer')">Open</button>` : ""}
        ${downloadUrl ? `<button class="inline-external-btn" type="button" onclick="window.open('${escapeText(downloadUrl)}','_blank','noopener,noreferrer')">Download</button>` : ""}
      </div>`;
    }).join("")
    : emptyState(emptyTitle, emptyDetail);
}

function renderBreakthroughList(limit = 12) {
  return itemList("breakthroughs", "No backend breakthrough records", "No breakthrough candidates are promoted into dashboard truth yet.", limit);
}

function renderSignalList(limit = 12) {
  return itemList("signals", "No live signal records", "Live signal ingestion is not populated yet.", limit);
}

function renderLiveSourceActivation() {
  const live = dashboardState.live_sources || {};
  const provider = live.provider || {};
  return `${sourceRow("Input boundary", "Stage 1 allowlist enforced", "ready")}
    ${sourceRow("Source universes", live.universes_configured ?? 0, "configured")}
    ${sourceRow("Live registry", live.allowed_domains ?? 0, "configured")}
    ${sourceRow("Provider gate", provider.status || "provider_not_configured", provider.live_search_enabled ? "enabled" : "gated")}`;
}

function renderSourceUniverseList(limit = 12) {
  return itemList("source_universes", "No source universes found", "Expected configured universes under data/source_universes.", limit);
}

function openPortal(sectionId) {
  activeSection = sectionId || "overview";
  render();
}

function portalButton(sectionId, title, detail, badge) {
  const nav = NAV.find((item) => item.id === sectionId) || {};
  return `<button class="portal-launch-btn" type="button" onclick="openPortal('${escapeText(sectionId)}')">
    <span class="portal-launch-icon">${escapeText(nav.icon || "P")}</span>
    <span class="portal-launch-copy">
      <strong>${escapeText(title)}</strong>
      <small>${escapeText(detail)}</small>
    </span>
    ${badge ? `<span class="portal-launch-badge">${escapeText(badge)}</span>` : ""}
  </button>`;
}

function renderPortalLauncher() {
  const first = dashboardState.first_run_readiness || {};
  const internet = dashboardState.internet_provider_diagnostics || {};
  const updates = dashboardState.update_logic_status || {};
  return `<div class="portal-grid">
    ${portalButton("first_run", "First Run", `${first.percent ?? "N/A"}% readiness / ${first.status || "waiting"}`, "proof")}
    ${portalButton("design_portal", "Design Portal", dashboardState.design_portal_workbench?.status || "preview", "workbench")}
    ${portalButton("portfolio", "Portfolio Package", dashboardState.post_run_handoff?.status || "waiting", "open")}
    ${portalButton("internet", "Internet Provider", internet.status || "provider", internet.live_search_enabled ? "metadata ready" : "gated")}
    ${portalButton("updates", "Update Governance", updates.status || "updates", updates.automatic_updates_enabled ? "review" : "locked")}
    ${portalButton("active_controls", "Active Controls", `${dashboardState.active_control_map?.controls?.length || 0} backend controls`, "controls")}
    ${portalButton("review_queue", "Review Queue", "portfolios, designs, evidence, updates", "review")}
    ${portalButton("web_ops", "Web Ops", internet.live_search_enabled ? "connectivity ready" : "connectivity staged", "internet")}
    ${portalButton("accounts", "Accounts", "login, users, email, provider links", "locked")}
  </div>`;
}

function renderPortalCommandCenter() {
  return `<div class="portal-command-row">
    <button class="portal-command-btn primary" type="button" onclick="startRuntimeCycle()">Start New Runtime Cycle</button>
    <button class="portal-command-btn" type="button" onclick="runPortfolioPath()">Run Portfolio Path</button>
    <button class="portal-command-btn" type="button" onclick="openPortal('design_portal')">Enter Design Portal</button>
    <button class="portal-command-btn" type="button" onclick="openPortal('active_controls')">Open Active Controls</button>
  </div>`;
}

function renderOperatorWorkflow() {
  const handoff = dashboardState.post_run_handoff || {};
  const locations = handoff.output_locations || {};
  const provider = dashboardState.internet_provider_diagnostics || {};
  const updates = dashboardState.update_logic_status || {};
  const controls = Array.isArray(dashboardState.active_control_map?.controls) ? dashboardState.active_control_map.controls : [];
  const portfolioUrl = locations.portfolio_view_url || locations.portfolio_latest_view_url || "/portfolio/artifacts/latest/view";
  const steps = [
    {
      label: "Step 1",
      title: "Review run proof",
      detail: dashboardState.first_run_readiness?.status || handoff.status || "waiting",
      action: "openPortal('first_run')",
      status: dashboardState.first_run_readiness?.percent >= 100 ? "ready" : "review",
    },
    {
      label: "Step 2",
      title: "Check provider gate",
      detail: provider.selected_provider ? `${provider.selected_provider} / ${provider.status || "provider"}` : "provider review",
      action: "openPortal('internet')",
      status: provider.research_grade_provider_ready ? "ready" : "review",
    },
    {
      label: "Step 3",
      title: "Run governed search",
      detail: "metadata-only quarantine",
      action: "openPortal('internet')",
      status: "review",
    },
    {
      label: "Step 4",
      title: "Open portfolio",
      detail: handoff.run_id || "latest package",
      action: `openPortfolioView('${escapeText(portfolioUrl)}')`,
      status: locations.portfolio_view_url || locations.portfolio_latest_view_url ? "ready" : "review",
    },
    {
      label: "Step 5",
      title: "Validate design package",
      detail: dashboardState.design_portal_workbench?.status || "preview",
      action: "openPortal('design_portal')",
      status: dashboardState.design_artifact_package?.status || dashboardState.design_portal_workbench?.status || "review",
    },
    {
      label: "Step 6",
      title: "Review locks and controls",
      detail: `${controls.length} read-only controls / updates ${updates.automatic_updates_enabled ? "enabled" : "locked"}`,
      action: "openPortal('active_controls')",
      status: controls.length ? "ready" : "review",
    },
  ];
  return `<div class="operator-workflow">
    ${steps.map((step) => `
      <button class="operator-step ${step.status === "ready" ? "operator-step-ready" : "operator-step-review"}" type="button" onclick="${step.action}">
        <span>${escapeText(step.label)}</span>
        <strong>${escapeText(step.title)}</strong>
        <small>${escapeText(step.detail)}</small>
      </button>`).join("")}
  </div>`;
}

function renderFirstRunSummary() {
  const first = dashboardState.first_run_readiness || {};
  const gaps = Array.isArray(first.gaps) ? first.gaps : [];
  const actions = Array.isArray(first.next_actions) ? first.next_actions : [];
  return `${sourceRow("First-run state", first.status || "waiting", first.status || "waiting")}
    ${sourceRow("Completion", `${first.percent ?? "N/A"}%`, gaps.length ? "review" : "ready")}
    ${sourceRow("Run id", first.run_id || "waiting", first.run_id ? "bound" : "waiting")}
    ${sourceRow("Route", first.route_selected || "waiting", first.route_selected ? "selected" : "waiting")}
    ${sourceRow("Runtime truth mutation", first.runtime_truth_mutated ? "mutated" : "blocked", first.runtime_truth_mutated ? "review" : "blocked")}
    ${actions.slice(0, 5).map((item, index) => sourceRow(`${index + 1}. ${item}`, "next action", index === 0 ? "next" : "queued")).join("")}`;
}

function renderFirstRun() {
  return `<div class="kpi-row">
    ${kpi("First Run", "F", "kpi-green")}
    ${kpi("Active Signals", "S", "kpi-purple")}
    ${kpi("Portfolio Items", "P", "kpi-teal")}
    ${kpi("Acquirer Matches", "A", "kpi-amber")}
  </div>
  ${card("Operator Workflow", renderOperatorWorkflow(), "step-by-step")}
  ${card("Portal Launcher", `${renderPortalLauncher()}${renderPortalCommandCenter()}`, "work surfaces")}
  ${card("First-Run Readiness", renderFirstRunSummary(), dashboardState.first_run_readiness?.status || "waiting")}
  ${card("First-Run Checks", itemList("first_run_readiness", "No first-run checks", "First-run checks are waiting for dashboard state."), "proof chain")}
  ${card("Post-Run Output Handoff", renderPostRunHandoff(), dashboardState.post_run_handoff?.status || "waiting")}`;
}

function renderInternetSummary() {
  const diagnostic = dashboardState.internet_provider_diagnostics || {};
  const evidence = diagnostic.evidence_state || {};
  const rates = diagnostic.rate_limits || {};
  const blockers = Array.isArray(diagnostic.blockers) ? diagnostic.blockers.join(", ") : "";
  const warnings = Array.isArray(diagnostic.warnings) ? diagnostic.warnings.join(", ") : "";
  return `${sourceRow("Provider status", diagnostic.status || "waiting", diagnostic.live_search_enabled ? "enabled" : diagnostic.status || "waiting")}
    ${sourceRow("Readiness", `${diagnostic.readiness_percent ?? "N/A"}%`, diagnostic.readiness_percent >= 100 ? "ready" : "review")}
    ${sourceRow("Fetch mode", diagnostic.fetch_mode || "waiting", diagnostic.fetch_enabled ? "ready" : "gated")}
    ${sourceRow("Selected provider", diagnostic.selected_provider || "none", diagnostic.research_grade_provider_ready ? "research grade" : diagnostic.fallback_metadata_provider_ready ? "fallback" : "gated")}
    ${sourceRow("Research-grade provider", diagnostic.research_grade_provider_ready ? "ready" : "missing key", diagnostic.research_grade_provider_ready ? "ready" : "review")}
    ${sourceRow("Fallback metadata provider", diagnostic.fallback_metadata_provider_ready ? "ready" : "gated", diagnostic.fallback_metadata_provider_ready ? "ready" : "review")}
    ${sourceRow("Weekly/rate guard", `${rates.max_queries_per_minute ?? 6}/min / ${rates.max_queries_per_session ?? 30}/session / ${rates.max_results_per_query ?? 8} results`, "ready")}
    ${sourceRow("Body reads", diagnostic.body_reads_allowed ? "allowed" : "blocked", diagnostic.body_reads_allowed ? "review" : "blocked")}
    ${sourceRow("Blockers", blockers || "none", blockers ? "blocked" : "ready")}
    ${sourceRow("Warnings", warnings || "none", warnings ? "review" : "ready")}
    ${sourceRow("Source universes", evidence.source_universes ?? 0, evidence.source_universes ? "configured" : "missing")}
    ${sourceRow("Promoted metadata", evidence.promoted_metadata_evidence ?? 0, evidence.promoted_metadata_evidence ? "present" : "waiting")}`;
}

function renderInternet() {
  const actions = Array.isArray(dashboardState.internet_provider_diagnostics?.next_actions)
    ? dashboardState.internet_provider_diagnostics.next_actions
    : [];
  const actionRows = actions.length
    ? actions.map((item, index) => sourceRow(`${index + 1}. ${item}`, "operator action", index === 0 ? "next" : "queued")).join("")
    : emptyState("No provider actions", "Provider diagnostics are waiting for dashboard state.");
  return `<div class="kpi-row">
    ${kpi("Provider Lanes", "L", "kpi-green")}
    ${kpi("Provider Blocks", "B", "kpi-amber")}
    ${kpi("Active Signals", "S", "kpi-purple")}
    ${kpi("Source Universes", "U", "kpi-blue")}
  </div>
  ${card("Internet Provider Diagnostic", renderInternetSummary(), dashboardState.internet_provider_diagnostics?.status || "provider")}
  ${card("Provider Stack", itemList("internet_provider_diagnostics", "No provider stack", "Provider stack diagnostics are waiting for backend state."), "metadata only")}
  ${card("Provider Next Actions", actionRows, "operator visible")}
  ${card("Governed Web Results", renderConnectedSearch(), "quarantined metadata")}`;
}

function renderWebOps() {
  const diagnostic = dashboardState.internet_provider_diagnostics || {};
  const update = dashboardState.update_logic_status || {};
  const probe = dashboardState.live_probe_status || {};
  const controls = Array.isArray(dashboardState.active_control_map?.controls) ? dashboardState.active_control_map.controls : [];
  const internetControls = controls.filter((item) => ["Internet", "Search", "Evidence", "Sources"].includes(item.category));
  const controlRows = internetControls.length
    ? internetControls.map((item) => sourceRow(item.button_label || item.label, `${item.primary_endpoint} / ${item.operation_mode}`, item.operation_mode || "review")).join("")
    : emptyState("No web controls", "Web and internet controls are waiting for the active control map.");
  return `<div class="ops-hero">
    <div>
      <span>Internet Readiness</span>
      <strong>${escapeText(diagnostic.selected_provider || "provider not selected")}</strong>
      <small>${escapeText(diagnostic.status || "provider review")} / body reads ${diagnostic.body_reads_allowed ? "allowed" : "blocked"}</small>
    </div>
    <div>
      <span>Connectivity Mode</span>
      <strong>${diagnostic.live_search_enabled ? "Metadata Search Ready" : "Staged"}</strong>
      <small>Live body ingestion and runtime truth writes remain operator-gated.</small>
    </div>
    <div>
      <span>Web Updates</span>
      <strong>${escapeText(update.status || "proposal review")}</strong>
      <small>Automatic update execution ${update.automatic_updates_enabled ? "enabled" : "blocked"}.</small>
    </div>
  </div>
  <div class="grid-2">
    ${card("Provider and Connectivity Gate", renderInternetSummary(), diagnostic.status || "provider")}
    ${card("Web Update Runway", renderUpdateSummary(), update.status || "updates")}
  </div>
  <div class="grid-2">
    ${card("Internet Controls", controlRows, `${internetControls.length} controls`)}
    ${card("Live Probe Boundary", `
      ${sourceRow("Probe status", probe.status || "not loaded", probe.status || "review")}
      ${sourceRow("Network execution", "manual metadata-only probe only", diagnostic.live_search_enabled ? "review" : "blocked")}
      ${sourceRow("Body reads", diagnostic.body_reads_allowed ? "allowed" : "blocked", diagnostic.body_reads_allowed ? "review" : "blocked")}
      ${sourceRow("Runtime truth mutation", "blocked until promotion approval", "blocked")}
    `, "governed")}
  </div>
  ${card("Governed Web Results", renderConnectedSearch(), "metadata quarantine")}`;
}

function renderUpdateSummary() {
  const update = dashboardState.update_logic_status || {};
  return `${sourceRow("Update status", update.status || "waiting", update.status || "waiting")}
    ${sourceRow("Available proposals", update.available_update_count ?? 0, update.available_update_count ? "review" : "none")}
    ${sourceRow("Automatic updates", update.automatic_updates_enabled ? "enabled" : "blocked", update.automatic_updates_enabled ? "review" : "blocked")}
    ${sourceRow("Package install performed", update.package_install_performed ? "yes" : "no", update.package_install_performed ? "review" : "blocked")}
    ${sourceRow("Install endpoints", update.install_endpoints_exposed ? "available" : "missing", update.install_endpoints_exposed ? "ready" : "blocked")}
    ${sourceRow("Stage endpoint", update.stage_endpoint || "missing", update.stage_endpoint ? "ready" : "blocked")}
    ${sourceRow("Apply endpoint", update.apply_endpoint || "missing", update.apply_endpoint ? "approval gated" : "blocked")}
    ${sourceRow("Runtime truth firewall", update.runtime_truth_firewall || "enabled", update.runtime_truth_firewall || "enabled")}
    ${sourceRow("Approval required", update.approval_required ? "yes" : "no", update.approval_required ? "review" : "blocked")}
    ${sourceRow("Mutation endpoints", update.mutation_endpoints_exposed ? "operator-gated" : "not exposed", update.mutation_endpoints_exposed ? "review" : "blocked")}
    ${sourceRow("Privileged surfaces", update.privileged_surfaces_exposed ? "exposed" : "not exposed", update.privileged_surfaces_exposed ? "review" : "blocked")}`;
}

function renderUpdateProposalControls() {
  const update = dashboardState.update_logic_status || {};
  const proposals = Array.isArray(update.updates) ? update.updates : [];
  if (!proposals.length) {
    return emptyState("No update proposals", "No governed update requests are waiting for review.");
  }
  return proposals.map((proposal) => {
    const install = proposal.install || {};
    const blockers = Array.isArray(install.blockers) ? install.blockers : [];
    const updateId = proposal.update_id || "unknown_update";
    return `<div class="update-proposal">
      ${sourceRow("Update", updateId, proposal.status || "review")}
      ${sourceRow("Trust", proposal.trusted ? "trusted" : "not trusted", proposal.trusted ? "ready" : "blocked")}
      ${sourceRow("Signature", proposal.signature_verified ? "verified" : "missing", proposal.signature_verified ? "ready" : "blocked")}
      ${sourceRow("Install status", install.status || "not staged", install.install_allowed ? "ready" : "review")}
      ${sourceRow("Package files", install.package_file_count ?? 0, install.package_file_count ? "attached" : "needed")}
      ${sourceRow("Rollback", install.rollback_supported ? "supported" : "not ready", install.rollback_supported ? "ready" : "blocked")}
      ${sourceRow("Install blockers", blockers.length ? blockers.join(", ") : "none", blockers.length ? "review" : "ready")}
      <div class="portal-command-row">
        <input class="update-approval-input" id="update-approval-${escapeText(updateId)}" type="text" placeholder="${escapeText(update.approval_phrase || "APPROVE GOVERNED UPDATE")}" />
        <button class="portal-command-btn" type="button" onclick="approveGovernedUpdate('${escapeText(updateId)}')">Approve</button>
        <button class="portal-command-btn" type="button" onclick="stageGovernedUpdate('${escapeText(updateId)}')">Stage Install</button>
        <button class="portal-command-btn primary" type="button" onclick="applyGovernedUpdate('${escapeText(updateId)}')">Apply Governed Update</button>
      </div>
    </div>`;
  }).join("");
}

function renderUpdateGovernanceResult() {
  if (!updateGovernanceResult) {
    return emptyState("No update action yet", "Approve, stage, or apply a governed update to see the endpoint response here.");
  }
  return `<pre class="json-preview">${escapeText(JSON.stringify(updateGovernanceResult, null, 2))}</pre>`;
}

function renderUpdates() {
  const actions = Array.isArray(dashboardState.update_logic_status?.next_actions)
    ? dashboardState.update_logic_status.next_actions
    : [];
  const actionRows = actions.length
    ? actions.map((item, index) => sourceRow(`${index + 1}. ${item}`, "update runway", index === 0 ? "next" : "queued")).join("")
    : emptyState("No update actions", "Update governance is waiting for backend state.");
  return `<div class="kpi-row">
    ${kpi("Available Updates", "U", "kpi-blue")}
    ${kpi("Update Blocks", "B", "kpi-amber")}
    ${kpi("Blocked", "X", "kpi-red")}
  </div>
  ${card("Update Governance", renderUpdateSummary(), dashboardState.update_logic_status?.status || "updates")}
  ${card("Update Proposals", renderUpdateProposalControls(), "approval and install")}
  ${card("Update Action Result", renderUpdateGovernanceResult(), "endpoint response")}
  ${card("Update Next Actions", actionRows, "manual approval only")}`;
}

function renderReviewQueuePortal() {
  const handoff = dashboardState.post_run_handoff || {};
  const locations = handoff.output_locations || {};
  const queueRows = itemList("review_queue", "No review queue items", "Finished outputs and evidence promotions will appear here for operator decision.");
  return `<div class="review-lane-grid">
    <button class="review-lane" type="button" onclick="openPortal('portfolio')">
      <span>Portfolio Reviews</span>
      <strong>${escapeText(handoff.status || "waiting")}</strong>
      <small>${escapeText(locations.portfolio_json_path || "portfolio output not loaded")}</small>
    </button>
    <button class="review-lane" type="button" onclick="openPortal('design_portal')">
      <span>Design Reviews</span>
      <strong>${escapeText(dashboardState.design_portal_workbench?.status || "preview")}</strong>
      <small>Blueprint, component map, design package, CAD/video slots.</small>
    </button>
    <button class="review-lane" type="button" onclick="openPortal('web_ops')">
      <span>Evidence Reviews</span>
      <strong>quarantine first</strong>
      <small>Promoted evidence requires manual approval before runtime truth.</small>
    </button>
    <button class="review-lane" type="button" onclick="openPortal('updates')">
      <span>Update Reviews</span>
      <strong>${escapeText(dashboardState.update_logic_status?.status || "locked")}</strong>
      <small>Sign-off, rollback plan, and owner approval required.</small>
    </button>
  </div>
  ${card("Unified Review Queue", queueRows, "operator decisions")}
  ${card("Post-Run Output Handoff", renderPostRunHandoff(), handoff.status || "waiting")}`;
}

function renderAccounts() {
  const provider = dashboardState.internet_provider_diagnostics || {};
  return `<div class="account-grid">
    <div class="account-card">
      <span>Authentication</span>
      <strong>Local operator session</strong>
      <small>Login and multi-user auth are planned surfaces; no browser-stored credentials are requested here.</small>
      ${statusTag("planned")}
    </div>
    <div class="account-card">
      <span>User Roles</span>
      <strong>Owner / Admin / Operator / Viewer</strong>
      <small>Role separation is staged visually so run controls, approvals, and admin settings can split cleanly.</small>
      ${statusTag("review")}
    </div>
    <div class="account-card">
      <span>Email Links</span>
      <strong>Not connected</strong>
      <small>Inbox/account linking should use explicit OAuth or app-password flow later; no secrets are shown or stored in the dashboard.</small>
      ${statusTag("blocked")}
    </div>
    <div class="account-card">
      <span>Provider Account</span>
      <strong>${escapeText(provider.selected_provider || "none")}</strong>
      <small>Provider key presence is represented by readiness only; plaintext keys never render.</small>
      ${statusTag(provider.research_grade_provider_ready ? "ready" : "review")}
    </div>
  </div>
  ${card("Account Governance", `
    ${sourceRow("Credential display", "plaintext secrets never render in dashboard", "blocked")}
    ${sourceRow("Email account access", "requires explicit operator setup and scoped permissions", "planned")}
    ${sourceRow("Admin approvals", "promotion/update actions require owner review", "review")}
    ${sourceRow("Audit trail", "account actions should write review-only audit events", "planned")}
  `, "locked")}`;
}

function renderSettings() {
  const provider = dashboardState.internet_provider_diagnostics || {};
  const update = dashboardState.update_logic_status || {};
  const standards = dashboardState.endpoint_standard_settings || {};
  const reconciliation = dashboardState.endpoint_reconciliation || {};
  const dependencyProof = dashboardState.dependency_chain_proof || {};
  const rates = provider.rate_limits || {};
  return `<div class="settings-grid">
    ${sourceRow("Environment", "development / local dashboard", "ready")}
    ${sourceRow("Search provider", provider.selected_provider || "not selected", provider.research_grade_provider_ready ? "ready" : "review")}
    ${sourceRow("Provider stack", Array.isArray(provider.provider_stack) ? provider.provider_stack.join(", ") : "tavily, duckduckgo", "review")}
    ${sourceRow("Live internet pack", provider.fetch_enabled ? provider.fetch_mode || "metadata_only_quarantine_first" : "provider gated", provider.fetch_enabled ? "ready" : "review")}
    ${sourceRow("Readiness", `${provider.readiness_percent ?? "N/A"}%`, provider.readiness_percent >= 100 ? "ready" : "review")}
    ${sourceRow("Rate limits", `${rates.max_queries_per_minute ?? 6}/min / ${rates.max_queries_per_session ?? 30}/session / ${rates.max_results_per_query ?? 8} results`, "ready")}
    ${sourceRow("CORS / host", window.location.host || "localhost", "local")}
    ${sourceRow("Web updates", update.automatic_updates_enabled ? "enabled" : "blocked", update.automatic_updates_enabled ? "review" : "blocked")}
    ${sourceRow("Updates pack", update.status || "proposal_review_ready", update.approval_required ? "approval required" : "ready")}
    ${sourceRow("Endpoint package", standards.package_endpoint || "/api/system/industry-standard-endpoint-package", standards.status || "review")}
    ${sourceRow("Endpoint reconciliation", `${reconciliation.unresolved_count ?? "N/A"} unresolved / ${reconciliation.compatibility_alias_count ?? 0} aliases`, reconciliation.status || "review")}
    ${sourceRow("Dependency proof", `${dependencyProof.passed_step_count ?? 0}/${dependencyProof.step_count ?? 0} steps`, dependencyProof.status || "not run")}
    ${sourceRow("OpenAPI contract", standards.openapi_endpoint || "/openapi.json", "ready")}
    ${sourceRow("CAD intent", standards.cad_intent_reviewable ? "/cad/intent reviewable" : "not exposed", standards.cad_export_enabled ? "export enabled" : "contract only")}
    ${sourceRow("Runtime truth mutation", "manual approval only", "blocked")}
  </div>
  <div class="grid-2">
    ${card("Operator Preferences", `
      ${sourceRow("Default landing page", "Overview with live run viewer and workflow rail", "planned")}
      ${sourceRow("Review queue filters", "Portfolio, Design, Evidence, Updates, Final Output", "planned")}
      ${sourceRow("Connectivity mode", "local / metadata-only / live-approved", "planned")}
    `, "visual setup")}
    ${card("Endpoint Standards Package", `
      ${sourceRow("Package file", standards.package_file || "data/endpoint_contracts/industry_standard_endpoint_package.json", standards.status || "review")}
      ${sourceRow("Standards mapped", `${standards.standards_count ?? 0} controls`, standards.standards_count ? "ready" : "review")}
      ${sourceRow("Critical endpoints", `${standards.mounted_expected_count ?? 0}/${standards.critical_endpoint_count ?? 0} mounted`, (standards.missing_expected_paths || []).length ? "review" : "ready")}
      ${sourceRow("Owner review", standards.owner_review_required_for_mutations ? "required for mutation/install endpoints" : "not required", standards.owner_review_required_for_mutations ? "ready" : "review")}
    `, standards.status || "standards")}
    ${card("Endpoint Reconciliation", `
      ${sourceRow("Report", "/api/system/endpoint-reconciliation", reconciliation.status || "review")}
      ${sourceRow("Frontend calls scanned", reconciliation.frontend_call_count ?? 0, "scanned")}
      ${sourceRow("Compatibility aliases", reconciliation.compatibility_alias_count ?? 0, reconciliation.compatibility_alias_count ? "ready" : "review")}
      ${sourceRow("Unresolved calls", reconciliation.unresolved_count ?? 0, reconciliation.unresolved_count ? "review" : "ready")}
    `, reconciliation.status || "reconciliation")}
    ${card("Dependency Chain Proof", `
      ${sourceRow("Proof endpoint", "/api/system/dependency-chain-proof", dependencyProof.status || "not run")}
      ${sourceRow("Steps", `${dependencyProof.passed_step_count ?? 0}/${dependencyProof.step_count ?? 0}`, dependencyProof.blocked_steps?.length ? "blocked" : dependencyProof.status || "not run")}
      ${sourceRow("Handoffs", `${dependencyProof.blocked_edges?.length ?? 0} blocked`, dependencyProof.blocked_edges?.length ? "review" : "ready")}
      ${sourceRow("Causal engine intake", dependencyProof.causal_engine_intake?.status || "deferred until cleanup lock", "deferred")}
    `, dependencyProof.status || "e2e proof")}
    ${card("System Settings Boundary", renderSafety(), "governed")}
  </div>`;
}

function renderAdmin() {
  const controls = Array.isArray(dashboardState.active_control_map?.controls) ? dashboardState.active_control_map.controls : [];
  return `<div class="admin-shell">
    <div class="admin-primary">
      ${card("Admin Console", `
        ${sourceRow("Role", "Owner/Admin only for destructive or credential-bearing actions", "planned")}
        ${sourceRow("Registered controls", `${controls.length} read-only or review-only controls`, controls.length ? "ready" : "review")}
        ${sourceRow("Automatic updates", "blocked", "blocked")}
        ${sourceRow("Secrets policy", "masked, never logged, never rendered", "ready")}
      `, "admin")}
      ${card("Control Map", renderActiveControlButtons(), "read only")}
    </div>
    <div class="admin-side">
      ${card("Governance Locks", renderSafety(), "locked")}
      ${card("Diagnostics", `
        ${sourceRow("Payload", "/api/dashboard/state", "ready")}
        ${sourceRow("Active controls", "/api/dashboard/active-control-map", "ready")}
        ${sourceRow("Health", "/health", "ready")}
      `, "routes")}
    </div>
  </div>`;
}

function renderOverview() {
  return `<div class="kpi-row">
    ${kpi("Operational Readiness", "%", "kpi-teal")}
    ${kpi("First Run", "F", "kpi-green")}
    ${kpi("Project Files", "F", "kpi-green")}
    ${kpi("Missing Files", "M", "kpi-red")}
    ${kpi("Route Wires", "R", "kpi-blue")}
    ${kpi("Wire Gaps", "G", "kpi-amber")}
    ${kpi("Breakthroughs", "B", "kpi-blue")}
    ${kpi("Portfolio Items", "P", "kpi-green")}
    ${kpi("Active Signals", "S", "kpi-purple")}
    ${kpi("Acquirer Matches", "A", "kpi-amber")}
  </div>
  ${card("Operator Workflow", renderOperatorWorkflow(), "step-by-step")}
  ${card("Portal Launcher", `${renderPortalLauncher()}${renderPortalCommandCenter()}`, "enter workbench")}
  ${card("Project File Wiring", renderProjectFileBindings(), dashboardState.project_file_bindings?.status || "loading")}
  ${card("First-Run Readiness", renderFirstRunSummary(), dashboardState.first_run_readiness?.status || "waiting")}
  ${card("Post-Run Output Handoff", renderPostRunHandoff(), dashboardState.post_run_handoff?.status || "waiting")}
  <div class="grid-2">
    ${card("Internet Provider Diagnostic", renderInternetSummary(), dashboardState.internet_provider_diagnostics?.status || "provider")}
    ${card("Update Governance", renderUpdateSummary(), dashboardState.update_logic_status?.status || "updates")}
  </div>
  ${card("Governed Web Results", renderCommandPlan(), "METADATA ONLY")}
  ${card("Direct Web Results", renderConnectedSearch(), "connected_search")}
  ${card("Platform Web View", renderPlatformBrowser(), "Open Page")}
  ${card("Command History", renderCommandHistory(), "RESEARCH INTAKE")}
  <div class="grid-2">
    ${card("Canonical Runtime Routes to Dashboard Fields", renderSystemWiring(), "wired")}
    ${card("Project Owners for Runtime Wiring", renderSystemOwners(), "bound")}
  </div>
  ${card("Pipeline Routes", `
    ${routeBox("portfolio", "P", "Portfolio Route", "Signal -> Trend -> Thesis -> Portfolio")}
    ${routeBox("acquisition", "A", "Acquisition Route", "PI -> Acquirer Match -> Deal Package")}
    ${routeBox("breakthrough", "B", "Breakthrough Route", "Signal -> BO -> Scoring -> Validation")}
    ${routeBox("design", "D", "Design Route", "BO -> Design Engine -> Architecture")}
  `, "LIVE")}`;
}

function renderLifecycle() {
  const lifecycle = dashboardState.lifecycle || {};
  const stages = Array.isArray(lifecycle.stages) ? lifecycle.stages : [];
  const body = stages.length
    ? stages.map((stage) => sourceRow(`${stage.number || stage.stage_number || ""}. ${stage.label || stage.name || stage.id}`, stage.reason || stage.group || "Lifecycle", stage.status || "pending")).join("")
    : emptyState("No lifecycle run yet", "Run the pipeline to populate the canonical 30-stage lifecycle spine.");
  return `${card("30-Stage Lifecycle Spine", body, lifecycle.route_selected || "waiting")}
    ${card("Canonical Runtime Routes to Dashboard Fields", renderSystemWiring(), "route truth")}`;
}

function renderSignals() {
  return `${card("Signal Feed", renderSignalList(), "governed")}
    ${card("Live Source Activation", renderLiveSourceActivation(), "governed")}
    ${card("Source Universes", renderSourceUniverseList(), "configured")}`;
}

function renderBreakthroughs() {
  return `${card("Breakthroughs", renderBreakthroughList(), "conditional")}
    ${card("Discovery Candidates", itemList("discovery", "No discovery candidates", "Discovery records will populate after runtime start or evaluation."), "review")}`;
}

function renderTechnology() {
  const tech = dashboardState.technology_base || {};
  const body = `${sourceRow("Reality Filter", tech.status || "technology_base", "active")}
    ${sourceRow("Manufacturable", metricValue("Manufacturable", 0), "tracked")}
    ${itemList("technology", "No technology records", "technology_base records are not exposed yet.")}`;
  return `${card("Tech Base", body, "technology_base")}
    ${card("Pipeline Activation Registry", renderPipelineActivation(), "pipeline_activation")}`;
}

function renderDesignPortal() {
  const portal = dashboardState.design_portal_workbench || {};
  const buildability = portal.buildability || {};
  const blueprintReadiness = portal.blueprint_readiness || {};
  const candidate = portal.candidate || {};
  const components = Array.isArray(portal.required_components) ? portal.required_components : [];
  const systems = Array.isArray(portal.required_systems) ? portal.required_systems : [];
  const gates = Array.isArray(portal.promotion_gates) ? portal.promotion_gates : [];
  const materials = portal.materials_manifest || {};
  const blueprintPackage = portal.blueprint_package || {};
  const commitment = portal.invention_commitment || {};
  const downstream = portal.downstream_route_contract || {};
  const artifactPackage = portal.artifact_package || dashboardState.design_artifact_package || {};
  const alert = portal.runtime_design_alert || {};
  const actions = Array.isArray(portal.portal_actions) ? portal.portal_actions : [];
  const validation = portal.validation_chain || {};
  const lastAction = dashboardState.design_portal_last_action || {};
  const nodes = Array.isArray(portal.architecture?.nodes) ? portal.architecture.nodes : [];
  const flows = Array.isArray(portal.architecture?.edges) ? portal.architecture.edges : [];
  const events = Array.isArray(portal.live_design_events) ? portal.live_design_events : [];
  const componentRows = components.length
    ? components.slice(0, 12).map((item) => sourceRow(
      item.label || item.id || "Required component",
      `${item.role || ""} / interfaces: ${(item.interfaces || []).join(", ") || "pending"}`,
      item.buildability || item.current_tech_status || "required",
    )).join("")
    : emptyState("No component map", "Design Portal has not exposed required components yet.");
  const systemRows = systems.length
    ? systems.map((item) => sourceRow(item.label || item.id, item.purpose || item.evidence_needed || "required system", item.status || "required")).join("")
    : emptyState("No required systems", "Required operating systems are not exposed yet.");
  const nodeRows = nodes.length
    ? nodes.map((item) => sourceRow(item.label || item.id, item.role || "architecture node", item.priority || "required")).join("")
    : emptyState("No architecture nodes", "Architecture preview is waiting on backend design context.");
  const flowRows = flows.length
    ? flows.map((item) => sourceRow(`${item.from} -> ${item.to}`, item.payload || "runtime payload", item.validation || "validated")).join("")
    : emptyState("No data flows", "Data-flow preview is waiting on the system design engine.");
  const gateRows = gates.length
    ? gates.map((item) => sourceRow(item.gate, item.required_evidence || item.reason || "promotion evidence", item.status || "review")).join("")
    : emptyState("No promotion gates", "Promotion gates are not exposed yet.");
  const materialRows = [
    ["Technology materials", materials.technology_materials],
    ["System materials", materials.system_materials],
    ["Component materials", materials.component_materials],
    ["Code materials", materials.code_materials],
    ["Deployment materials", materials.deployment_materials],
  ].map(([label, rows]) => sourceRow(label, `${Array.isArray(rows) ? rows.length : 0} required`, Array.isArray(rows) && rows.length ? "listed" : "pending")).join("");
  const routeRows = `${sourceRow("Commit to build attempt", commitment.status || "needs_more_validation", commitment.commit_to_build_attempt ? "ready" : "review")}
    ${sourceRow("Viability score", commitment.viability_score ?? "N/A", commitment.conditions?.viable ? "viable" : "review")}
    ${sourceRow("Downstream route", downstream.route || "portfolio_creation_optimization_until_design_validated", downstream.status || "route review")}
    ${sourceRow("Portfolio required", downstream.portfolio_required, downstream.portfolio_required ? "required" : "off")}
    ${sourceRow("Acquirer matching required", downstream.acquirer_matching_required, downstream.acquirer_matching_required ? "required" : "off")}
    ${sourceRow("Package required", downstream.package_required, downstream.package_required ? "required" : "off")}`;
  const actionRows = actions.length
    ? `<div class="design-action-grid">${actions.map((action) => `
      <button class="design-action-btn" type="button" ${action.enabled ? "" : "disabled"} onclick="runDesignPortalAction('${escapeText(action.id)}')">
        <span>${escapeText(action.label || action.id)}</span>
        <small>${escapeText(action.kind || "action")}</small>
      </button>`).join("")}</div>
      ${lastAction.action_id ? sourceRow("Last action", lastAction.action_id, lastAction.status || "recorded") : ""}`
    : emptyState("No portal actions", "Design Portal action controls are not exposed yet.");
  const validationRows = Array.isArray(validation.checks)
    ? validation.checks.map((item) => sourceRow(item.label || item.id, "runtime route continuity", item.passed ? "pass" : "review")).join("")
    : emptyState("No validation chain", "Route validation checks are not exposed yet.");
  const alertRows = `${sourceRow("Runtime alert", alert.operator_message || "watching for design triggers", alert.status || "watching")}
    ${sourceRow("Trigger type", alert.trigger_type || "no_design_alert", alert.severity || "low")}
    ${sourceRow("Validation chain", `${validation.completion_percent ?? 0}%`, validation.status || "partial")}`;
  const artifactRows = `${sourceRow("Artifact package", artifactPackage.folder_name || "not generated", artifactPackage.status || "pending")}
    ${sourceRow("Blueprint/material files", `${artifactPackage.artifact_count ?? 0} package artifacts`, "generated")}
    ${sourceRow("CAD viewer", artifactPackage.cad_viewer_required, artifactPackage.cad_viewer_required ? "required" : "off")}
    ${sourceRow("Video viewer", artifactPackage.video_viewer_required, artifactPackage.video_viewer_required ? "required" : "off")}
    ${sourceRow("Manual review", artifactPackage.manual_review_required, artifactPackage.manual_review_required ? "required" : "off")}`;
  const viewerRows = `${sourceRow("CAD / 3D viewer", "STEP, STL, OBJ, GLB, DXF asset slot", artifactPackage.cad_viewer_required ? "ready" : "off")}
    ${sourceRow("CAD export contract", "/cad/export-contract", "prepared / disabled")}
    ${sourceRow("Video / simulation viewer", "MP4, WEBM, MOV simulation slot", artifactPackage.video_viewer_required ? "ready" : "off")}
    ${sourceRow("Import/generation slots", "operator-attached or generated assets", "ready")}`;
  const viewerSurface = `<div class="viewer-surface-grid">
    <div class="cad-viewer-pane">
      <div class="viewer-title">CAD / 3D Viewer</div>
      <div class="viewer-model-box">
        <div class="viewer-axis axis-x"></div>
        <div class="viewer-axis axis-y"></div>
        <div class="viewer-cube">3D</div>
      </div>
      <div class="viewer-caption">Ready for STEP, STL, OBJ, GLB, GLTF, DXF</div>
    </div>
    <div class="video-viewer-pane">
      <div class="viewer-title">Video / Simulation Viewer</div>
      <div class="viewer-video-box">
        <div class="viewer-play">▶</div>
      </div>
      <div class="viewer-caption">Ready for MP4, WEBM, MOV simulation/demo assets</div>
    </div>
  </div>`;
  const eventRows = events.length
    ? events.map((item) => sourceRow(`${item.stage}. ${item.label}`, "live design stage window 16-22", item.runtime_status || "preview")).join("")
    : emptyState("No live design events", "Runtime stage events are not exposed yet.");
  return `${card("Design Portal Entry", `${renderPortalCommandCenter()}${actionRows}`, "click to work")}
  ${card("Post-Run Output Handoff", renderPostRunHandoff(), dashboardState.post_run_handoff?.status || "waiting")}
  ${card("Live Design Workbench", `
    ${sourceRow("Candidate", candidate.title || "Design candidate", portal.status || "preview_ready")}
    ${sourceRow("Route", candidate.route || portal.runtime_stage?.route_selected || "not selected", portal.runtime_stage?.design_route_activated ? "design active" : "design preview")}
    ${sourceRow("Current-tech compatible", buildability.current_tech_compatible, buildability.current_tech_compatible ? "buildable" : "review")}
    ${sourceRow("Sci-fi risk", buildability.sci_fi_risk || "unknown", buildability.sci_fi_risk || "review")}
    ${sourceRow("Blueprint readiness", blueprintReadiness.state || "needs_more_validation", blueprintReadiness.ready ? "ready" : "review")}
  `, portal.mode || "design portal")}
  ${card("Breakthrough / Discovery Design Alert", alertRows, alert.status || "watching")}
  <div class="grid-2">
    ${card("Required Components", componentRows, `${components.length} components`)}
    ${card("Required Systems", systemRows, `${systems.length} systems`)}
  </div>
  <div class="grid-2">
    ${card("Architecture Preview", nodeRows, portal.architecture?.style || "modular")}
    ${card("Runtime Data Flows", flowRows, `${flows.length} flows`)}
  </div>
  <div class="grid-2">
    ${card("Materials, Code, and Systems Needed", materialRows, materials.schema || "materials manifest")}
    ${card("Blueprint and Route Contract", routeRows, blueprintPackage.status || "blueprint draft")}
  </div>
  <div class="grid-2">
    ${card("Artifact Package", artifactRows, artifactPackage.status || "package")}
    ${card("CAD and Video Viewers", viewerRows, "viewer slots")}
  </div>
  ${card("Design Asset Viewer Surface", viewerSurface, "CAD + simulation")}
  <div class="grid-2">
    ${card("Portal Functions", actionRows, "actions")}
    ${card("Route Validation Chain", validationRows, validation.status || "validation")}
  </div>
  <div class="grid-2">
    ${card("Buildability Gates", gateRows, buildability.promotion_recommendation || "promotion review")}
    ${card("Live Design Runtime", eventRows, "stages 16-22")}
  </div>`;
}

function renderPortfolio() {
  return `${card("Portfolio Portal Actions", renderPortalCommandCenter(), "run / open")}
    ${card("Post-Run Output Handoff", renderPostRunHandoff(), dashboardState.post_run_handoff?.status || "waiting")}
    ${card("Portfolio", itemList("portfolio", "No portfolio records", "Portfolio records will populate after the default route runs."), "portfolio_creation_optimization")}`;
}

function renderDeals() {
  return `${card("Deal Portal Actions", renderPortalCommandCenter(), "run / review")}
    ${card("Deal Discovery", itemList("deals", "No deal packages", "Deal package records are not available yet."), "acquisition")}`;
}

function renderAcquirers() {
  return `${card("Acquirer Portal Actions", renderPortalCommandCenter(), "match / review")}
    ${card("Acquirer Match", itemList("acquirers", "No acquirer matches", "Acquirer matches will populate after acquisition routing."), "strategic")}`;
}

function renderStrategicWorld() {
  const strategic = dashboardState.strategic_world || {};
  const governance = strategic.governance || {};
  const authority = strategic.authority || {};
  const domains = Array.isArray(strategic.domains) ? strategic.domains.join(", ") : "waiting";
  const themes = Array.isArray(strategic.world_snapshot?.cross_domain_themes)
    ? strategic.world_snapshot.cross_domain_themes.join(", ")
    : "waiting";
  const rows = records("strategic_world");
  const recommendations = rows.length
    ? rows.map((item) => sourceRow(
      item.title || item.name || "Strategic recommendation",
      item.summary || item.domain || "operator review",
      item.status || "recommendation",
    )).join("")
    : emptyState("No strategic recommendations", "The next eligible run will attach ranked world-intelligence options.");
  return `<div class="kpi-row">
    ${kpi("Strategic Options", "O", "kpi-teal")}
    ${kpi("Recommendations", "R", "kpi-green")}
    ${kpi("Pending Review", "P", "kpi-amber")}
  </div>
  ${card("Strategic World Intelligence", `
    ${sourceRow("Layer status", strategic.status || "waiting_for_run", strategic.status || "waiting")}
    ${sourceRow("Domains", domains, domains === "waiting" ? "waiting" : "mapped")}
    ${sourceRow("Cross-domain themes", themes, themes === "waiting" ? "waiting" : "mapped")}
    ${sourceRow("Execution boundary", governance.execution_boundary || "recommendation_only", governance.external_execution_allowed ? "review" : "blocked")}
    ${sourceRow("External execution", governance.external_execution_allowed ? "allowed" : "blocked", governance.external_execution_allowed ? "review" : "blocked")}
    ${sourceRow("Runtime truth mutation", authority.runtime_truth_mutated ? "mutated" : "blocked", authority.runtime_truth_mutated ? "review" : "blocked")}
  `, strategic.status || "waiting")}
  ${card("Ranked Recommendations", recommendations, `${rows.length || 0} recommendations`)}`;
}

function renderModeCards() {
  const modePayload = dashboardState.intelligence_modes || {};
  const modes = modePayload.operator_selectable_modes || {};
  const order = ["deterministic", "connected", "hybrid"];
  const classMap = { deterministic: "mode-det", connected: "mode-con", hybrid: "mode-hyb" };
  const iconMap = { deterministic: "D", connected: "C", hybrid: "H" };
  return `<div class="mode-panel">
    ${order.map((id) => {
      const mode = modes[id] || {};
      const active = modePayload.active_mode === id ? " active-mode" : "";
      const state = mode.operator_state || (mode.enabled ? "ready_to_execute" : "ready_to_activate");
      const blockers = Array.isArray(mode.blockers) && mode.blockers.length ? mode.blockers.join(", ") : "none";
      return `<div class="mode-card ${classMap[id]}${active}">
        <div class="mode-card-icon">${iconMap[id]}</div>
        <div class="mode-card-name">${escapeText(mode.label || id)}</div>
        <div class="mode-card-desc">${escapeText(mode.operator_purpose || mode.description || "")}</div>
        <div class="chip-row">
          ${statusTag(mode.platform_ready === false ? "platform gap" : "platform ready")}
          ${statusTag(mode.activation_ready ? "activation ready" : "activation gap")}
          ${statusTag(mode.execution_ready ? "execution ready" : state)}
        </div>
        <div class="source-meta">Blockers: ${escapeText(blockers)}</div>
      </div>`;
    }).join("")}
  </div>`;
}

function renderModeWorkflow() {
  const modePayload = dashboardState.intelligence_modes || {};
  const steps = Array.isArray(modePayload.operator_workflow_order) ? modePayload.operator_workflow_order : [];
  return steps.length
    ? steps.map((step, index) => sourceRow(`${index + 1}. ${step.replaceAll("_", " ")}`, "platform-first activation sequence", index === 0 ? "current" : "queued")).join("")
    : emptyState("No mode workflow", "Mode workflow order is not exposed by the backend yet.");
}

function renderModes() {
  const modePayload = dashboardState.intelligence_modes || {};
  return `${card("Mode Control", `
    ${sourceRow("Active mode", dashboardState.active_intelligence_mode || "deterministic", "ready")}
    ${sourceRow("Platform mode completion", `${modePayload.platform_mode_completion_percent ?? "N/A"}%`, "operator ready")}
    ${sourceRow("Activation mode completion", `${modePayload.activation_mode_completion_percent ?? "N/A"}%`, "ready")}
    ${sourceRow("Live execution readiness", `${modePayload.live_execution_completion_percent ?? "N/A"}%`, "provider gated")}
    ${sourceRow("Provider gate", dashboardState.live_sources?.provider?.status || "provider_not_configured", dashboardState.live_sources?.provider?.live_search_enabled ? "enabled" : "gated")}
    ${renderModeCards()}
  `, "platform first")}
  ${card("Mode Workflow", renderModeWorkflow(), "operator sequence")}
  ${card("Safety Status", renderSafety(), "governed")}`;
}

function renderGovernance() {
  return `${card("Governance", itemList("governance", "No governance events", "Governance records will appear after controlled operations."), "authority")}
    ${card("Safety Status", renderSafety(), "locked")}`;
}

function renderActiveControlSummary() {
  const map = dashboardState.active_control_map || {};
  const controls = Array.isArray(map.controls) ? map.controls : [];
  const categories = Array.isArray(map.categories) ? map.categories.join(", ") : "waiting";
  return `${sourceRow("Control map", `${controls.length || 0} backend-bound controls`, map.status || "loading")}
    ${sourceRow("Categories", categories, controls.length ? "mapped" : "waiting")}
    ${sourceRow("Unsafe authority", map.authority?.unsafe_authority_unlocked === false ? "blocked" : "unknown", map.authority?.unsafe_authority_unlocked === false ? "blocked" : "review")}
    ${sourceRow("Result pane", "claire-active-control-result-pane", "ready")}`;
}

function renderActiveControlButtons() {
  const map = dashboardState.active_control_map || {};
  const controls = Array.isArray(map.controls) ? map.controls : [];
  if (!controls.length) {
    return emptyState("No active controls", "The dashboard is waiting for /api/dashboard/active-control-map.");
  }
  return `<div class="active-control-grid">
    ${controls.map((control) => `
      <button class="active-control-btn" type="button" onclick="runActiveControl('${escapeText(control.key)}')">
        <span>${escapeText(control.button_label || control.label || control.key)}</span>
        <small>${escapeText(control.category || "Capability")} / ${escapeText(control.operation_mode || "read_only")}</small>
      </button>`).join("")}
  </div>`;
}

function renderActiveControlResult() {
  if (!activeControlResult) {
    return emptyState("No control selected", "Click a control to fetch its primary backend endpoint and show the read-only result here.");
  }
  const endpointRows = activeControlResult.endpoints.map((entry) => sourceRow(
    entry.endpoint,
    entry.error || `HTTP ${entry.status_code}`,
    entry.ok ? "ok" : "blocked",
  )).join("");
  const preview = JSON.stringify(activeControlResult.primary_payload || activeControlResult, null, 2);
  return `<div id="claire-active-control-result-pane" class="active-control-result">
    ${sourceRow(activeControlResult.label || activeControlResult.key, activeControlResult.primary_endpoint, activeControlResult.status || "loaded")}
    ${endpointRows}
    <pre class="result-json">${escapeText(preview.slice(0, 7000))}</pre>
  </div>`;
}

function renderActiveControls() {
  return `${card("Active Control Map", renderActiveControlSummary(), dashboardState.active_control_map?.status || "loading")}
    ${card("Visible Backend Controls", renderActiveControlButtons(), "15 capabilities")}
    ${card("Control Result Pane", renderActiveControlResult(), "read only")}`;
}

function renderLearning() {
  return card("Learning Loop", itemList("learning", "No learning records", "Verified recursive feedback appears after eligible runs."), "verified memory");
}

function renderSubsystems() {
  return `<div class="kpi-row">
    ${kpi("Active Pipelines", "A", "kpi-green")}
    ${kpi("Pipeline Gaps", "G", "kpi-amber")}
    ${kpi("Tech Records", "T", "kpi-blue")}
    ${kpi("API Endpoint", "E", "kpi-teal")}
    ${kpi("Version", "V", "kpi-purple")}
  </div>
  ${card("Pipeline Activation Registry", renderPipelineActivation(), "pipeline_activation")}
  ${card("Canonical Runtime Routes to Dashboard Fields", renderSystemWiring(), "wired")}
  ${card("Project Owners for Runtime Wiring", renderSystemOwners(), "bound")}
  ${card("Subsystem Registry", renderSubsystemRegistry(), "backend_bound")}`;
}

function renderPipelineActivation() {
  const activation = dashboardState.pipeline_activation || {};
  const pipelines = Array.isArray(activation.pipelines) ? activation.pipelines : [];
  const rows = pipelines.length ? pipelines : [
    { name: "Active Pipelines", status: `${activation.activated_count || 0} active`, path: "pipeline_activation" },
    { name: "Pipeline Gaps", status: `${activation.placeholder_count || 0} placeholders`, path: "pipeline_activation" },
  ];
  return rows.map((item) => sourceRow(item.name || item.id || "Pipeline", item.path || item.owner || "pipeline_activation", item.status || "ready")).join("");
}

function renderSubsystemRegistry() {
  const subsystems = dashboardState.subsystems || dashboardState.systems || {};
  const rows = Array.isArray(subsystems) ? subsystems : Object.entries(subsystems).map(([name, value]) => ({ name, status: value?.status || value }));
  return rows.length
    ? rows.slice(0, 16).map((item) => sourceRow(item.name || item.id || "Subsystem", item.owner || item.path || "runtime", item.status || "ready")).join("")
    : emptyState("No subsystem registry", "Subsystem records are not exposed yet.");
}

function renderSafety() {
  return `${sourceRow("Runtime truth writes", "blocked unless explicitly governed", "blocked")}
    ${sourceRow("Live body ingestion", "review required before promotion", "review")}
    ${sourceRow("Route activation", "signals and conditions decide runtime branch", "ready")}
    ${sourceRow("Dashboard authority", "presentation only, backend owns truth", "ready")}`;
}

function card(title, body, badge) {
  return `<div class="card" style="margin-bottom:16px">
    <div class="card-header"><span class="card-title">${escapeText(title)}</span>${badge ? `<span class="live-badge"><span class="live-dot"></span>${escapeText(badge)}</span>` : ""}</div>
    <div class="card-body-scroll">${body}</div>
  </div>`;
}

function routeBox(type, icon, name, desc) {
  const selected = dashboardState.system_wiring?.selected_route || dashboardState.lifecycle?.route_selected || "";
  const active = selected.includes(type) || (type === "portfolio" && selected === "portfolio_creation_optimization");
  return `<div class="route-box route-${type}">
    <div class="route-icon">${escapeText(icon)}</div>
    <div><div class="route-name">${escapeText(name)}</div><div class="route-desc">${escapeText(desc)}</div></div>
    <div class="route-count">${active ? "selected" : "wired"}</div>
  </div>`;
}

const RENDERERS = {
  overview: renderOverview,
  lifecycle: renderLifecycle,
  signals: renderSignals,
  breakthroughs: renderBreakthroughs,
  technology: renderTechnology,
  design_portal: renderDesignPortal,
  portfolio: renderPortfolio,
  deals: renderDeals,
  acquirers: renderAcquirers,
  strategic_world: renderStrategicWorld,
  modes: renderModes,
  active_controls: renderActiveControls,
  review_queue: renderReviewQueuePortal,
  web_ops: renderWebOps,
  first_run: renderFirstRun,
  internet: renderInternet,
  updates: renderUpdates,
  accounts: renderAccounts,
  settings: renderSettings,
  admin: renderAdmin,
  governance: renderGovernance,
  learning: renderLearning,
  subsystems: renderSubsystems,
};

function buildNav() {
  const nav = document.getElementById("nav-items");
  if (!nav) return;
  const groups = [
    { label: "Intelligence", items: ["overview", "lifecycle", "signals", "breakthroughs"] },
    { label: "Portfolio & Deals", items: ["technology", "design_portal", "portfolio", "deals", "acquirers", "strategic_world"] },
    { label: "Operations", items: ["first_run", "review_queue", "web_ops", "internet", "updates"] },
    { label: "System", items: ["modes", "governance", "learning", "subsystems"] },
    { label: "Access & Admin", items: ["accounts", "settings", "admin", "active_controls"] },
  ];
  nav.innerHTML = groups.map((group) => `
    <div class="nav-section-label">${escapeText(group.label)}</div>
    ${group.items.map((id) => {
      const item = NAV.find((entry) => entry.id === id);
      return `<div class="nav-item ${id === activeSection ? "active" : ""}" data-id="${id}">
        <span class="nav-icon">${item.icon}</span><span>${escapeText(item.label)}</span>
      </div>`;
    }).join("")}
  `).join("");
  nav.querySelectorAll(".nav-item").forEach((node) => {
    node.addEventListener("click", () => setSection(node.dataset.id));
  });
}

function setSection(id) {
  activeSection = id || "overview";
  render();
}

function render() {
  buildNav();
  const title = NAV.find((item) => item.id === activeSection)?.label || "Overview";
  const titleNode = document.querySelector(".topbar-title");
  const subNode = document.querySelector(".topbar-sub");
  if (titleNode) titleNode.textContent = title;
  if (subNode) subNode.textContent = "Claire AI - ACS2 Platform - v19.61";
  const content = document.getElementById("main-content");
  if (content) content.innerHTML = (RENDERERS[activeSection] || renderOverview)();
  const health = document.getElementById("health-status-text");
  if (health) health.textContent = dashboardState.system_wiring?.missing?.length ? `GAPS ${dashboardState.system_wiring.missing.length}` : "READY";
}

async function refreshDashboardState() {
  let nextState = {};
  try {
    nextState = await fetchJson("/api/dashboard/state");
  } catch (error) {
    nextState = {
      metrics: {},
      records: {},
      project_file_bindings: { status: "backend_error", bindings: [] },
      system_wiring: { status: "backend_error", routes: [], owner_groups: [], missing: [] },
    };
  }
  dashboardState = nextState;
  dashboardState.operator_status = await fetchJson("/operator/status").catch(() => ({}));
  dashboardState.file_readiness = await fetchJson("/api/system/file-readiness").catch(() => ({}));
  dashboardState.route_integrity = await fetchJson("/api/system/route-integrity").catch(() => ({}));
  dashboardState.live_probe_status = await fetchJson("/api/governed/live-probe/status").catch(() => ({}));
  dashboardState.active_control_map = await fetchJson("/api/dashboard/active-control-map").catch(() => (
    dashboardState.active_control_map && Array.isArray(dashboardState.active_control_map.controls)
      ? dashboardState.active_control_map
      : { status: "backend_error", controls: [] }
  ));
  render();
}

async function runActiveControl(controlKey) {
  const map = dashboardState.active_control_map || {};
  const controls = Array.isArray(map.controls) ? map.controls : [];
  const control = controls.find((item) => item.key === controlKey);
  if (!control) return;
  const endpoints = [control.primary_endpoint, ...(control.secondary_endpoints || [])].filter(Boolean);
  activeControlResult = {
    key: control.key,
    label: control.label,
    primary_endpoint: control.primary_endpoint,
    status: "loading",
    endpoints: [],
    authority: {
      execution_enabled: control.execution_enabled,
      network_request_authority: control.network_request_authority,
      body_read_allowed: control.body_read_allowed,
      runtime_mutation_allowed: control.runtime_mutation_allowed,
    },
  };
  activeSection = "active_controls";
  render();
  const results = [];
  let primaryPayload = null;
  for (const endpoint of endpoints) {
    try {
      const payload = await fetchJson(endpoint, { method: "GET", cache: "no-store" });
      results.push({ endpoint, ok: true, status_code: 200 });
      if (endpoint === control.primary_endpoint) primaryPayload = payload;
    } catch (error) {
      results.push({ endpoint, ok: false, status_code: 0, error: error.message });
    }
  }
  activeControlResult = {
    ...activeControlResult,
    status: results[0]?.ok ? "loaded" : "endpoint_blocked_or_missing",
    endpoints: results,
    primary_payload: primaryPayload,
  };
  render();
}

async function runPortfolioPath() {
  await fetchJson("/evaluate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      raw_input: "Run the 30-stage Claire lifecycle through the default signal, trend, thesis, and portfolio intelligence path using the local governed project files.",
      mode: "deterministic",
      source_mode: "local_source_pack",
    }),
  });
  await refreshDashboardState();
}

async function startRuntimeCycle() {
  await fetchJson("/runtime/continuous/start", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ trigger: "dashboard" }),
  });
  await refreshDashboardState();
}

async function runAction(action) {
  if (action === "/evaluate") return runPortfolioPath();
  if (action === "/runtime/continuous/start") return startRuntimeCycle();
  return null;
}

function bindActions() {
  document.querySelectorAll("[data-action]").forEach((button) => {
    button.addEventListener("click", async () => {
      const action = button.getAttribute("data-action");
      button.disabled = true;
      try {
        await runAction(action);
      } finally {
        button.disabled = false;
      }
    });
  });
  const input = document.querySelector(".search-bar input");
  const searchButton = document.querySelector(".search-submit-btn");
  const webButton = document.querySelector(".search-web-btn");
  if (searchButton && input) searchButton.addEventListener("click", () => runProviderSearch(input.value));
  if (input) input.addEventListener("keydown", (event) => {
    if (event.key === "Enter") runProviderSearch(input.value);
  });
  if (webButton && input) webButton.addEventListener("click", () => openExternalSearch(input.value));
}

function tickClock() {
  const node = document.getElementById("live-clock");
  if (node) node.textContent = new Date().toLocaleString();
}

document.addEventListener("DOMContentLoaded", () => {
  buildNav();
  bindActions();
  tickClock();
  render();
  refreshDashboardState();
  setInterval(tickClock, 1000);
  setInterval(refreshDashboardState, 15000);
});
