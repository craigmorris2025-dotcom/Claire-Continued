/*
Claire Syntalion v19.82B.11
Governed Probe Result Review Queue Bridge

Cockpit-only review bridge.
Backend remains truth owner.
Frontend does not promote probe results.
Frontend does not create discoveries.
Frontend does not create breakthrough claims.
Frontend does not create portfolio claims.
Frontend does not alter runtime truth.

Reads:
- GET /runtime/continuous/review-queue

Observes:
- window.ClaireSourceUniverseWorkspace.state.lastProbe when available

This build intentionally does not POST promotion requests unless a future backend route explicitly owns that action.
*/

(function () {
  "use strict";

  const BUILD = "v19.82B.11";

  const STATE = {
    reviewQueue: null,
    lastProbeSnapshot: null,
    lastLoadedAt: null,
    lastError: null,
  };

  function byId(id) {
    return document.getElementById(id);
  }

  function asArray(value) {
    return Array.isArray(value) ? value : [];
  }

  function safeText(value, fallback) {
    if (value === null || value === undefined || value === "") return fallback || "Unavailable";
    return String(value);
  }

  function nowIso() {
    return new Date().toISOString();
  }

  async function requestJson(url, options) {
    const response = await fetch(url, Object.assign({
      headers: { "Content-Type": "application/json" },
      cache: "no-store"
    }, options || {}));

    let payload = null;
    try {
      payload = await response.json();
    } catch (err) {
      payload = { error: "non_json_response", detail: String(err) };
    }

    if (!response.ok) {
      const message = payload && (payload.detail || payload.error || payload.message);
      throw new Error(message || ("HTTP " + response.status));
    }

    return payload;
  }

  function ensureWorkspace() {
    if (!document.body) return null;

    let existing = byId("claire-probe-review-bridge");
    if (existing) return existing;

    const section = document.createElement("section");
    section.id = "claire-probe-review-bridge";
    section.className = "claire-probe-review-bridge";
    section.setAttribute("data-build", BUILD);
    section.innerHTML = `
      <div class="claire-prb-header">
        <div>
          <p class="claire-prb-kicker">Operator Review Bridge</p>
          <h2>Probe-to-review governance</h2>
          <p class="claire-prb-subtitle">
            Shows governed probe output beside the backend review queue. Promotion remains backend-owned and operator-gated.
          </p>
        </div>
        <div class="claire-prb-actions">
          <button type="button" id="claire-prb-refresh" class="claire-prb-button">Refresh Review Queue</button>
          <button type="button" id="claire-prb-capture" class="claire-prb-button claire-prb-button-primary">Capture Last Probe</button>
        </div>
      </div>

      <div class="claire-prb-grid">
        <article class="claire-prb-card">
          <div class="claire-prb-card-title">Last Governed Probe Snapshot</div>
          <div id="claire-prb-probe-snapshot" class="claire-prb-content">
            <div class="claire-prb-empty">No source-universe probe has been captured for review in this cockpit session.</div>
          </div>
        </article>

        <article class="claire-prb-card">
          <div class="claire-prb-card-title">Backend Review Queue</div>
          <div id="claire-prb-review-queue" class="claire-prb-content">
            <div class="claire-prb-empty">Loading backend-owned review queue...</div>
          </div>
        </article>

        <article class="claire-prb-card">
          <div class="claire-prb-card-title">Governance Status</div>
          <div id="claire-prb-governance" class="claire-prb-content">
            <div class="claire-prb-lock">No frontend promotion. No truth mutation. Operator review required.</div>
          </div>
        </article>
      </div>
    `;

    const anchor =
      byId("claire-source-universe-workspace") ||
      byId("claire-enterprise-runtime-grid") ||
      byId("claire-cockpit-main") ||
      document.querySelector("main") ||
      document.body;

    if (anchor.id === "claire-source-universe-workspace") {
      anchor.insertAdjacentElement("afterend", section);
    } else {
      anchor.appendChild(section);
    }

    byId("claire-prb-refresh").addEventListener("click", loadReviewQueue);
    byId("claire-prb-capture").addEventListener("click", captureLastProbe);

    return section;
  }

  function normalizeReviewQueue(payload) {
    if (!payload) return [];
    if (Array.isArray(payload)) return payload;
    if (Array.isArray(payload.review_queue)) return payload.review_queue;
    if (Array.isArray(payload.items)) return payload.items;
    if (Array.isArray(payload.candidates)) return payload.candidates;
    if (payload.data && Array.isArray(payload.data.review_queue)) return payload.data.review_queue;
    return [];
  }

  function queueCounts(payload, items) {
    const source = payload || {};
    return {
      total: source.total_count ?? source.total ?? items.length,
      discovery: source.discovery_count ?? source.discoveries ?? countType(items, "discovery"),
      breakthrough: source.breakthrough_count ?? source.breakthroughs ?? countType(items, "breakthrough"),
      portfolio: source.portfolio_count ?? source.portfolio ?? countType(items, "portfolio"),
      design: source.design_count ?? source.design ?? countType(items, "design"),
    };
  }

  function countType(items, typeName) {
    return asArray(items).filter((item) => {
      const type = String(item.type || item.category || item.route || "").toLowerCase();
      return type.includes(typeName);
    }).length;
  }

  function captureLastProbe() {
    const workspace = window.ClaireSourceUniverseWorkspace;
    const probe = workspace && workspace.state ? workspace.state.lastProbe : null;

    if (!probe) {
      STATE.lastProbeSnapshot = {
        status: "no_probe_available",
        message: "No governed source-universe probe is currently available from the Source Universe Workspace.",
        captured_at: nowIso(),
        frontend_truth_mutation: false,
      };
    } else {
      STATE.lastProbeSnapshot = {
        status: "captured_for_operator_review_display_only",
        captured_at: nowIso(),
        frontend_truth_mutation: false,
        promotion_state: "not_promoted_frontend_display_only",
        backend_review_required: true,
        probe: probe,
      };
    }

    renderAll();
  }

  async function loadReviewQueue() {
    ensureWorkspace();
    try {
      const payload = await requestJson("/runtime/continuous/review-queue");
      STATE.reviewQueue = payload;
      STATE.lastLoadedAt = nowIso();
      STATE.lastError = null;
    } catch (err) {
      STATE.reviewQueue = null;
      STATE.lastError = String(err && err.message ? err.message : err);
      STATE.lastLoadedAt = nowIso();
    }
    renderAll();
  }

  function renderProbeSnapshot() {
    const container = byId("claire-prb-probe-snapshot");
    if (!container) return;

    const snapshot = STATE.lastProbeSnapshot;

    if (!snapshot) {
      container.innerHTML = `<div class="claire-prb-empty">No source-universe probe has been captured for review in this cockpit session.</div>`;
      return;
    }

    const blocked = snapshot.status === "no_probe_available";
    const probe = snapshot.probe || {};
    const candidates = asArray(probe.candidates || probe.results || probe.items);

    container.innerHTML = `
      <div class="${blocked ? "claire-prb-warning" : "claire-prb-success"}">
        ${escapeHtml(safeText(snapshot.status, "Captured"))}
        <span>${escapeHtml(safeText(snapshot.captured_at, nowIso()))}</span>
      </div>

      <div class="claire-prb-metrics">
        <div><span>Candidate Count</span><strong>${candidates.length}</strong></div>
        <div><span>Promotion</span><strong>Backend Only</strong></div>
        <div><span>Mutation</span><strong>Disabled</strong></div>
      </div>

      <div class="claire-prb-section">
        <h4>Captured Payload</h4>
        <pre>${escapeHtml(JSON.stringify(snapshot, null, 2))}</pre>
      </div>
    `;
  }

  function renderReviewQueue() {
    const container = byId("claire-prb-review-queue");
    if (!container) return;

    if (STATE.lastError && !STATE.reviewQueue) {
      container.innerHTML = `
        <div class="claire-prb-warning">
          Backend review queue unavailable.
          <span>${escapeHtml(STATE.lastError)}</span>
        </div>
      `;
      return;
    }

    if (!STATE.reviewQueue) {
      container.innerHTML = `<div class="claire-prb-empty">Review queue not loaded yet.</div>`;
      return;
    }

    const items = normalizeReviewQueue(STATE.reviewQueue);
    const counts = queueCounts(STATE.reviewQueue, items);
    const visibleItems = items.slice(0, 6);

    container.innerHTML = `
      <div class="claire-prb-metrics">
        <div><span>Total</span><strong>${escapeHtml(counts.total)}</strong></div>
        <div><span>Discovery</span><strong>${escapeHtml(counts.discovery)}</strong></div>
        <div><span>Breakthrough</span><strong>${escapeHtml(counts.breakthrough)}</strong></div>
        <div><span>Portfolio</span><strong>${escapeHtml(counts.portfolio)}</strong></div>
        <div><span>Design</span><strong>${escapeHtml(counts.design)}</strong></div>
      </div>

      <div class="claire-prb-section">
        <h4>Visible Queue Items</h4>
        ${renderQueueItems(visibleItems)}
      </div>

      <div class="claire-prb-section">
        <h4>Backend Queue Payload</h4>
        <pre>${escapeHtml(JSON.stringify(STATE.reviewQueue, null, 2))}</pre>
      </div>
    `;
  }

  function renderQueueItems(items) {
    if (!items || items.length === 0) {
      return `<div class="claire-prb-empty">Backend review queue returned no visible items.</div>`;
    }

    return `<div class="claire-prb-items">${
      items.map((item) => {
        const title = item.title || item.name || item.headline || item.id || "Review item";
        const route = item.route || item.type || item.category || "unclassified";
        const status = item.status || item.state || "pending_review";
        return `
          <div class="claire-prb-item">
            <strong>${escapeHtml(title)}</strong>
            <span>${escapeHtml(route)} · ${escapeHtml(status)}</span>
          </div>
        `;
      }).join("")
    }</div>`;
  }

  function renderGovernance() {
    const container = byId("claire-prb-governance");
    if (!container) return;

    container.innerHTML = `
      <div class="claire-prb-lock">Backend owns promotion. Cockpit displays probe and queue state only.</div>
      <ul class="claire-prb-rules">
        <li>No frontend-created discoveries.</li>
        <li>No frontend-created breakthrough claims.</li>
        <li>No frontend-created portfolio decisions.</li>
        <li>No frontend route scoring.</li>
        <li>No runtime truth mutation.</li>
        <li>Operator review is required before promotion.</li>
      </ul>
    `;
  }

  function renderAll() {
    ensureWorkspace();
    renderProbeSnapshot();
    renderReviewQueue();
    renderGovernance();
  }

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  window.ClaireProbeReviewQueueBridge = {
    version: BUILD,
    state: STATE,
    captureLastProbe,
    loadReviewQueue
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => {
      renderAll();
      loadReviewQueue();
    });
  } else {
    renderAll();
    loadReviewQueue();
  }
})();
