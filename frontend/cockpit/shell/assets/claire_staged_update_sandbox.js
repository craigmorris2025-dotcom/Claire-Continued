/*
Claire Staged Update Sandbox — S513-S519
Presentation-only cockpit helper. Backend owns truth.
*/

(function () {
  "use strict";

  const ClaireStagedUpdateSandboxVersion = "v19.89.8-S513-S519";

  const ClaireStagedUpdateSandboxAuthority = Object.freeze({
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
    packageExecutionEnabled: false,
    sandboxFileWritePerformed: false,
    sandboxCreated: false,
    testExecutionPerformed: false,
    promotionPerformed: false
  });

  function ensureStagedSandboxPanel() {
    let panel = document.getElementById("claire-staged-update-sandbox-panel");
    if (panel) return panel;

    panel = document.createElement("section");
    panel.id = "claire-staged-update-sandbox-panel";
    panel.className = "claire-staged-update-sandbox-panel";
    panel.setAttribute("data-version", ClaireStagedUpdateSandboxVersion);
    panel.innerHTML = [
      "<div class='claire-sandbox-panel-header'>",
      "<span>Claire Staged Update Sandbox Contract</span>",
      "<small>Profile • Impact Map • Dry Run • Promotion Gate</small>",
      "</div>",
      "<div id='claire-sandbox-panel-body' class='claire-sandbox-panel-body'>",
      "<p>Staged update sandbox contract is ready. No sandbox is created and no tests are executed.</p>",
      "</div>",
      "<footer>Presentation-only. No package install, sandbox write, test execution, promotion, or runtime mutation occurs.</footer>"
    ].join("");

    const target =
      document.getElementById("claire-governed-update-inspector-panel") ||
      document.getElementById("claire-answer-memory-replay-panel") ||
      document.querySelector("main") ||
      document.body;

    target.appendChild(panel);
    return panel;
  }

  function renderClaireStagedSandbox(output) {
    const panel = ensureStagedSandboxPanel();
    const body = panel.querySelector("#claire-sandbox-panel-body");
    const profile = (output && output.sandbox_profile) || output || {};
    const dryRun = (output && output.dry_run) || {};

    body.innerHTML = [
      "<article class='claire-sandbox-card'>",
      "<div class='claire-sandbox-card-topline'>",
      "<strong>" + escapeHtml(profile.sandbox_id || "Sandbox profile") + "</strong>",
      "<span>" + escapeHtml(profile.sandbox_status || "contract-ready") + "</span>",
      "</div>",
      "<div class='claire-sandbox-badges'>",
      "<span>Create now: false</span>",
      "<span>Sandbox created: false</span>",
      "<span>Tests executed: " + escapeHtml(Boolean(dryRun.test_execution_performed)) + "</span>",
      "<span>Promotion: false</span>",
      "</div>",
      "<p>Future sandbox creation requires metadata review, rollback proof, declared tests, and operator approval.</p>",
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

  window.ClaireStagedUpdateSandbox = Object.freeze({
    version: ClaireStagedUpdateSandboxVersion,
    authority: ClaireStagedUpdateSandboxAuthority,
    ensureStagedSandboxPanel,
    renderClaireStagedSandbox
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", ensureStagedSandboxPanel);
  } else {
    ensureStagedSandboxPanel();
  }
})();
