(function () {
  "use strict";

  const PANEL_ID = "governed-search-session-panel";

  function text(value, fallback) {
    if (value === null || value === undefined || value === "") return fallback || "unknown";
    return String(value);
  }

  function computeSearchSession(payload) {
    const overlay = payload && payload.governed_route_activity_overlay ? payload.governed_route_activity_overlay : {};
    const presence = payload && payload.continuous_runtime_presence ? payload.continuous_runtime_presence : {};
    const routes = Array.isArray(overlay.routes) ? overlay.routes : [];
    const searchRoute = routes.find((route) => route && route.route === "governed_search") || {};
    const searchState = searchRoute.state || "inactive";

    let sessionState = "available";
    if (searchState === "degraded") sessionState = "degraded";
    else if (searchState === "active" || searchState === "recovering") sessionState = searchState;

    return {
      version: "v19.89.8-S21",
      status: "active",
      session_state: sessionState,
      authority: {
        backend_owns_truth: true,
        cockpit_presentation_only: true,
        runtime_authority: "blocked",
        fail_closed_governance: true,
        autonomous_execution_expansion: false,
        live_search_execution: "blocked_from_cockpit"
      },
      summary: {
        selected_route: (overlay.summary || {}).selected_route || "unknown",
        presence_state: presence.presence_state || "unknown",
        search_route_state: searchState,
        search_owned_surfaces: searchRoute.owned_surface_count || 0,
        last_payload_freshness: ((presence.summary || {}).last_payload_freshness) || "unknown"
      },
      session_controls: {
        query_entry_visible: true,
        execution_authority: "blocked",
        manual_review_required: true,
        evidence_promotion_required: true,
        automatic_runtime_mutation: false
      }
    };
  }

  function stateClass(state) {
    const clean = text(state, "available").toLowerCase();
    if (clean === "active") return "search-session-active";
    if (clean === "degraded") return "search-session-degraded";
    if (clean === "recovering") return "search-session-recovering";
    return "search-session-available";
  }

  function ensurePanel() {
    let panel = document.getElementById(PANEL_ID);
    if (panel) return panel;

    panel = document.createElement("section");
    panel.id = PANEL_ID;
    panel.className = "claire-card governed-search-session-card";
    panel.innerHTML = `
      <div class="governed-search-session-header">
        <div>
          <div class="governed-search-session-kicker">Governed Search Session</div>
          <h2>Search Session Control</h2>
        </div>
        <div class="governed-search-session-badge">execution blocked - review required</div>
      </div>
      <div class="governed-search-session-query-row">
        <input id="governed-search-session-input" type="text" placeholder="Governed search query surface - execution authority blocked" disabled>
        <button id="governed-search-session-button" disabled>Review Only</button>
      </div>
      <div id="governed-search-session-body" class="governed-search-session-body">
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
    const body = panel.querySelector("#governed-search-session-body");
    const session = payload && payload.governed_search_session
      ? payload.governed_search_session
      : computeSearchSession(payload || {});
    const summary = session.summary || {};
    const controls = session.session_controls || {};

    panel.classList.remove("search-session-active", "search-session-degraded", "search-session-recovering", "search-session-available");
    panel.classList.add(stateClass(session.session_state));

    body.innerHTML = `
      <span><strong>Session:</strong> ${text(session.session_state, "available")}</span>
      <span><strong>Search route:</strong> ${text(summary.search_route_state, "inactive")}</span>
      <span><strong>Presence:</strong> ${text(summary.presence_state, "unknown")}</span>
      <span><strong>Surfaces:</strong> ${text(summary.search_owned_surfaces, "0")}</span>
      <span><strong>Execution:</strong> ${text(controls.execution_authority, "blocked")}</span>
      <span><strong>Manual review:</strong> ${controls.manual_review_required === false ? "not required" : "required"}</span>
      <span><strong>Evidence promotion:</strong> ${controls.evidence_promotion_required === false ? "not required" : "required"}</span>
      <span><strong>Runtime mutation:</strong> blocked</span>
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

  window.ClaireGovernedSearchSession = {
    version: "v19.89.8-S21",
    render,
    authority: "presentation_only_runtime_authority_blocked"
  };
})();
