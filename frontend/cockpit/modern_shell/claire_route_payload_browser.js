/*
 * Claire S48 route/payload browser.
 * Read-only route browser. No runtime truth mutation.
 */

export const CLAIRE_ROUTE_PAYLOAD_BROWSER_CONTRACT = Object.freeze({
  version: "v19.89.8-S48R1-R8",
  backendOwnsTruth: true,
  cockpitPresentationOnly: true,
  runtimeTruthMutationAllowed: false,
  operatorMutationEnabled: false,
  automaticUpdatesEnabled: false,
  autonomousExecutionEnabled: false,
  responseMode: "read_only_artifact"
});

export async function browseReadOnlyRoute(path) {
  const response = await fetch(path, {
    method: "GET",
    cache: "no-store",
    headers: { "Accept": "application/json" }
  });
  const payload = await response.json();
  return {
    path,
    status: response.status,
    available: response.ok,
    payload,
    runtimeTruthMutationAllowed: false,
    operatorMutationEnabled: false,
    responseMode: "read_only_artifact"
  };
}
