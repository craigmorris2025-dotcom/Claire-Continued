(function () {
  "use strict";

  const PANEL_ID = "continuous-browser-runtime-loop-panel";
  const STORAGE_KEY = "claire_s24_browser_loop_last_payload_observed_at";

  function text(value, fallback) {
    if (value === null || value === undefined || value === "") return fallback || "unknown";
    return String(value);
  }

  function nowIso() {
    return new Date().toISOString();
  }

  function computeLoop(payload) {
    const continuity = payload && payload.runtime_continuity_visualization ? payload.runtime_continuity_visualization : {};
    const presence = payload && payload.continuous_runtime_presence ? payload.continuous_runtime_presence : {};
    const search = payload && payload.governed_search_session ? payload.governed_search_session : {};

    const continuitySummary = continuity.summary || {};
    const presenceSummary = presence.summary || {};
    const searchSummary = search.summary || {};

    const continuityState = continuity.continuity_state || "unknown";
    const presenceState = presence.presence_state || "unknown";
    const searchState = search.session_state || "unknown";

    let loopState = "observing";
    if (continuityState === "degraded" || presenceState === "degraded" || searchState === "degraded") {
      loopState = "degraded_observation";
    } else if (continuityState === "recovering" || presenceState === "recovering" || searchState === "recovering") {
      loopState = "recovery_observation";
    } else if (continuityState === "continuous" && (presenceState === "active" || presenceState === "present")) {
      loopState = "continuous_observation";
    }

    return {
      version: "v19.89.8-S24",
      status: "active",
      loop_state: loopState,
      observed_at_utc: nowIso(),
      polling: {
        canonical_payload_interval_ms: 10000,
        mode: "observe_only",
        writes_enabled: false,
        runtime_mutation_enabled: false
      },
      authority: {
        backend_owns_truth: true,
        cockpit_presentation_only: true,
        runtime_authority: "blocked",
        fail_closed_governance: true,
        autonomous_execution_expansion: false,
        browser_execution_authority: "blocked"
      },
      summary: {
        continuity_state: continuityState,
        presence_state: presenceState,
        search_session_state: searchState,
        selected_route: continuitySummary.selected_route || searchSummary.selected_route || "unknown",
        payload_freshness: continuitySummary.payload_freshness || presenceSummary.last_payload_freshness || "unknown",
        evidence_total: continuitySummary.evidence_total || 0
      }
    };
  }

  function ensurePanel() {
    let panel = document.getElementById(PANEL_ID);
    if (panel) return panel;

    panel = document.createElement("section");
    panel.id = PANEL_ID;
    panel.className = "claire-card continuous-browser-runtime-loop-card";
    panel.innerHTML = `
      <div class="continuous-browser-loop-header">
        <div>
          <div class="continuous-browser-loop-kicker">Continuous Browser Runtime Loop</div>
          <h2>Browser Observation Loop</h2>
        </div>
        <div class="continuous-browser-loop-badge">observe only - authority blocked</div>
      </div>
      <div id="continuous-browser-loop-summary" class="continuous-browser-loop-summary">Waiting for canonical payload.</div>
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

  function stateClass(state) {
    if (state === "degraded_observation") return "browser-loop-degraded";
    if (state === "recovery_observation") return "browser-loop-recovering";
    if (state === "continuous_observation") return "browser-loop-continuous";
    return "browser-loop-observing";
  }

  function render(payload) {
    const panel = ensurePanel();
    const loop = payload && payload.continuous_browser_runtime_loop ? payload.continuous_browser_runtime_loop : computeLoop(payload || {});
    const summary = loop.summary || {};
    const summaryEl = panel.querySelector("#continuous-browser-loop-summary");

    panel.classList.remove("browser-loop-degraded", "browser-loop-recovering", "browser-loop-continuous", "browser-loop-observing");
    panel.classList.add(stateClass(loop.loop_state));

    try {
      window.localStorage.setItem(STORAGE_KEY, loop.observed_at_utc || nowIso());
    } catch (error) {}

    summaryEl.innerHTML = `
      <span><strong>Loop:</strong> ${text(loop.loop_state, "observing")}</span>
      <span><strong>Route:</strong> ${text(summary.selected_route, "unknown")}</span>
      <span><strong>Continuity:</strong> ${text(summary.continuity_state, "unknown")}</span>
      <span><strong>Presence:</strong> ${text(summary.presence_state, "unknown")}</span>
      <span><strong>Search:</strong> ${text(summary.search_session_state, "unknown")}</span>
      <span><strong>Freshness:</strong> ${text(summary.payload_freshness, "unknown")}</span>
      <span><strong>Writes:</strong> blocked</span>
      <span><strong>Observed:</strong> ${text(loop.observed_at_utc, "unknown")}</span>
    `;
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

  window.ClaireContinuousBrowserRuntimeLoop = {
    version: "v19.89.8-S24",
    render,
    authority: "presentation_only_runtime_authority_blocked"
  };
})();
