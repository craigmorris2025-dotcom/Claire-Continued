/*
Claire Domain Answer Routes — S478-S484
Presentation-only cockpit helper. Backend owns truth.
*/

(function () {
  "use strict";

  const ClaireDomainAnswerRoutesVersion = "v19.89.8-S478-S484";

  const ClaireDomainAnswerRoutesAuthority = Object.freeze({
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

  function ensureDomainRoutesPanel() {
    let panel = document.getElementById("claire-domain-answer-routes-panel");
    if (panel) return panel;

    panel = document.createElement("section");
    panel.id = "claire-domain-answer-routes-panel";
    panel.className = "claire-domain-answer-routes-panel";
    panel.setAttribute("data-version", ClaireDomainAnswerRoutesVersion);
    panel.innerHTML = [
      "<div class='claire-domain-panel-header'>",
      "<span>Claire Domain Answer Routes</span>",
      "<small>Market • Research • Engineering • Synthesis</small>",
      "</div>",
      "<div id='claire-domain-routes-body' class='claire-domain-routes-body'>",
      "<p>Domain-routed Claire answers are ready for governed, evidence-aware presentation.</p>",
      "</div>",
      "<footer>Presentation-only. No live web, network request, browser execution, body read, or runtime mutation.</footer>"
    ].join("");

    const target =
      document.getElementById("claire-knowledge-base-registry-panel") ||
      document.getElementById("claire-evidence-backed-answer-panel") ||
      document.querySelector("main") ||
      document.body;

    target.appendChild(panel);
    return panel;
  }

  function renderClaireDomainRoute(routeOutput) {
    const panel = ensureDomainRoutesPanel();
    const body = panel.querySelector("#claire-domain-routes-body");
    const route = (routeOutput && routeOutput.route_selection) || {};
    const sections = (routeOutput && routeOutput.route_sections) || {};
    const sectionKeys = Object.keys(sections).slice(0, 6);

    const rows = sectionKeys.map(function (key) {
      return "<li><strong>" + escapeHtml(key.replaceAll("_", " ")) + ":</strong> " +
        escapeHtml(typeof sections[key] === "string" ? sections[key] : JSON.stringify(sections[key])) +
        "</li>";
    }).join("");

    body.innerHTML = [
      "<article class='claire-domain-route-card'>",
      "<div class='claire-domain-card-topline'>",
      "<strong>" + escapeHtml(route.label || "Claire domain route") + "</strong>",
      "<span>" + escapeHtml(route.selected_domain_route || "unknown") + "</span>",
      "</div>",
      "<p>" + escapeHtml(route.primary_goal || "No route goal available.") + "</p>",
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

  window.ClaireDomainAnswerRoutes = Object.freeze({
    version: ClaireDomainAnswerRoutesVersion,
    authority: ClaireDomainAnswerRoutesAuthority,
    ensureDomainRoutesPanel,
    renderClaireDomainRoute
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", ensureDomainRoutesPanel);
  } else {
    ensureDomainRoutesPanel();
  }
})();
