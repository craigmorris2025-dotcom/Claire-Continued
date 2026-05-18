/*
Claire Syntalion v19.89.3
Safe Operator Action Console

Contract-driven cockpit controls.
Backend owns truth.
*/
(function () {
  "use strict";

  const API_BASE = (window.localStorage && localStorage.getItem("CLAIRE_API_BASE")) || "http://127.0.0.1:8000";

  const ROUTES = {
    controls: API_BASE + "/system/operator-controls",
    controlsSummary: API_BASE + "/system/operator-controls/summary"
  };

  const SAFE_GET_KEYS = new Set([
    "continuous_status",
    "review_queue",
    "provider_status",
    "universes",
    "latest_run",
    "project_inventory"
  ]);

  const PROTECTED_POST_KEYS = new Set([
    "manual_run_start",
    "continuous_start",
    "continuous_pause",
    "search_live"
  ]);

  async function fetchJson(url, options) {
    const r = await fetch(url, Object.assign({
      cache: "no-store",
      headers: { "Accept": "application/json", "Content-Type": "application/json" }
    }, options || {}));
    const text = await r.text();
    let data = null;
    try { data = text ? JSON.parse(text) : null; } catch (_) { data = { raw: text }; }
    if (!r.ok) {
      const err = new Error(url + " returned HTTP " + r.status);
      err.response = data;
      throw err;
    }
    return data;
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
    let panel = document.getElementById("claire-safe-operator-action-console");
    if (panel) return panel;

    panel = document.createElement("section");
    panel.id = "claire-safe-operator-action-console";
    panel.setAttribute("data-claire-panel", "safe-operator-action-console");
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
      '<div style="letter-spacing:.18em;color:#70f3ff;font-weight:800;font-size:12px;">SAFE OPERATOR ACTION CONSOLE</div>',
      '<div style="font-size:13px;opacity:.78;margin-top:4px;">Contract-driven controls. Read actions run directly. Write/start actions are protected.</div>',
      '</div>',
      '<button id="claire-action-refresh" style="padding:8px 12px;border-radius:10px;border:1px solid rgba(130,170,255,.35);background:rgba(20,35,60,.9);color:#dce8ff;cursor:pointer;">Refresh</button>',
      '</div>',
      '<div id="claire-action-console-summary" style="font-size:13px;opacity:.9;margin-bottom:12px;"></div>',
      '<div id="claire-action-console-grid" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:10px;"></div>',
      '<pre id="claire-action-console-output" style="margin-top:12px;max-height:280px;overflow:auto;background:rgba(0,0,0,.32);border:1px solid rgba(130,170,255,.22);border-radius:12px;padding:12px;color:#dce8ff;font-size:12px;white-space:pre-wrap;"></pre>'
    ].join("");

    const controls = document.getElementById("claire-operator-control-contracts");
    if (controls && controls.parentElement) controls.parentElement.insertBefore(panel, controls.nextSibling);
    else document.body.appendChild(panel);

    const refreshButton = document.getElementById("claire-action-refresh");
    if (refreshButton) refreshButton.addEventListener("click", refresh);

    return panel;
  }

  function setOutput(value) {
    const out = document.getElementById("claire-action-console-output");
    if (!out) return;
    if (typeof value === "string") out.textContent = value;
    else out.textContent = JSON.stringify(value, null, 2);
  }

  function actionMode(control) {
    if (control.status !== "available") return "disabled";
    if (SAFE_GET_KEYS.has(control.key) && control.method === "GET") return "read";
    if (PROTECTED_POST_KEYS.has(control.key) && control.method === "POST") return "protected";
    if (control.method === "GET") return "read";
    return "protected";
  }

  async function runControl(control) {
    const mode = actionMode(control);
    const url = API_BASE + control.route;

    if (mode === "disabled") {
      setOutput("Control unavailable: " + control.label + "\nRoute: " + control.method + " " + control.route);
      return;
    }

    if (mode === "protected") {
      const ok = window.confirm(
        "Protected operator action:\n\n" +
        control.label + "\n" +
        control.method + " " + control.route + "\n\n" +
        "This will call the backend route exactly as contracted. Continue?"
      );
      if (!ok) {
        setOutput("Canceled protected action: " + control.label);
        return;
      }
    }

    try {
      setOutput("Calling " + control.method + " " + control.route + " ...");
      let result;
      if (control.method === "GET") {
        result = await fetchJson(url, { method: "GET" });
      } else {
        const body = buildBody(control);
        result = await fetchJson(url, { method: control.method, body: JSON.stringify(body) });
      }
      setOutput({
        action: control.key,
        route: control.route,
        method: control.method,
        status: "ok",
        result: result
      });
    } catch (error) {
      setOutput({
        action: control.key,
        route: control.route,
        method: control.method,
        status: "error",
        error: error.message,
        response: error.response || null
      });
    }
  }

  function buildBody(control) {
    if (control.key === "manual_run_start") {
      return {
        raw_input: "Operator-triggered governed Claire runtime check from cockpit action console.",
        mode: "operator_console",
        route_preference: "auto",
        evidence_required: true
      };
    }
    if (control.key === "search_live") {
      return {
        query: "Claire governed live search readiness check",
        mode: "operator_console_probe",
        limit: 3
      };
    }
    return {
      source: "cockpit_action_console",
      requested_at: new Date().toISOString()
    };
  }

  function render(data) {
    ensurePanel();

    const summary = document.getElementById("claire-action-console-summary");
    const grid = document.getElementById("claire-action-console-grid");
    const s = data.summary || {};

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
      const mode = actionMode(control);
      const c = color(control.status);
      const disabled = mode === "disabled";
      const label = mode === "read" ? "Read" : mode === "protected" ? "Protected Run" : "Unavailable";

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
        '<div style="font-size:11px;opacity:.68;margin-top:6px;">' + esc(control.safe_mode || "") + '</div>',
        '<button style="margin-top:10px;padding:8px 10px;border-radius:10px;border:1px solid rgba(130,170,255,.35);background:' + (disabled ? "rgba(80,80,80,.35)" : "rgba(20,35,60,.95)") + ';color:#dce8ff;cursor:' + (disabled ? "not-allowed" : "pointer") + ';" ' + (disabled ? "disabled" : "") + '>' + label + '</button>'
      ].join("");

      const button = card.querySelector("button");
      if (button && !disabled) button.addEventListener("click", () => runControl(control));

      grid.appendChild(card);
    });

    window.__CLAIRE_SAFE_OPERATOR_ACTIONS__ = data;
  }

  async function refresh() {
    ensurePanel();
    try {
      const data = await fetchJson(ROUTES.controls, { method: "GET" });
      render(data);
      document.documentElement.setAttribute("data-claire-action-console", "connected");
    } catch (error) {
      setOutput("Action console unavailable: " + error.message);
      document.documentElement.setAttribute("data-claire-action-console", "unavailable");
      window.__CLAIRE_ACTION_CONSOLE_ERROR__ = error;
    }
  }

  window.ClaireSafeOperatorActionConsole = { routes: ROUTES, refresh: refresh };

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", refresh);
  else refresh();

  setInterval(refresh, 30000);
})();
