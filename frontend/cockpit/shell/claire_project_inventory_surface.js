/*
Claire Syntalion v19.89.0
Project Inventory + Source Surface Wiring

Presentation-only cockpit surface.
Backend owns project inventory truth.
*/
(function () {
  "use strict";

  const API_BASE = (window.localStorage && localStorage.getItem("CLAIRE_API_BASE")) || "http://127.0.0.1:8000";
  const ROUTES = {
    inventory: API_BASE + "/system/project-inventory",
    summary: API_BASE + "/system/project-inventory/summary",
    sourceStatus: API_BASE + "/system/source-surface/status"
  };

  async function fetchJson(url) {
    const r = await fetch(url, { method: "GET", cache: "no-store", headers: { "Accept": "application/json" } });
    if (!r.ok) throw new Error(url + " returned HTTP " + r.status);
    return await r.json();
  }

  function fmtBytes(bytes) {
    if (!bytes && bytes !== 0) return "0 B";
    const units = ["B", "KB", "MB", "GB"];
    let value = Number(bytes) || 0;
    let idx = 0;
    while (value >= 1024 && idx < units.length - 1) {
      value = value / 1024;
      idx += 1;
    }
    return (idx === 0 ? value.toFixed(0) : value.toFixed(1)) + " " + units[idx];
  }

  function ensurePanel() {
    let panel = document.getElementById("claire-project-inventory-surface");
    if (panel) return panel;

    panel = document.createElement("section");
    panel.id = "claire-project-inventory-surface";
    panel.setAttribute("data-claire-panel", "project-inventory-surface");
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
      '<div style="letter-spacing:.18em;color:#70f3ff;font-weight:800;font-size:12px;">PROJECT CONNECTION SURFACE</div>',
      '<div id="claire-project-root" style="font-size:12px;opacity:.72;margin-top:4px;">checking project root...</div>',
      '</div>',
      '<div id="claire-project-status" style="font-weight:800;color:#9dffbc;">checking</div>',
      '</div>',
      '<div id="claire-project-summary" style="font-size:13px;opacity:.9;margin-bottom:12px;"></div>',
      '<div id="claire-project-grid" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:10px;"></div>'
    ].join("");

    const runtimeStrip = document.getElementById("claire-runtime-surface-strip");
    if (runtimeStrip && runtimeStrip.parentElement) {
      runtimeStrip.parentElement.insertBefore(panel, runtimeStrip.nextSibling);
    } else {
      const header = document.querySelector("header") || document.body.firstElementChild;
      if (header && header.parentElement) header.parentElement.insertBefore(panel, header.nextSibling);
      else document.body.insertBefore(panel, document.body.firstChild);
    }

    return panel;
  }

  function render(inv) {
    ensurePanel();
    const status = document.getElementById("claire-project-status");
    const root = document.getElementById("claire-project-root");
    const summary = document.getElementById("claire-project-summary");
    const grid = document.getElementById("claire-project-grid");

    if (status) status.textContent = inv.status || "unknown";
    if (root) root.textContent = inv.project_root || "";
    if (summary) {
      const t = inv.totals || {};
      summary.textContent = [
        "surfaces: " + (t.existing_surfaces || 0) + " connected",
        "files indexed: " + (t.files || 0),
        "folders indexed: " + (t.directories || 0),
        "size: " + fmtBytes(t.bytes || 0)
      ].join(" | ");
    }

    if (!grid) return;
    grid.innerHTML = "";

    (inv.inventory || []).forEach((item) => {
      const card = document.createElement("div");
      card.style.cssText = [
        "border:1px solid rgba(130,170,255,0.24)",
        "border-radius:12px",
        "padding:12px",
        "background:rgba(8,14,27,0.74)"
      ].join(";");

      const color = item.exists ? "#9dffbc" : "#ffb4b4";
      card.innerHTML = [
        '<div style="display:flex;justify-content:space-between;gap:8px;align-items:center;">',
        '<div style="font-weight:800;">' + escapeHtml(item.key || item.path) + '</div>',
        '<div style="color:' + color + ';font-size:12px;font-weight:800;">' + (item.exists ? "connected" : "missing") + '</div>',
        '</div>',
        '<div style="font-size:12px;opacity:.75;margin-top:4px;">' + escapeHtml(item.path || "") + '</div>',
        '<div style="font-size:12px;opacity:.9;margin-top:8px;">files: ' + (item.files || 0) + ' · folders: ' + (item.directories || 0) + '</div>',
        '<div style="font-size:11px;opacity:.65;margin-top:6px;">' + escapeHtml(item.purpose || "") + '</div>'
      ].join("");
      grid.appendChild(card);
    });

    window.__CLAIRE_PROJECT_INVENTORY__ = inv;
  }

  function escapeHtml(value) {
    return String(value == null ? "" : value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  async function refresh() {
    ensurePanel();
    try {
      const inv = await fetchJson(ROUTES.inventory);
      render(inv);
      document.documentElement.setAttribute("data-claire-project-inventory", "connected");
    } catch (error) {
      const status = document.getElementById("claire-project-status");
      const summary = document.getElementById("claire-project-summary");
      if (status) {
        status.textContent = "unavailable";
        status.style.color = "#ffb4b4";
      }
      if (summary) summary.textContent = "Project inventory endpoint unavailable: " + error.message;
      document.documentElement.setAttribute("data-claire-project-inventory", "unavailable");
      window.__CLAIRE_PROJECT_INVENTORY_ERROR__ = error;
    }
  }

  window.ClaireProjectInventorySurface = {
    routes: ROUTES,
    refresh: refresh
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", refresh);
  } else {
    refresh();
  }

  setInterval(refresh, 30000);
})();
