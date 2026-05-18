/*
Claire Validation Result Intake — S534-S540
Presentation-only cockpit helper. Backend owns truth.
*/

(function () {
  "use strict";

  const ClaireValidationResultIntakeVersion = "v19.89.8-S534-S540";

  const ClaireValidationResultIntakeAuthority = Object.freeze({
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
    packageDownloadPerformed: false,
    packageInstallPerformed: false,
    validationExecutionPerformed: false,
    testExecutionPerformed: false,
    promotionPerformed: false,
    resultPersistentWritePerformed: false,
    resultFetchPerformed: false
  });

  function ensureValidationResultPanel() {
    let panel = document.getElementById("claire-validation-result-intake-panel");
    if (panel) return panel;

    panel = document.createElement("section");
    panel.id = "claire-validation-result-intake-panel";
    panel.className = "claire-validation-result-intake-panel";
    panel.setAttribute("data-version", ClaireValidationResultIntakeVersion);
    panel.innerHTML = [
      "<div class='claire-result-intake-header'>",
      "<span>Claire Validation Result Intake</span>",
      "<small>Results • Evidence • Readiness • Review</small>",
      "</div>",
      "<div id='claire-result-intake-body' class='claire-result-intake-body'>",
      "<p>Validation result intake is ready. Results are supplied for review; Claire runs nothing here.</p>",
      "</div>",
      "<footer>Presentation-only. No result fetch, command execution, test execution, persistence, promotion, or runtime mutation occurs.</footer>"
    ].join("");

    const target =
      document.getElementById("claire-update-evidence-review-queue-panel") ||
      document.getElementById("claire-controlled-update-validation-plan-panel") ||
      document.querySelector("main") ||
      document.body;

    target.appendChild(panel);
    return panel;
  }

  function renderClaireValidationResultIntake(intake) {
    const panel = ensureValidationResultPanel();
    const body = panel.querySelector("#claire-result-intake-body");
    const records = (intake && intake.records) || [];
    const rows = records.slice(0, 6).map(function (record) {
      return [
        "<article class='claire-result-record-card'>",
        "<div class='claire-result-record-topline'>",
        "<strong>" + escapeHtml(record.command_id || "validation command") + "</strong>",
        "<span>" + escapeHtml(record.status || "not_provided") + "</span>",
        "</div>",
        "<p>" + escapeHtml(record.summary || "") + "</p>",
        "<small>Operator supplied: " + escapeHtml(Boolean(record.operator_supplied)) + "</small>",
        "</article>"
      ].join("");
    }).join("");

    body.innerHTML = [
      "<div class='claire-result-intake-badges'>",
      "<span>Records: " + escapeHtml((intake && intake.record_count) ?? records.length) + "</span>",
      "<span>State: " + escapeHtml((intake && intake.result_readiness_state) || "awaiting_results") + "</span>",
      "<span>Execution: false</span>",
      "<span>Persistence: false</span>",
      "</div>",
      rows || "<p>No validation results supplied.</p>"
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

  window.ClaireValidationResultIntake = Object.freeze({
    version: ClaireValidationResultIntakeVersion,
    authority: ClaireValidationResultIntakeAuthority,
    ensureValidationResultPanel,
    renderClaireValidationResultIntake
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", ensureValidationResultPanel);
  } else {
    ensureValidationResultPanel();
  }
})();
