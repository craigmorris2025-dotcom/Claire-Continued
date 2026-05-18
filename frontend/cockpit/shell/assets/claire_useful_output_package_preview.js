/*
Claire Useful Output Package Preview — S492-S498
Presentation-only cockpit helper. Backend owns truth.
*/

(function () {
  "use strict";

  const ClaireUsefulOutputPackagePreviewVersion = "v19.89.8-S492-S498";

  const ClaireUsefulOutputPackagePreviewAuthority = Object.freeze({
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
    packageExecutionEnabled: false,
    packageExportPerformed: false
  });

  function ensurePackagePreviewPanel() {
    let panel = document.getElementById("claire-useful-output-package-preview-panel");
    if (panel) return panel;

    panel = document.createElement("section");
    panel.id = "claire-useful-output-package-preview-panel";
    panel.className = "claire-useful-output-package-preview-panel";
    panel.setAttribute("data-version", ClaireUsefulOutputPackagePreviewVersion);
    panel.innerHTML = [
      "<div class='claire-package-preview-header'>",
      "<span>Claire Useful Output Package Preview</span>",
      "<small>Review-only • Evidence • Sections • Export Stub</small>",
      "</div>",
      "<div id='claire-package-preview-body' class='claire-package-preview-body'>",
      "<p>Useful output package previews are ready. Packages remain review-only.</p>",
      "</div>",
      "<footer>No runtime mutation, automatic update, autonomous action, live web execution, or package export is performed.</footer>"
    ].join("");

    const target =
      document.getElementById("claire-innovation-route-escalation-panel") ||
      document.getElementById("claire-domain-answer-routes-panel") ||
      document.querySelector("main") ||
      document.body;

    target.appendChild(panel);
    return panel;
  }

  function renderClairePackagePreview(preview) {
    const panel = ensurePackagePreviewPanel();
    const body = panel.querySelector("#claire-package-preview-body");
    const sections = (preview && preview.sections) || {};
    const sectionRows = Object.keys(sections).slice(0, 8).map(function (key) {
      return "<li><strong>" + escapeHtml(key.replaceAll("_", " ")) + ":</strong> " +
        escapeHtml(typeof sections[key] === "string" ? sections[key] : JSON.stringify(sections[key])) +
        "</li>";
    }).join("");

    body.innerHTML = [
      "<article class='claire-package-preview-card'>",
      "<div class='claire-package-preview-topline'>",
      "<strong>" + escapeHtml((preview && preview.label) || "Useful output preview") + "</strong>",
      "<span>" + escapeHtml((preview && preview.review_status) || "review-required") + "</span>",
      "</div>",
      "<div class='claire-package-preview-badges'>",
      "<span>Type: " + escapeHtml((preview && preview.package_type) || "unknown") + "</span>",
      "<span>Score: " + escapeHtml((preview && preview.readiness_score) ?? "n/a") + "</span>",
      "<span>Export ready: " + escapeHtml(Boolean(preview && preview.export_manifest && preview.export_manifest.export_ready)) + "</span>",
      "</div>",
      "<p>" + escapeHtml((preview && preview.summary) || "No package summary available.") + "</p>",
      "<ul>" + sectionRows + "</ul>",
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

  window.ClaireUsefulOutputPackagePreview = Object.freeze({
    version: ClaireUsefulOutputPackagePreviewVersion,
    authority: ClaireUsefulOutputPackagePreviewAuthority,
    ensurePackagePreviewPanel,
    renderClairePackagePreview
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", ensurePackagePreviewPanel);
  } else {
    ensurePackagePreviewPanel();
  }
})();
