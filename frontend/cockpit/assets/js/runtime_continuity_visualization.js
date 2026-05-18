(function () {
  "use strict";

  const PANEL_ID = "runtime-continuity-visualization-panel";

  function text(value, fallback) {
    if (value === null || value === undefined || value === "") return fallback || "unknown";
    return String(value);
  }

  function computeContinuity(payload) {
    const timeline = payload && payload.governed_runtime_timeline ? payload.governed_runtime_timeline : {};
    const overlay = payload && payload.governed_route_activity_overlay ? payload.governed_route_activity_overlay : {};
    const presence = payload && payload.continuous_runtime_presence ? payload.continuous_runtime_presence : {};
    const evidence = payload && payload.governed_evidence_basket ? payload.governed_evidence_basket : {};

    const timelineSummary = timeline.summary || {};
    const overlaySummary = overlay.summary || {};
    const presenceSummary = presence.summary || {};
    const evidenceSummary = evidence.summary || {};
    const routeCounts = overlaySummary.state_counts || {};
    const events = Array.isArray(timeline.events) ? timeline.events : [];

    const degradedRoutes = Number(routeCounts.degraded || 0);
    const recoveringRoutes = Number(routeCounts.recovering || 0);
    const evidenceTotal = Number(evidenceSummary.evidence_total || 0);

    let state = "continuous";
    if (degradedRoutes) state = "degraded";
    else if (recoveringRoutes) state = "recovering";
    else if (!events.length && evidenceTotal === 0) state = "initializing";

    return {
      version: "v19.89.8-S23",
      status: "active",
      continuity_state: state,
      authority: {
        backend_owns_truth: true,
        cockpit_presentation_only: true,
        runtime_authority: "blocked",
        fail_closed_governance: true,
        autonomous_execution_expansion: false
      },
      summary: {
        selected_route: overlaySummary.selected_route || "unknown",
        terminal_state: timelineSummary.last_terminal_state || "unknown",
        presence_state: presence.presence_state || "unknown",
        timeline_event_total: events.length,
        evidence_total: evidenceTotal,
        degraded_routes: degradedRoutes,
        recovering_routes: recoveringRoutes,
        payload_freshness: timelineSummary.last_payload_freshness || presenceSummary.last_payload_freshness || "unknown"
      },
      continuity_chain: [
        { node: "timeline", state: timeline.events ? "available" : "missing", detail: timelineSummary.last_terminal_state || "unknown" },
        { node: "route activity", state: overlay.routes ? "available" : "missing", detail: overlaySummary.selected_route || "unknown" },
        { node: "presence", state: presence.presence_state || "missing", detail: presenceSummary.last_payload_freshness || "unknown" },
        { node: "evidence", state: evidence.items ? "available" : "missing", detail: evidenceTotal + " items" }
      ]
    };
  }

  function stateClass(state) {
    const clean = text(state, "continuous").toLowerCase();
    if (clean === "degraded") return "continuity-degraded";
    if (clean === "recovering") return "continuity-recovering";
    if (clean === "initializing") return "continuity-initializing";
    return "continuity-continuous";
  }

  function ensurePanel() {
    let panel = document.getElementById(PANEL_ID);
    if (panel) return panel;

    panel = document.createElement("section");
    panel.id = PANEL_ID;
    panel.className = "claire-card runtime-continuity-card";
    panel.innerHTML = `
      <div class="runtime-continuity-header">
        <div>
          <div class="runtime-continuity-kicker">Runtime Continuity</div>
          <h2>Continuity Visualization</h2>
        </div>
        <div class="runtime-continuity-badge">presentation only - authority blocked</div>
      </div>
      <div id="runtime-continuity-summary" class="runtime-continuity-summary">Waiting for canonical payload.</div>
      <div id="runtime-continuity-chain" class="runtime-continuity-chain"></div>
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
    const continuity = payload && payload.runtime_continuity_visualization
      ? payload.runtime_continuity_visualization
      : computeContinuity(payload || {});
    const summary = continuity.summary || {};
    const chain = Array.isArray(continuity.continuity_chain) ? continuity.continuity_chain : [];
    const summaryEl = panel.querySelector("#runtime-continuity-summary");
    const chainEl = panel.querySelector("#runtime-continuity-chain");

    panel.classList.remove("continuity-continuous", "continuity-degraded", "continuity-recovering", "continuity-initializing");
    panel.classList.add(stateClass(continuity.continuity_state));

    summaryEl.innerHTML = `
      <span><strong>Continuity:</strong> ${text(continuity.continuity_state, "continuous")}</span>
      <span><strong>Route:</strong> ${text(summary.selected_route, "unknown")}</span>
      <span><strong>Terminal:</strong> ${text(summary.terminal_state, "unknown")}</span>
      <span><strong>Presence:</strong> ${text(summary.presence_state, "unknown")}</span>
      <span><strong>Timeline events:</strong> ${text(summary.timeline_event_total, "0")}</span>
      <span><strong>Evidence:</strong> ${text(summary.evidence_total, "0")}</span>
      <span><strong>Authority:</strong> blocked</span>
    `;

    chainEl.innerHTML = chain.map((node) => `
      <div class="runtime-continuity-node">
        <div class="runtime-continuity-node-name">${text(node.node, "node")}</div>
        <div class="runtime-continuity-node-state">${text(node.state, "unknown")}</div>
        <div class="runtime-continuity-node-detail">${text(node.detail, "unknown")}</div>
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

  window.ClaireRuntimeContinuityVisualization = {
    version: "v19.89.8-S23",
    render,
    authority: "presentation_only_runtime_authority_blocked"
  };
})();
