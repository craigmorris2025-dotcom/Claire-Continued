/*
Claire Innovation Route Escalation — S485-S491
Presentation-only cockpit helper. Backend owns truth.
*/

(function () {
  "use strict";

  const ClaireInnovationRouteEscalationVersion = "v19.89.8-S485-S491";

  const ClaireInnovationRouteEscalationAuthority = Object.freeze({
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
    bodyReadAllowed: false,
    automaticEscalationExecutionEnabled: false
  });

  function ensureInnovationPanel() {
    let panel = document.getElementById("claire-innovation-route-escalation-panel");
    if (panel) return panel;

    panel = document.createElement("section");
    panel.id = "claire-innovation-route-escalation-panel";
    panel.className = "claire-innovation-route-escalation-panel";
    panel.setAttribute("data-version", ClaireInnovationRouteEscalationVersion);
    panel.innerHTML = [
      "<div class='claire-innovation-panel-header'>",
      "<span>Claire Innovation Route Escalation</span>",
      "<small>Potential • Candidates • Operator Review</small>",
      "</div>",
      "<div id='claire-innovation-panel-body' class='claire-innovation-panel-body'>",
      "<p>Innovation potential detection is ready. Route candidates are advisory only.</p>",
      "</div>",
      "<footer>Presentation-only. Escalation detection does not execute route transitions or mutate runtime truth.</footer>"
    ].join("");

    const target =
      document.getElementById("claire-domain-answer-routes-panel") ||
      document.getElementById("claire-knowledge-base-registry-panel") ||
      document.querySelector("main") ||
      document.body;

    target.appendChild(panel);
    return panel;
  }

  function renderClaireInnovationDetection(detection) {
    const panel = ensureInnovationPanel();
    const body = panel.querySelector("#claire-innovation-panel-body");
    const candidates = (detection && detection.route_candidates) || [];
    const rows = candidates.slice(0, 5).map(function (candidate) {
      return [
        "<article class='claire-route-candidate-card'>",
        "<div class='claire-route-candidate-topline'>",
        "<strong>" + escapeHtml(candidate.label || candidate.candidate_key || "Route candidate") + "</strong>",
        "<span>" + escapeHtml(candidate.composite_score ?? "n/a") + "</span>",
        "</div>",
        "<p>" + escapeHtml(candidate.route_id || "") + "</p>",
        "<small>Review required: " + escapeHtml(Boolean(candidate.qualifies_for_review)) + "</small>",
        "</article>"
      ].join("");
    }).join("");

    body.innerHTML = [
      "<div class='claire-innovation-summary'>",
      "<span>Level: " + escapeHtml((detection && detection.innovation_potential_level) || "unknown") + "</span>",
      "<span>Score: " + escapeHtml((detection && detection.innovation_score) ?? "n/a") + "</span>",
      "<span>Operator review: " + escapeHtml(Boolean(detection && detection.requires_operator_review)) + "</span>",
      "</div>",
      "<div class='claire-route-candidate-list'>" + (rows || "<p>No route candidates available.</p>") + "</div>"
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

  window.ClaireInnovationRouteEscalation = Object.freeze({
    version: ClaireInnovationRouteEscalationVersion,
    authority: ClaireInnovationRouteEscalationAuthority,
    ensureInnovationPanel,
    renderClaireInnovationDetection
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", ensureInnovationPanel);
  } else {
    ensureInnovationPanel();
  }
})();
