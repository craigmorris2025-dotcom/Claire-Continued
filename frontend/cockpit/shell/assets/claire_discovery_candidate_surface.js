/*
Claire Syntalion v19.82B.12
Discovery Candidate Cockpit Surface

Enterprise cockpit presentation layer only.

Backend remains source of truth.
Frontend displays governed candidate state only.

Reads:
- GET /runtime/continuous/review-queue
- GET /dashboard/payload

Never:
- create discoveries
- promote discoveries
- fabricate lifecycle stages
- fabricate scoring
- mutate runtime truth
*/

(function () {
  "use strict";

  const BUILD = "v19.82B.12";

  const STATE = {
    queuePayload: null,
    dashboardPayload: null,
    discoveryCandidates: [],
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
    if (value === null || value === undefined || value === "") {
      return fallback || "Unavailable";
    }
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

    let existing = byId("claire-discovery-candidate-surface");
    if (existing) return existing;

    const section = document.createElement("section");
    section.id = "claire-discovery-candidate-surface";
    section.className = "claire-discovery-candidate-surface";
    section.setAttribute("data-build", BUILD);

    section.innerHTML = `
      <div class="claire-dcs-header">
        <div>
          <p class="claire-dcs-kicker">Discovery Candidate Surface</p>
          <h2>Governed discovery intelligence</h2>
          <p class="claire-dcs-subtitle">
            Displays backend-governed discovery candidates, lifecycle routing context, and review state without frontend-generated intelligence claims.
          </p>
        </div>

        <div class="claire-dcs-actions">
          <button type="button" id="claire-dcs-refresh" class="claire-dcs-button">
            Refresh Discovery Surface
          </button>
        </div>
      </div>

      <div class="claire-dcs-grid">
        <article class="claire-dcs-card">
          <div class="claire-dcs-card-title">Discovery Candidate Counts</div>
          <div id="claire-dcs-counts" class="claire-dcs-content">
            <div class="claire-dcs-empty">Waiting for backend discovery payload...</div>
          </div>
        </article>

        <article class="claire-dcs-card">
          <div class="claire-dcs-card-title">Active Discovery Candidates</div>
          <div id="claire-dcs-candidates" class="claire-dcs-content">
            <div class="claire-dcs-empty">No discovery candidates loaded yet.</div>
          </div>
        </article>

        <article class="claire-dcs-card">
          <div class="claire-dcs-card-title">Lifecycle / Route Context</div>
          <div id="claire-dcs-lifecycle" class="claire-dcs-content">
            <div class="claire-dcs-empty">Awaiting backend lifecycle context.</div>
          </div>
        </article>
      </div>

      <div class="claire-dcs-lockline">
        Discovery candidates shown here remain backend-owned review candidates until operator-approved promotion.
      </div>
    `;

    const anchor =
      byId("claire-probe-review-bridge") ||
      byId("claire-source-universe-workspace") ||
      byId("claire-enterprise-runtime-grid") ||
      byId("claire-cockpit-main") ||
      document.querySelector("main") ||
      document.body;

    if (
      anchor.id === "claire-probe-review-bridge" ||
      anchor.id === "claire-source-universe-workspace"
    ) {
      anchor.insertAdjacentElement("afterend", section);
    } else {
      anchor.appendChild(section);
    }

    byId("claire-dcs-refresh").addEventListener("click", refreshSurface);

    return section;
  }

  function normalizeQueue(payload) {
    if (!payload) return [];
    if (Array.isArray(payload)) return payload;
    if (Array.isArray(payload.review_queue)) return payload.review_queue;
    if (Array.isArray(payload.items)) return payload.items;
    if (Array.isArray(payload.candidates)) return payload.candidates;
    if (payload.data && Array.isArray(payload.data.review_queue)) {
      return payload.data.review_queue;
    }
    return [];
  }

  function normalizeDiscoveryCandidates(queueItems) {
    return asArray(queueItems).filter((item) => {
      const text = JSON.stringify(item).toLowerCase();
      return (
        text.includes("discovery") ||
        text.includes("trend") ||
        text.includes("gap") ||
        text.includes("signal")
      );
    });
  }

  async function refreshSurface() {
    ensureWorkspace();

    try {
      const queuePayload = await requestJson("/runtime/continuous/review-queue");
      STATE.queuePayload = queuePayload;

      try {
        STATE.dashboardPayload = await requestJson("/dashboard/payload");
      } catch (dashboardErr) {
        STATE.dashboardPayload = {
          status: "dashboard_payload_unavailable",
          detail: String(dashboardErr && dashboardErr.message ? dashboardErr.message : dashboardErr),
        };
      }

      const queueItems = normalizeQueue(queuePayload);
      STATE.discoveryCandidates = normalizeDiscoveryCandidates(queueItems);

      STATE.lastLoadedAt = nowIso();
      STATE.lastError = null;
    } catch (err) {
      STATE.lastError = String(err && err.message ? err.message : err);
      STATE.lastLoadedAt = nowIso();
      STATE.discoveryCandidates = [];
    }

    renderAll();
  }

  function renderCounts() {
    const container = byId("claire-dcs-counts");
    if (!container) return;

    if (STATE.lastError) {
      container.innerHTML = `
        <div class="claire-dcs-warning">
          Discovery backend unavailable.
          <span>${escapeHtml(STATE.lastError)}</span>
        </div>
      `;
      return;
    }

    const candidates = asArray(STATE.discoveryCandidates);

    const trendCount = candidates.filter((item) => {
      return JSON.stringify(item).toLowerCase().includes("trend");
    }).length;

    const gapCount = candidates.filter((item) => {
      return JSON.stringify(item).toLowerCase().includes("gap");
    }).length;

    const signalCount = candidates.filter((item) => {
      return JSON.stringify(item).toLowerCase().includes("signal");
    }).length;

    container.innerHTML = `
      <div class="claire-dcs-metrics">
        <div>
          <span>Total Discovery Candidates</span>
          <strong>${candidates.length}</strong>
        </div>

        <div>
          <span>Trend Signals</span>
          <strong>${trendCount}</strong>
        </div>

        <div>
          <span>Gap Opportunities</span>
          <strong>${gapCount}</strong>
        </div>

        <div>
          <span>Signal Candidates</span>
          <strong>${signalCount}</strong>
        </div>
      </div>

      <div class="claire-dcs-lock">
        Backend-governed candidates only. Frontend scoring and promotion disabled.
      </div>
    `;
  }

  function renderCandidates() {
    const container = byId("claire-dcs-candidates");
    if (!container) return;

    const candidates = asArray(STATE.discoveryCandidates);

    if (candidates.length === 0) {
      container.innerHTML = `
        <div class="claire-dcs-empty">
          No backend discovery candidates currently available.
        </div>
      `;
      return;
    }

    const visible = candidates.slice(0, 8);

    container.innerHTML = `
      <div class="claire-dcs-candidate-list">
        ${visible.map(renderCandidateCard).join("")}
      </div>
    `;
  }

  function renderCandidateCard(candidate) {
    const title =
      candidate.title ||
      candidate.name ||
      candidate.headline ||
      candidate.id ||
      "Discovery Candidate";

    const route =
      candidate.route ||
      candidate.type ||
      candidate.category ||
      "discovery";

    const status =
      candidate.status ||
      candidate.state ||
      "pending_review";

    const lifecycle =
      candidate.lifecycle_stage ||
      candidate.stage ||
      "candidate_analysis";

    const confidence =
      candidate.confidence ||
      candidate.score ||
      "backend_only";

    return `
      <article class="claire-dcs-candidate-card">
        <div class="claire-dcs-candidate-top">
          <strong>${escapeHtml(title)}</strong>
          <span>${escapeHtml(status)}</span>
        </div>

        <div class="claire-dcs-pill-row">
          <span>${escapeHtml(route)}</span>
          <span>${escapeHtml(lifecycle)}</span>
          <span>${escapeHtml(String(confidence))}</span>
        </div>

        <div class="claire-dcs-candidate-note">
          Review candidate only. Backend truth ownership preserved.
        </div>
      </article>
    `;
  }

  function renderLifecycle() {
    const container = byId("claire-dcs-lifecycle");
    if (!container) return;

    const payload = STATE.dashboardPayload || {};
    const lifecycle = payload.lifecycle || payload.lifecycle_state || {};
    const selectedRoute =
      payload.selected_route ||
      payload.route ||
      lifecycle.selected_route ||
      "unavailable";

    const terminalState =
      payload.terminal_state ||
      lifecycle.terminal_state ||
      "runtime_active";

    const activeStage =
      lifecycle.active_stage ||
      lifecycle.current_stage ||
      "candidate_analysis";

    const stageCount =
      lifecycle.total_stages ||
      lifecycle.stage_count ||
      30;

    container.innerHTML = `
      <div class="claire-dcs-metrics">
        <div>
          <span>Selected Route</span>
          <strong>${escapeHtml(String(selectedRoute))}</strong>
        </div>

        <div>
          <span>Terminal State</span>
          <strong>${escapeHtml(String(terminalState))}</strong>
        </div>

        <div>
          <span>Active Stage</span>
          <strong>${escapeHtml(String(activeStage))}</strong>
        </div>

        <div>
          <span>Lifecycle Stages</span>
          <strong>${escapeHtml(String(stageCount))}</strong>
        </div>
      </div>

      <div class="claire-dcs-section">
        <h4>Lifecycle Payload</h4>
        <pre>${escapeHtml(JSON.stringify(lifecycle, null, 2))}</pre>
      </div>
    `;
  }

  function renderAll() {
    ensureWorkspace();
    renderCounts();
    renderCandidates();
    renderLifecycle();
  }

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  window.ClaireDiscoveryCandidateSurface = {
    version: BUILD,
    state: STATE,
    refreshSurface,
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", refreshSurface);
  } else {
    refreshSurface();
  }
})();
