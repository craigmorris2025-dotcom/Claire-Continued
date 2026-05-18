(function () {
  "use strict";

  const PANEL_ID = "governed-route-activity-overlay-panel";

  function text(value, fallback) {
    if (value === null || value === undefined || value === "") return fallback || "unknown";
    return String(value);
  }

  function stateClass(state) {
    const clean = text(state, "inactive").toLowerCase();
    if (clean === "active") return "route-state-active";
    if (clean === "degraded") return "route-state-degraded";
    if (clean === "recovering") return "route-state-recovering";
    return "route-state-inactive";
  }

  function ensurePanel() {
    let panel = document.getElementById(PANEL_ID);
    if (panel) return panel;

    panel = document.createElement("section");
    panel.id = PANEL_ID;
    panel.className = "claire-card governed-route-activity-overlay-card";
    panel.innerHTML = `
      <div class="governed-route-overlay-header">
        <div>
          <div class="governed-route-overlay-kicker">Governed Route Activity</div>
          <h2>Route Activity Overlay</h2>
        </div>
        <div class="governed-route-overlay-badge">presentation only - authority blocked</div>
      </div>
      <div id="governed-route-overlay-summary" class="governed-route-overlay-summary">Waiting for canonical payload.</div>
      <div id="governed-route-overlay-grid" class="governed-route-overlay-grid"></div>
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

  function overlayFromPayload(payload) {
    if (!payload || typeof payload !== "object") return null;
    return payload.governed_route_activity_overlay || null;
  }

  function render(payload) {
    const panel = ensurePanel();
    const overlay = overlayFromPayload(payload);
    const summaryEl = panel.querySelector("#governed-route-overlay-summary");
    const gridEl = panel.querySelector("#governed-route-overlay-grid");

    if (!overlay || typeof overlay !== "object") {
      summaryEl.textContent = "Route overlay unavailable from canonical payload.";
      gridEl.innerHTML = "";
      return;
    }

    const summary = overlay.summary || {};
    const routes = Array.isArray(overlay.routes) ? overlay.routes : [];
    const counts = summary.state_counts || {};

    summaryEl.innerHTML = `
      <span><strong>Routes:</strong> ${text(summary.route_total, "0")}</span>
      <span><strong>Selected:</strong> ${text(summary.selected_route, "unknown")}</span>
      <span><strong>Active:</strong> ${text(counts.active, "0")}</span>
      <span><strong>Degraded:</strong> ${text(counts.degraded, "0")}</span>
      <span><strong>Recovering:</strong> ${text(counts.recovering, "0")}</span>
      <span><strong>Authority:</strong> ${text((overlay.authority || {}).runtime_authority, "blocked")}</span>
    `;

    gridEl.innerHTML = routes.map((route) => `
      <div class="governed-route-tile ${stateClass(route.state)}">
        <div class="governed-route-name">${text(route.route, "route")}</div>
        <div class="governed-route-state">${text(route.state, "inactive")}${route.selected ? " / selected" : ""}</div>
        <div class="governed-route-meta">
          <span>surfaces: ${text(route.owned_surface_count, "0")}</span>
          <span>freshness: ${text(route.freshness, "unknown")}</span>
          <span>health: ${text(route.health, "unknown")}</span>
        </div>
      </div>
    `).join("");
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
    setInterval(poll, 15000);
  });

  window.ClaireGovernedRouteActivityOverlay = {
    version: "v19.89.8-S19",
    render,
    authority: "presentation_only_runtime_authority_blocked"
  };
})();
