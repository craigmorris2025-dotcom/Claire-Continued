(function () {
  "use strict";

  const PANEL_ID = "continuous-runtime-presence-panel";

  function text(value, fallback) {
    if (value === null || value === undefined || value === "") return fallback || "unknown";
    return String(value);
  }

  function computePresence(payload) {
    const timeline = payload && payload.governed_runtime_timeline ? payload.governed_runtime_timeline : {};
    const overlay = payload && payload.governed_route_activity_overlay ? payload.governed_route_activity_overlay : {};
    const health = payload && payload.canonical_cockpit_surface_health ? payload.canonical_cockpit_surface_health : {};

    const timelineSummary = timeline.summary || {};
    const overlaySummary = overlay.summary || {};
    const healthSummary = health.summary || {};
    const counts = overlaySummary.state_counts || {};

    const issueTotal = Number(healthSummary.issue_total || 0);
    const degradedRoutes = Number(counts.degraded || 0);
    const recoveringRoutes = Number(counts.recovering || 0);
    const activeRoutes = Number(counts.active || 0);

    let state = "present";
    if (issueTotal || degradedRoutes) state = "degraded";
    else if (recoveringRoutes) state = "recovering";
    else if (activeRoutes) state = "active";

    return {
      version: "v19.89.8-S20",
      status: "active",
      presence_state: state,
      authority: {
        backend_owns_truth: true,
        cockpit_presentation_only: true,
        runtime_authority: "blocked",
        fail_closed_governance: true,
        autonomous_execution_expansion: false
      },
      summary: {
        selected_route: overlaySummary.selected_route || "unknown",
        active_routes: activeRoutes,
        degraded_routes: degradedRoutes,
        recovering_routes: recoveringRoutes,
        surface_issue_total: issueTotal,
        last_payload_freshness: timelineSummary.last_payload_freshness || "unknown",
        last_connection_state: timelineSummary.last_connection_state || "unknown"
      }
    };
  }

  function stateClass(state) {
    const clean = text(state, "present").toLowerCase();
    if (clean === "active") return "presence-active";
    if (clean === "degraded") return "presence-degraded";
    if (clean === "recovering") return "presence-recovering";
    return "presence-present";
  }

  function ensurePanel() {
    let panel = document.getElementById(PANEL_ID);
    if (panel) return panel;

    panel = document.createElement("section");
    panel.id = PANEL_ID;
    panel.className = "claire-card continuous-runtime-presence-card";
    panel.innerHTML = `
      <div class="continuous-runtime-presence-header">
        <div>
          <div class="continuous-runtime-presence-kicker">Continuous Runtime Presence</div>
          <h2>Runtime Presence</h2>
        </div>
        <div class="continuous-runtime-presence-badge">presentation only - authority blocked</div>
      </div>
      <div id="continuous-runtime-presence-body" class="continuous-runtime-presence-body">
        Waiting for canonical payload.
      </div>
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
    const body = panel.querySelector("#continuous-runtime-presence-body");
    const presence = computePresence(payload || {});
    const summary = presence.summary || {};
    panel.classList.remove("presence-active", "presence-degraded", "presence-recovering", "presence-present");
    panel.classList.add(stateClass(presence.presence_state));

    body.innerHTML = `
      <span><strong>State:</strong> ${text(presence.presence_state, "present")}</span>
      <span><strong>Selected:</strong> ${text(summary.selected_route, "unknown")}</span>
      <span><strong>Active routes:</strong> ${text(summary.active_routes, "0")}</span>
      <span><strong>Degraded:</strong> ${text(summary.degraded_routes, "0")}</span>
      <span><strong>Recovering:</strong> ${text(summary.recovering_routes, "0")}</span>
      <span><strong>Issues:</strong> ${text(summary.surface_issue_total, "0")}</span>
      <span><strong>Freshness:</strong> ${text(summary.last_payload_freshness, "unknown")}</span>
      <span><strong>Authority:</strong> blocked</span>
    `;
  }

  function poll() {
    fetch("/dashboard/payload", { cache: "no-store" })
      .then((response) => response.ok ? response.json() : null)
      .then((payload) => {
        if (payload) render(payload);
      })
      .catch(() => ensurePanel());
  }

  document.addEventListener("DOMContentLoaded", function () {
    ensurePanel();
    window.addEventListener("claire:canonical-payload", function (event) {
      render(event.detail || {});
    });
    window.addEventListener("claire:payload", function (event) {
      render(event.detail || {});
    });
    poll();
    setInterval(poll, 10000);
  });

  window.ClaireContinuousRuntimePresence = {
    version: "v19.89.8-S20",
    render,
    authority: "presentation_only_runtime_authority_blocked"
  };
})();
