// Claire Syntalion v19.89.8-A5
// Active Cockpit Authority Surface Reconciliation
// Cockpit presentation only. Backend owns truth. Runtime authority remains blocked.

(function () {
  "use strict";

  const VERSION = "v19.89.8-A5";

  function now() {
    return new Date().toISOString();
  }

  function scriptSources() {
    return Array.from(document.scripts || []).map(function (s) {
      return s.src || s.getAttribute("src") || "[inline]";
    });
  }

  function linkSources() {
    return Array.from(document.querySelectorAll("link[href]")).map(function (l) {
      return l.href || l.getAttribute("href");
    });
  }

  function shellIdentity() {
    return {
      href: window.location.href,
      pathname: window.location.pathname,
      title: document.title || "",
      bodyClasses: document.body ? Array.from(document.body.classList || []) : [],
      hasCockpitShellPath: String(window.location.href).indexOf("cockpit_shell") >= 0,
      hasCommandCenterPath: String(window.location.href).indexOf("command_center") >= 0,
      hasFileProtocol: String(window.location.protocol) === "file:",
      protocol: window.location.protocol
    };
  }

  async function tryJson(path) {
    try {
      const res = await fetch(path, {
        method: "GET",
        headers: { "Accept": "application/json" },
        cache: "no-store"
      });
      if (!res.ok) {
        return { ok: false, status: res.status, error: "http_" + res.status };
      }
      return { ok: true, status: res.status, data: await res.json() };
    } catch (err) {
      return { ok: false, status: null, error: String(err && err.message ? err.message : err) };
    }
  }

  function detectSurfaces() {
    const scripts = scriptSources();
    const html = document.documentElement ? document.documentElement.outerHTML : "";

    return {
      canonicalFetchClientPresent: !!window.ClaireCanonicalFetch,
      canonicalFetchVersion: window.ClaireCanonicalFetch ? window.ClaireCanonicalFetch.version : null,
      liveBackendWidgetPresent: html.indexOf("Claire Live Backend") >= 0,
      activeRouteTruthTextPresent: html.indexOf("Active Route Truth") >= 0,
      synchronizationProofTextPresent: html.indexOf("SYNCHRONIZATION PROOF") >= 0,
      loadedScripts: scripts,
      loadedLinks: linkSources(),
      likelyLegacyApiJsLoaded: scripts.some(function (s) { return s.indexOf("api.js") >= 0; }),
      likelyPlatformJsLoaded: scripts.some(function (s) { return s.indexOf("platform.js") >= 0; }),
      likelyCanonicalFetchLoaded: scripts.some(function (s) { return s.indexOf("claire_canonical_fetch_client.js") >= 0; }),
      likelyPayloadBridgeLoaded: scripts.some(function (s) { return s.indexOf("payload") >= 0 || s.indexOf("bridge") >= 0; })
    };
  }

  async function buildAuthorityReport() {
    const report = {
      version: VERSION,
      checked_at: now(),
      backend_owns_truth: true,
      cockpit_presentation_only: true,
      frontend_truth_allowed: false,
      runtime_authority_expanded: false,
      autonomous_runtime_enabled: false,
      shell: shellIdentity(),
      surfaces: detectSurfaces(),
      backend: {},
      mismatch_reason: null,
      recommended_next_state: "continue_authority_reconciliation"
    };

    report.backend.dashboard_payload = await tryJson("/dashboard/payload");
    report.backend.dashboard_payload_status = await tryJson("/dashboard/payload/status");
    report.backend.cockpit_fetch_map_summary = await tryJson("/system/cockpit-fetch-map/summary");
    report.backend.route_owner_registry_summary = await tryJson("/system/route-owner-registry/summary");
    report.backend.duplicate_route_fail_test_summary = await tryJson("/system/duplicate-route-fail-test/summary");

    const payloadOk = !!(report.backend.dashboard_payload && report.backend.dashboard_payload.ok);
    const fetchMapOk = !!(report.backend.cockpit_fetch_map_summary && report.backend.cockpit_fetch_map_summary.ok);
    const canonicalClient = !!report.surfaces.canonicalFetchClientPresent;

    if (payloadOk && !canonicalClient) {
      report.mismatch_reason = "backend_payload_visible_but_canonical_fetch_client_not_loaded_in_active_shell";
    } else if (payloadOk && canonicalClient && fetchMapOk) {
      report.mismatch_reason = "active_shell_has_backend_and_canonical_client; backend_fetch_map_may_be_scanning_static_files_or_legacy_surface";
    } else if (!payloadOk && canonicalClient) {
      report.mismatch_reason = "canonical_client_loaded_but_backend_payload_unavailable_from_active_shell";
    } else {
      report.mismatch_reason = "active_shell_authority_unresolved";
    }

    window.ClaireActiveCockpitAuthority = report;
    window.dispatchEvent(new CustomEvent("claire:active-cockpit-authority-report", { detail: report }));
    return report;
  }

  function renderReport(report) {
    const target =
      document.querySelector("[data-claire-active-authority-report]") ||
      document.getElementById("claire-active-authority-report") ||
      document.querySelector("[data-claire-route-truth-json]");

    if (!target) return;

    const compact = {
      status: report.backend.dashboard_payload && report.backend.dashboard_payload.ok ? "backend_payload_connected" : "backend_payload_unavailable",
      shell_protocol: report.shell.protocol,
      shell_pathname: report.shell.pathname,
      canonical_fetch_client_present: report.surfaces.canonicalFetchClientPresent,
      canonical_fetch_version: report.surfaces.canonicalFetchVersion,
      active_scripts_count: report.surfaces.loadedScripts.length,
      payload_bridge_loaded: report.surfaces.likelyPayloadBridgeLoaded,
      legacy_api_js_loaded: report.surfaces.likelyLegacyApiJsLoaded,
      legacy_platform_js_loaded: report.surfaces.likelyPlatformJsLoaded,
      mismatch_reason: report.mismatch_reason,
      runtime_authority_expanded: false
    };

    target.textContent = JSON.stringify(compact, null, 2);
  }

  async function run() {
    const report = await buildAuthorityReport();
    renderReport(report);
    return report;
  }

  window.ClaireActiveCockpitAuthorityTools = {
    version: VERSION,
    run,
    buildAuthorityReport
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", run);
  } else {
    run();
  }
})();
