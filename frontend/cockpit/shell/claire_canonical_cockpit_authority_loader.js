// Claire Syntalion v19.89.8-S3
// Canonical Cockpit Authority Loader Lock
// Backend owns truth. Cockpit presentation only. Runtime authority remains blocked.

(function () {
  "use strict";

  const VERSION = "v19.89.8-S3";

  const manifest = {
    version: VERSION,
    backend_owns_truth: true,
    cockpit_presentation_only: true,
    frontend_truth_allowed: false,
    runtime_authority_expanded: false,
    safe_to_expand_runtime_authority: false,
    active_shell: "frontend/cockpit/shell/cockpit_shell.html",
    active_chain: [
      "frontend/cockpit/shell/cockpit_shell.html",
      "frontend/cockpit/shell/claire_canonical_fetch_map_lock.js",
      "frontend/js/claire_canonical_fetch_client.js",
      "frontend/cockpit/shared/canonical_payload_adapter.js",
      "frontend/cockpit/shell/claire_cockpit_runtime_surface.js",
      "frontend/cockpit/shell/claire_runtime_execution_surface.js",
      "frontend/cockpit/shell/claire_runtime_state_surface.js",
      "frontend/cockpit/shell/claire_review_queue_surface.js",
      "frontend/cockpit/shell/claire_active_route_truth_panel.js"
    ],
    canonical_routes: [
      "/dashboard/payload",
      "/dashboard/payload/status",
      "/system/cockpit-fetch-map/summary",
      "/system/route-owner-registry/summary",
      "/system/duplicate-route-fail-test/summary",
      "/system/runtime-execution/summary",
      "/system/runtime-state/summary",
      "/system/runtime-propagation/summary",
      "/system/review-queue/summary"
    ],
    inactive_compatibility_mode: "manifest_only_do_not_delete"
  };

  function expose() {
    window.ClaireCanonicalCockpitAuthority = manifest;
    window.ClaireRuntimeAuthorityExpanded = false;
    document.documentElement.setAttribute("data-claire-canonical-cockpit", VERSION);
    document.documentElement.setAttribute("data-claire-runtime-authority-expanded", "false");
    return manifest;
  }

  window.ClaireCanonicalCockpitAuthorityTools = {
    version: VERSION,
    expose: expose,
    manifest: manifest
  };

  expose();
})();
