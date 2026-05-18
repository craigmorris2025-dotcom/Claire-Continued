// Claire Syntalion v19 Dashboard Payload Fetch Wiring
// Contract-driven dashboard bridge.
// Reads only: GET /dashboard/payload

(function () {
  "use strict";

  const ENDPOINT = "/dashboard/payload";
  const ROOT_ID = "claire-dashboard-payload-bridge";

  function escapeHtml(value) {
    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function safeStatus(value) {
    return escapeHtml(value || "unknown");
  }

  function ensureRoot() {
    let root = document.getElementById(ROOT_ID);
    if (root) return root;

    root = document.createElement("section");
    root.id = ROOT_ID;
    root.className = "claire-payload-bridge";
    root.innerHTML = `
      <div class="claire-payload-bridge__header">
        <div>
          <p class="claire-payload-bridge__eyebrow">Canonical Payload Bridge</p>
          <h2>Claire Runtime Dashboard</h2>
        </div>
        <div id="claire-payload-bridge-status" class="claire-payload-bridge__status">Loading</div>
      </div>
      <div id="claire-payload-bridge-summary" class="claire-payload-bridge__summary"></div>
      <div id="claire-payload-bridge-panels" class="claire-payload-bridge__panels"></div>
      <details class="claire-payload-bridge__raw">
        <summary>Raw canonical payload</summary>
        <pre id="claire-payload-bridge-raw"></pre>
      </details>
    `;

    const main = document.querySelector("main") || document.body;
    if (main.firstChild) {
      main.insertBefore(root, main.firstChild);
    } else {
      main.appendChild(root);
    }
    return root;
  }

  function setStatus(text, state) {
    const status = document.getElementById("claire-payload-bridge-status");
    if (!status) return;
    status.textContent = text;
    status.dataset.state = state || "unknown";
  }

  function renderSummary(payload) {
    const summaryRoot = document.getElementById("claire-payload-bridge-summary");
    if (!summaryRoot) return;

    const summary = payload.summary || {};
    const items = [
      ["Runtime", summary.runtime_status],
      ["Stages", summary.stage_count],
      ["Route", summary.route_status],
      ["Web", summary.web_status],
      ["Operator", summary.operator_review_status],
      ["Panels", summary.panel_count],
    ];

    summaryRoot.innerHTML = items.map(([label, value]) => `
      <article class="claire-payload-bridge__metric">
        <span>${escapeHtml(label)}</span>
        <strong>${safeStatus(value)}</strong>
      </article>
    `).join("");
  }

  function stageRuntimeHtml(section) {
    const stages = (section && section.stages) || [];
    const visible = stages.slice(0, 30);
    return `
      <div class="claire-payload-bridge__stage-list">
        ${visible.map(stage => `
          <div class="claire-payload-bridge__stage">
            <span class="claire-payload-bridge__stage-index">${escapeHtml(stage.index)}</span>
            <span class="claire-payload-bridge__stage-name">${escapeHtml(stage.name)}</span>
            <span class="claire-payload-bridge__stage-status">${safeStatus(stage.status)}</span>
          </div>
        `).join("")}
      </div>
    `;
  }

  function objectPreview(value) {
    if (!value || typeof value !== "object") {
      return `<p class="claire-payload-bridge__empty">No payload loaded.</p>`;
    }
    const keys = Object.keys(value).slice(0, 12);
    if (!keys.length) {
      return `<p class="claire-payload-bridge__empty">Payload is empty.</p>`;
    }
    return `
      <ul class="claire-payload-bridge__keys">
        ${keys.map(key => `<li><strong>${escapeHtml(key)}</strong>: ${escapeHtml(shortValue(value[key]))}</li>`).join("")}
      </ul>
    `;
  }

  function shortValue(value) {
    if (value === null || value === undefined) return "";
    if (typeof value === "object") {
      if (Array.isArray(value)) return `Array(${value.length})`;
      return `Object(${Object.keys(value).length})`;
    }
    const text = String(value);
    return text.length > 120 ? text.slice(0, 117) + "..." : text;
  }

  function panelBody(panel, sections) {
    const key = panel.payload_key;
    const section = sections ? sections[key] : null;

    if (key === "stage_runtime") {
      return stageRuntimeHtml(section);
    }

    if (section && section.payload && typeof section.payload === "object") {
      return objectPreview(section.payload);
    }

    return objectPreview(section);
  }

  function renderPanels(payload) {
    const panelsRoot = document.getElementById("claire-payload-bridge-panels");
    if (!panelsRoot) return;

    const panels = payload.panels || [];
    const sections = payload.sections || {};

    panelsRoot.innerHTML = panels.map(panel => `
      <article class="claire-payload-bridge__panel" data-panel="${escapeHtml(panel.id)}">
        <div class="claire-payload-bridge__panel-header">
          <h3>${escapeHtml(panel.title || panel.id)}</h3>
          <span>${safeStatus(panel.status)}</span>
        </div>
        ${panelBody(panel, sections)}
      </article>
    `).join("");
  }

  function renderRaw(payload) {
    const raw = document.getElementById("claire-payload-bridge-raw");
    if (!raw) return;
    raw.textContent = JSON.stringify(payload, null, 2);
  }

  function renderPayload(payload) {
    ensureRoot();
    setStatus("Payload loaded", "ready");
    renderSummary(payload);
    renderPanels(payload);
    renderRaw(payload);
  }

  function renderError(error) {
    ensureRoot();
    setStatus("Backend payload unavailable", "error");
    const summaryRoot = document.getElementById("claire-payload-bridge-summary");
    const panelsRoot = document.getElementById("claire-payload-bridge-panels");
    if (summaryRoot) {
      summaryRoot.innerHTML = `
        <article class="claire-payload-bridge__metric">
          <span>Status</span>
          <strong>Backend offline or payload route unavailable</strong>
        </article>
      `;
    }
    if (panelsRoot) {
      panelsRoot.innerHTML = `
        <article class="claire-payload-bridge__panel">
          <div class="claire-payload-bridge__panel-header">
            <h3>Dashboard Payload Bridge</h3>
            <span>blocked</span>
          </div>
          <p class="claire-payload-bridge__empty">${escapeHtml(error && error.message ? error.message : error)}</p>
        </article>
      `;
    }
  }

  async function loadPayload() {
    ensureRoot();
    setStatus("Loading payload", "loading");

    try {
      const response = await fetch(ENDPOINT, { cache: "no-store" });
      if (!response.ok) {
        throw new Error(`GET ${ENDPOINT} returned ${response.status}`);
      }
      const payload = await response.json();
      window.ClaireCanonicalDashboardPayload = payload;
      renderPayload(payload);
    } catch (error) {
      console.error("Claire dashboard payload bridge failed:", error);
      renderError(error);
    }
  }

  window.ClaireDashboardPayloadBridge = {
    endpoint: ENDPOINT,
    loadPayload,
    renderPayload,
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", loadPayload);
  } else {
    loadPayload();
  }
})();
