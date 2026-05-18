/*
 * Claire modern cockpit shell.
 * Fetch-only, presentation-only, read-only dashboard bridge.
 */

export const CLAIRE_MODERN_COCKPIT_CONTRACT = Object.freeze({
  version: "v19.89.8-S46R5-S47R8",
  backendOwnsTruth: true,
  cockpitPresentationOnly: true,
  presentationOnly: true,
  runtimeTruthMutationAllowed: false,
  runtimeMutationAllowed: false,
  operatorMutationEnabled: false,
  automaticUpdatesEnabled: false,
  autonomousExecutionEnabled: false,
  browserExecutionEnabled: false,
  responseMode: "read_only_artifact"
});

export function createReadOnlyCard(title, payload) {
  const card = document.createElement("article");
  card.className = "claire-modern-card";
  card.dataset.responseMode = "read_only_artifact";
  card.dataset.runtimeTruthMutationAllowed = "false";
  card.dataset.operatorMutationEnabled = "false";

  const heading = document.createElement("h3");
  heading.textContent = title;

  const pre = document.createElement("pre");
  pre.textContent = JSON.stringify(payload, null, 2);

  card.appendChild(heading);
  card.appendChild(pre);
  return card;
}

export async function fetchBackendTruth(path) {
  const response = await fetch(path, {
    method: "GET",
    cache: "no-store",
    headers: { "Accept": "application/json" }
  });
  return {
    path,
    ok: response.ok,
    status: response.status,
    payload: await response.json(),
    presentationOnly: true,
    runtimeTruthMutationAllowed: false,
    operatorMutationEnabled: false,
    responseMode: "read_only_artifact"
  };
}
