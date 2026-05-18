/*
Claire Syntalion v19.89.1
Operator Surface Coverage Map
*/
(function () {
  "use strict";

  const API_BASE = (window.localStorage && localStorage.getItem("CLAIRE_API_BASE")) || "http://127.0.0.1:8000";
  const ROUTES = {
    surfaces: API_BASE + "/system/operator-surfaces",
    summary: API_BASE + "/system/operator-surfaces/summary",
    missing: API_BASE + "/system/operator-surfaces/missing"
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
    if (status === "complete") return "#9dffbc";
    if (status === "partial") return "#ffe08a";
    return "#ffb4b4";
  }

  function ensurePanel() {
    let panel = document.getElementById("claire-operator-surface-map");
    if (panel) return panel;

    panel = document.createElement("section");
    panel.id = "claire-operator-surface-map";
    panel.setAttribute("data-claire-panel", "operator-surface-map");
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
      '<div style="letter-spacing:.18em;color:#70f3ff;font-weight:800;font-size:12px;">OPERATOR SURFACE COVERAGE</div>',
      '<div style="font-size:13px;opacity:.78;margin-top:4px;">Maps existing backend capability to cockpit/operator surfaces before deep dashboard wiring.</div>',
      '</div>',
      '<div id="claire-operator-surface-status" style="font-weight:800;">checking</div>',
      '</div>',
      '<div id="claire-operator-surface-summary" style="font-size:13px;opacity:.9;margin-bottom:12px;"></div>',
      '<div id="claire-operator-surface-grid" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:10px;"></div>'
    ].join("");

    const projectPanel = document.getElementById("claire-project-inventory-surface");
    if (projectPanel && projectPanel.parentElement) {
      projectPanel.parentElement.insertBefore(panel, projectPanel.nextSibling);
    } else {
      document.body.appendChild(panel);
    }

    return panel;
  }

  function render(data) {
    ensurePanel();
    const status = document.getElementById("claire-operator-surface-status");
    const summary = document.getElementById("claire-operator-surface-summary");
    const grid = document.getElementById("claire-operator-surface-grid");

    const s = data.summary || {};
    if (status) status.textContent = data.status || "mapped";
    if (summary) {
      summary.textContent = [
        "surfaces: " + (s.total_surfaces || 0),
        "complete: " + (s.complete || 0),
        "partial: " + (s.partial || 0),
        "missing: " + (s.missing || 0),
        "routes: " + (s.live_route_count || 0)
      ].join(" | ");
    }

    if (!grid) return;
    grid.innerHTML = "";

    (data.surfaces || []).forEach(surface => {
      const card = document.createElement("div");
      const c = color(surface.status);
      card.style.cssText = [
        "border:1px solid rgba(130,170,255,0.24)",
        "border-radius:12px",
        "padding:12px",
        "background:rgba(8,14,27,0.74)"
      ].join(";");

      const missing = (surface.missing_routes || []).slice(0, 5).map(r => "<li>" + esc(r) + "</li>").join("");
      const present = (surface.present_routes || []).length;

      card.innerHTML = [
        '<div style="display:flex;justify-content:space-between;gap:8px;align-items:center;">',
        '<div style="font-weight:800;">' + esc(surface.label) + '</div>',
        '<div style="color:' + c + ';font-size:12px;font-weight:800;">' + esc(surface.status) + '</div>',
        '</div>',
        '<div style="font-size:12px;opacity:.75;margin-top:6px;">' + esc(surface.purpose) + '</div>',
        '<div style="font-size:12px;margin-top:8px;">coverage: ' + Math.round((surface.coverage || 0) * 100) + '% · present: ' + present + '</div>',
        missing ? '<div style="font-size:11px;opacity:.68;margin-top:8px;">missing:<ul style="margin:4px 0 0 16px;padding:0;">' + missing + '</ul></div>' : ''
      ].join("");
      grid.appendChild(card);
    });

    window.__CLAIRE_OPERATOR_SURFACES__ = data;
  }

  async function refresh() {
    ensurePanel();
    try {
      const data = await fetchJson(ROUTES.surfaces);
      render(data);
      document.documentElement.setAttribute("data-claire-operator-surfaces", "connected");
    } catch (error) {
      const status = document.getElementById("claire-operator-surface-status");
      const summary = document.getElementById("claire-operator-surface-summary");
      if (status) {
        status.textContent = "unavailable";
        status.style.color = "#ffb4b4";
      }
      if (summary) summary.textContent = "Operator surface endpoint unavailable: " + error.message;
      window.__CLAIRE_OPERATOR_SURFACES_ERROR__ = error;
    }
  }

  window.ClaireOperatorSurfaceMap = { routes: ROUTES, refresh: refresh };

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", refresh);
  else refresh();

  setInterval(refresh, 30000);
})();
