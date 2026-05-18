/*
Claire Evidence-Backed Answers — S464-S470
Presentation-only cockpit renderer. Backend owns truth.
*/

(function () {
  "use strict";

  const ClaireEvidenceBackedAnswersVersion = "v19.89.8-S464-S470";

  const ClaireEvidenceBackedAnswersAuthority = Object.freeze({
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

  function ensureEvidencePanel() {
    let panel = document.getElementById("claire-evidence-backed-answer-panel");
    if (panel) return panel;

    panel = document.createElement("section");
    panel.id = "claire-evidence-backed-answer-panel";
    panel.className = "claire-evidence-backed-answer-panel";
    panel.setAttribute("data-version", ClaireEvidenceBackedAnswersVersion);
    panel.innerHTML = [
      "<div class='claire-evidence-panel-header'>",
      "<span>Claire Evidence-Backed Answers</span>",
      "<small>Claims • Sources • Confidence • Verification</small>",
      "</div>",
      "<div id='claire-evidence-answer-body' class='claire-evidence-answer-body'>",
      "<p>Evidence-backed answer model is ready. Unsupported claims must be marked for verification.</p>",
      "</div>",
      "<footer>Presentation-only. No live research, network request, body read, or runtime mutation is performed here.</footer>"
    ].join("");

    const target =
      document.getElementById("claire-command-response-stack") ||
      document.getElementById("claire-intelligence-answer-panel") ||
      document.querySelector("main") ||
      document.body;

    target.appendChild(panel);
    return panel;
  }

  function renderClaireEvidenceBackedAnswer(answer) {
    const panel = ensureEvidencePanel();
    const body = panel.querySelector("#claire-evidence-answer-body");
    const basket = (answer && answer.evidence_basket) || {};
    const support = basket.support_summary || {};
    const claims = (answer && answer.claims) || [];
    const claimRows = claims.map(function (claim) {
      return "<li><strong>" + escapeHtml(claim.status || "unknown") + "</strong> — " +
        escapeHtml(claim.text || "") + "</li>";
    }).join("");

    body.innerHTML = [
      "<article class='claire-evidence-answer-card'>",
      "<div class='claire-evidence-topline'>",
      "<span>Quality: " + escapeHtml((answer && answer.answer_quality_state) || "unknown") + "</span>",
      "<span>Confidence: " + escapeHtml((answer && answer.confidence) ?? "n/a") + "</span>",
      "<span>Support: " + escapeHtml(support.support_level || "unknown") + "</span>",
      "</div>",
      "<p>" + escapeHtml((answer && answer.direct_answer) || "No answer text available.") + "</p>",
      "<ul class='claire-evidence-claims'>" + claimRows + "</ul>",
      "</article>"
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

  window.ClaireEvidenceBackedAnswers = Object.freeze({
    version: ClaireEvidenceBackedAnswersVersion,
    authority: ClaireEvidenceBackedAnswersAuthority,
    ensureEvidencePanel,
    renderClaireEvidenceBackedAnswer
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", ensureEvidencePanel);
  } else {
    ensureEvidencePanel();
  }
})();
