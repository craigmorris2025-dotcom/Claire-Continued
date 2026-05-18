
// Claire Syntalion v19.89.8-S9
// Canonical Sidebar/System Synchronization
// Backend owns truth. Cockpit presentation only.

(function () {
  "use strict";

  const VERSION = "v19.89.8-S9";

  const ROUTES = {
    payloadStatus: "/dashboard/payload/status",
    runtimeState: "/system/runtime-state/summary",
    cockpitFetchMap: "/system/cockpit-fetch-map/summary"
  };

  const state = {
    version: VERSION,
    backend_owns_truth: true,
    cockpit_presentation_only: true,
    runtime_authority_expanded: false,
    safe_to_expand_runtime_authority: false,
    synchronized: false,
    canonical_runtime_state: "unavailable",
    sidebar_updates: [],
    route_data: {}
  };

  async function fetchJson(route) {
    try {
      const res = await fetch(route, {
        method: "GET",
        headers: { "Accept": "application/json" },
        cache: "no-store"
      });

      const text = await res.text();

      let data = null;

      try {
        data = JSON.parse(text);
      } catch (err) {
        data = { raw: text };
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
        route,
        error: String(err && err.message ? err.message : err)
      };
    }
  }

  async function collect() {
    const out = {};

    for (const [key, route] of Object.entries(ROUTES)) {
      out[key] = await fetchJson(route);
    }

    state.route_data = out;

    return out;
  }

  function canonicalize(routes) {
    if (!routes) return "unavailable";

    const payload = routes.payloadStatus;
    const runtime = routes.runtimeState;

    if (payload && payload.ok && runtime && runtime.ok) {
      return "live";
    }

    if ((payload && payload.ok) || (runtime && runtime.ok)) {
      return "degraded";
    }

    return "unavailable";
  }

  function candidateSidebarNodes() {
    return Array.from(document.querySelectorAll(
      "nav *, aside *, [class*='sidebar'] *, [id*='sidebar'] *"
    ));
  }

  function shouldReplace(text) {
    const lowered = text.toLowerCase();

    return (
      lowered.includes("connected") ||
      lowered.includes("available") ||
      lowered.includes("complete") ||
      lowered.includes("active") ||
      lowered.includes("healthy") ||
      lowered.includes("live") ||
      lowered.includes("degraded") ||
      lowered.includes("offline") ||
      lowered.includes("unavailable") ||
      lowered.includes("failed")
    );
  }

  function applySidebarState(canonicalState) {
    const updates = [];

    for (const node of candidateSidebarNodes()) {
      if (!node || node.children.length > 0) continue;

      const text = (node.innerText || "").trim();

      if (!text || text.length > 40) continue;

      if (!shouldReplace(text)) continue;

      const before = text;

      let after = canonicalState;

      if (canonicalState === "live") {
        after = "Live";
      } else if (canonicalState === "degraded") {
        after = "Degraded";
      } else {
        after = "Unavailable";
      }

      node.textContent = after;

      node.setAttribute(
        "data-claire-s9-synchronized",
        canonicalState
      );

      updates.push({
        before,
        after
      });
    }

    state.sidebar_updates = updates;
    state.synchronized = true;
  }

  function applyDocumentState(canonicalState) {
    document.documentElement.setAttribute(
      "data-claire-canonical-runtime-state",
      canonicalState
    );

    document.documentElement.setAttribute(
      "data-claire-runtime-authority-expanded",
      "false"
    );
  }

  async function run() {
    const routes = await collect();

    const canonicalState = canonicalize(routes);

    state.canonical_runtime_state = canonicalState;

    applySidebarState(canonicalState);

    applyDocumentState(canonicalState);

    window.ClaireCanonicalSidebarSynchronization = state;

    return state;
  }

  window.ClaireCanonicalSidebarSynchronizationTools = {
    version: VERSION,
    run,
    state
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", run);
  } else {
    run();
  }

  setInterval(run, 30000);
})();
