// Claire Syntalion v19.89.8-S6
// File-Origin Canonical API Bridge
// Visible dashboard remains file:///. Approved backend fetches route to http://127.0.0.1:8000.
// Backend owns truth. Cockpit presentation only. Runtime authority remains blocked.

(function () {
  "use strict";

  const VERSION = "v19.89.8-S6";
  const BACKEND_ORIGIN = "http://127.0.0.1:8000";

  const APPROVED_PREFIXES = [
    "/dashboard/",
    "/system/",
    "/api/dashboard/",
    "/runtime/",
    "/runs/",
    "/docs",
    "/openapi.json"
  ];

  const APPROVED_EXACT = [
    "/",
    "/dashboard",
    "/dashboard/payload",
    "/dashboard/payload/status",
    "/system/cockpit-fetch-map/summary",
    "/system/route-owner-registry/summary",
    "/system/duplicate-route-fail-test/summary",
    "/system/runtime-execution/summary",
    "/system/runtime-state/summary",
    "/system/runtime-propagation/summary",
    "/system/review-queue/summary"
  ];

  const state = {
    version: VERSION,
    backend_origin: BACKEND_ORIGIN,
    file_origin_bridge_active: true,
    backend_owns_truth: true,
    cockpit_presentation_only: true,
    frontend_truth_allowed: false,
    runtime_authority_expanded: false,
    safe_to_expand_runtime_authority: false,
    rewrites: [],
    blocked: []
  };

  function isApprovedBackendPath(path) {
    if (!path || typeof path !== "string") return false;
    if (APPROVED_EXACT.includes(path)) return true;
    return APPROVED_PREFIXES.some(function (prefix) {
      return path.startsWith(prefix);
    });
  }

  function normalizeFetchInput(input) {
    if (typeof input === "string") {
      return { url: input, kind: "string" };
    }
    if (input && typeof input.url === "string") {
      return { url: input.url, kind: "request" };
    }
    return { url: null, kind: "unknown" };
  }

  function shouldRewrite(url) {
    if (!url || typeof url !== "string") return false;

    // Already absolute HTTP/S: leave alone.
    if (url.startsWith("http://") || url.startsWith("https://")) return false;

    // Only backend-like absolute paths.
    if (!url.startsWith("/")) return false;

    return isApprovedBackendPath(url);
  }

  function rewriteUrl(url) {
    if (!shouldRewrite(url)) return url;
    return BACKEND_ORIGIN + url;
  }

  const nativeFetch = window.fetch.bind(window);

  window.fetch = function claireS6CanonicalFetchBridge(input, init) {
    const info = normalizeFetchInput(input);

    if (info.kind === "string" && shouldRewrite(info.url)) {
      const rewritten = rewriteUrl(info.url);
      state.rewrites.push({
        at: new Date().toISOString(),
        from: info.url,
        to: rewritten
      });
      return nativeFetch(rewritten, init);
    }

    if (info.kind === "request" && shouldRewrite(info.url)) {
      const rewritten = rewriteUrl(info.url);
      state.rewrites.push({
        at: new Date().toISOString(),
        from: info.url,
        to: rewritten
      });
      const cloned = new Request(rewritten, input);
      return nativeFetch(cloned, init);
    }

    return nativeFetch(input, init);
  };

  async function probe() {
    const checks = [
      "/dashboard/payload/status",
      "/system/runtime-execution/summary",
      "/system/runtime-state/summary",
      "/system/review-queue/summary",
      "/system/cockpit-fetch-map/summary"
    ];

    const results = {};
    for (const route of checks) {
      try {
        const response = await fetch(route, {
          method: "GET",
          headers: { "Accept": "application/json" },
          cache: "no-store"
        });
        results[route] = { ok: response.ok, status: response.status };
      } catch (err) {
        results[route] = {
          ok: false,
          error: String(err && err.message ? err.message : err)
        };
      }
    }

    state.last_probe_at = new Date().toISOString();
    state.last_probe = results;
    return state;
  }

  window.ClaireFileOriginCanonicalApiBridge = state;
  window.ClaireFileOriginCanonicalApiBridgeTools = {
    version: VERSION,
    probe: probe,
    state: state
  };

  document.documentElement.setAttribute("data-claire-file-origin-api-bridge", VERSION);
  document.documentElement.setAttribute("data-claire-runtime-authority-expanded", "false");

  // Probe once, then allow S4/S5 and existing panels to refresh normally.
  probe();
})();
