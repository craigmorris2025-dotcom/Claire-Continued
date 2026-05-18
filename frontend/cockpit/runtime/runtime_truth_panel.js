// Claire Syntalion v19.70 — Runtime Truth / Evidence Panel
// Displays evidence/truth baskets only if backend payload supplies them.

export function createRuntimeTruthPanel(options = {}) {
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
    const evidence = normalizeEvidence(input.payload);
    container.innerHTML = `
      <section class="runtime-panel runtime-truth-panel" data-claire-panel="runtime-truth">
        <header class="runtime-panel__header">
          <div>
            <p class="runtime-panel__eyebrow">Truth</p>
            <h2>Runtime Truth / Evidence</h2>
          </div>
          <span class="truth-badge">No fabricated evidence</span>
        </header>
        ${input.lastError ? `<div class="runtime-alert runtime-alert--error">${escapeHtml(input.lastError)}</div>` : ""}
        ${evidence.length ? renderEvidence(evidence) : `<div class="runtime-empty">No evidence basket is present in the canonical payload.</div>`}
      </section>
    `;
  }

  return { load, render, snapshot };
}

export function normalizeEvidence(payload) {
  const raw = payload?.runtime_truth?.evidence
    || payload?.truth?.evidence
    || payload?.evidence
    || payload?.runtime?.evidence
    || [];
  const items = Array.isArray(raw) ? raw : Object.values(raw || {});
  return items.map((item) => ({
    title: item.title || item.name || item.source || "Evidence item",
    status: item.status || item.trust_status || item.state || "unknown",
    summary: item.summary || item.description || item.reason || "",
  }));
}

function renderEvidence(evidence) {
  return `
    <div class="evidence-list">
      ${evidence.map((item) => `
        <article class="evidence-card">
          <strong>${escapeHtml(item.title)}</strong>
          <span>${escapeHtml(item.status)}</span>
          ${item.summary ? `<p>${escapeHtml(item.summary)}</p>` : ""}
        </article>
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
