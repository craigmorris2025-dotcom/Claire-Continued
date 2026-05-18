// Claire Syntalion v19.89.8-S4
// Canonical Surface Wiring Pass
// Backend owns truth. Cockpit presentation only. Runtime authority remains blocked.

(function () {
  "use strict";

  const VERSION = "v19.89.8-S4";

  const ROUTES = {
    payload: "/dashboard/payload",
    payloadStatus: "/dashboard/payload/status",
    runtimeExecution: "/system/runtime-execution/summary",
    runtimeState: "/system/runtime-state/summary",
    runtimePropagation: "/system/runtime-propagation/summary",
    reviewQueue: "/system/review-queue/summary",
    routeOwnerRegistry: "/system/route-owner-registry/summary",
    duplicateRouteFailTest: "/system/duplicate-route-fail-test/summary",
    cockpitFetchMap: "/system/cockpit-fetch-map/summary"
  };

  const state = {
    version: VERSION,
    backend_owns_truth: true,
    cockpit_presentation_only: true,
    frontend_truth_allowed: false,
    runtime_authority_expanded: false,
    safe_to_expand_runtime_authority: false,
    checked_at: null,
    routes: {},
    panels: {}
  };

  async function getJson(route) {
    try {
      const response = await fetch(route, {
        method: "GET",
        headers: { "Accept": "application/json" },
        cache: "no-store"
      });
      const text = await response.text();
      let data = null;
      try {
        data = JSON.parse(text);
      } catch (err) {
        data = { raw: text };
      }
      return { ok: response.ok, status: response.status, route, data };
    } catch (err) {
      return {
        ok: false,
        status: null,
        route,
        error: String(err && err.message ? err.message : err)
      };
    }
  }

  async function collect() {
    const entries = Object.entries(ROUTES);
    const results = {};
    for (const [key, route] of entries) {
      results[key] = await getJson(route);
    }
    state.checked_at = new Date().toISOString();
    state.routes = results;
    return state;
  }

  function normalizeText(value) {
    if (value === null || value === undefined) return "";
    if (typeof value === "string") return value;
    try { return JSON.stringify(value, null, 2); } catch (err) { return String(value); }
  }

  function setTextBySelectors(selectors, value) {
    for (const selector of selectors) {
      const node = document.querySelector(selector);
      if (node) {
        node.textContent = value;
        return true;
      }
    }
    return false;
  }

  function findPanelByText(textNeedles) {
    const needles = Array.isArray(textNeedles) ? textNeedles : [textNeedles];
    const candidates = Array.from(document.querySelectorAll("section, article, div"));
    return candidates.find(function (node) {
      const text = node.innerText || "";
      return needles.every(function (needle) {
        return text.toLowerCase().indexOf(String(needle).toLowerCase()) >= 0;
      });
    });
  }

  function writePre(panel, payload) {
    if (!panel) return false;
    let pre = panel.querySelector("pre[data-claire-s4-canonical-output]");
    if (!pre) {
      pre = document.createElement("pre");
      pre.setAttribute("data-claire-s4-canonical-output", "true");
      pre.style.whiteSpace = "pre-wrap";
      pre.style.marginTop = "14px";
      pre.style.maxHeight = "340px";
      pre.style.overflow = "auto";
      panel.appendChild(pre);
    }
    pre.textContent = normalizeText(payload);
    return true;
  }

  function statusFromRoute(routeResult) {
    if (!routeResult) return "unavailable";
    if (routeResult.ok) return "connected";
    return "unavailable";
  }

  function compactRoute(routeResult) {
    if (!routeResult) return { ok: false, status: null };
    return {
      ok: !!routeResult.ok,
      status: routeResult.status,
      route: routeResult.route,
      data: routeResult.data
    };
  }

  function renderActiveRouteTruth() {
    const panel = findPanelByText(["Active Route Truth"]);
    if (!panel) return false;

    const fetchMap = state.routes.cockpitFetchMap || {};
    const registry = state.routes.routeOwnerRegistry || {};
    const duplicates = state.routes.duplicateRouteFailTest || {};
    const payloadStatus = state.routes.payloadStatus || {};

    const summary = {
      version: VERSION,
      status: statusFromRoute(payloadStatus),
      payload: statusFromRoute(payloadStatus),
      cockpit_shell: state.routes.cockpitFetchMap && state.routes.cockpitFetchMap.ok ? "canonical-bound" : "unavailable",
      duplicates: duplicates.ok ? "checked" : "unavailable",
      backend_owns_truth: true,
      cockpit_presentation_only: true,
      runtime_authority_expanded: false,
      safe_to_expand_runtime_authority: false,
      route_status: {
        payload_status: payloadStatus.status || null,
        cockpit_fetch_map: fetchMap.status || null,
        route_owner_registry: registry.status || null,
        duplicate_route_fail_test: duplicates.status || null
      },
      data: {
        payload_status: payloadStatus.data || null,
        cockpit_fetch_map: fetchMap.data || null,
        route_owner_registry: registry.data || null,
        duplicate_route_fail_test: duplicates.data || null
      }
    };

    writePre(panel, summary);
    state.panels.activeRouteTruth = true;
    return true;
  }

  function renderRuntimeExecution() {
    const panel = findPanelByText(["Runtime Execution"]);
    if (!panel) return false;
    writePre(panel, {
      version: VERSION,
      panel: "runtime_execution",
      runtime_authority_expanded: false,
      safe_to_expand_runtime_authority: false,
      result: compactRoute(state.routes.runtimeExecution)
    });
    state.panels.runtimeExecution = true;
    return true;
  }

  function renderRuntimeState() {
    const panel = findPanelByText(["Runtime State"]);
    if (!panel) return false;
    writePre(panel, {
      version: VERSION,
      panel: "runtime_state",
      runtime_authority_expanded: false,
      safe_to_expand_runtime_authority: false,
      result: compactRoute(state.routes.runtimeState)
    });
    state.panels.runtimeState = true;
    return true;
  }

  function renderReviewQueue() {
    const panel = findPanelByText(["Review Queue"]);
    if (!panel) return false;
    writePre(panel, {
      version: VERSION,
      panel: "review_queue",
      runtime_authority_expanded: false,
      safe_to_expand_runtime_authority: false,
      result: compactRoute(state.routes.reviewQueue)
    });
    state.panels.reviewQueue = true;
    return true;
  }

  function renderRouteOwnerRegistry() {
    const panel = findPanelByText(["Route Owner"]);
    if (!panel) return false;
    writePre(panel, {
      version: VERSION,
      panel: "route_owner_registry",
      runtime_authority_expanded: false,
      safe_to_expand_runtime_authority: false,
      result: compactRoute(state.routes.routeOwnerRegistry)
    });
    state.panels.routeOwnerRegistry = true;
    return true;
  }

  function renderDuplicateRouteFailTest() {
    const panel = findPanelByText(["Duplicate"]);
    if (!panel) return false;
    writePre(panel, {
      version: VERSION,
      panel: "duplicate_route_fail_test",
      runtime_authority_expanded: false,
      safe_to_expand_runtime_authority: false,
      result: compactRoute(state.routes.duplicateRouteFailTest)
    });
    state.panels.duplicateRouteFailTest = true;
    return true;
  }

  function renderRuntimePropagation() {
    const panel = findPanelByText(["Runtime Propagation"]);
    if (!panel) return false;
    writePre(panel, {
      version: VERSION,
      panel: "runtime_propagation",
      runtime_authority_expanded: false,
      safe_to_expand_runtime_authority: false,
      result: compactRoute(state.routes.runtimePropagation)
    });
    state.panels.runtimePropagation = true;
    return true;
  }

  function suppressFalseOfflineText() {
    // Conservative: only add a data flag; do not mass-edit visual design.
    document.documentElement.setAttribute("data-claire-s4-canonical-wired", "true");
    document.documentElement.setAttribute("data-claire-runtime-authority-expanded", "false");
  }

  function renderAll() {
    state.panels = {};
    renderActiveRouteTruth();
    renderRuntimeExecution();
    renderRuntimeState();
    renderReviewQueue();
    renderRouteOwnerRegistry();
    renderDuplicateRouteFailTest();
    renderRuntimePropagation();
    suppressFalseOfflineText();
    window.ClaireCanonicalSurfaceWiring = state;
    return state;
  }

  async function run() {
    await collect();
    renderAll();
    return state;
  }

  window.ClaireCanonicalSurfaceWiringTools = {
    version: VERSION,
    routes: ROUTES,
    state,
    collect,
    renderAll,
    run
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", run);
  } else {
    run();
  }

  setInterval(run, 30000);
})();
