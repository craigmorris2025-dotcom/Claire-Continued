
(function () {
  "use strict";

  const VERSION = "v19.89.8-S11";

  const ROUTES = {
    payloadStatus: "/dashboard/payload/status",
    runtimeState: "/system/runtime-state/summary",
    runtimeExecution: "/system/runtime-execution/summary",
    cockpitFetchMap: "/system/cockpit-fetch-map/summary"
  };

  const telemetry = {
    version: VERSION,
    backend_owns_truth: true,
    cockpit_presentation_only: true,
    runtime_authority_expanded: false,
    safe_to_expand_runtime_authority: false,
    collected_at: null,
    synchronization_state: "unknown",
    canonical_chain_health: "unknown",
    payload_freshness_ms: null,
    route_timings_ms: {},
    route_states: {},
    cadence_ms: null,
    cycles: 0
  };

  let lastCycleAt = null;

  async function timedFetch(route) {
    const start = performance.now();

    try {
      const response = await fetch(route, {
        method: "GET",
        headers: { "Accept": "application/json" },
        cache: "no-store"
      });

      const end = performance.now();

      let data = null;

      try {
        data = await response.json();
      } catch (err) {
        data = {};
      }

      return {
        ok: response.ok,
        status: response.status,
        duration_ms: Math.round(end - start),
        data
      };

    } catch (err) {
      const end = performance.now();

      return {
        ok: false,
        duration_ms: Math.round(end - start),
        error: String(err)
      };
    }
  }

  async function collectRoutes() {
    const out = {};

    for (const [key, route] of Object.entries(ROUTES)) {
      out[key] = await timedFetch(route);
    }

    return out;
  }

  function determineHealth(routes) {
    const values = Object.values(routes);

    const okCount = values.filter(v => v && v.ok).length;

    if (okCount === values.length) {
      return "live";
    }

    if (okCount > 0) {
      return "degraded";
    }

    return "unavailable";
  }

  function determineSyncState(routes) {
    if (
      routes.payloadStatus &&
      routes.payloadStatus.ok &&
      routes.runtimeState &&
      routes.runtimeState.ok
    ) {
      return "synchronized";
    }

    return "partial";
  }

  function updateCadence() {
    const now = Date.now();

    if (lastCycleAt !== null) {
      telemetry.cadence_ms = now - lastCycleAt;
    }

    lastCycleAt = now;
  }

  function applyDocumentState() {
    document.documentElement.setAttribute(
      "data-claire-telemetry-health",
      telemetry.canonical_chain_health
    );

    document.documentElement.setAttribute(
      "data-claire-runtime-authority-expanded",
      "false"
    );
  }

  function ensureTelemetryPanel() {
    let panel = document.querySelector("[data-claire-s11-telemetry-panel]");

    if (!panel) {
      panel = document.createElement("section");

      panel.setAttribute(
        "data-claire-s11-telemetry-panel",
        "true"
      );

      panel.style.marginTop = "16px";
      panel.style.padding = "12px";
      panel.style.border = "1px solid rgba(255,255,255,0.1)";
      panel.style.borderRadius = "10px";
      panel.style.background = "rgba(255,255,255,0.03)";

      const anchor =
        document.querySelector("main") ||
        document.querySelector("[class*=content]") ||
        document.body;

      anchor.appendChild(panel);
    }

    return panel;
  }

  function renderTelemetryPanel() {
    const panel = ensureTelemetryPanel();

    panel.innerHTML = "";

    const title = document.createElement("h3");
    title.textContent = "Canonical Runtime Telemetry";
    panel.appendChild(title);

    const pre = document.createElement("pre");

    pre.style.whiteSpace = "pre-wrap";
    pre.style.maxHeight = "320px";
    pre.style.overflow = "auto";

    pre.textContent = JSON.stringify({
      version: telemetry.version,
      synchronization_state: telemetry.synchronization_state,
      canonical_chain_health: telemetry.canonical_chain_health,
      payload_freshness_ms: telemetry.payload_freshness_ms,
      cadence_ms: telemetry.cadence_ms,
      route_timings_ms: telemetry.route_timings_ms,
      route_states: telemetry.route_states,
      cycles: telemetry.cycles,
      runtime_authority_expanded: false
    }, null, 2);

    panel.appendChild(pre);
  }

  async function run() {
    updateCadence();

    const started = Date.now();

    const routes = await collectRoutes();

    telemetry.collected_at = new Date().toISOString();

    telemetry.route_timings_ms = {};
    telemetry.route_states = {};

    for (const [key, result] of Object.entries(routes)) {
      telemetry.route_timings_ms[key] = result.duration_ms || null;
      telemetry.route_states[key] = result.ok ? "live" : "unavailable";
    }

    telemetry.synchronization_state =
      determineSyncState(routes);

    telemetry.canonical_chain_health =
      determineHealth(routes);

    telemetry.payload_freshness_ms =
      Date.now() - started;

    telemetry.cycles += 1;

    applyDocumentState();

    renderTelemetryPanel();

    window.ClaireCanonicalRuntimeTelemetry = telemetry;

    return telemetry;
  }

  window.ClaireCanonicalRuntimeTelemetryTools = {
    version: VERSION,
    run,
    telemetry
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", run);
  } else {
    run();
  }

  setInterval(run, 30000);
})();
