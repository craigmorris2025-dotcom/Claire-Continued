
// Claire Syntalion v19.89.8-S5
// Surface Availability Reconciliation
// Backend owns truth. Cockpit presentation only.

(function () {
  "use strict";

  const VERSION = "v19.89.8-S5";

  const ROUTES = {
    payloadStatus: "/dashboard/payload/status",
    runtimeExecution: "/system/runtime-execution/summary",
    runtimeState: "/system/runtime-state/summary",
    runtimePropagation: "/system/runtime-propagation/summary",
    reviewQueue: "/system/review-queue/summary",
    routeOwnerRegistry: "/system/route-owner-registry/summary",
    duplicateRouteFailTest: "/system/duplicate-route-fail-test/summary",
    cockpitFetchMap: "/system/cockpit-fetch-map/summary"
  };

  const reconciliation = {
    version: VERSION,
    backend_owns_truth: true,
    cockpit_presentation_only: true,
    runtime_authority_expanded: false,
    safe_to_expand_runtime_authority: false,
    checked_at: null,
    routes: {},
    panels: {}
  };

  async function fetchRoute(route) {
    try {
      const res = await fetch(route, {
        method: "GET",
        headers: { "Accept": "application/json" },
        cache: "no-store"
      });

      let data = null;
      try {
        data = await res.json();
      } catch (err) {
        data = { parse_error: true };
      }

      return {
        ok: res.ok,
        status: res.status,
        route,
        data
      };
    } catch (err) {
      return {
        ok: false,
        status: null,
        route,
        error: String(err)
      };
    }
  }

  async function collect() {
    const out = {};
    for (const [key, route] of Object.entries(ROUTES)) {
      out[key] = await fetchRoute(route);
    }
    reconciliation.checked_at = new Date().toISOString();
    reconciliation.routes = out;
    return out;
  }

  function classify(result) {
    if (!result) return "not_yet_wired";
    if (result.ok) return "wired_and_responding";
    return "wired_but_unavailable";
  }

  function findPanel(label) {
    const nodes = Array.from(document.querySelectorAll("section,article,div"));
    return nodes.find(n => (n.innerText || "").toLowerCase().includes(label.toLowerCase()));
  }

  function setPanelStatus(panel, status) {
    if (!panel) return;
    panel.setAttribute("data-claire-s5-status", status);

    let badge = panel.querySelector("[data-claire-s5-badge]");
    if (!badge) {
      badge = document.createElement("div");
      badge.setAttribute("data-claire-s5-badge", "true");
      badge.style.marginTop = "10px";
      badge.style.fontWeight = "700";
      panel.appendChild(badge);
    }

    badge.textContent = "Canonical Status: " + status;

    if (status === "wired_and_responding") {
      panel.setAttribute("data-claire-panel-live", "true");
    }
  }

  function render() {
    const mappings = [
      ["active route truth", reconciliation.routes.payloadStatus],
      ["runtime execution", reconciliation.routes.runtimeExecution],
      ["runtime state", reconciliation.routes.runtimeState],
      ["runtime propagation", reconciliation.routes.runtimePropagation],
      ["review queue", reconciliation.routes.reviewQueue],
      ["route owner", reconciliation.routes.routeOwnerRegistry],
      ["duplicate", reconciliation.routes.duplicateRouteFailTest]
    ];

    for (const [label, result] of mappings) {
      const panel = findPanel(label);
      const status = classify(result);
      reconciliation.panels[label] = status;
      setPanelStatus(panel, status);
    }

    window.ClaireSurfaceAvailabilityReconciliation = reconciliation;
  }

  async function run() {
    await collect();
    render();
    return reconciliation;
  }

  window.ClaireSurfaceAvailabilityReconciliationTools = {
    version: VERSION,
    run,
    reconciliation
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", run);
  } else {
    run();
  }

})();
