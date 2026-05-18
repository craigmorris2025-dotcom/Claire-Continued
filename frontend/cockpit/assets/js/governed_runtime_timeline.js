(function () {
  "use strict";

  const PANEL_ID = "governed-runtime-timeline-panel";
  const LIST_ID = "governed-runtime-timeline-list";

  function text(value, fallback) {
    if (value === null || value === undefined || value === "") return fallback || "unknown";
    return String(value);
  }

  function classNameForSeverity(severity) {
    const clean = text(severity, "info").toLowerCase();
    if (clean === "warning") return "timeline-severity-warning";
    if (clean === "recovered") return "timeline-severity-recovered";
    if (clean === "guarded") return "timeline-severity-guarded";
    return "timeline-severity-info";
  }

  function ensurePanel() {
    let panel = document.getElementById(PANEL_ID);
    if (panel) return panel;

    panel = document.createElement("section");
    panel.id = PANEL_ID;
    panel.className = "claire-card governed-runtime-timeline-card s16-renderer-lock";
    panel.innerHTML = `
      <div class="governed-runtime-timeline-header">
        <div>
          <div class="governed-runtime-timeline-kicker">Governed Runtime Timeline</div>
          <h2>Classified Historical Trace</h2>
        </div>
        <div class="governed-runtime-timeline-badge">presentation only - authority blocked</div>
      </div>
      <div class="governed-runtime-timeline-summary" id="governed-runtime-timeline-summary">
        Waiting for canonical timeline payload.
      </div>
      <div class="governed-runtime-classification-row" id="governed-runtime-classification-row"></div>
      <div id="${LIST_ID}" class="governed-runtime-timeline-list"></div>
    `;

    const preferredTargets = ["#runtime-surface", "#operator-surface", "#main-content", "main", "#app", "body"];
    for (const selector of preferredTargets) {
      const target = document.querySelector(selector);
      if (target) {
        target.appendChild(panel);
        return panel;
      }
    }

    document.body.appendChild(panel);
    return panel;
  }

  function timelineFromPayload(payload) {
    if (!payload || typeof payload !== "object") return null;
    return payload.governed_runtime_timeline || payload.runtime_timeline || null;
  }

  function renderClassificationSummary(panel, timeline) {
    const row = panel.querySelector("#governed-runtime-classification-row");
    if (!row) return;

    const classificationSummary = timeline.classification_summary || {};
    const counts = classificationSummary.counts || {};
    const keys = Object.keys(counts).sort();

    if (!keys.length) {
      row.innerHTML = `<span class="timeline-chip timeline-severity-info">classification pending</span>`;
      return;
    }

    row.innerHTML = keys.map((key) => {
      const cls = key === "route_degradation"
        ? "timeline-severity-warning"
        : key === "route_recovery"
          ? "timeline-severity-recovered"
          : key === "governance"
            ? "timeline-severity-guarded"
            : "timeline-severity-info";
      return `<span class="timeline-chip ${cls}">${key}: ${counts[key]}</span>`;
    }).join("");
  }

  function render(payload) {
    const panel = ensurePanel();
    const timeline = timelineFromPayload(payload);
    const summaryEl = panel.querySelector("#governed-runtime-timeline-summary");
    const listEl = panel.querySelector("#" + LIST_ID);

    if (!timeline || typeof timeline !== "object") {
      summaryEl.textContent = "Timeline unavailable from canonical payload. Cockpit remains presentation-only.";
      listEl.innerHTML = "";
      return;
    }

    const authority = timeline.authority || {};
    const summary = timeline.summary || {};
    const classificationSummary = timeline.classification_summary || {};
    const events = Array.isArray(timeline.events) ? timeline.events.slice(-16).reverse() : [];

    summaryEl.innerHTML = `
      <span><strong>Status:</strong> ${text(timeline.status, "unknown")}</span>
      <span><strong>Events:</strong> ${text(summary.event_total || classificationSummary.event_total, "0")}</span>
      <span><strong>Route:</strong> ${text(summary.last_route || classificationSummary.last_route, "unknown")}</span>
      <span><strong>Terminal:</strong> ${text(summary.last_terminal_state || classificationSummary.last_terminal_state, "unknown")}</span>
      <span><strong>Freshness:</strong> ${text(summary.last_payload_freshness, "unknown")}</span>
      <span><strong>Authority:</strong> ${text(authority.runtime_authority, "blocked")}</span>
    `;

    renderClassificationSummary(panel, timeline);

    if (!events.length) {
      listEl.innerHTML = `<div class="governed-runtime-timeline-empty">No classified timeline events recorded yet.</div>`;
      return;
    }

    listEl.innerHTML = events.map((event) => {
      const severityClass = classNameForSeverity(event.severity);
      return `
        <div class="governed-runtime-timeline-event ${severityClass}">
          <div class="governed-runtime-timeline-event-type">
            ${text(event.classification || event.type, "event")}
            <small>${text(event.severity, "info")}</small>
          </div>
          <div class="governed-runtime-timeline-event-body">
            <strong>${text(event.field, "state")}</strong>
            <span>${text(event.from, "unknown")} -> ${text(event.to, "unknown")}</span>
          </div>
          <div class="governed-runtime-timeline-event-time">${text(event.timestamp, "unknown time")}</div>
        </div>
      `;
    }).join("");
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

  window.ClaireGovernedTimelineRendererLock = {
    version: "v19.89.8-S16",
    render,
    authority: "presentation_only_runtime_authority_blocked"
  };
})();
