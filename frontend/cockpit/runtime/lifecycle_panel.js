// Claire Syntalion v19.70 — Lifecycle Panel
// Renders canonical 30-stage lifecycle data when present. Missing stages remain truthful unavailable states.

const CANONICAL_STAGE_COUNT = 30;

export function createLifecyclePanel(options = {}) {
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

  function snapshot() {
    return Object.freeze({ ...state });
  }

  function render(container, input = state) {
    if (!container) return;
    const stages = normalizeLifecycleStages(input.payload);
    const available = stages.some((stage) => stage.status !== "unavailable" || stage.name !== "Stage unavailable");

    container.innerHTML = `
      <section class="runtime-panel lifecycle-panel" data-claire-panel="lifecycle">
        <header class="runtime-panel__header">
          <div>
            <p class="runtime-panel__eyebrow">Lifecycle</p>
            <h2>30-Stage Runtime Lifecycle</h2>
          </div>
          <span class="truth-badge">Canonical payload</span>
        </header>
        ${input.lastError ? `<div class="runtime-alert runtime-alert--error">${escapeHtml(input.lastError)}</div>` : ""}
        ${available ? renderStageList(stages) : `<div class="runtime-empty">Lifecycle stages are unavailable in the canonical payload. No stages are being invented.</div>`}
      </section>
    `;
  }

  return { load, render, snapshot };
}

export function normalizeLifecycleStages(payload) {
  const raw = payload?.lifecycle?.stages
    || payload?.runtime?.lifecycle?.stages
    || payload?.thirty_stage_payload?.stages
    || payload?.stages
    || [];

  const array = Array.isArray(raw) ? raw : Object.values(raw || {});
  if (!array.length) {
    return Array.from({ length: CANONICAL_STAGE_COUNT }, (_, index) => ({
      index: index + 1,
      name: "Stage unavailable",
      status: "unavailable",
      reason: "No canonical lifecycle stage supplied.",
    }));
  }

  return array.slice(0, CANONICAL_STAGE_COUNT).map((stage, index) => ({
    index: Number(stage.index || stage.stage_index || stage.stage || index + 1),
    name: stage.name || stage.stage_name || stage.title || `Stage ${index + 1}`,
    status: stage.status || stage.state || "unknown",
    reason: stage.reason || stage.skipped_reason || stage.message || "",
  }));
}

function renderStageList(stages) {
  return `
    <ol class="lifecycle-stage-list">
      ${stages.map((stage) => `
        <li class="lifecycle-stage" data-stage-status="${escapeHtml(stage.status)}">
          <span class="lifecycle-stage__index">${escapeHtml(stage.index)}</span>
          <div>
            <strong>${escapeHtml(stage.name)}</strong>
            <p>${escapeHtml(stage.status)}${stage.reason ? ` — ${escapeHtml(stage.reason)}` : ""}</p>
          </div>
        </li>
      `).join("")}
    </ol>
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
