/*
Claire Governed Update Readiness Demo — S569-S575
Presentation-only cockpit helper. Backend owns truth.
*/

(function () {
  "use strict";

  const ClaireGovernedUpdateReadinessDemoVersion = "v19.89.8-S569-S575";

  const ClaireGovernedUpdateReadinessDemoAuthority = Object.freeze({
    backendOwnsTruth: true,
    cockpitPresentationOnly: true,
    runtimeTruthMutationAllowed: false,
    runtimeTruthWriteAllowed: false,
    runtimeMutationEnabled: false,
    automaticUpdatesEnabled: false,
    autonomousExecutionEnabled: false,
    liveWebExecutionEnabled: false,
    networkRequestPerformed: false,
    packageDownloadPerformed: false,
    packageInstallPerformed: false,
    promotionPerformed: false,
    updateApplyAllowed: false,
    backupCreated: false,
    restorePerformed: false,
    readinessDemoPersistentWritePerformed: false
  });

  function ensureReadinessDemoPanel() {
    let panel = document.getElementById("claire-governed-update-readiness-demo-panel");
    if (panel) return panel;

    panel = document.createElement("section");
    panel.id = "claire-governed-update-readiness-demo-panel";
    panel.className = "claire-governed-update-readiness-demo-panel";
    panel.setAttribute("data-version", ClaireGovernedUpdateReadinessDemoVersion);
    panel.innerHTML = [
      "<div class='claire-readiness-demo-header'>",
      "<span>Claire Governed Update Readiness Demo</span>",
      "<small>S569–S575 Final Session Plateau</small>",
      "</div>",
      "<div id='claire-readiness-demo-body' class='claire-readiness-demo-body'>",
      "<p>End-to-end readiness demo is ready. Next phase moves to web/source/search issues.</p>",
      "</div>",
      "<footer>Presentation-only. No live web, download, install, apply, promotion, backup, restore, or runtime mutation occurs.</footer>"
    ].join("");

    const target =
      document.getElementById("claire-update-control-cockpit-panel") ||
      document.getElementById("claire-operator-staged-update-handoff-panel") ||
      document.querySelector("main") ||
      document.body;

    target.appendChild(panel);
    return panel;
  }

  function renderClaireGovernedUpdateReadinessDemo(summary) {
    const panel = ensureReadinessDemoPanel();
    const body = panel.querySelector("#claire-readiness-demo-body");
    const passed = (summary && summary.passed_path) || {};
    const blocked = (summary && summary.blocked_path) || {};

    body.innerHTML = [
      "<article class='claire-readiness-demo-card'>",
      "<div class='claire-readiness-demo-topline'>",
      "<strong>" + escapeHtml((summary && summary.title) || "S575 Governed Update Readiness Demo") + "</strong>",
      "<span>" + escapeHtml((summary && summary.primary_status) || "complete_review_only") + "</span>",
      "</div>",
      "<div class='claire-readiness-demo-badges'>",
      "<span>Passed path: " + escapeHtml(passed.promotion_decision || "review") + "</span>",
      "<span>Blocked path: " + escapeHtml(blocked.promotion_decision || "blocked") + "</span>",
      "<span>Apply: false</span>",
      "<span>Live web: false</span>",
      "</div>",
      "<p>" + escapeHtml((summary && summary.operator_message) || "Ready to move to web/source/search issues.") + "</p>",
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

  window.ClaireGovernedUpdateReadinessDemo = Object.freeze({
    version: ClaireGovernedUpdateReadinessDemoVersion,
    authority: ClaireGovernedUpdateReadinessDemoAuthority,
    ensureReadinessDemoPanel,
    renderClaireGovernedUpdateReadinessDemo
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", ensureReadinessDemoPanel);
  } else {
    ensureReadinessDemoPanel();
  }
})();
