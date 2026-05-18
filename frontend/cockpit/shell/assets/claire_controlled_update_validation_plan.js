/*
Claire Controlled Update Validation Plan — S520-S526
Presentation-only cockpit helper. Backend owns truth.
*/

(function () {
  "use strict";

  const ClaireControlledUpdateValidationPlanVersion = "v19.89.8-S520-S526";

  const ClaireControlledUpdateValidationPlanAuthority = Object.freeze({
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
    promotionPerformed: false
  });

  function ensureValidationPlanPanel() {
    let panel = document.getElementById("claire-controlled-update-validation-plan-panel");
    if (panel) return panel;

    panel = document.createElement("section");
    panel.id = "claire-controlled-update-validation-plan-panel";
    panel.className = "claire-controlled-update-validation-plan-panel";
    panel.setAttribute("data-version", ClaireControlledUpdateValidationPlanVersion);
    panel.innerHTML = [
      "<div class='claire-validation-plan-header'>",
      "<span>Claire Controlled Update Validation Plan</span>",
      "<small>Commands • Preflight • Rollback • Gate</small>",
      "</div>",
      "<div id='claire-validation-plan-body' class='claire-validation-plan-body'>",
      "<p>Controlled update validation plan is ready. Commands are declarative only.</p>",
      "</div>",
      "<footer>Presentation-only. No command execution, test execution, install, promotion, or runtime mutation occurs.</footer>"
    ].join("");

    const target =
      document.getElementById("claire-staged-update-sandbox-panel") ||
      document.getElementById("claire-governed-update-inspector-panel") ||
      document.querySelector("main") ||
      document.body;

    target.appendChild(panel);
    return panel;
  }

  function renderClaireControlledValidationPlan(plan) {
    const panel = ensureValidationPlanPanel();
    const body = panel.querySelector("#claire-validation-plan-body");
    const manifest = (plan && plan.command_manifest) || {};
    const commands = manifest.commands || [];
    const rows = commands.slice(0, 6).map(function (command) {
      return "<li><strong>" + escapeHtml(command.label || command.command_id) + "</strong> — allowed now: false; executed: false</li>";
    }).join("");

    body.innerHTML = [
      "<article class='claire-validation-plan-card'>",
      "<div class='claire-validation-card-topline'>",
      "<strong>" + escapeHtml((plan && plan.execution_plan_id) || "Controlled validation plan") + "</strong>",
      "<span>" + escapeHtml((plan && plan.gate_state) || "blocked") + "</span>",
      "</div>",
      "<div class='claire-validation-badges'>",
      "<span>Commands: " + escapeHtml(manifest.command_count ?? commands.length) + "</span>",
      "<span>Execution allowed: false</span>",
      "<span>Validation performed: false</span>",
      "<span>Promotion: false</span>",
      "</div>",
      "<ul>" + rows + "</ul>",
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

  window.ClaireControlledUpdateValidationPlan = Object.freeze({
    version: ClaireControlledUpdateValidationPlanVersion,
    authority: ClaireControlledUpdateValidationPlanAuthority,
    ensureValidationPlanPanel,
    renderClaireControlledValidationPlan
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", ensureValidationPlanPanel);
  } else {
    ensureValidationPlanPanel();
  }
})();
