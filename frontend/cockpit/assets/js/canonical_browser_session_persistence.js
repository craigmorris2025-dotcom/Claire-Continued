(function () {
  "use strict";

  const PANEL_ID = "canonical-browser-session-persistence-panel";
  const STORAGE_KEY = "claire_canonical_browser_session_v19_89_8_s26";

  function text(value, fallback) {
    if (value === null || value === undefined || value === "") return fallback || "unknown";
    return String(value);
  }

  function nowIso() {
    return new Date().toISOString();
  }

  function computeSession(payload) {
    const loop = payload && payload.continuous_browser_runtime_loop ? payload.continuous_browser_runtime_loop : {};
    const continuity = payload && payload.runtime_continuity_visualization ? payload.runtime_continuity_visualization : {};
    const workflow = payload && payload.governed_operator_workflow ? payload.governed_operator_workflow : {};
    const evidence = payload && payload.governed_evidence_basket ? payload.governed_evidence_basket : {};

    const loopSummary = loop.summary || {};
    const continuitySummary = continuity.summary || {};
    const workflowSummary = workflow.summary || {};
    const evidenceSummary = evidence.summary || {};

    return {
      version: "v19.89.8-S26",
      status: "active",
      observed_at_utc: nowIso(),
      authority: {
        backend_owns_truth: true,
        cockpit_presentation_only: true,
        runtime_authority: "blocked",
        browser_execution_authority: "blocked",
        browser_storage: "presentation_state_only",
        runtime_mutation_enabled: false,
        autonomous_execution_expansion: false
      },
      session_snapshot: {
        selected_route: loopSummary.selected_route || continuitySummary.selected_route || "unknown",
        loop_state: loop.loop_state || "unknown",
        continuity_state: continuity.continuity_state || "unknown",
        workflow_total: workflowSummary.workflow_total || 0,
        manual_review_required: workflowSummary.manual_review_required || false,
        evidence_total: evidenceSummary.evidence_total || 0,
        payload_freshness: loopSummary.payload_freshness || continuitySummary.payload_freshness || "unknown"
      },
      persistence_policy: {
        storage_scope: "browser_local_storage",
        contains_runtime_truth: false,
        contains_credentials: false,
        contains_live_execution_state: false,
        restore_behavior: "display_last_observed_session_only",
        write_back_to_runtime: false
      }
    };
  }

  function loadStoredSession() {
    try {
      const raw = window.localStorage.getItem(STORAGE_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch (error) {
      return null;
    }
  }

  function saveStoredSession(session) {
    try {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(session));
    } catch (error) {}
  }

  function ensurePanel() {
    let panel = document.getElementById(PANEL_ID);
    if (panel) return panel;

    panel = document.createElement("section");
    panel.id = PANEL_ID;
    panel.className = "claire-card canonical-browser-session-card";
    panel.innerHTML = `
      <div class="canonical-browser-session-header">
        <div>
          <div class="canonical-browser-session-kicker">Canonical Browser Session</div>
          <h2>Session Persistence</h2>
        </div>
        <div class="canonical-browser-session-badge">UI continuity only - authority blocked</div>
      </div>
      <div id="canonical-browser-session-summary" class="canonical-browser-session-summary">Waiting for canonical payload.</div>
      <div id="canonical-browser-session-stored" class="canonical-browser-session-stored"></div>
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
    const session = payload && payload.canonical_browser_session_persistence
      ? payload.canonical_browser_session_persistence
      : computeSession(payload || {});
    const snapshot = session.session_snapshot || {};
    const summaryEl = panel.querySelector("#canonical-browser-session-summary");
    const storedEl = panel.querySelector("#canonical-browser-session-stored");

    saveStoredSession(session);
    const stored = loadStoredSession();
    const storedSnapshot = stored && stored.session_snapshot ? stored.session_snapshot : {};

    summaryEl.innerHTML = `
      <span><strong>Route:</strong> ${text(snapshot.selected_route, "unknown")}</span>
      <span><strong>Loop:</strong> ${text(snapshot.loop_state, "unknown")}</span>
      <span><strong>Continuity:</strong> ${text(snapshot.continuity_state, "unknown")}</span>
      <span><strong>Workflow:</strong> ${text(snapshot.workflow_total, "0")}</span>
      <span><strong>Evidence:</strong> ${text(snapshot.evidence_total, "0")}</span>
      <span><strong>Storage:</strong> presentation only</span>
      <span><strong>Runtime writeback:</strong> blocked</span>
    `;

    storedEl.innerHTML = `
      <div class="canonical-browser-session-stored-title">Last observed browser session</div>
      <div class="canonical-browser-session-stored-grid">
        <span>Observed: ${text(stored && stored.observed_at_utc, "unknown")}</span>
        <span>Route: ${text(storedSnapshot.selected_route, "unknown")}</span>
        <span>Freshness: ${text(storedSnapshot.payload_freshness, "unknown")}</span>
      </div>
    `;
  }

  function poll() {
    fetch("/dashboard/payload", { cache: "no-store" })
      .then((response) => response.ok ? response.json() : null)
      .then((payload) => { if (payload) render(payload); })
      .catch(() => {
        const panel = ensurePanel();
        const stored = loadStoredSession();
        const storedEl = panel.querySelector("#canonical-browser-session-stored");
        if (stored && storedEl) {
          storedEl.innerHTML = `<div class="canonical-browser-session-stored-title">Last observed session retained locally; backend not reached by this poll.</div>`;
        }
      });
  }

  document.addEventListener("DOMContentLoaded", function () {
    ensurePanel();
    window.addEventListener("claire:canonical-payload", function (event) { render(event.detail || {}); });
    window.addEventListener("claire:payload", function (event) { render(event.detail || {}); });
    poll();
    setInterval(poll, 10000);
  });

  window.ClaireCanonicalBrowserSessionPersistence = {
    version: "v19.89.8-S26",
    render,
    authority: "presentation_only_runtime_authority_blocked"
  };
})();
