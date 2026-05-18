// Claire Syntalion v19.70 — Runtime Status Panel
// Truth rule: this panel renders only canonical payload/status values supplied by shared adapters.

export function createRuntimeStatusPanel(options = {}) {
  const adapter = options.payloadAdapter || null;
  const apiClient = options.apiClient || null;
  const state = {
    status: null,
    payload: null,
    lastError: null,
    lastUpdated: null,
  };

  async function load() {
    state.lastError = null;
    try {
      if (adapter && typeof adapter.loadCanonicalDashboardPayload === "function") {
        state.payload = await adapter.loadCanonicalDashboardPayload();
      } else if (adapter && typeof adapter.getCanonicalDashboardPayload === "function") {
        state.payload = await adapter.getCanonicalDashboardPayload();
      } else if (apiClient && typeof apiClient.getDashboardPayload === "function") {
        state.payload = await apiClient.getDashboardPayload();
      } else {
        state.payload = null;
      }

      if (adapter && typeof adapter.loadDashboardPayloadStatus === "function") {
        state.status = await adapter.loadDashboardPayloadStatus();
      } else if (apiClient && typeof apiClient.getDashboardPayloadStatus === "function") {
        state.status = await apiClient.getDashboardPayloadStatus();
      } else {
        state.status = deriveStatusFromPayload(state.payload);
      }
      state.lastUpdated = new Date().toISOString();
      return snapshot();
    } catch (error) {
      state.lastError = error instanceof Error ? error.message : String(error);
      state.lastUpdated = new Date().toISOString();
      return snapshot();
    }
  }

  function snapshot() {
    return Object.freeze({ ...state });
  }

  function render(container, input = state) {
    if (!container) return;
    const status = input.status || deriveStatusFromPayload(input.payload);
    const payload = input.payload || null;
    const runtime = payload?.runtime || payload?.runtime_status || payload?.system_runtime || {};
    const terminalState = runtime.terminal_state || payload?.terminal_state || status?.terminal_state || "unavailable";
    const runId = runtime.run_id || payload?.run_id || status?.run_id || "unavailable";
    const health = runtime.health || status?.health || status?.status || payload?.status || "unknown";

    container.innerHTML = `
      <section class="runtime-panel runtime-status-panel" data-claire-panel="runtime-status">
        <header class="runtime-panel__header">
          <div>
            <p class="runtime-panel__eyebrow">Runtime</p>
            <h2>Runtime Status</h2>
          </div>
          <span class="truth-badge">Backend truth only</span>
        </header>
        ${input.lastError ? `<div class="runtime-alert runtime-alert--error">${escapeHtml(input.lastError)}</div>` : ""}
        <div class="runtime-kpi-grid">
          ${metric("Health", health)}
          ${metric("Run ID", runId)}
          ${metric("Terminal State", terminalState)}
          ${metric("Updated", input.lastUpdated || "not loaded")}
        </div>
        ${payload ? "" : `<div class="runtime-empty">Canonical payload unavailable. No runtime state is being fabricated.</div>`}
      </section>
    `;
  }

  return { load, render, snapshot };
}

export function deriveStatusFromPayload(payload) {
  if (!payload || typeof payload !== "object") {
    return { status: "unavailable", health: "unknown", terminal_state: "unavailable" };
  }
  const runtime = payload.runtime || payload.runtime_status || payload.system_runtime || {};
  return {
    status: payload.status || runtime.status || "available",
    health: runtime.health || payload.health || "unknown",
    terminal_state: runtime.terminal_state || payload.terminal_state || "unavailable",
    run_id: runtime.run_id || payload.run_id || "unavailable",
  };
}

function metric(label, value) {
  return `
    <article class="runtime-kpi">
      <span>${escapeHtml(label)}</span>
      <strong>${escapeHtml(String(value ?? "unavailable"))}</strong>
    </article>
  `;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}
