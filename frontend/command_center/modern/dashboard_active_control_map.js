"use strict";
(function () {
  window.ClaireDashboardActiveControlMap = window.ClaireDashboardActiveControlMap || {
    build: "v19.89.8-s1323-s1350-active-control-map",
    status: "mounted",
    endpoint: "/api/dashboard/active-control-map",
    loaded: false,
    AUDIT_VISIBLE_BACKEND_BINDINGS: [
      "/api/search/governed/plans",
      "/api/governed/runtime-spine",
      "/api/dashboard/active-control-map"
    ],
    safety: "body reads blocked; runtime mutation blocked"
  };

  function escapeHtml(value) {
    return String(value == null ? "" : value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;");
  }

  async function fetchJson(url) {
    const response = await fetch(url, {
      method: "GET",
      headers: { "Accept": "application/json" },
      cache: "no-store"
    });
    return { response, payload: await response.json() };
  }

  function ensurePanel() {
    let panel = document.querySelector(".claire-active-control-map");
    if (panel) return panel;

    panel = document.createElement("section");
    panel.className = "claire-active-control-map";
    panel.setAttribute("aria-label", "Dashboard active control map");
    panel.innerHTML = [
      '<div class="claire-active-control-header">',
      "<div>",
      '<p class="claire-active-control-kicker">Operator control map</p>',
      "<h2>Active Backend Controls</h2>",
      "<p>Visible review-only bindings for the required backend capabilities. Live web, body reads, command execution, updates, and runtime mutation remain blocked.</p>",
      "</div>",
      '<span class="claire-active-control-chip" data-claire-active-control-count>Loading</span>',
      "</div>",
      '<div class="claire-active-control-grid" data-claire-active-control-grid></div>',
      '<div class="claire-active-control-result" id="claire-active-control-result-pane" aria-live="polite">',
      "<strong>Select a control to fetch its backend result.</strong>",
      "<p>Each button uses GET and renders the response here without unlocking execution authority.</p>",
      "</div>"
    ].join("");

    const anchor =
      document.querySelector("main") ||
      document.querySelector(".dashboard-shell") ||
      document.querySelector(".shell") ||
      document.body;
    anchor.appendChild(panel);
    return panel;
  }

  function renderLocks(authority) {
    const blocked = (authority && authority.blocked) || {};
    return Object.entries(blocked)
      .map(([key, value]) => "<span>" + escapeHtml(key.replaceAll("_", " ")) + ": " + escapeHtml(value) + "</span>")
      .join("");
  }

  function renderControls(payload) {
    const panel = ensurePanel();
    const controls = Array.isArray(payload.controls) ? payload.controls : [];
    const grid = panel.querySelector("[data-claire-active-control-grid]");
    const count = panel.querySelector("[data-claire-active-control-count]");
    if (count) count.textContent = "Active controls: " + controls.length;
    if (!grid) return;

    grid.innerHTML = controls
      .map((control) => [
        '<article class="claire-active-control-card" data-control-key="' + escapeHtml(control.key) + '">',
        '<div class="claire-control-topline">',
        "<span>" + escapeHtml(control.category || "Control") + "</span>",
        "<span>" + escapeHtml(control.operation_mode || "read_only") + "</span>",
        "</div>",
        "<h3>" + escapeHtml(control.label) + "</h3>",
        "<p>" + escapeHtml(control.description) + "</p>",
        '<small class="claire-control-endpoint">' + escapeHtml(control.primary_endpoint) + "</small>",
        '<button type="button" data-control-endpoint="' + escapeHtml(control.primary_endpoint) + '" data-control-key="' + escapeHtml(control.key) + '">',
        escapeHtml(control.button_label || "Fetch control"),
        "</button>",
        "</article>"
      ].join(""))
      .join("");

    grid.querySelectorAll("button[data-control-endpoint]").forEach((button) => {
      button.addEventListener("click", () => fetchControlResult(button.dataset.controlEndpoint, button.dataset.controlKey));
    });
  }

  function renderResult(endpoint, status, payload) {
    const pane = document.getElementById("claire-active-control-result-pane") || ensurePanel().querySelector(".claire-active-control-result");
    if (!pane) return;
    const authority = window.ClaireDashboardActiveControlMap.payload && window.ClaireDashboardActiveControlMap.payload.authority;
    pane.innerHTML = [
      '<div class="claire-control-result-card">',
      '<div class="claire-control-result-topline">',
      "<span>GET " + escapeHtml(endpoint) + "</span>",
      "<span>Status " + escapeHtml(status) + "</span>",
      "</div>",
      "<h3>Backend Result</h3>",
      "<p>Review-only fetch complete. Body reads blocked. Runtime mutation blocked. Command execution blocked.</p>",
      '<div class="claire-control-locks">' + renderLocks(authority) + "</div>",
      "<pre>" + escapeHtml(JSON.stringify(payload, null, 2)) + "</pre>",
      "</div>"
    ].join("");
  }

  async function fetchControlResult(endpoint, key) {
    const pane = document.getElementById("claire-active-control-result-pane");
    if (pane) {
      pane.innerHTML = "<strong>Fetching " + escapeHtml(key || endpoint) + "...</strong><p>GET only; unsafe authority remains blocked.</p>";
    }
    try {
      const { response, payload } = await fetchJson(endpoint);
      renderResult(endpoint, response.status, payload);
    } catch (error) {
      if (pane) {
        pane.innerHTML = [
          '<div class="claire-control-result-card claire-control-error">',
          "<h3>Control Fetch Failed</h3>",
          "<p>" + escapeHtml(endpoint) + "</p>",
          "<pre>" + escapeHtml(String(error && error.message ? error.message : error)) + "</pre>",
          "</div>"
        ].join("");
      }
    }
  }

  async function loadActiveControlMap() {
    try {
      const { response, payload } = await fetchJson("/api/dashboard/active-control-map");
      window.ClaireDashboardActiveControlMap.loaded = true;
      window.ClaireDashboardActiveControlMap.status_code = response.status;
      window.ClaireDashboardActiveControlMap.payload = payload;
      renderControls(payload);
    } catch (error) {
      window.ClaireDashboardActiveControlMap.loaded = false;
      window.ClaireDashboardActiveControlMap.error = String(error && error.message ? error.message : error);
      const panel = ensurePanel();
      const result = panel.querySelector(".claire-active-control-result");
      if (result) {
        result.innerHTML = "<strong>Active control map unavailable.</strong><p>" + escapeHtml(window.ClaireDashboardActiveControlMap.error) + "</p>";
      }
    }
  }

  window.ClaireDashboardActiveControlMap.fetchControlResult = fetchControlResult;
  window.ClaireDashboardActiveControlMap.renderControls = renderControls;

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", loadActiveControlMap);
  } else {
    loadActiveControlMap();
  }
})();
