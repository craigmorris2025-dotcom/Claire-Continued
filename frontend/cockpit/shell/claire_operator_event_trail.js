/*
Claire Syntalion v19.89.4
Operator Event Trail + Action Proof Surface
*/
(function () {
  "use strict";

  const API_BASE = (window.localStorage && localStorage.getItem("CLAIRE_API_BASE")) || "http://127.0.0.1:8000";
  const ROUTES = {
    events: API_BASE + "/system/operator-events",
    summary: API_BASE + "/system/operator-events/summary",
    record: API_BASE + "/system/operator-events/record"
  };

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

  function ensurePanel() {
    let panel = document.getElementById("claire-operator-event-trail");
    if (panel) return panel;

    panel = document.createElement("section");
    panel.id = "claire-operator-event-trail";
    panel.setAttribute("data-claire-panel", "operator-event-trail");
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
      '<div style="letter-spacing:.18em;color:#70f3ff;font-weight:800;font-size:12px;">OPERATOR EVENT TRAIL</div>',
      '<div style="font-size:13px;opacity:.78;margin-top:4px;">Auditable cockpit action and backend-response trail.</div>',
      '</div>',
      '<button id="claire-event-refresh" style="padding:8px 12px;border-radius:10px;border:1px solid rgba(130,170,255,.35);background:rgba(20,35,60,.9);color:#dce8ff;cursor:pointer;">Refresh</button>',
      '</div>',
      '<div id="claire-event-summary" style="font-size:13px;opacity:.9;margin-bottom:12px;"></div>',
      '<div id="claire-event-list" style="display:grid;gap:8px;"></div>'
    ].join("");

    const actionConsole = document.getElementById("claire-safe-operator-action-console");
    if (actionConsole && actionConsole.parentElement) actionConsole.parentElement.insertBefore(panel, actionConsole.nextSibling);
    else document.body.appendChild(panel);

    const refreshButton = document.getElementById("claire-event-refresh");
    if (refreshButton) refreshButton.addEventListener("click", refresh);

    return panel;
  }

  async function record(event) {
    try {
      return await fetchJson(ROUTES.record, {
        method: "POST",
        body: JSON.stringify(Object.assign({ source: "cockpit" }, event || {}))
      });
    } catch (error) {
      window.__CLAIRE_OPERATOR_EVENT_RECORD_ERROR__ = error;
      return null;
    }
  }

  function render(data) {
    ensurePanel();
    const summary = document.getElementById("claire-event-summary");
    const list = document.getElementById("claire-event-list");

    if (summary) summary.textContent = "events: " + (data.count || 0);

    if (!list) return;
    list.innerHTML = "";

    const events = (data.events || []).slice().reverse().slice(0, 20);
    if (!events.length) {
      list.innerHTML = '<div style="opacity:.72;">No operator events recorded yet.</div>';
      return;
    }

    events.forEach(event => {
      const card = document.createElement("div");
      const status = event.status || "unknown";
      const color = status === "ok" || status === "recorded" ? "#9dffbc" : status === "error" ? "#ffb4b4" : "#ffe08a";
      card.style.cssText = [
        "border:1px solid rgba(130,170,255,0.24)",
        "border-radius:12px",
        "padding:10px 12px",
        "background:rgba(8,14,27,0.74)"
      ].join(";");

      card.innerHTML = [
        '<div style="display:flex;justify-content:space-between;gap:8px;align-items:center;">',
        '<div style="font-weight:800;">' + esc(event.action || event.event_type || "operator_event") + '</div>',
        '<div style="color:' + color + ';font-size:12px;font-weight:800;">' + esc(status) + '</div>',
        '</div>',
        '<div style="font-size:12px;opacity:.75;margin-top:4px;">' + esc(event.method || "") + ' ' + esc(event.route || "") + '</div>',
        '<div style="font-size:11px;opacity:.65;margin-top:4px;">' + esc(event.timestamp_utc || "") + '</div>',
        event.message ? '<div style="font-size:12px;margin-top:6px;">' + esc(event.message) + '</div>' : ''
      ].join("");
      list.appendChild(card);
    });

    window.__CLAIRE_OPERATOR_EVENTS__ = data;
  }

  async function refresh() {
    ensurePanel();
    try {
      const data = await fetchJson(ROUTES.events + "?limit=100", { method: "GET" });
      render(data);
      document.documentElement.setAttribute("data-claire-operator-events", "connected");
    } catch (error) {
      const summary = document.getElementById("claire-event-summary");
      if (summary) summary.textContent = "Operator event trail unavailable: " + error.message;
      window.__CLAIRE_OPERATOR_EVENTS_ERROR__ = error;
    }
  }

  // Patch the action console output writer if present by observing result output.
  function installActionConsoleObserver() {
    const out = document.getElementById("claire-action-console-output");
    if (!out || out.__claireEventObserverInstalled) return;
    out.__claireEventObserverInstalled = true;

    let last = "";
    const observer = new MutationObserver(() => {
      const text = out.textContent || "";
      if (!text || text === last) return;
      last = text;

      let parsed = null;
      try { parsed = JSON.parse(text); } catch (_) {}
      if (parsed && parsed.action) {
        record({
          event_type: "operator_action_result",
          surface: "safe_operator_action_console",
          action: parsed.action,
          route: parsed.route,
          method: parsed.method,
          status: parsed.status,
          message: parsed.error || "Action completed",
          details: parsed
        }).then(refresh);
      }
    });
    observer.observe(out, { childList: true, subtree: true, characterData: true });
  }

  window.ClaireOperatorEventTrail = {
    routes: ROUTES,
    refresh: refresh,
    record: record
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () {
      ensurePanel();
      installActionConsoleObserver();
      refresh();
    });
  } else {
    ensurePanel();
    installActionConsoleObserver();
    refresh();
  }

  setInterval(function () {
    installActionConsoleObserver();
    refresh();
  }, 30000);
})();
