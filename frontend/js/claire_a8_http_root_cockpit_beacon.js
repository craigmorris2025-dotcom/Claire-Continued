

(function () {
  "use strict";
  var VERSION = "v19.89.8-A8";

  function listScripts() {
    return Array.from(document.scripts || []).map(function (s) {
      return s.src || s.getAttribute("src") || "[inline:" + (s.id || "anonymous") + "]";
    });
  }

  function payload() {
    var loadedScripts = listScripts();
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
      detected: {
        http_origin: window.location.protocol === "http:" || window.location.protocol === "https:",
        active_route_truth_text_present: document.documentElement.innerText.indexOf("Active Route Truth") >= 0,
        live_backend_widget_text_present: document.documentElement.innerText.indexOf("Claire Live Backend") >= 0,
        canonical_fetch_client_present: !!window.ClaireCanonicalFetch,
        likely_payload_bridge_loaded: loadedScripts.some(function (s) {
          var low = String(s).toLowerCase();
          return low.indexOf("payload") >= 0 || low.indexOf("bridge") >= 0;
        }),
        a8_inline_beacon_loaded: true
      }
    };
  }

  async function probeBackend() {
    var routes = [
      "/dashboard/payload",
      "/dashboard/payload/status",
      "/system/cockpit-fetch-map/summary",
      "/system/route-owner-registry/summary",
      "/system/duplicate-route-fail-test/summary"
    ];
    var out = {};
    for (var i = 0; i < routes.length; i++) {
      var route = routes[i];
      try {
        var res = await fetch(route, {
          method: "GET",
          headers: { "Accept": "application/json" },
          cache: "no-store"
        });
        out[route] = { ok: res.ok, status: res.status };
      } catch (err) {
        out[route] = { ok: false, error: String(err && err.message ? err.message : err) };
      }
    }
    return out;
  }

  async function run() {
    var p = payload();
    p.backend_probe = await probeBackend();
    window.ClaireLiveCockpitAuthorityBeacon = p;
    window.ClaireA8HttpRootCockpitBeacon = p;
    window.dispatchEvent(new CustomEvent("claire:a8-http-root-cockpit-beacon", { detail: p }));
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
})();

