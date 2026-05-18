/*
Claire Knowledge Base Registry — S471-S477
Presentation-only cockpit helper. Backend owns truth.
*/

(function () {
  "use strict";

  const ClaireKnowledgeBaseRegistryVersion = "v19.89.8-S471-S477";

  const ClaireKnowledgeBaseRegistryAuthority = Object.freeze({
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

  function ensureKnowledgePanel() {
    let panel = document.getElementById("claire-knowledge-base-registry-panel");
    if (panel) return panel;

    panel = document.createElement("section");
    panel.id = "claire-knowledge-base-registry-panel";
    panel.className = "claire-knowledge-base-registry-panel";
    panel.setAttribute("data-version", ClaireKnowledgeBaseRegistryVersion);
    panel.innerHTML = [
      "<div class='claire-kb-panel-header'>",
      "<span>Claire Knowledge Base Registry</span>",
      "<small>Documents • Domains • Routes • Trust</small>",
      "</div>",
      "<div id='claire-kb-panel-body' class='claire-kb-panel-body'>",
      "<p>Curated Claire knowledge registry is ready for governed, evidence-aware answers.</p>",
      "</div>",
      "<footer>Presentation-only. No external file reads, live search, network request, or runtime mutation occurs here.</footer>"
    ].join("");

    const target =
      document.getElementById("claire-evidence-backed-answer-panel") ||
      document.getElementById("claire-command-response-stack") ||
      document.querySelector("main") ||
      document.body;

    target.appendChild(panel);
    return panel;
  }

  function renderClaireKnowledgeResults(results) {
    const panel = ensureKnowledgePanel();
    const body = panel.querySelector("#claire-kb-panel-body");
    const list = Array.isArray(results) ? results : [];

    const rows = list.map(function (item) {
      return [
        "<article class='claire-kb-source-card'>",
        "<div class='claire-kb-card-topline'>",
        "<strong>" + escapeHtml(item.title || item.doc_id || "Knowledge source") + "</strong>",
        "<span>" + escapeHtml(item.trust_tier || "unknown") + "</span>",
        "</div>",
        "<p>" + escapeHtml(item.summary || "") + "</p>",
        "<small>Score: " + escapeHtml(item.score ?? "n/a") + "</small>",
        "</article>"
      ].join("");
    }).join("");

    body.innerHTML = rows || "<p>No knowledge registry results available yet.</p>";
  }

  function escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  window.ClaireKnowledgeBaseRegistry = Object.freeze({
    version: ClaireKnowledgeBaseRegistryVersion,
    authority: ClaireKnowledgeBaseRegistryAuthority,
    ensureKnowledgePanel,
    renderClaireKnowledgeResults
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", ensureKnowledgePanel);
  } else {
    ensureKnowledgePanel();
  }
})();
