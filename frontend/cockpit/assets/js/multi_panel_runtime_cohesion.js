(function () {
  "use strict";

  const PANEL_ID = "multi-panel-runtime-cohesion-panel";

  const PANEL_KEYS = [
    ["governed_runtime_timeline", "timeline"],
    ["governed_route_activity_overlay", "route activity"],
    ["continuous_runtime_presence", "presence"],
    ["governed_search_session", "search session"],
    ["governed_evidence_basket", "evidence basket"],
    ["runtime_continuity_visualization", "runtime continuity"],
    ["continuous_browser_runtime_loop", "browser loop"],
    ["governed_operator_workflow", "operator workflow"],
    ["canonical_browser_session_persistence", "browser session"]
  ];

  function text(value, fallback) {
    if (value === null || value === undefined || value === "") return fallback || "unknown";
    return String(value);
  }

  function computeCohesion(payload) {
    const panels = PANEL_KEYS.map(([key, label]) => {
      const value = payload && payload[key] ? payload[key] : null;
      const available = value && typeof value === "object";
      const authority = available && value.authority ? value.authority : {};
      const summary = available && value.summary ? value.summary : {};
      const runtimeAuthority = authority.runtime_authority || "blocked";
      const autonomousExpansion = authority.autonomous_execution_expansion === undefined ? false : authority.autonomous_execution_expansion;

      let state = available ? "available" : "missing";
      if (available && runtimeAuthority !== "blocked") state = "authority_drift";
      else if (available && autonomousExpansion !== false) state = "expansion_drift";

      return {
        key,
        label,
        state,
        available: Boolean(available),
        runtime_authority: runtimeAuthority,
        autonomous_execution_expansion: autonomousExpansion,
        selected_route: summary.selected_route || "unknown",
        payload_freshness: summary.payload_freshness || summary.last_payload_freshness || "unknown"
      };
    });

    const missing = panels.filter((panel) => panel.state === "missing");
    const drift = panels.filter((panel) => panel.state === "authority_drift" || panel.state === "expansion_drift");
    const selectedRoutes = Array.from(new Set(panels.map((panel) => panel.selected_route).filter((route) => route && route !== "unknown"))).sort();

    let cohesionState = "cohesive";
    if (drift.length) cohesionState = "blocked";
    else if (missing.length) cohesionState = "partial";
    else if (selectedRoutes.length > 1) cohesionState = "route_inconsistent";

    return {
      version: "v19.89.8-S27",
      status: "active",
      cohesion_state: cohesionState,
      authority: {
        backend_owns_truth: true,
        cockpit_presentation_only: true,
        runtime_authority: "blocked",
        browser_execution_authority: "blocked",
        runtime_mutation_enabled: false,
        fail_closed_governance: true,
        autonomous_execution_expansion: false
      },
      summary: {
        panel_total: panels.length,
        available_total: panels.filter((panel) => panel.available).length,
        missing_total: missing.length,
        drift_total: drift.length,
        selected_routes: selectedRoutes,
        payload_propagation: missing.length ? "partial" : "complete",
        runtime_cohesion: cohesionState
      },
      panels
    };
  }

  function stateClass(state) {
    if (state === "blocked") return "cohesion-blocked";
    if (state === "partial") return "cohesion-partial";
    if (state === "route_inconsistent") return "cohesion-inconsistent";
    return "cohesion-cohesive";
  }

  function panelStateClass(state) {
    if (state === "missing") return "panel-missing";
    if (state === "authority_drift" || state === "expansion_drift") return "panel-drift";
    return "panel-available";
  }

  function ensurePanel() {
    let panel = document.getElementById(PANEL_ID);
    if (panel) return panel;

    panel = document.createElement("section");
    panel.id = PANEL_ID;
    panel.className = "claire-card multi-panel-runtime-cohesion-card";
    panel.innerHTML = `
      <div class="multi-panel-cohesion-header">
        <div>
          <div class="multi-panel-cohesion-kicker">Multi-Panel Runtime Cohesion</div>
          <h2>Cockpit Cohesion</h2>
        </div>
        <div class="multi-panel-cohesion-badge">presentation only - authority blocked</div>
      </div>
      <div id="multi-panel-cohesion-summary" class="multi-panel-cohesion-summary">Waiting for canonical payload.</div>
      <div id="multi-panel-cohesion-grid" class="multi-panel-cohesion-grid"></div>
    `;

    const targets = ["#runtime-surface", "#operator-surface", "#main-content", "main", "#app", "body"];
    for (const selector of targets) {
      const target = document.querySelector(selector);
      if (target) {
        target.appendChild(panel);
        return panel;
      }
    }
    document.body.appendChild(panel);
    return panel;
  }

  function render(payload) {
    const panel = ensurePanel();
    const cohesion = payload && payload.multi_panel_runtime_cohesion ? payload.multi_panel_runtime_cohesion : computeCohesion(payload || {});
    const summary = cohesion.summary || {};
    const panels = Array.isArray(cohesion.panels) ? cohesion.panels : [];
    const summaryEl = panel.querySelector("#multi-panel-cohesion-summary");
    const gridEl = panel.querySelector("#multi-panel-cohesion-grid");

    panel.classList.remove("cohesion-cohesive", "cohesion-partial", "cohesion-blocked", "cohesion-inconsistent");
    panel.classList.add(stateClass(cohesion.cohesion_state));

    summaryEl.innerHTML = `
      <span><strong>Cohesion:</strong> ${text(cohesion.cohesion_state, "unknown")}</span>
      <span><strong>Panels:</strong> ${text(summary.available_total, "0")} / ${text(summary.panel_total, "0")}</span>
      <span><strong>Missing:</strong> ${text(summary.missing_total, "0")}</span>
      <span><strong>Drift:</strong> ${text(summary.drift_total, "0")}</span>
      <span><strong>Propagation:</strong> ${text(summary.payload_propagation, "unknown")}</span>
      <span><strong>Authority:</strong> blocked</span>
    `;

    gridEl.innerHTML = panels.map((item) => `
      <div class="multi-panel-cohesion-item ${panelStateClass(item.state)}">
        <div class="cohesion-panel-label">${text(item.label, "panel")}</div>
        <div class="cohesion-panel-state">${text(item.state, "unknown")}</div>
        <div class="cohesion-panel-meta">
          <span>route: ${text(item.selected_route, "unknown")}</span>
          <span>freshness: ${text(item.payload_freshness, "unknown")}</span>
          <span>authority: ${text(item.runtime_authority, "blocked")}</span>
        </div>
      </div>
    `).join("");
  }

  function poll() {
    fetch("/dashboard/payload", { cache: "no-store" })
      .then((response) => response.ok ? response.json() : null)
      .then((payload) => { if (payload) render(payload); })
      .catch(() => ensurePanel());
  }

  document.addEventListener("DOMContentLoaded", function () {
    ensurePanel();
    window.addEventListener("claire:canonical-payload", function (event) { render(event.detail || {}); });
    window.addEventListener("claire:payload", function (event) { render(event.detail || {}); });
    poll();
    setInterval(poll, 10000);
  });

  window.ClaireMultiPanelRuntimeCohesion = {
    version: "v19.89.8-S27",
    render,
    authority: "presentation_only_runtime_authority_blocked"
  };
})();
