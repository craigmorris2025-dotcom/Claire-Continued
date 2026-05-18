/*
 * Claire S56 output package browser.
 * Presentation-only review bundle renderer.
 */

export const CLAIRE_OUTPUT_PACKAGE_BROWSER_CONTRACT = Object.freeze({
  version: "v19.89.8-S56R1-R8",
  backendOwnsTruth: true,
  cockpitPresentationOnly: true,
  presentationOnly: true,
  runtimeTruthMutationAllowed: false,
  runtimeTruthWriteAllowed: false,
  operatorMutationEnabled: false,
  automaticUpdatesEnabled: false,
  autonomousExecutionEnabled: false,
  manualPromotionRequired: true,
  quarantineRequired: true,
  responseMode: "read_only_artifact"
});

export function createOutputPackageCard(bundle) {
  const article = document.createElement("article");
  article.className = "claire-output-package-card";
  article.dataset.routeId = bundle.route_id;
  article.dataset.runtimeTruthMutationAllowed = "false";
  article.dataset.operatorMutationEnabled = "false";
  const title = document.createElement("h3");
  title.textContent = bundle.bundle_id;
  const state = document.createElement("p");
  state.textContent = `State: ${bundle.bundle_state}; Review required: ${bundle.review_required}`;
  article.appendChild(title);
  article.appendChild(state);
  return article;
}
