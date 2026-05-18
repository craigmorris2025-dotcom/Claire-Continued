(function () {
  "use strict";

  const PANEL_ID = "governed-runtime-workspace-continuity-panel";

  function text(value, fallback) {
    if (value === null || value === undefined || value === "") return fallback || "unknown";
    return String(value);
  }

  function computeWorkspace(payload) {
    const orchestration = payload && payload.governed_operational_session_orchestration ? payload.governed_operational_session_orchestration : {};
    const browserSession = payload && payload.canonical_browser_session_persistence ? payload.canonical_browser_session_persistence : {};
    const workflow = payload && payload.governed_operator_workflow ? payload.governed_operator_workflow : {};
    const evidence = payload && payload.governed_evidence_basket ? payload.governed_evidence_basket : {};
    const cohesion = payload && payload.multi_panel_runtime_cohesion ? payload.multi_panel_runtime_cohesion : {};
    const continuity = payload && payload.runtime_continuity_visualization ? payload.runtime_continuity_visualization : {};

    const orchSummary = orchestration.summary || {};
    const sessionSnapshot = browserSession.session_snapshot || {};
    const workflowSummary = workflow.summary || {};
    const evidenceSummary = evidence.summary || {};
    const cohesionSummary = cohesion.summary || {};
    const continuitySummary = continuity.summary || {};

    const selectedRoute = orchSummary.selected_route || sessionSnapshot.selected_route || continuitySummary.selected_route || "unknown";
    const missingPanels = Number(cohesionSummary.missing_total || orchSummary.missing_panel_total || 0);
    const driftTotal = Number(cohesionSummary.drift_total || orchSummary.authority_drift_total || 0);
    const workflowTotal = Number(workflowSummary.workflow_total || orchSummary.workflow_total || 0);
    const evidenceTotal = Number(evidenceSummary.evidence_total || orchSummary.evidence_total || 0);

    let workspaceState = "continuous";
    if (driftTotal) workspaceState = "blocked";
    else if (missingPanels) workspaceState = "partial";
    else if (orchestration.session_state === "review_required" || workflowSummary.manual_review_required) workspaceState = "review_required";
    else if (continuity.continuity_state === "degraded" || continuity.continuity_state === "recovering") workspaceState = continuity.continuity_state;

    return {
      version: "v19.89.8-S29",
      status: "active",
      workspace_id: "workspace:" + selectedRoute,
      workspace_state: workspaceState,
      authority: {
        backend_owns_truth: true,
        cockpit_presentation_only: true,
        runtime_authority: "blocked",
        browser_execution_authority: "blocked",
        operator_mutation_enabled: false,
        runtime_mutation_enabled: false,
        workspace_mutation_enabled: false,
        fail_closed_governance: true,
        autonomous_execution_expansion: false
      },
      summary: {
        selected_route: selectedRoute,
        workflow_total: workflowTotal,
        evidence_total: evidenceTotal,
        missing_panel_total: missingPanels,
        authority_drift_total: driftTotal,
        manual_review_required: Boolean(workflowSummary.manual_review_required),
        payload_freshness: sessionSnapshot.payload_freshness || continuitySummary.payload_freshness || "unknown",
        continuity_state: continuity.continuity_state || "unknown",
        session_state: orchestration.session_state || "unknown"
      },
      workspace_dimensions: [
        { dimension: "route_workspace", state: selectedRoute !== "unknown" ? "bound" : "unbound", detail: selectedRoute },
        { dimension: "session_workspace", state: orchestration.session_state || "unknown", detail: Array.isArray(orchestration.session_bindings) ? orchestration.session_bindings.length + " bindings" : "0 bindings" },
        { dimension: "workflow_workspace", state: workflowTotal ? "active" : "idle", detail: workflowTotal + " workflow items" },
        { dimension: "evidence_workspace", state: evidenceTotal ? "active" : "empty", detail: evidenceTotal + " evidence items" },
        { dimension: "cohesion_workspace", state: cohesion.cohesion_state || "unknown", detail: cohesionSummary.payload_propagation || "unknown" }
      ]
    };
  }

  function stateClass(state) {
    if (state === "blocked") return "workspace-blocked";
    if (state === "partial") return "workspace-partial";
    if (state === "review_required") return "workspace-review";
    if (state === "degraded") return "workspace-degraded";
    if (state === "recovering") return "workspace-recovering";
    return "workspace-continuous";
  }

  function ensurePanel() {
    let panel = document.getElementById(PANEL_ID);
    if (panel) return panel;

    panel = document.createElement("section");
    panel.id = PANEL_ID;
    panel.className = "claire-card governed-runtime-workspace-continuity-card";
    panel.innerHTML = `
      <div class="runtime-workspace-header">
        <div>
          <div class="runtime-workspace-kicker">Runtime Workspace Continuity</div>
          <h2>Governed Workspace</h2>
        </div>
        <div class="runtime-workspace-badge">presentation only - mutation blocked</div>
      </div>
      <div id="runtime-workspace-summary" class="runtime-workspace-summary">Waiting for canonical payload.</div>
      <div id="runtime-workspace-dimensions" class="runtime-workspace-dimensions"></div>
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
    const workspace = payload && payload.governed_runtime_workspace_continuity
      ? payload.governed_runtime_workspace_continuity
      : computeWorkspace(payload || {});
    const summary = workspace.summary || {};
    const dimensions = Array.isArray(workspace.workspace_dimensions) ? workspace.workspace_dimensions : [];
    const summaryEl = panel.querySelector("#runtime-workspace-summary");
    const dimensionsEl = panel.querySelector("#runtime-workspace-dimensions");

    panel.classList.remove("workspace-blocked", "workspace-partial", "workspace-review", "workspace-degraded", "workspace-recovering", "workspace-continuous");
    panel.classList.add(stateClass(workspace.workspace_state));

    summaryEl.innerHTML = `
      <span><strong>Workspace:</strong> ${text(workspace.workspace_state, "unknown")}</span>
      <span><strong>ID:</strong> ${text(workspace.workspace_id, "unknown")}</span>
      <span><strong>Route:</strong> ${text(summary.selected_route, "unknown")}</span>
      <span><strong>Session:</strong> ${text(summary.session_state, "unknown")}</span>
      <span><strong>Workflow:</strong> ${text(summary.workflow_total, "0")}</span>
      <span><strong>Evidence:</strong> ${text(summary.evidence_total, "0")}</span>
      <span><strong>Mutation:</strong> blocked</span>
    `;

    dimensionsEl.innerHTML = dimensions.map((item) => `
      <div class="runtime-workspace-dimension">
        <div class="workspace-dimension-name">${text(item.dimension, "dimension")}</div>
        <div class="workspace-dimension-state">${text(item.state, "unknown")}</div>
        <div class="workspace-dimension-detail">${text(item.detail, "unknown")}</div>
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

  window.ClaireGovernedRuntimeWorkspaceContinuity = {
    version: "v19.89.8-S29",
    render,
    authority: "presentation_only_runtime_authority_blocked"
  };
})();
