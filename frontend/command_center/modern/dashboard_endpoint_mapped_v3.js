"use strict";

(function () {
  const mapEl = document.getElementById("claire-endpoint-map");
  const endpointMap = mapEl ? JSON.parse(mapEl.textContent || "{}") : { endpoints: [], portals: [], summary: {} };
  const state = { endpoints: Array.isArray(endpointMap.endpoints) ? endpointMap.endpoints : [], domainFilter: "all", search: "", activePortal: "overview" };
  const $ = (selector) => document.querySelector(selector);

  function escapeHtml(value) {
    return String(value == null ? "" : value).replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;").replaceAll("'", "&#039;");
  }
  function safeJson(value) { try { return JSON.stringify(value, null, 2); } catch (error) { return String(value); } }
  function setReady(key, text, stateName) { const el = document.querySelector(`[data-ready="${key}"]`); if (el) { el.textContent = text; el.dataset.state = stateName || "unknown"; } }

  async function fetchJson(path) {
    const response = await fetch(path, { method: "GET", headers: { "Accept": "application/json" }, cache: "no-store" });
    const contentType = response.headers.get("content-type") || "";
    const payload = contentType.includes("application/json") ? await response.json() : { raw_text: await response.text() };
    return { status: response.status, ok: response.ok, payload };
  }

  function filteredEndpoints() {
    const term = state.search.trim().toLowerCase();
    return state.endpoints.filter((ep) => {
      if (state.domainFilter !== "all" && ep.domain_key !== state.domainFilter) return false;
      if (!term) return true;
      const text = `${ep.path} ${(ep.methods || []).join(" ")} ${ep.domain_label} ${ep.name} ${ep.module}`.toLowerCase();
      return text.includes(term);
    });
  }

  function renderEndpoints() {
    const list = $("#endpoint-list");
    if (!list) return;
    const endpoints = filteredEndpoints();
    if (!endpoints.length) { list.innerHTML = `<div class="empty-state"><strong>No endpoints matched.</strong></div>`; return; }
    list.innerHTML = "";
    for (const ep of endpoints) {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "endpoint-button";
      button.dataset.endpointPath = ep.path;
      button.dataset.domainKey = ep.domain_key;
      button.dataset.policy = ep.execution_policy;
      const methodTags = (ep.methods || []).map((m) => `<span class="${m === "GET" ? "tag tag--get" : "tag tag--post"}">${escapeHtml(m)}</span>`).join("");
      const policyTag = ep.button_policy === "fetch_result_pane" ? `<span class="tag tag--get">fetchable</span>` : `<span class="tag tag--blocked">blocked/mapped</span>`;
      button.innerHTML = `<strong>${escapeHtml(ep.domain_label)}</strong><code>${escapeHtml(ep.path)}</code><span class="endpoint-meta">${methodTags}${policyTag}<span class="tag">${escapeHtml(ep.id)}</span></span>`;
      button.addEventListener("click", () => runEndpoint(ep));
      list.appendChild(button);
    }
  }

  async function runEndpoint(ep) {
    const pane = $("#result-pane");
    if (!pane) return;
    if (ep.button_policy !== "fetch_result_pane" || !(ep.methods || []).includes("GET")) {
      pane.innerHTML = `<div class="result-header"><strong>${escapeHtml(ep.domain_label)}</strong><code>${escapeHtml(ep.path)}</code><span class="tag tag--blocked">Execution blocked</span></div><p>This endpoint is mapped into the operator dashboard, but direct execution is blocked because it is parameterized, non-GET, or not allowed as a read-only review endpoint.</p><pre>${escapeHtml(safeJson(ep))}</pre>`;
      return;
    }
    pane.innerHTML = `<div class="result-header"><strong>${escapeHtml(ep.domain_label)}</strong><code>GET ${escapeHtml(ep.path)}</code><span class="tag tag--get">Fetching real backend endpoint</span></div>`;
    try {
      const result = await fetchJson(ep.path);
      pane.innerHTML = `<div class="result-header"><strong>${escapeHtml(ep.domain_label)}</strong><code>GET ${escapeHtml(ep.path)}</code><span class="tag ${result.ok ? "tag--get" : "tag--blocked"}">status ${result.status}</span></div><pre>${escapeHtml(safeJson(result.payload))}</pre>`;
      routePayloadToPortal(ep, result.payload);
    } catch (error) {
      pane.innerHTML = `<div class="result-header"><strong>Fetch failed</strong><code>${escapeHtml(ep.path)}</code></div><pre>${escapeHtml(String(error && error.message ? error.message : error))}</pre>`;
    }
  }

  function endpointsForPortal(portalKey) {
    const rules = {
      overview: ["system", "dashboard"],
      lifecycle: ["lifecycle", "route_decision"],
      evidence: ["search_evidence"],
      portfolio: ["portfolio"],
      breakthrough: ["breakthrough_design"],
      acquisition: ["acquisition_package"],
      updates: ["update_governance"],
      qa: ["qa_cognitive"],
      memory: ["memory_replay"],
      systems: ["existing_system"],
      diagnostics: ["system", "dashboard", "other", "exports"]
    };
    return state.endpoints.filter((ep) => (rules[portalKey] || []).includes(ep.domain_key));
  }

  function renderPortals() {
    for (const panel of document.querySelectorAll("[data-portal-panel]")) {
      const key = panel.dataset.portalPanel;
      panel.classList.toggle("is-active", key === state.activePortal);
      const out = document.getElementById(`portal-${key}-output`);
      const actions = document.getElementById(`portal-${key}-actions`);
      if (!out || !actions) continue;
      const eps = endpointsForPortal(key);
      out.innerHTML = `<p><strong>${eps.length}</strong> mapped endpoints for this portal.</p><pre>${escapeHtml(safeJson(eps.slice(0, 30)))}</pre>`;
      actions.innerHTML = "";
      for (const ep of eps.slice(0, 18)) {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "portal-action-button";
        btn.textContent = `${(ep.methods || []).join("/")} ${ep.path}`;
        btn.addEventListener("click", () => runEndpoint(ep));
        actions.appendChild(btn);
      }
    }
    for (const tab of document.querySelectorAll("[data-portal-tab]")) tab.classList.toggle("is-active", tab.dataset.portalTab === state.activePortal);
  }

  function routePayloadToPortal(ep, payload) {
    const portalByDomain = { lifecycle: "lifecycle", route_decision: "lifecycle", search_evidence: "evidence", portfolio: "portfolio", breakthrough_design: "breakthrough", acquisition_package: "acquisition", update_governance: "updates", qa_cognitive: "qa", memory_replay: "memory", existing_system: "systems", system: "diagnostics", dashboard: "overview", exports: "diagnostics", other: "diagnostics" };
    const portal = portalByDomain[ep.domain_key] || "diagnostics";
    const out = document.getElementById(`portal-${portal}-output`);
    if (out) out.innerHTML = `<p><strong>Latest routed result:</strong> ${escapeHtml(ep.path)}</p><pre>${escapeHtml(safeJson(payload))}</pre>`;
  }

  function renderSystemReadiness(payload) {
    const out = document.getElementById("portal-diagnostics-output") || $("#result-pane");
    if (!out || !payload) return;
    const pollution = payload.pollution_summary || {};
    const requiredRoots = Array.isArray(payload.required_roots) ? payload.required_roots : [];
    const pollutionRoots = Array.isArray(payload.pollution_roots) ? payload.pollution_roots : [];
    out.innerHTML = [
      `<p><strong>Operational file readiness:</strong> ${escapeHtml(payload.status || "unknown")}</p>`,
      `<p>Required roots present: ${requiredRoots.filter((item) => item.exists).length}/${requiredRoots.length}. Pollution roots: ${escapeHtml(pollution.pollution_root_count || 0)}. Pollution files: ${escapeHtml(pollution.pollution_file_count || 0)}.</p>`,
      `<pre>${escapeHtml(safeJson({
        missing_required: payload.missing_required || [],
        target_missing: payload.target_missing || [],
        blockers: payload.blockers || [],
        pollution_summary: pollution,
        pollution_roots: pollutionRoots.map((item) => ({ name: item.name, file_count: item.file_count, size_mb: item.size_mb, cleanup_class: item.cleanup_class }))
      }))}</pre>`
    ].join("");
  }

  function setOpsCard(prefix, status, detail, stateName) {
    const statusEl = document.getElementById(`ops-${prefix}-status`);
    const detailEl = document.getElementById(`ops-${prefix}-detail`);
    const card = statusEl ? statusEl.closest("article") : null;
    if (statusEl) statusEl.textContent = status || "Unknown";
    if (detailEl) detailEl.textContent = detail || "";
    if (card) card.dataset.state = stateName || "degraded";
  }

  function appendRouteIntegrity(payload) {
    const out = document.getElementById("portal-diagnostics-output") || $("#result-pane");
    if (!out || !payload) return;
    const dashboardPayload = payload.dashboard_payload || {};
    out.innerHTML += [
      `<p><strong>Route integrity:</strong> ${escapeHtml(payload.status || "unknown")}</p>`,
      `<pre>${escapeHtml(safeJson({
        route_count: payload.route_count,
        duplicate_route_count: payload.duplicate_route_count,
        dashboard_payload: dashboardPayload,
        blockers: payload.blockers || []
      }))}</pre>`
    ].join("");
  }

  function wireFilters() {
    for (const chip of document.querySelectorAll("[data-domain-filter]")) {
      chip.addEventListener("click", () => {
        state.domainFilter = chip.dataset.domainFilter || "all";
        document.querySelectorAll("[data-domain-filter]").forEach((el) => el.classList.toggle("is-active", el === chip));
        renderEndpoints();
      });
    }
  }
  function wirePortals() {
    for (const tab of document.querySelectorAll("[data-portal-tab]")) {
      tab.addEventListener("click", () => { state.activePortal = tab.dataset.portalTab || "overview"; renderPortals(); });
    }
  }
  function wireCommand() {
    const form = $("#dashboard-command-form");
    const input = $("#dashboard-search-input");
    if (!form || !input) return;
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      state.search = input.value || "";
      renderEndpoints();
      const pane = $("#result-pane");
      if (pane) pane.innerHTML = `<div class="result-header"><strong>Command/search staged</strong><code>${escapeHtml(state.search)}</code><span class="tag">review-only</span></div><p>The command bar filters the endpoint map now. Autonomous command execution remains blocked until explicit governed execution is implemented.</p><pre>${escapeHtml(safeJson({ query: state.search, mode: ($("#dashboard-command-mode") || {}).value || "endpoint", authority: "review_only" }))}</pre>`;
    });
    input.addEventListener("input", () => { state.search = input.value || ""; renderEndpoints(); });
  }

  async function bootstrapStatus() {
    setReady("authority", "Authority: blocked/review-only", "blocked");
    setReady("endpoint-map", `Endpoint map: ${endpointMap.summary.endpoint_count || 0} endpoints`, "ok");
    try { const payloadStatus = await fetchJson("/dashboard/payload/status"); setReady("payload", `Payload status: ${payloadStatus.status}`, payloadStatus.ok ? "ok" : "blocked"); } catch (error) { setReady("payload", "Payload: unavailable", "blocked"); }
    try { const controls = await fetchJson("/api/dashboard/active-control-map"); setReady("active-controls", `Active controls: ${controls.status}`, controls.ok ? "ok" : "blocked"); } catch (error) { setReady("active-controls", "Active controls: unavailable", "blocked"); }
    try {
      const readiness = await fetchJson("/api/system/file-readiness");
      const payload = readiness.payload || {};
      const pollution = payload.pollution_summary || {};
      setReady("file-readiness", `Files: ${payload.status || readiness.status} / pollution ${pollution.pollution_root_count || 0}`, readiness.ok && payload.status !== "missing" ? "ok" : "blocked");
      setOpsCard(
        "system",
        payload.status || "unknown",
        `${(payload.blockers || []).length} blockers; ${pollution.pollution_file_count || 0} pollution files tracked.`,
        payload.status === "ready" ? "ready" : "degraded"
      );
      renderSystemReadiness(payload);
    } catch (error) {
      setReady("file-readiness", "Files: unavailable", "blocked");
      setOpsCard("system", "unavailable", "File readiness endpoint did not respond.", "blocked");
    }
    try {
      const integrity = await fetchJson("/api/system/route-integrity");
      const payload = integrity.payload || {};
      setReady("route-integrity", `Routes: ${payload.status || integrity.status} / dup ${payload.duplicate_route_count || 0}`, integrity.ok && payload.status === "ready" ? "ok" : "blocked");
      setOpsCard(
        "route",
        payload.status || "unknown",
        `${payload.route_count || 0} routes; ${payload.duplicate_route_count || 0} duplicate owners; payload owner locked: ${payload.dashboard_payload && payload.dashboard_payload.canonical_payload_locked ? "yes" : "no"}.`,
        payload.status === "ready" ? "ready" : "degraded"
      );
      appendRouteIntegrity(payload);
    } catch (error) {
      setReady("route-integrity", "Routes: unavailable", "blocked");
      setOpsCard("route", "unavailable", "Route integrity endpoint did not respond.", "blocked");
    }
    try {
      const live = await fetchJson("/api/governed/live-probe/status");
      const payload = live.payload || {};
      setOpsCard(
        "live",
        payload.status || "unknown",
        `Ready: ${payload.ready ? "yes" : "no"}; method: ${payload.method_allowed || "blocked"}; body reads: ${payload.body_read_allowed ? "allowed" : "blocked"}.`,
        payload.ready ? "degraded" : "blocked"
      );
    } catch (error) {
      setOpsCard("live", "unavailable", "Governed live-probe status did not respond.", "blocked");
    }
    try {
      const payloadResult = await fetchJson("/dashboard/payload");
      const payload = payloadResult.payload || {};
      const authority = payload.authority || {};
      setOpsCard(
        "payload",
        payload.status || "unknown",
        `Backend owns truth: ${payload.backend_owns_truth ? "yes" : "no"}; lifecycle stages: ${(payload.lifecycle_stages || []).length || (payload.lifecycle && payload.lifecycle.stage_count) || 0}; live web: ${authority.live_web_execution || payload.live_web_execution_status || "blocked"}.`,
        payloadResult.ok && payload.backend_owns_truth ? "ready" : "degraded"
      );
    } catch (error) {
      setOpsCard("payload", "unavailable", "Dashboard payload did not respond.", "blocked");
    }
    setReady("dashboard", "Dashboard route: V3 active", "ok");
  }

  document.addEventListener("DOMContentLoaded", () => { wireFilters(); wirePortals(); wireCommand(); renderEndpoints(); renderPortals(); bootstrapStatus(); });
  window.ClaireDashboardV3 = { endpointMap, state, renderEndpoints, runEndpoint, renderPortals };
})();
