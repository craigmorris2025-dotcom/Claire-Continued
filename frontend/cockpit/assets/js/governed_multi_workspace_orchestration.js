(function () {
  "use strict";

  const PANEL_ID = "governed-multi-workspace-orchestration-panel";

  function text(value, fallback) {
    if (value === null || value === undefined || value === "") return fallback || "unknown";
    return String(value);
  }

  function computeTopology(payload) {
    const workspace = payload && payload.governed_runtime_workspace_continuity ? payload.governed_runtime_workspace_continuity : {};
    const orchestration = payload && payload.governed_operational_session_orchestration ? payload.governed_operational_session_orchestration : {};
    const cohesion = payload && payload.multi_panel_runtime_cohesion ? payload.multi_panel_runtime_cohesion : {};
    const overlay = payload && payload.governed_route_activity_overlay ? payload.governed_route_activity_overlay : {};
    const evidence = payload && payload.governed_evidence_basket ? payload.governed_evidence_basket : {};
    const workflow = payload && payload.governed_operator_workflow ? payload.governed_operator_workflow : {};

    const workspaceSummary = workspace.summary || {};
    const orchSummary = orchestration.summary || {};
    const cohesionSummary = cohesion.summary || {};
    const evidenceSummary = evidence.summary || {};
    const workflowSummary = workflow.summary || {};

    const selectedRoute = workspaceSummary.selected_route || orchSummary.selected_route || "unknown";
    const evidenceTotal = Number(evidenceSummary.evidence_total || workspaceSummary.evidence_total || 0);
    const workflowTotal = Number(workflowSummary.workflow_total || workspaceSummary.workflow_total || 0);
    const missingTotal = Number(cohesionSummary.missing_total || workspaceSummary.missing_panel_total || 0);
    const driftTotal = Number(cohesionSummary.drift_total || workspaceSummary.authority_drift_total || 0);

    let workspaces = [];
    if (Array.isArray(overlay.routes)) {
      workspaces = overlay.routes.map((route) => ({
        workspace_id: "workspace:" + (route.route || "unknown"),
        route: route.route || "unknown",
        state: route.state || "unknown",
        selected: Boolean(route.selected),
        owned_surface_count: Number(route.owned_surface_count || 0),
        runtime_authority: "blocked",
        workspace_mutation_enabled: false
      }));
    }

    if (!workspaces.length) {
      workspaces.push({
        workspace_id: "workspace:" + selectedRoute,
        route: selectedRoute,
        state: workspace.workspace_state || "unknown",
        selected: selectedRoute !== "unknown",
        owned_surface_count: 0,
        runtime_authority: "blocked",
        workspace_mutation_enabled: false
      });
    }

    let topologyState = "coordinated";
    if (driftTotal) topologyState = "blocked";
    else if (missingTotal) topologyState = "partial";
    else if (workspaces.some((item) => item.state === "degraded")) topologyState = "degraded";
    else if (workspaces.some((item) => item.state === "recovering")) topologyState = "recovering";
    else if (workspace.workspace_state === "review_required" || workflowSummary.manual_review_required) topologyState = "review_required";

    return {
      version: "v19.89.8-S30",
      status: "active",
      topology_state: topologyState,
      authority: {
        backend_owns_truth: true,
        cockpit_presentation_only: true,
        runtime_authority: "blocked",
        browser_execution_authority: "blocked",
        operator_mutation_enabled: false,
        runtime_mutation_enabled: false,
        workspace_mutation_enabled: false,
        multi_workspace_mutation_enabled: false,
        fail_closed_governance: true,
        autonomous_execution_expansion: false
      },
      summary: {
        workspace_total: workspaces.length,
        selected_route: selectedRoute,
        workflow_total: workflowTotal,
        evidence_total: evidenceTotal,
        missing_panel_total: missingTotal,
        authority_drift_total: driftTotal,
        manual_review_required: Boolean(workflowSummary.manual_review_required),
        payload_propagation: cohesionSummary.payload_propagation || "unknown",
        workspace_state: workspace.workspace_state || "unknown",
        session_state: orchestration.session_state || "unknown"
      },
      workspaces
    };
  }

  function stateClass(state) {
    if (state === "blocked") return "multi-workspace-blocked";
    if (state === "partial") return "multi-workspace-partial";
    if (state === "review_required") return "multi-workspace-review";
    if (state === "degraded") return "multi-workspace-degraded";
    if (state === "recovering") return "multi-workspace-recovering";
    return "multi-workspace-coordinated";
  }

  function workspaceClass(state) {
    if (state === "degraded") return "workspace-node-degraded";
    if (state === "recovering") return "workspace-node-recovering";
    if (state === "active") return "workspace-node-active";
    return "workspace-node-neutral";
  }

  function ensurePanel() {
    let panel = document.getElementById(PANEL_ID);
    if (panel) return panel;

    panel = document.createElement("section");
    panel.id = PANEL_ID;
    panel.className = "claire-card governed-multi-workspace-orchestration-card";
    panel.innerHTML = `
      <div class="multi-workspace-header">
        <div>
          <div class="multi-workspace-kicker">Multi-Workspace Orchestration</div>
          <h2>Operational Workspace Topology</h2>
        </div>
        <div class="multi-workspace-badge">presentation only - mutation blocked</div>
      </div>
      <div id="multi-workspace-summary" class="multi-workspace-summary">Waiting for canonical payload.</div>
      <div id="multi-workspace-grid" class="multi-workspace-grid"></div>
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
    const topology = payload && payload.governed_multi_workspace_orchestration
      ? payload.governed_multi_workspace_orchestration
      : computeTopology(payload || {});
    const summary = topology.summary || {};
    const workspaces = Array.isArray(topology.workspaces) ? topology.workspaces : [];
    const summaryEl = panel.querySelector("#multi-workspace-summary");
    const gridEl = panel.querySelector("#multi-workspace-grid");

    panel.classList.remove("multi-workspace-blocked", "multi-workspace-partial", "multi-workspace-review", "multi-workspace-degraded", "multi-workspace-recovering", "multi-workspace-coordinated");
    panel.classList.add(stateClass(topology.topology_state));

    summaryEl.innerHTML = `
      <span><strong>Topology:</strong> ${text(topology.topology_state, "unknown")}</span>
      <span><strong>Workspaces:</strong> ${text(summary.workspace_total, "0")}</span>
      <span><strong>Selected route:</strong> ${text(summary.selected_route, "unknown")}</span>
      <span><strong>Workflow:</strong> ${text(summary.workflow_total, "0")}</span>
      <span><strong>Evidence:</strong> ${text(summary.evidence_total, "0")}</span>
      <span><strong>Mutation:</strong> blocked</span>
    `;

    gridEl.innerHTML = workspaces.map((workspace) => `
      <div class="multi-workspace-node ${workspaceClass(workspace.state)}">
        <div class="multi-workspace-node-id">${text(workspace.workspace_id, "workspace")}</div>
        <div class="multi-workspace-node-state">${text(workspace.state, "unknown")}${workspace.selected ? " / selected" : ""}</div>
        <div class="multi-workspace-node-meta">
          <span>route: ${text(workspace.route, "unknown")}</span>
          <span>surfaces: ${text(workspace.owned_surface_count, "0")}</span>
          <span>authority: blocked</span>
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

  window.ClaireGovernedMultiWorkspaceOrchestration = {
    version: "v19.89.8-S30",
    render,
    authority: "presentation_only_runtime_authority_blocked"
  };
})();
