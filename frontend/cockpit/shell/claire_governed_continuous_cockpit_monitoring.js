
(function () {
  "use strict";

  const VERSION = "v19.89.8-S12";

  const ROUTES = {
    payloadStatus: "/dashboard/payload/status",
    runtimeState: "/system/runtime-state/summary",
    runtimeExecution: "/system/runtime-execution/summary",
    cockpitFetchMap: "/system/cockpit-fetch-map/summary"
  };

  const monitor = {
    version: VERSION,
    backend_owns_truth: true,
    cockpit_presentation_only: true,
    runtime_authority_expanded: false,
    safe_to_expand_runtime_authority: false,
    monitoring_active: true,
    cycles: 0,
    alerts: [],
    health: "unknown",
    last_run_at: null,
    drift_detected: false,
    synchronization_degraded: false,
    stale_runtime_detected: false
  };

  let previousSnapshot = null;

  async function fetchJson(route) {
    try {
      const response = await fetch(route, {
        method: "GET",
        headers: { "Accept": "application/json" },
        cache: "no-store"
      });

      let data = null;

      try {
        data = await response.json();
      } catch (err) {
        data = {};
      }

      return {
        ok: response.ok,
        status: response.status,
        data
      };

    } catch (err) {
      return {
        ok: false,
        error: String(err)
      };
    }
  }

  async function collectSnapshot() {
    const out = {};

    for (const [key, route] of Object.entries(ROUTES)) {
      out[key] = await fetchJson(route);
    }

    return out;
  }

  function shallowSignature(snapshot) {
    return JSON.stringify({
      payload: snapshot.payloadStatus && snapshot.payloadStatus.status,
      runtime: snapshot.runtimeState && snapshot.runtimeState.status,
      execution: snapshot.runtimeExecution && snapshot.runtimeExecution.status,
      fetchMap: snapshot.cockpitFetchMap && snapshot.cockpitFetchMap.status
    });
  }

  function evaluate(snapshot) {
    monitor.alerts = [];

    const payloadOk = snapshot.payloadStatus && snapshot.payloadStatus.ok;
    const runtimeOk = snapshot.runtimeState && snapshot.runtimeState.ok;
    const executionOk = snapshot.runtimeExecution && snapshot.runtimeExecution.ok;

    if (!(payloadOk && runtimeOk)) {
      monitor.synchronization_degraded = true;
      monitor.alerts.push("Synchronization degraded");
    } else {
      monitor.synchronization_degraded = false;
    }

    if (!executionOk) {
      monitor.stale_runtime_detected = true;
      monitor.alerts.push("Runtime execution unavailable");
    } else {
      monitor.stale_runtime_detected = false;
    }

    const currentSignature = shallowSignature(snapshot);

    if (previousSnapshot && previousSnapshot !== currentSignature) {
      monitor.drift_detected = true;
      monitor.alerts.push("Payload/runtime drift observed");
    } else {
      monitor.drift_detected = false;
    }

    previousSnapshot = currentSignature;

    if (
      payloadOk &&
      runtimeOk &&
      executionOk &&
      !monitor.drift_detected
    ) {
      monitor.health = "live";
    } else if (
      payloadOk ||
      runtimeOk ||
      executionOk
    ) {
      monitor.health = "degraded";
    } else {
      monitor.health = "unavailable";
    }
  }

  function ensurePanel() {
    let panel = document.querySelector("[data-claire-s12-monitoring-panel]");

    if (!panel) {
      panel = document.createElement("section");

      panel.setAttribute(
        "data-claire-s12-monitoring-panel",
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

  function render() {
    const panel = ensurePanel();

    panel.innerHTML = "";

    const title = document.createElement("h3");
    title.textContent = "Governed Continuous Cockpit Monitoring";
    panel.appendChild(title);

    const pre = document.createElement("pre");

    pre.style.whiteSpace = "pre-wrap";
    pre.style.maxHeight = "320px";
    pre.style.overflow = "auto";

    pre.textContent = JSON.stringify({
      version: monitor.version,
      monitoring_active: monitor.monitoring_active,
      health: monitor.health,
      drift_detected: monitor.drift_detected,
      synchronization_degraded: monitor.synchronization_degraded,
      stale_runtime_detected: monitor.stale_runtime_detected,
      alerts: monitor.alerts,
      cycles: monitor.cycles,
      runtime_authority_expanded: false
    }, null, 2);

    panel.appendChild(pre);

    document.documentElement.setAttribute(
      "data-claire-governed-monitoring-health",
      monitor.health
    );

    document.documentElement.setAttribute(
      "data-claire-runtime-authority-expanded",
      "false"
    );
  }

  async function run() {
    const snapshot = await collectSnapshot();

    monitor.cycles += 1;
    monitor.last_run_at = new Date().toISOString();

    evaluate(snapshot);

    render();

    window.ClaireGovernedContinuousCockpitMonitoring = monitor;

    return monitor;
  }

  window.ClaireGovernedContinuousCockpitMonitoringTools = {
    version: VERSION,
    run,
    monitor
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", run);
  } else {
    run();
  }

  setInterval(run, 30000);
})();
