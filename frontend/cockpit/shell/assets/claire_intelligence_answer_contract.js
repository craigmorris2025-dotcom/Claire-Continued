/*
Claire Intelligence Answer Contract — S450-S456
Presentation-only cockpit helper. Backend owns truth.
*/

(function () {
  "use strict";

  const ClaireIntelligenceAnswerContractVersion = "v19.89.8-S450-S456";

  const ClaireIntelligenceAnswerAuthority = Object.freeze({
    backendOwnsTruth: true,
    cockpitPresentationOnly: true,
    runtimeTruthMutationAllowed: false,
    runtimeTruthWriteAllowed: false,
    runtimeMutationEnabled: false,
    automaticUpdatesEnabled: false,
    autonomousCrawlingEnabled: false,
    autonomousExecutionEnabled: false,
    autonomousAgentExecutionEnabled: false,
    liveWebExecutionEnabled: false,
    browserExecutionEnabled: false,
    networkRequestPerformed: false,
    bodyReadAllowed: false
  });

  const domainLabels = Object.freeze({
    general: "General",
    market: "Market Intelligence",
    research: "Research Intelligence",
    engineering: "Engineering Intelligence",
    portfolio: "Portfolio Intelligence",
    breakthrough: "Breakthrough Intelligence",
    acquisition: "Acquisition Intelligence",
    governance: "Governance / Safety"
  });

  function ensurePanel() {
    let panel = document.getElementById("claire-intelligence-answer-panel");
    if (panel) return panel;

    panel = document.createElement("section");
    panel.id = "claire-intelligence-answer-panel";
    panel.className = "claire-intelligence-answer-panel";
    panel.setAttribute("data-version", ClaireIntelligenceAnswerContractVersion);
    panel.innerHTML = [
      "<div class='claire-answer-panel-header'>",
      "<span>Claire Intelligence Answer Contract</span>",
      "<small>Governed • Read-only • Presentation-only</small>",
      "</div>",
      "<div class='claire-answer-panel-body' id='claire-intelligence-answer-body'>",
      "<p>Claire Q&A foundation is ready for governed intelligence-routed responses.</p>",
      "</div>",
      "<div class='claire-answer-panel-footer'>Runtime mutation, autonomous execution, automatic updates, and uncontrolled live web action remain blocked.</div>"
    ].join("");

    const target =
      document.querySelector("[data-claire-command-surface]") ||
      document.querySelector("main") ||
      document.body;

    target.appendChild(panel);
    return panel;
  }

  function renderClaireIntelligenceAnswer(answer) {
    const panel = ensurePanel();
    const body = panel.querySelector("#claire-intelligence-answer-body");
    const classification = (answer && answer.classification) || {};
    const domain = classification.domain || "general";

    body.innerHTML = [
      "<div class='claire-answer-card'>",
      "<div class='claire-answer-card-topline'>",
      "<span class='claire-answer-domain'>" + (domainLabels[domain] || domain) + "</span>",
      "<span class='claire-answer-confidence'>Confidence: " + (answer.confidence ?? classification.confidence ?? "n/a") + "</span>",
      "</div>",
      "<p class='claire-answer-direct'>" + escapeHtml(answer.direct_answer || "No answer generated yet.") + "</p>",
      "<div class='claire-answer-meta'>",
      "<span>Route: " + escapeHtml(answer.route_hint || classification.default_route || "none") + "</span>",
      "<span>Evidence: " + escapeHtml(answer.evidence_requirement || classification.evidence_requirement || "unknown") + "</span>",
      "<span>Innovation: " + String(Boolean(answer.innovation_potential || classification.innovation_potential)) + "</span>",
      "</div>",
      "</div>"
    ].join("");
  }

  function escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  window.ClaireIntelligenceAnswerContract = Object.freeze({
    version: ClaireIntelligenceAnswerContractVersion,
    authority: ClaireIntelligenceAnswerAuthority,
    ensurePanel,
    renderClaireIntelligenceAnswer
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", ensurePanel);
  } else {
    ensurePanel();
  }
})();
