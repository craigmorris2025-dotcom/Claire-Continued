(function () {
  "use strict";

  const PANEL_ID = "governed-operational-session-orchestration-panel";

  function text(value, fallback) {
    if (value === null || value === undefined || value === "") return fallback || "unknown";
    return String(value);
  }

  function computeOrchestration(payload) {
    const cohesion = payload && payload.multi_panel_runtime_cohesion ? payload.multi_panel_runtime_cohesion : {};
    const browserSession = payload && payload.canonical_browser_session_persistence ? payload.canonical_browser_session_persistence : {};
    const workflow = payload && payload.governed_operator_workflow ? payload.governed_operator_workflow : {};
    const continuity = payload && payload.runtime_continuity_visualization ? payload.runtime_continuity_visualization : {};
    const evidence = payload && payload.governed_evidence_basket ? payload.governed_evidence_basket : {};
    const loop = payload && payload.continuous_browser_runtime_loop ? payload.continuous_browser_runtime_loop : {};

    const cohesionSummary = cohesion.summary || {};
    const sessionSnapshot = browserSession.session_snapshot || {};
    const workflowSummary = workflow.summary || {};
    const continuitySummary = continuity.summary || {};
    const evidenceSummary = evidence.summary || {};
    const loopSummary = loop.summary || {};

    const selectedRoute = sessionSnapshot.selected_route || continuitySummary.selected_route || loopSummary.selected_route || "unknown";
    const missingTotal = Number(cohesionSummary.missing_total || 0);
    const driftTotal = Number(cohesionSummary.drift_total || 0);
    const workflowTotal = Number(workflowSummary.workflow_total || 0);
    const evidenceTotal = Number(evidenceSummary.evidence_total || sessionSnapshot.evidence_total || 0);

    let sessionState = "orchestrated";
    if (driftTotal) sessionState = "blocked";
    else if (missingTotal) sessionState = "partial";
    else if (workflowSummary.manual_review_required) sessionState = "review_required";

    return {
      version: "v19.89.8-S28",
      status: "active",
      session_state: sessionState,
      authority: {
        backend_owns_truth: true,
        cockpit_presentation_only: true,
        runtime_authority: "blocked",
        browser_execution_authority: "blocked",
        operator_mutation_enabled: false,
        runtime_mutation_enabled: false,
        fail_closed_governance: true,
        autonomous_execution_expansion: false
      },
      summary: {
        selected_route: selectedRoute,
        workflow_total: workflowTotal,
        evidence_total: evidenceTotal,
        missing_panel_total: missingTotal,
        authority_drift_total: driftTotal,
        manual_review_required: Boolean(workflowSummary.manual_review_required),
        payload_propagation: cohesionSummary.payload_propagation || "unknown",
        continuity_state: continuity.continuity_state || "unknown",
        loop_state: loop.loop_state || "unknown"
      },
      session_bindings: [
        { binding: "route_session", state: selectedRoute !== "unknown" ? "bound" : "unbound", detail: selectedRoute },
        { binding: "workflow_session", state: workflowTotal ? "active" : "idle", detail: workflowTotal + " workflow items" },
        { binding: "evidence_session", state: evidenceTotal ? "active" : "empty", detail: evidenceTotal + " evidence items" },
        { binding: "cohesion_session", state: cohesion.cohesion_state || "unknown", detail: cohesionSummary.payload_propagation || "unknown" },
        { binding: "browser_loop_session", state: loop.loop_state || "unknown", detail: loopSummary.payload_freshness || "unknown" }
      ]
    };
  }

  function stateClass(state) {
    if (state === "blocked") return "session-orchestration-blocked";
    if (state === "partial") return "session-orchestration-partial";
    if (state === "review_required") return "session-orchestration-review";
    return "session-orchestration-active";
  }

  function ensurePanel() {
    let panel = document.getElementById(PANEL_ID);
    if (panel) return panel;

    panel = document.createElement("section");
    panel.id = PANEL_ID;
    panel.className = "claire-card governed-operational-session-orchestration-card";
    panel.innerHTML = `
      <div class="operational-session-header">
        <div>
          <div class="operational-session-kicker">Operational Session Orchestration</div>
          <h2>Governed Session Orchestration</h2>
        </div>
        <div class="operational-session-badge">presentation only - authority blocked</div>
      </div>
      <div id="operational-session-summary" class="operational-session-summary">Waiting for canonical payload.</div>
      <div id="operational-session-bindings" class="operational-session-bindings"></div>
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
    const orchestration = payload && payload.governed_operational_session_orchestration
      ? payload.governed_operational_session_orchestration
      : computeOrchestration(payload || {});
    const summary = orchestration.summary || {};
    const bindings = Array.isArray(orchestration.session_bindings) ? orchestration.session_bindings : [];
    const summaryEl = panel.querySelector("#operational-session-summary");
    const bindingsEl = panel.querySelector("#operational-session-bindings");

    panel.classList.remove("session-orchestration-active", "session-orchestration-blocked", "session-orchestration-partial", "session-orchestration-review");
    panel.classList.add(stateClass(orchestration.session_state));

    summaryEl.innerHTML = `
      <span><strong>Session:</strong> ${text(orchestration.session_state, "unknown")}</span>
      <span><strong>Route:</strong> ${text(summary.selected_route, "unknown")}</span>
      <span><strong>Workflows:</strong> ${text(summary.workflow_total, "0")}</span>
      <span><strong>Evidence:</strong> ${text(summary.evidence_total, "0")}</span>
      <span><strong>Missing panels:</strong> ${text(summary.missing_panel_total, "0")}</span>
      <span><strong>Drift:</strong> ${text(summary.authority_drift_total, "0")}</span>
      <span><strong>Authority:</strong> blocked</span>
    `;

    bindingsEl.innerHTML = bindings.map((item) => `
      <div class="operational-session-binding">
        <div class="binding-name">${text(item.binding, "binding")}</div>
        <div class="binding-state">${text(item.state, "unknown")}</div>
        <div class="binding-detail">${text(item.detail, "unknown")}</div>
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

  window.ClaireGovernedOperationalSessionOrchestration = {
    version: "v19.89.8-S28",
    render,
    authority: "presentation_only_runtime_authority_blocked"
  };
})();
