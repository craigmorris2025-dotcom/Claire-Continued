(function () {
  "use strict";

  const PANEL_ID = "governed-operator-workflow-panel";

  function text(value, fallback) {
    if (value === null || value === undefined || value === "") return fallback || "unknown";
    return String(value);
  }

  function computeWorkflow(payload) {
    const items = [];
    const evidence = payload && payload.governed_evidence_basket ? payload.governed_evidence_basket : {};
    const continuity = payload && payload.runtime_continuity_visualization ? payload.runtime_continuity_visualization : {};
    const search = payload && payload.governed_search_session ? payload.governed_search_session : {};
    const overlay = payload && payload.governed_route_activity_overlay ? payload.governed_route_activity_overlay : {};

    const evidenceTotal = Number((evidence.summary || {}).evidence_total || 0);
    if (evidenceTotal) {
      items.push({
        workflow_id: "evidence_review",
        label: "Evidence Review",
        state: "review_required",
        count: evidenceTotal,
        operator_action: "review_only"
      });
    }

    if ((search.session_controls || {}).manual_review_required !== false) {
      items.push({
        workflow_id: "search_review",
        label: "Governed Search Review",
        state: "manual_review_required",
        count: 1,
        operator_action: "acknowledge_only"
      });
    }

    if (continuity.continuity_state === "degraded" || continuity.continuity_state === "recovering") {
      items.push({
        workflow_id: "continuity_watch",
        label: "Continuity Watch",
        state: continuity.continuity_state,
        count: Number((continuity.summary || {}).degraded_routes || 0) + Number((continuity.summary || {}).recovering_routes || 0),
        operator_action: "observe_recovery"
      });
    }

    if (Array.isArray(overlay.routes)) {
      overlay.routes.forEach((route) => {
        if (route && (route.state === "degraded" || route.state === "recovering")) {
          items.push({
            workflow_id: "route_" + (route.route || "unknown"),
            label: "Route: " + (route.route || "unknown"),
            state: route.state || "unknown",
            count: Number(route.issue_total || 0),
            operator_action: "observe_route"
          });
        }
      });
    }

    if (!items.length) {
      items.push({
        workflow_id: "normal_observation",
        label: "Normal Observation",
        state: "no_operator_action_required",
        count: 0,
        operator_action: "observe_only"
      });
    }

    return {
      version: "v19.89.8-S25",
      status: "active",
      authority: {
        backend_owns_truth: true,
        cockpit_presentation_only: true,
        runtime_authority: "blocked",
        browser_execution_authority: "blocked",
        operator_actions: "review_acknowledge_observe_only",
        autonomous_execution_expansion: false
      },
      summary: {
        workflow_total: items.length,
        operator_mutation_enabled: false,
        manual_review_required: items.some((item) => item.state === "review_required" || item.state === "manual_review_required")
      },
      items: items.slice(-16)
    };
  }

  function ensurePanel() {
    let panel = document.getElementById(PANEL_ID);
    if (panel) return panel;

    panel = document.createElement("section");
    panel.id = PANEL_ID;
    panel.className = "claire-card governed-operator-workflow-card";
    panel.innerHTML = `
      <div class="governed-operator-workflow-header">
        <div>
          <div class="governed-operator-workflow-kicker">Governed Operator Workflow</div>
          <h2>Operator Workflow</h2>
        </div>
        <div class="governed-operator-workflow-badge">review only - authority blocked</div>
      </div>
      <div id="governed-operator-workflow-summary" class="governed-operator-workflow-summary">Waiting for canonical payload.</div>
      <div id="governed-operator-workflow-list" class="governed-operator-workflow-list"></div>
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
    const workflow = payload && payload.governed_operator_workflow ? payload.governed_operator_workflow : computeWorkflow(payload || {});
    const summary = workflow.summary || {};
    const items = Array.isArray(workflow.items) ? workflow.items : [];
    const summaryEl = panel.querySelector("#governed-operator-workflow-summary");
    const listEl = panel.querySelector("#governed-operator-workflow-list");

    summaryEl.innerHTML = `
      <span><strong>Workflows:</strong> ${text(summary.workflow_total, "0")}</span>
      <span><strong>Manual review:</strong> ${summary.manual_review_required ? "required" : "not required"}</span>
      <span><strong>Operator mutation:</strong> blocked</span>
      <span><strong>Authority:</strong> blocked</span>
    `;

    listEl.innerHTML = items.map((item) => `
      <div class="governed-operator-workflow-item">
        <div class="workflow-label">${text(item.label, "Workflow")}</div>
        <div class="workflow-state">${text(item.state, "unknown")}</div>
        <div class="workflow-action">${text(item.operator_action, "observe_only")}</div>
        <div class="workflow-count">${text(item.count, "0")}</div>
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

  window.ClaireGovernedOperatorWorkflow = {
    version: "v19.89.8-S25",
    render,
    authority: "presentation_only_runtime_authority_blocked"
  };
})();
