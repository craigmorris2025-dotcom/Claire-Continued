/*
 * Claire S45 cockpit bridge.
 *
 * Presentation-only bridge asset.
 * It fetches backend-owned read-only payloads and renders operator cards.
 * It does not mutate runtime truth, does not execute autonomous actions,
 * does not perform automatic updates, and does not run browser automation.
 */

export const S45_COCKPIT_BRIDGE_CONTRACT = Object.freeze({
  version: "v19.89.8-S45R1-R8",
  presentationOnly: true,
  backendOwnsTruth: true,
  runtimeTruthMutationAllowed: false,
  operatorMutationEnabled: false,
  autonomousExecutionEnabled: false,
  automaticUpdatesEnabled: false,
  browserExecutionEnabled: false,
  responseMode: "read_only_artifact"
});

export async function fetchReadOnlySurface(fetchPath) {
  const response = await fetch(fetchPath, {
    method: "GET",
    cache: "no-store",
    headers: { "Accept": "application/json" }
  });

  return {
    path: fetchPath,
    status: response.status,
    ok: response.ok,
    payload: await response.json(),
    presentationOnly: true,
    runtimeTruthMutationAllowed: false,
    operatorMutationEnabled: false,
    responseMode: "read_only_artifact"
  };
}

export function renderOperatorCard(target, surfaceResult) {
  if (!target) {
    return {
      rendered: false,
      reason: "missing_target",
      presentationOnly: true,
      runtimeTruthMutationAllowed: false
    };
  }

  const card = document.createElement("section");
  card.className = "s45-operator-card";
  card.dataset.responseMode = "read_only_artifact";
  card.dataset.runtimeTruthMutationAllowed = "false";
  card.dataset.operatorMutationEnabled = "false";

  const title = document.createElement("h3");
  title.textContent = surfaceResult.path;

  const state = document.createElement("p");
  state.textContent = surfaceResult.ok ? "Available" : "Unavailable";

  const pre = document.createElement("pre");
  pre.textContent = JSON.stringify(surfaceResult.payload, null, 2);

  card.appendChild(title);
  card.appendChild(state);
  card.appendChild(pre);
  target.appendChild(card);

  return {
    rendered: true,
    presentationOnly: true,
    runtimeTruthMutationAllowed: false,
    operatorMutationEnabled: false,
    responseMode: "read_only_artifact"
  };
}
