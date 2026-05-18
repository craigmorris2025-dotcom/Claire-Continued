// Claire Syntalion v19.70 — Run History Panel
// Uses run history present in canonical payload only.

export function createRunHistoryPanel(options = {}) {
  const adapter = options.payloadAdapter || null;
  const state = { payload: null, lastError: null, lastUpdated: null };

  async function load() {
    state.lastError = null;
    try {
      if (adapter && typeof adapter.loadCanonicalDashboardPayload === "function") {
        state.payload = await adapter.loadCanonicalDashboardPayload();
      } else if (adapter && typeof adapter.getCanonicalDashboardPayload === "function") {
        state.payload = await adapter.getCanonicalDashboardPayload();
      }
      state.lastUpdated = new Date().toISOString();
      return snapshot();
    } catch (error) {
      state.lastError = error instanceof Error ? error.message : String(error);
      state.lastUpdated = new Date().toISOString();
      return snapshot();
    }
  }

  function snapshot() { return Object.freeze({ ...state }); }

  function render(container, input = state) {
    if (!container) return;
    const runs = normalizeRunHistory(input.payload);
    container.innerHTML = `
      <section class="runtime-panel run-history-panel" data-claire-panel="run-history">
        <header class="runtime-panel__header">
          <div>
            <p class="runtime-panel__eyebrow">History</p>
            <h2>Run History</h2>
          </div>
          <span class="truth-badge">Payload-owned</span>
        </header>
        ${input.lastError ? `<div class="runtime-alert runtime-alert--error">${escapeHtml(input.lastError)}</div>` : ""}
        ${runs.length ? renderRuns(runs) : `<div class="runtime-empty">Run history is not present in the canonical payload.</div>`}
      </section>
    `;
  }

  return { load, render, snapshot };
}

export function normalizeRunHistory(payload) {
  const raw = payload?.run_history || payload?.runtime?.run_history || payload?.history?.runs || [];
  const runs = Array.isArray(raw) ? raw : Object.values(raw || {});
  return runs.map((run) => ({
    run_id: run.run_id || run.id || "unavailable",
    status: run.status || run.state || "unknown",
    terminal_state: run.terminal_state || "unavailable",
    created_at: run.created_at || run.timestamp || run.started_at || "unavailable",
  }));
}

function renderRuns(runs) {
  return `
    <div class="run-history-table" role="table">
      <div class="run-history-row run-history-row--head" role="row">
        <span>Run</span><span>Status</span><span>Terminal</span><span>Created</span>
      </div>
      ${runs.map((run) => `
        <div class="run-history-row" role="row">
          <span>${escapeHtml(run.run_id)}</span>
          <span>${escapeHtml(run.status)}</span>
          <span>${escapeHtml(run.terminal_state)}</span>
          <span>${escapeHtml(run.created_at)}</span>
        </div>
      `).join("")}
    </div>
  `;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}
