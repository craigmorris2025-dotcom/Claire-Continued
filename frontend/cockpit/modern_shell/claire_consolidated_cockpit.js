/*
 * Claire S50 consolidated cockpit shell.
 * Fetch-only and presentation-only.
 */

import { browseReadOnlyRoute } from "./claire_route_payload_browser.js";
import { CLAIRE_GOVERNED_WEB_PANEL_CONTRACT } from "./claire_governed_web_panels.js";

export const CLAIRE_CONSOLIDATED_COCKPIT_CONTRACT = Object.freeze({
  version: "v19.89.8-S50R1-R8",
  backendOwnsTruth: true,
  cockpitPresentationOnly: true,
  runtimeTruthMutationAllowed: false,
  operatorMutationEnabled: false,
  automaticUpdatesEnabled: false,
  autonomousExecutionEnabled: false,
  liveWebExecutionEnabled: false,
  responseMode: "read_only_artifact"
});

export async function loadConsolidatedReadOnlyRoute(path) {
  return browseReadOnlyRoute(path);
}

export function governedWebContract() {
  return CLAIRE_GOVERNED_WEB_PANEL_CONTRACT;
}
