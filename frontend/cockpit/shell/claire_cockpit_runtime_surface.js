/*
Claire Syntalion v19.88.9
Cockpit Runtime Surface Wiring

Presentation-only layer.
Backend owns truth.
*/

(function () {
  "use strict";

  const API_BASE = (window.localStorage && localStorage.getItem("CLAIRE_API_BASE")) || "http://127.0.0.1:8000";

  const ROUTES = {
    status: API_BASE + "/dashboard/payload/status",
    payload: API_BASE + "/dashboard/payload",
    continuousStatus: API_BASE + "/runtime/continuous/status",
    reviewQueue: API_BASE + "/runtime/continuous/review-queue",
    latestRun: API_BASE + "/runs/latest",
    universes: API_BASE + "/universes",
    projectConnection: API_BASE + "/system/project-connection/status",
    fetchMap: API_BASE + "/system/cockpit-fetch-map"
  };

  function textOf(node) {
    return (node && node.textContent ? node.textContent : "").trim();
  }

  function normalize(value, fallback) {
    if (value === undefined || value === null || value === "") return fallback;
    if (typeof value === "object") return JSON.stringify(value);
    return String(value);
  }

  function pick(obj, paths, fallback) {
    for (const path of paths) {
      const value = path.split(".").reduce((cur, key) => cur && Object.prototype.hasOwnProperty.call(cur, key) ? cur[key] : undefined, obj);
      if (value !== undefined && value !== null && value !== "") return value;
    }
    return fallback;
  }

  async function fetchJson(url) {
    const r = await fetch(url, {
      method: "GET",
      cache: "no-store",
      headers: { "Accept": "application/json" }
    });
    if (!r.ok) throw new Error(url + " returned HTTP " + r.status);
    return await r.json();
  }

  function findCardByLabel(label) {
    const wanted = label.toLowerCase();
    const nodes = Array.from(document.querySelectorAll("div, section, article, aside"));
    for (const node of nodes) {
      const t = textOf(node).toLowerCase();
      if (t.includes(wanted)) {
        const card = node.closest("section, article, aside, div");
        if (card) return card;
      }
    }
    return null;
  }

  function replaceFollowingValue(label, value) {
    const wanted = label.toLowerCase();
    const all = Array.from(document.querySelectorAll("body *")).filter(el => el.children.length === 0);
    for (const el of all) {
      if (textOf(el).toLowerCase() === wanted) {
        let current = el;
        for (let i = 0; i < 8 && current; i++) {
          let next = current.nextElementSibling;
          while (next) {
            if (textOf(next) && textOf(next).toLowerCase() !== wanted) {
              next.textContent = value;
              return true;
            }
            next = next.nextElementSibling;
          }
          current = current.parentElement;
        }
      }
    }
    return false;
  }

  function replaceExactText(oldText, newText) {
    const all = Array.from(document.querySelectorAll("body *")).filter(el => el.children.length === 0);
    for (const el of all) {
      if (textOf(el) === oldText) {
        el.textContent = newText;
        return true;
      }
    }
    return false;
  }

  function ensureSystemStrip() {
    let strip = document.getElementById("claire-runtime-surface-strip");
    if (strip) return strip;

    strip = document.createElement("section");
    strip.id = "claire-runtime-surface-strip";
    strip.setAttribute("data-claire-panel", "runtime-surface-strip");
    strip.style.cssText = [
      "margin:16px 26px",
      "padding:14px 18px",
      "border:1px solid rgba(105,158,255,0.32)",
      "border-radius:16px",
      "background:rgba(12,21,38,0.72)",
      "color:#dce8ff",
      "font-family:Segoe UI,Arial,sans-serif"
    ].join(";");

    strip.innerHTML = [
      '<div style="letter-spacing:.18em;color:#70f3ff;font-weight:800;font-size:12px;margin-bottom:10px;">LIVE RUNTIME SURFACE</div>',
      '<div style="display:grid;grid-template-columns:repeat(5,minmax(140px,1fr));gap:12px;">',
      '<div><div style="opacity:.65;font-size:11px;">Backend</div><div id="claire-ui-backend" style="font-weight:800;">checking</div></div>',
      '<div><div style="opacity:.65;font-size:11px;">Payload</div><div id="claire-ui-payload" style="font-weight:800;">checking</div></div>',
      '<div><div style="opacity:.65;font-size:11px;">Runtime</div><div id="claire-ui-runtime" style="font-weight:800;">checking</div></div>',
      '<div><div style="opacity:.65;font-size:11px;">Route</div><div id="claire-ui-route" style="font-weight:800;">checking</div></div>',
      '<div><div style="opacity:.65;font-size:11px;">Project</div><div id="claire-ui-project" style="font-weight:800;">checking</div></div>',
      '</div>',
      '<div id="claire-ui-summary" style="margin-top:10px;opacity:.82;font-size:12px;"></div>'
    ].join("");

    const header = document.querySelector("header") || document.body.firstElementChild;
    if (header && header.parentElement) {
      header.parentElement.insertBefore(strip, header.nextSibling);
    } else {
      document.body.insertBefore(strip, document.body.firstChild);
    }
    return strip;
  }

  function set(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = normalize(value, "unavailable");
  }

  function countPanels(payload) {
    if (Array.isArray(payload.panels)) return payload.panels.length;
    if (payload.dashboard && Array.isArray(payload.dashboard.panels)) return payload.dashboard.panels.length;
    return null;
  }

  function countStages(payload) {
    if (Array.isArray(payload.lifecycle_stages)) return payload.lifecycle_stages.length;
    if (payload.lifecycle && Array.isArray(payload.lifecycle.stages)) return payload.lifecycle.stages.length;
    if (Array.isArray(payload.stages)) return payload.stages.length;
    return null;
  }

  function buildTruth(payload, extras) {
    const panels = countPanels(payload);
    const stages = countStages(payload);
    const version = pick(payload, ["version", "current_version", "meta.version"], "connected");
    const runtime = pick(payload, ["runtime_state", "runtime.status", "continuous_runtime.status", "status"], "connected");
    const route = pick(payload, ["selected_route", "route", "route_state", "terminal_state"], "backend-owned");
    const run = pick(payload, ["run.id", "latest_run.id", "active_run.id", "run_state"], "none");
    const project = pick(extras.project || {}, ["status"], "unknown");

    return { version, runtime, route, run, project, panels, stages };
  }

  function applyVisibleCards(truth) {
    replaceFollowingValue("BACKEND", "connected");
    replaceFollowingValue("PAYLOAD", "live");
    replaceFollowingValue("RUN", truth.run || "none");

    replaceExactText("unavailable", truth.runtime || "connected");
    replaceExactText("pending_evidence", truth.route || "backend-owned");

    set("claire-ui-backend", "connected");
    set("claire-ui-payload", truth.panels ? "live · " + truth.panels + " panels" : "live");
    set("claire-ui-runtime", truth.runtime || "connected");
    set("claire-ui-route", truth.route || "backend-owned");
    set("claire-ui-project", truth.project || "connected");

    const summary = [];
    summary.push("version: " + truth.version);
    if (truth.stages !== null) summary.push("stages: " + truth.stages);
    if (truth.panels !== null) summary.push("panels: " + truth.panels);
    summary.push("backend truth: active");
    set("claire-ui-summary", summary.join(" | "));
  }

  async function refresh() {
    ensureSystemStrip();

    const extras = {};
    let payload = null;

    try {
      payload = await fetchJson(ROUTES.payload);
      try { extras.project = await fetchJson(ROUTES.projectConnection); } catch (_) {}
      try { extras.continuous = await fetchJson(ROUTES.continuousStatus); } catch (_) {}
      try { extras.latestRun = await fetchJson(ROUTES.latestRun); } catch (_) {}

      const truth = buildTruth(payload, extras);

      if (extras.continuous && typeof extras.continuous === "object") {
        truth.runtime = pick(extras.continuous, ["status", "state", "runtime_state"], truth.runtime);
      }
      if (extras.latestRun && typeof extras.latestRun === "object") {
        truth.run = pick(extras.latestRun, ["id", "run_id", "status", "state"], truth.run);
      }

      applyVisibleCards(truth);
      document.documentElement.setAttribute("data-claire-runtime-surface", "connected");
      window.__CLAIRE_RUNTIME_SURFACE__ = { truth, payload, extras, routes: ROUTES };
    } catch (error) {
      set("claire-ui-backend", "unavailable");
      set("claire-ui-payload", "unavailable");
      set("claire-ui-runtime", "unavailable");
      set("claire-ui-route", "unknown");
      set("claire-ui-project", "unknown");
      set("claire-ui-summary", "Runtime surface could not read backend payload: " + error.message);
      document.documentElement.setAttribute("data-claire-runtime-surface", "unavailable");
      window.__CLAIRE_RUNTIME_SURFACE_ERROR__ = error;
    }
  }

  window.ClaireCockpitRuntimeSurface = {
    routes: ROUTES,
    refresh: refresh
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", refresh);
  } else {
    refresh();
  }

  window.addEventListener("claire:backend-payload", function (event) {
    try {
      const truth = buildTruth(event.detail || {}, {});
      applyVisibleCards(truth);
    } catch (_) {}
  });

  setInterval(refresh, 15000);
})();
