/*
Claire Syntalion v19.89.2
Operator Control Contract Surface
*/
(function () {
  "use strict";

  const API_BASE = (window.localStorage && localStorage.getItem("CLAIRE_API_BASE")) || "http://127.0.0.1:8000";
  const ROUTES = {
    controls: API_BASE + "/system/operator-controls",
    summary: API_BASE + "/system/operator-controls/summary",
    unavailable: API_BASE + "/system/operator-controls/unavailable"
  };

  async function fetchJson(url) {
    const r = await fetch(url, { method: "GET", cache: "no-store", headers: { "Accept": "application/json" } });
    if (!r.ok) throw new Error(url + " returned HTTP " + r.status);
    return await r.json();
  }

  function esc(value) {
    return String(value == null ? "" : value)
      .replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;").replaceAll("'", "&#039;");
  }

  function color(status) {
    if (status === "available") return "#9dffbc";
    if (status === "blocked") return "#ffe08a";
    return "#ffb4b4";
  }

  function ensurePanel() {
    let panel = document.getElementById("claire-operator-control-contracts");
    if (panel) return panel;

    panel = document.createElement("section");
    panel.id = "claire-operator-control-contracts";
    panel.setAttribute("data-claire-panel", "operator-control-contracts");
    panel.style.cssText = [
      "margin:16px 26px",
      "padding:16px 18px",
      "border:1px solid rgba(105,158,255,0.32)",
      "border-radius:16px",
      "background:rgba(10,18,34,0.78)",
      "color:#dce8ff",
      "font-family:Segoe UI,Arial,sans-serif"
    ].join(";");

    panel.innerHTML = [
      '<div style="display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:12px;">',
      '<div>',
      '<div style="letter-spacing:.18em;color:#70f3ff;font-weight:800;font-size:12px;">OPERATOR CONTROL CONTRACTS</div>',
      '<div style="font-size:13px;opacity:.78;margin-top:4px;">Shows which dashboard controls are backed by real backend routes.</div>',
      '</div>',
      '<div id="claire-operator-control-status" style="font-weight:800;">checking</div>',
      '</div>',
      '<div id="claire-operator-control-summary" style="font-size:13px;opacity:.9;margin-bottom:12px;"></div>',
      '<div id="claire-operator-control-grid" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:10px;"></div>'
    ].join("");

    const surfaces = document.getElementById("claire-operator-surface-map");
    if (surfaces && surfaces.parentElement) surfaces.parentElement.insertBefore(panel, surfaces.nextSibling);
    else document.body.appendChild(panel);

    return panel;
  }

  function render(data) {
    ensurePanel();
    const status = document.getElementById("claire-operator-control-status");
    const summary = document.getElementById("claire-operator-control-summary");
    const grid = document.getElementById("claire-operator-control-grid");

    const s = data.summary || {};
    if (status) status.textContent = data.status || "mapped";
    if (summary) {
      summary.textContent = [
        "controls: " + (s.total_controls || 0),
        "available: " + (s.available || 0),
        "unavailable: " + (s.unavailable || 0),
        "blocked: " + (s.blocked || 0)
      ].join(" | ");
    }

    if (!grid) return;
    grid.innerHTML = "";

    (data.controls || []).forEach(control => {
      const card = document.createElement("div");
      const c = color(control.status);
      card.style.cssText = [
        "border:1px solid rgba(130,170,255,0.24)",
        "border-radius:12px",
        "padding:12px",
        "background:rgba(8,14,27,0.74)"
      ].join(";");

      card.innerHTML = [
        '<div style="display:flex;justify-content:space-between;gap:8px;align-items:center;">',
        '<div style="font-weight:800;">' + esc(control.label) + '</div>',
        '<div style="color:' + c + ';font-size:12px;font-weight:800;">' + esc(control.status) + '</div>',
        '</div>',
        '<div style="font-size:12px;opacity:.75;margin-top:6px;">' + esc(control.method) + ' ' + esc(control.route) + '</div>',
        '<div style="font-size:12px;margin-top:8px;">surface: ' + esc(control.surface) + '</div>',
        '<div style="font-size:11px;opacity:.68;margin-top:6px;">safe mode: ' + esc(control.safe_mode) + '</div>'
      ].join("");

      grid.appendChild(card);
    });

    window.__CLAIRE_OPERATOR_CONTROLS__ = data;
  }

  async function refresh() {
    ensurePanel();
    try {
      const data = await fetchJson(ROUTES.controls);
      render(data);
      document.documentElement.setAttribute("data-claire-operator-controls", "connected");
    } catch (error) {
      const status = document.getElementById("claire-operator-control-status");
      const summary = document.getElementById("claire-operator-control-summary");
      if (status) {
        status.textContent = "unavailable";
        status.style.color = "#ffb4b4";
      }
      if (summary) summary.textContent = "Operator control endpoint unavailable: " + error.message;
      window.__CLAIRE_OPERATOR_CONTROLS_ERROR__ = error;
    }
  }

  window.ClaireOperatorControlContracts = { routes: ROUTES, refresh: refresh };

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", refresh);
  else refresh();

  setInterval(refresh, 30000);
})();
