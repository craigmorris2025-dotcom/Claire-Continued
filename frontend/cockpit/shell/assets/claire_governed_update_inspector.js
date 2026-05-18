/*
Claire Governed Update Inspector — S506-S512
Presentation-only cockpit helper. Backend owns truth.
*/

(function () {
  "use strict";

  const ClaireGovernedUpdateInspectorVersion = "v19.89.8-S506-S512";

  const ClaireGovernedUpdateInspectorAuthority = Object.freeze({
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
    packageExportPerformed: false
  });

  function ensureUpdateInspectorPanel() {
    let panel = document.getElementById("claire-governed-update-inspector-panel");
    if (panel) return panel;

    panel = document.createElement("section");
    panel.id = "claire-governed-update-inspector-panel";
    panel.className = "claire-governed-update-inspector-panel";
    panel.setAttribute("data-version", ClaireGovernedUpdateInspectorVersion);
    panel.innerHTML = [
      "<div class='claire-update-panel-header'>",
      "<span>Claire Governed Update Inspector</span>",
      "<small>Metadata • Zero-trust • Rollback • Approval</small>",
      "</div>",
      "<div id='claire-update-panel-body' class='claire-update-panel-body'>",
      "<p>Governed update inspection readiness is active. Metadata inspection only; no download or apply.</p>",
      "</div>",
      "<footer>Presentation-only. No package download, install, runtime mutation, live web execution, or automatic update occurs.</footer>"
    ].join("");

    const target =
      document.getElementById("claire-answer-memory-replay-panel") ||
      document.getElementById("claire-useful-output-package-preview-panel") ||
      document.querySelector("main") ||
      document.body;

    target.appendChild(panel);
    return panel;
  }

  function renderClaireUpdateInspection(inspection) {
    const panel = ensureUpdateInspectorPanel();
    const body = panel.querySelector("#claire-update-panel-body");
    const candidate = (inspection && inspection.candidate) || {};
    const blockers = [];
    if (inspection && inspection.missing_fields && inspection.missing_fields.length) {
      blockers.push("Missing fields: " + inspection.missing_fields.join(", "));
    }
    if (inspection && inspection.protected_path_hits && inspection.protected_path_hits.length) {
      blockers.push("Protected paths: " + inspection.protected_path_hits.join(", "));
    }

    body.innerHTML = [
      "<article class='claire-update-inspection-card'>",
      "<div class='claire-update-card-topline'>",
      "<strong>" + escapeHtml(candidate.name || candidate.package_id || "Update candidate") + "</strong>",
      "<span>" + escapeHtml((inspection && inspection.risk_level) || "unknown") + "</span>",
      "</div>",
      "<div class='claire-update-badges'>",
      "<span>Score: " + escapeHtml((inspection && inspection.readiness_score) ?? "n/a") + "</span>",
      "<span>Metadata only: " + escapeHtml((inspection && inspection.inspection_scope) || "unknown") + "</span>",
      "<span>Apply allowed: false</span>",
      "</div>",
      "<p>" + escapeHtml(candidate.declared_purpose || "No purpose declared.") + "</p>",
      "<small>" + escapeHtml(blockers.join(" | ") || "No metadata blockers in preview.") + "</small>",
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

  window.ClaireGovernedUpdateInspector = Object.freeze({
    version: ClaireGovernedUpdateInspectorVersion,
    authority: ClaireGovernedUpdateInspectorAuthority,
    ensureUpdateInspectorPanel,
    renderClaireUpdateInspection
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", ensureUpdateInspectorPanel);
  } else {
    ensureUpdateInspectorPanel();
  }
})();
