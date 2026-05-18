/*
 * Claire S53 useful output browser.
 * Presentation-only useful output card renderer.
 */

export const CLAIRE_USEFUL_OUTPUT_BROWSER_CONTRACT = Object.freeze({
  version: "v19.89.8-S53R1-R8",
  backendOwnsTruth: true,
  cockpitPresentationOnly: true,
  presentationOnly: true,
  runtimeTruthMutationAllowed: false,
  runtimeMutationAllowed: false,
  operatorMutationEnabled: false,
  automaticUpdatesEnabled: false,
  autonomousExecutionEnabled: false,
  manualPromotionRequired: true,
  quarantineRequired: true,
  responseMode: "read_only_artifact"
});

export function createUsefulOutputCard(card) {
  const article = document.createElement("article");
  article.className = "claire-useful-output-card";
  article.dataset.routeId = card.route_id;
  article.dataset.responseMode = "read_only_artifact";
  article.dataset.runtimeTruthMutationAllowed = "false";
  article.dataset.operatorMutationEnabled = "false";

  const title = document.createElement("h3");
  title.textContent = card.title;

  const headline = document.createElement("strong");
  headline.textContent = card.headline;

  const summary = document.createElement("p");
  summary.textContent = card.summary;

  const meta = document.createElement("p");
  meta.textContent = `Terminal: ${card.terminal_state} | Review: ${card.review_state}`;

  article.appendChild(title);
  article.appendChild(headline);
  article.appendChild(summary);
  article.appendChild(meta);

  return article;
}
