/*
Claire Syntalion v19.88.7
Local cockpit live backend bridge.
Backend remains truth owner. Cockpit renders backend payload/status.
*/
(function () {
  "use strict";
  const DEFAULT_BASE = "http://127.0.0.1:8000";
  const API_BASE = (window.localStorage && localStorage.getItem("CLAIRE_API_BASE")) || DEFAULT_BASE;
  const ROUTES = {
    docs: API_BASE + "/docs",
    status: API_BASE + "/dashboard/payload/status",
    payload: API_BASE + "/dashboard/payload",
    health: API_BASE + "/health"
  };

  function nowText() { return new Date().toLocaleTimeString(); }

  function ensureProofPanel() {
    let panel = document.getElementById("claire-live-backend-proof");
    if (panel) return panel;
    panel = document.createElement("section");
    panel.id = "claire-live-backend-proof";
    panel.setAttribute("data-claire-panel", "live-backend-proof");
    panel.style.cssText = [
      "position:fixed","right:16px","bottom:16px","z-index:99999","max-width:420px",
      "background:rgba(8,12,20,0.94)","color:#e8f0ff",
      "border:1px solid rgba(120,160,255,0.35)","border-radius:14px",
      "box-shadow:0 10px 30px rgba(0,0,0,0.35)",
      "font-family:Segoe UI,Arial,sans-serif","font-size:12px","line-height:1.35","padding:12px 14px"
    ].join(";");
    panel.innerHTML = [
      '<div style="font-weight:700;font-size:13px;margin-bottom:6px;">Claire Live Backend</div>',
      '<div id="claire-live-backend-state">checking...</div>',
      '<div id="claire-live-backend-summary" style="margin-top:6px;opacity:.88;"></div>',
      '<div style="margin-top:8px;opacity:.75;">',
      '<a target="_blank" style="color:#9fc0ff;" href="' + ROUTES.docs + '">docs</a>',
      ' · <a target="_blank" style="color:#9fc0ff;" href="' + ROUTES.status + '">status</a>',
      ' · <a target="_blank" style="color:#9fc0ff;" href="' + ROUTES.payload + '">payload</a>',
      '</div>'
    ].join("");
    document.body.appendChild(panel);
    return panel;
  }

  function setText(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value == null ? "" : String(value);
  }

  function readPath(obj, path) {
    if (!obj || !path) return undefined;
    return path.split(".").reduce((cur, key) => (cur && Object.prototype.hasOwnProperty.call(cur, key)) ? cur[key] : undefined, obj);
  }

  function setKnownFields(payload) {
    const fields = {
      "claire-runtime-state": payload.runtime_state || payload.state || payload.status,
      "claire-terminal-state": payload.terminal_state,
      "claire-selected-route": payload.selected_route || payload.route,
      "claire-confidence": payload.confidence || payload.confidence_score,
      "claire-version": payload.version || payload.current_version,
      "claire-last-updated": nowText()
    };
    Object.entries(fields).forEach(([id, value]) => setText(id, value));
    document.querySelectorAll("[data-claire-field]").forEach((el) => {
      const value = readPath(payload, el.getAttribute("data-claire-field"));
      if (value !== undefined && value !== null) el.textContent = typeof value === "object" ? JSON.stringify(value, null, 2) : String(value);
    });
    window.__CLAIRE_BACKEND_PAYLOAD__ = payload;
    window.dispatchEvent(new CustomEvent("claire:backend-payload", { detail: payload }));
  }

  function summarizePayload(payload) {
    if (!payload || typeof payload !== "object") return "Payload unavailable.";
    const parts = [];
    if (payload.version || payload.current_version) parts.push("version: " + (payload.version || payload.current_version));
    if (payload.status) parts.push("status: " + payload.status);
    if (payload.runtime_state || payload.state) parts.push("runtime: " + (payload.runtime_state || payload.state));
    if (payload.terminal_state) parts.push("terminal: " + payload.terminal_state);
    if (payload.selected_route || payload.route) parts.push("route: " + (payload.selected_route || payload.route));
    if (Array.isArray(payload.lifecycle_stages)) parts.push("stages: " + payload.lifecycle_stages.length);
    if (Array.isArray(payload.panels)) parts.push("panels: " + payload.panels.length);
    if (payload.dashboard && Array.isArray(payload.dashboard.panels)) parts.push("panels: " + payload.dashboard.panels.length);
    return parts.length ? parts.join(" | ") : "Payload fetched; keys: " + Object.keys(payload).slice(0, 10).join(", ");
  }

  async function fetchJson(url) {
    const response = await fetch(url, { method: "GET", cache: "no-store", headers: { "Accept": "application/json" } });
    if (!response.ok) throw new Error(url + " returned HTTP " + response.status);
    return await response.json();
  }

  async function refresh() {
    ensureProofPanel();
    const state = document.getElementById("claire-live-backend-state");
    const summary = document.getElementById("claire-live-backend-summary");
    try {
      if (state) state.textContent = "checking backend...";
      let status = null;
      try { status = await fetchJson(ROUTES.status); } catch (statusError) { status = { warning: statusError.message }; }
      const payload = await fetchJson(ROUTES.payload);
      if (state) { state.textContent = "CONNECTED at " + nowText(); state.style.color = "#9dffbc"; }
      if (summary) summary.textContent = (status ? "status ok" : "status unknown") + " | " + summarizePayload(payload);
      setKnownFields(payload);
      document.documentElement.setAttribute("data-claire-backend", "connected");
    } catch (error) {
      if (state) { state.textContent = "NOT CONNECTED: " + error.message; state.style.color = "#ffb4b4"; }
      if (summary) summary.textContent = "Expected routes: " + ROUTES.status + " and " + ROUTES.payload;
      document.documentElement.setAttribute("data-claire-backend", "unavailable");
      window.__CLAIRE_BACKEND_ERROR__ = error;
    }
  }

  window.ClaireLiveBackendBridge = { routes: ROUTES, refresh: refresh };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", refresh);
  else refresh();
  setInterval(refresh, 15000);
})();
