(function () {
  "use strict";

  const PANEL_ID = "governed-operational-topology-continuity-panel";

  function text(value, fallback) {
    if (value === null || value === undefined || value === "") return fallback || "unknown";
    return String(value);
  }

  function computeContinuity(payload) {
    const multiWorkspace = payload && payload.governed_multi_workspace_orchestration ? payload.governed_multi_workspace_orchestration : {};
    const workspace = payload && payload.governed_runtime_workspace_continuity ? payload.governed_runtime_workspace_continuity : {};
    const orchestration = payload && payload.governed_operational_session_orchestration ? payload.governed_operational_session_orchestration : {};
    const cohesion = payload && payload.multi_panel_runtime_cohesion ? payload.multi_panel_runtime_cohesion : {};
    const loop = payload && payload.continuous_browser_runtime_loop ? payload.continuous_browser_runtime_loop : {};

    const topologySummary = multiWorkspace.summary || {};
    const workspaceSummary = workspace.summary || {};
    const sessionSummary = orchestration.summary || {};
    const cohesionSummary = cohesion.summary || {};
    const loopSummary = loop.summary || {};

    const workspaceTotal = Number(topologySummary.workspace_total || 0);
    const missingTotal = Number(topologySummary.missing_panel_total || cohesionSummary.missing_total || 0);
    const driftTotal = Number(topologySummary.authority_drift_total || cohesionSummary.drift_total || 0);

    const topologyState = multiWorkspace.topology_state || "unknown";
    const workspaceState = workspace.workspace_state || "unknown";
    const sessionState = orchestration.session_state || "unknown";
    const loopState = loop.loop_state || "unknown";

    let continuityState = "continuous";
    if (driftTotal || topologyState === "blocked") continuityState = "blocked";
    else if (missingTotal || topologyState === "partial") continuityState = "partial";
    else if (topologyState === "degraded" || topologyState === "recovering") continuityState = topologyState;
    else if (topologyState === "review_required" || workspaceState === "review_required" || sessionState === "review_required") continuityState = "review_required";
    else if (topologyState === "unknown" && workspaceState === "unknown") continuityState = "initializing";

    return {
      version: "v19.89.8-S31",
      status: "active",
      continuity_state: continuityState,
      authority: {
        backend_owns_truth: true,
        cockpit_presentation_only: true,
        runtime_authority: "blocked",
        browser_execution_authority: "blocked",
        operator_mutation_enabled: false,
        runtime_mutation_enabled: false,
        workspace_mutation_enabled: false,
        topology_mutation_enabled: false,
        fail_closed_governance: true,
        autonomous_execution_expansion: false
      },
      summary: {
        workspace_total: workspaceTotal,
        selected_route: topologySummary.selected_route || workspaceSummary.selected_route || "unknown",
        topology_state: topologyState,
        workspace_state: workspaceState,
        session_state: sessionState,
        loop_state: loopState,
        missing_panel_total: missingTotal,
        authority_drift_total: driftTotal,
        payload_propagation: topologySummary.payload_propagation || cohesionSummary.payload_propagation || "unknown",
        manual_review_required: Boolean(topologySummary.manual_review_required || workspaceSummary.manual_review_required)
      },
      continuity_chain: [
        { layer: "multi_workspace_topology", state: topologyState, detail: workspaceTotal + " workspaces" },
        { layer: "workspace_continuity", state: workspaceState, detail: workspaceSummary.selected_route || "unknown" },
        { layer: "session_orchestration", state: sessionState, detail: sessionSummary.selected_route || "unknown" },
        { layer: "panel_cohesion", state: cohesion.cohesion_state || "unknown", detail: cohesionSummary.payload_propagation || "unknown" },
        { layer: "browser_loop", state: loopState, detail: loopSummary.payload_freshness || "unknown" }
      ]
    };
  }

  function stateClass(state) {
    if (state === "blocked") return "topology-continuity-blocked";
    if (state === "partial") return "topology-continuity-partial";
    if (state === "review_required") return "topology-continuity-review";
    if (state === "degraded") return "topology-continuity-degraded";
    if (state === "recovering") return "topology-continuity-recovering";
    if (state === "initializing") return "topology-continuity-initializing";
    return "topology-continuity-continuous";
  }

  function ensurePanel() {
    let panel = document.getElementById(PANEL_ID);
    if (panel) return panel;

    panel = document.createElement("section");
    panel.id = PANEL_ID;
    panel.className = "claire-card governed-operational-topology-continuity-card";
    panel.innerHTML = `
      <div class="topology-continuity-header">
        <div>
          <div class="topology-continuity-kicker">Operational Topology Continuity</div>
          <h2>Topology Continuity</h2>
        </div>
        <div class="topology-continuity-badge">presentation only - topology mutation blocked</div>
      </div>
      <div id="topology-continuity-summary" class="topology-continuity-summary">Waiting for canonical payload.</div>
      <div id="topology-continuity-chain" class="topology-continuity-chain"></div>
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
    const continuity = payload && payload.governed_operational_topology_continuity
      ? payload.governed_operational_topology_continuity
      : computeContinuity(payload || {});
    const summary = continuity.summary || {};
    const chain = Array.isArray(continuity.continuity_chain) ? continuity.continuity_chain : [];
    const summaryEl = panel.querySelector("#topology-continuity-summary");
    const chainEl = panel.querySelector("#topology-continuity-chain");

    panel.classList.remove("topology-continuity-blocked", "topology-continuity-partial", "topology-continuity-review", "topology-continuity-degraded", "topology-continuity-recovering", "topology-continuity-initializing", "topology-continuity-continuous");
    panel.classList.add(stateClass(continuity.continuity_state));

    summaryEl.innerHTML = `
      <span><strong>Continuity:</strong> ${text(continuity.continuity_state, "unknown")}</span>
      <span><strong>Workspaces:</strong> ${text(summary.workspace_total, "0")}</span>
      <span><strong>Route:</strong> ${text(summary.selected_route, "unknown")}</span>
      <span><strong>Topology:</strong> ${text(summary.topology_state, "unknown")}</span>
      <span><strong>Session:</strong> ${text(summary.session_state, "unknown")}</span>
      <span><strong>Mutation:</strong> blocked</span>
    `;

    chainEl.innerHTML = chain.map((item) => `
      <div class="topology-continuity-node">
        <div class="topology-continuity-node-layer">${text(item.layer, "layer")}</div>
        <div class="topology-continuity-node-state">${text(item.state, "unknown")}</div>
        <div class="topology-continuity-node-detail">${text(item.detail, "unknown")}</div>
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

  window.ClaireGovernedOperationalTopologyContinuity = {
    version: "v19.89.8-S31",
    render,
    authority: "presentation_only_runtime_authority_blocked"
  };
})();
