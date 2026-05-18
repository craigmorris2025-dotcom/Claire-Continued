/*
Claire Update-Control Cockpit Wiring — S562-S568
Presentation-only cockpit helper. Backend owns truth.
*/

(function () {
  "use strict";

  const ClaireUpdateControlCockpitWiringVersion = "v19.89.8-S562-S568";

  const ClaireUpdateControlCockpitWiringAuthority = Object.freeze({
    backendOwnsTruth: true,
    cockpitPresentationOnly: true,
    runtimeTruthMutationAllowed: false,
    runtimeTruthWriteAllowed: false,
    runtimeMutationEnabled: false,
    automaticUpdatesEnabled: false,
    autonomousExecutionEnabled: false,
    liveWebExecutionEnabled: false,
    packageDownloadPerformed: false,
    packageInstallPerformed: false,
    promotionPerformed: false,
    updateApplyAllowed: false,
    backupCreated: false,
    restorePerformed: false,
    cockpitActionExecutionPerformed: false,
    cockpitPersistentWritePerformed: false
  });

  function ensureUpdateControlPanel() {
    let panel = document.getElementById("claire-update-control-cockpit-panel");
    if (panel) return panel;

    panel = document.createElement("section");
    panel.id = "claire-update-control-cockpit-panel";
    panel.className = "claire-update-control-cockpit-panel";
    panel.setAttribute("data-version", ClaireUpdateControlCockpitWiringVersion);
    panel.innerHTML = [
      "<div class='claire-update-control-header'>",
      "<span>Claire Governed Update Control</span>",
      "<small>S506–S568 Readiness Runway</small>",
      "</div>",
      "<div id='claire-update-control-body' class='claire-update-control-body'>",
      "<p>Update-control cockpit wiring is ready. Backend truth remains review-only.</p>",
      "</div>",
      "<footer>Presentation-only. No apply, install, download, command execution, promotion, backup, restore, or runtime mutation occurs.</footer>"
    ].join("");

    const target =
      document.getElementById("claire-operator-staged-update-handoff-panel") ||
      document.getElementById("claire-rollback-recovery-gate-panel") ||
      document.querySelector("main") ||
      document.body;

    target.appendChild(panel);
    return panel;
  }

  function renderClaireUpdateControlCockpit(payload) {
    const panel = ensureUpdateControlPanel();
    const body = panel.querySelector("#claire-update-control-body");
    const registry = (payload && payload.panel_registry) || {};
    const readiness = (payload && payload.runway_readiness) || {};
    const panels = registry.panels || [];
    const buttons = ((payload && payload.action_buttons) || {}).buttons || [];
    const panelRows = panels.map(function (item) {
      return "<li><strong>" + escapeHtml(item.label || item.panel_id) + "</strong> — " + escapeHtml(item.authority || "review_only") + "</li>";
    }).join("");
    const buttonRows = buttons.map(function (item) {
      return "<button type='button' class='claire-update-control-button' disabled>" + escapeHtml(item.label || item.button_id) + "</button>";
    }).join("");

    body.innerHTML = [
      "<div class='claire-update-control-badges'>",
      "<span>Status: " + escapeHtml((payload && payload.primary_status) || "review_only_ready") + "</span>",
      "<span>Modules: " + escapeHtml(readiness.ready_stage_count || 0) + "/" + escapeHtml(readiness.module_count || 0) + "</span>",
      "<span>Apply: false</span>",
      "<span>Install: false</span>",
      "</div>",
      "<div class='claire-update-control-actions'>" + buttonRows + "</div>",
      "<ul class='claire-update-control-stage-list'>" + panelRows + "</ul>"
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

  window.ClaireUpdateControlCockpitWiring = Object.freeze({
    version: ClaireUpdateControlCockpitWiringVersion,
    authority: ClaireUpdateControlCockpitWiringAuthority,
    ensureUpdateControlPanel,
    renderClaireUpdateControlCockpit
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", ensureUpdateControlPanel);
  } else {
    ensureUpdateControlPanel();
  }
})();
