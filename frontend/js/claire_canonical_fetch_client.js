// Claire Syntalion v19.89.8-A4
// Canonical cockpit fetch client.
// Backend owns truth. Cockpit presentation only.
// Runtime expansion remains blocked until authority/cockpit reconciliation passes.

(function () {
  "use strict";

  const CANONICAL_ROUTES = [
    "/dashboard/payload",
    "/dashboard/payload/status",
    "/system/runtime-execution/summary",
    "/system/runtime-state/summary",
    "/system/runtime-propagation/summary",
    "/system/review-queue/summary",
    "/system/route-owner-registry/summary",
    "/system/duplicate-route-fail-test/summary"
  ];

  const LEGACY_ROUTE_MAP = {
    "/api/command": "/dashboard/payload",
    "/api/platform/status": "/dashboard/payload/status",
    "/api/platform/resolve": "/system/runtime-state/summary"
  };

  const state = {
    version: "v19.89.8-A4",
    canonicalRoutes: CANONICAL_ROUTES.slice(),
    legacyRouteMap: Object.assign({}, LEGACY_ROUTE_MAP),
    lastResults: {},
    failures: {},
    fallbackUsed: {},
    runtimeAuthorityExpanded: false,
    autonomousRuntimeEnabled: false
  };

  function sameOriginUrl(path) {
    if (!path || typeof path !== "string") {
      throw new Error("Canonical fetch path must be a string.");
    }
    if (!path.startsWith("/")) {
      throw new Error("Canonical fetch path must be same-origin absolute.");
    }
    return path;
  }

  async function fetchJson(path, options) {
    const url = sameOriginUrl(path);
    const response = await fetch(url, Object.assign({
      method: "GET",
      headers: { "Accept": "application/json" },
      cache: "no-store"
    }, options || {}));

    if (!response.ok) {
      throw new Error("Canonical route " + url + " returned " + response.status);
    }

    const data = await response.json();
    state.lastResults[url] = {
      ok: true,
      at: new Date().toISOString(),
      status: response.status
    };
    return data;
  }

  async function canonical(path, options) {
    if (!CANONICAL_ROUTES.includes(path)) {
      state.failures[path] = {
        ok: false,
        at: new Date().toISOString(),
        reason: "route_not_approved_for_cockpit_fetch"
      };
      throw new Error("Cockpit fetch blocked: " + path + " is not an approved canonical route.");
    }
    return fetchJson(path, options);
  }

  async function fetchLegacy(legacyPath, options) {
    const canonicalPath = LEGACY_ROUTE_MAP[legacyPath];
    if (!canonicalPath) {
      state.failures[legacyPath] = {
        ok: false,
        at: new Date().toISOString(),
        reason: "legacy_route_not_mapped"
      };
      throw new Error("Legacy cockpit fetch blocked: " + legacyPath + " is not mapped to a canonical route.");
    }

    try {
      return await canonical(canonicalPath, options);
    } catch (canonicalError) {
      state.fallbackUsed[legacyPath] = {
        canonical: canonicalPath,
        at: new Date().toISOString(),
        reason: String(canonicalError && canonicalError.message ? canonicalError.message : canonicalError)
      };

      const response = await fetch(sameOriginUrl(legacyPath), Object.assign({
        method: "GET",
        headers: { "Accept": "application/json" },
        cache: "no-store"
      }, options || {}));

      if (!response.ok) {
        throw new Error("Legacy fallback " + legacyPath + " returned " + response.status);
      }
      return response.json();
    }
  }

  async function loadRequiredSummaries() {
    const out = {};
    for (const route of CANONICAL_ROUTES) {
      try {
        out[route] = { ok: true, data: await canonical(route) };
      } catch (err) {
        out[route] = { ok: false, error: String(err && err.message ? err.message : err) };
      }
    }
    return out;
  }

  window.ClaireCanonicalFetch = {
    version: state.version,
    state,
    routes: CANONICAL_ROUTES.slice(),
    legacyRouteMap: Object.assign({}, LEGACY_ROUTE_MAP),
    canonical,
    fetchLegacy,
    loadRequiredSummaries
  };

  window.dispatchEvent(new CustomEvent("claire:canonical-fetch-ready", {
    detail: { version: state.version, routeCount: CANONICAL_ROUTES.length }
  }));
})();
