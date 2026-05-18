/* Claire Syntalion v19.89.8-A3 Canonical Cockpit Fetch Map Lock */
window.ClaireCanonicalFetchMapLock = {
  "version": "v19.89.8-A3",
  "backendOwnsTruth": true,
  "cockpitPresentationOnly": true,
  "frontendTruthAllowed": false,
  "approvedFetchRoutes": [
    "/dashboard/payload",
    "/dashboard/payload/status",
    "/runs/start",
    "/runtime/continuous/review-queue",
    "/runtime/continuous/status",
    "/system/duplicate-route-fail-test/summary",
    "/system/operator-controls/summary",
    "/system/operator-events/summary",
    "/system/project-inventory/summary",
    "/system/review-queue/summary",
    "/system/route-owner-registry/summary",
    "/system/runtime-execution/summary",
    "/system/runtime-propagation/summary",
    "/system/runtime-state/summary",
    "/universes"
  ],
  "canonicalFetchMapEndpoint": "/system/cockpit-fetch-map",
  "summaryEndpoint": "/system/cockpit-fetch-map/summary"
};
