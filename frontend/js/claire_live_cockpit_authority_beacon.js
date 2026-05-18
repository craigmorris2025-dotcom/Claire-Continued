
// Claire Syntalion v19.89.8-A6 SAFE
// Live Cockpit Authority Beacon.
// Frontend-only diagnostic. Backend owns truth. Runtime authority remains blocked.

(function () {
  "use strict";

  const VERSION = "v19.89.8-A6-SAFE";

  function listScripts() {
    return Array.from(document.scripts || []).map(function (s) {
      return s.src || s.getAttribute("src") || "[inline]";
    });
  }

  function listLinks() {
    return Array.from(document.querySelectorAll("link[href]") || []).map(function (l) {
      return l.href || l.getAttribute("href");
    });
  }

  function payload() {
    const loadedScripts = listScripts();

    return {
      version: VERSION,
      reported_at: new Date().toISOString(),
      backend_owns_truth: true,
      cockpit_presentation_only: true,
      frontend_truth_allowed: false,
      runtime_authority_expanded: false,
      autonomous_runtime_enabled: false,
      shell: {
        href: window.location.href,
        protocol: window.location.protocol,
        pathname: window.location.pathname,
        title: document.title || "",
        body_class: document.body ? Array.from(document.body.classList || []) : []
      },
      loaded_scripts: loadedScripts,
      loaded_links: listLinks(),
      detected: {
        canonical_fetch_client_present: !!window.ClaireCanonicalFetch,
        canonical_fetch_version: window.ClaireCanonicalFetch ? window.ClaireCanonicalFetch.version : null,
        active_authority_tools_present: !!window.ClaireActiveCockpitAuthorityTools,
        live_backend_widget_text_present: document.documentElement.innerText.indexOf("Claire Live Backend") >= 0,
        active_route_truth_text_present: document.documentElement.innerText.indexOf("Active Route Truth") >= 0,
        likely_api_js_loaded: loadedScripts.some(function (s) { return s.indexOf("api.js") >= 0; }),
        likely_platform_js_loaded: loadedScripts.some(function (s) { return s.indexOf("platform.js") >= 0; }),
        likely_payload_bridge_loaded: loadedScripts.some(function (s) {
          const low = String(s).toLowerCase();
          return low.indexOf("payload") >= 0 || low.indexOf("bridge") >= 0;
        }),
        likely_canonical_fetch_loaded: loadedScripts.some(function (s) {
          return String(s).indexOf("claire_canonical_fetch_client.js") >= 0;
        }),
        likely_live_beacon_loaded: loadedScripts.some(function (s) {
          return String(s).indexOf("claire_live_cockpit_authority_beacon.js") >= 0;
        })
      }
    };
  }

  async function probeBackend() {
    const out = {};
    const routes = [
      "/dashboard/payload",
      "/dashboard/payload/status",
      "/system/cockpit-fetch-map/summary",
      "/system/route-owner-registry/summary",
      "/system/duplicate-route-fail-test/summary"
    ];

    for (const route of routes) {
      try {
        const res = await fetch(route, {
          method: "GET",
          headers: { "Accept": "application/json" },
          cache: "no-store"
        });
        out[route] = {
          ok: res.ok,
          status: res.status
        };
      } catch (err) {
        out[route] = {
          ok: false,
          error: String(err && err.message ? err.message : err)
        };
      }
    }

    return out;
  }

  async function run() {
    const p = payload();
    p.backend_probe = await probeBackend();
    window.ClaireLiveCockpitAuthorityBeacon = p;
    window.dispatchEvent(new CustomEvent("claire:live-cockpit-authority-beacon-safe", { detail: p }));
    return p;
  }

  window.ClaireLiveCockpitAuthorityBeaconTools = {
    version: VERSION,
    payload: payload,
    probeBackend: probeBackend,
    run: run
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", run);
  } else {
    run();
  }

  setInterval(run, 60000);
})();
