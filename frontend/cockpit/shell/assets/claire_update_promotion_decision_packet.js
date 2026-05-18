/*
Claire Update Promotion Decision Packet — S541-S547
Presentation-only cockpit helper. Backend owns truth.
*/

(function () {
  "use strict";

  const ClaireUpdatePromotionDecisionPacketVersion = "v19.89.8-S541-S547";

  const ClaireUpdatePromotionDecisionPacketAuthority = Object.freeze({
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
    promotionAllowedNow: false,
    updateApplyAllowed: false,
    decisionPersistentWritePerformed: false
  });

  function ensurePromotionPacketPanel() {
    let panel = document.getElementById("claire-update-promotion-decision-packet-panel");
    if (panel) return panel;

    panel = document.createElement("section");
    panel.id = "claire-update-promotion-decision-packet-panel";
    panel.className = "claire-update-promotion-decision-packet-panel";
    panel.setAttribute("data-version", ClaireUpdatePromotionDecisionPacketVersion);
    panel.innerHTML = [
      "<div class='claire-promotion-packet-header'>",
      "<span>Claire Update Promotion Decision Packet</span>",
      "<small>Eligibility • Blockers • Approval Boundary</small>",
      "</div>",
      "<div id='claire-promotion-packet-body' class='claire-promotion-packet-body'>",
      "<p>Promotion decision packet is ready. It is review-only and cannot apply updates.</p>",
      "</div>",
      "<footer>Presentation-only. No promotion, apply, install, persistent decision write, or runtime mutation occurs.</footer>"
    ].join("");

    const target =
      document.getElementById("claire-validation-result-intake-panel") ||
      document.getElementById("claire-update-evidence-review-queue-panel") ||
      document.querySelector("main") ||
      document.body;

    target.appendChild(panel);
    return panel;
  }

  function renderClairePromotionDecisionPacket(packet) {
    const panel = ensurePromotionPacketPanel();
    const body = panel.querySelector("#claire-promotion-packet-body");
    const blockers = (packet && packet.blockers) || [];

    body.innerHTML = [
      "<article class='claire-promotion-packet-card'>",
      "<div class='claire-promotion-packet-topline'>",
      "<strong>" + escapeHtml((packet && packet.promotion_packet_id) || "promotion packet") + "</strong>",
      "<span>" + escapeHtml((packet && packet.packet_status) || "held") + "</span>",
      "</div>",
      "<div class='claire-promotion-packet-badges'>",
      "<span>Decision: " + escapeHtml((packet && packet.decision) || "unknown") + "</span>",
      "<span>Promotion: false</span>",
      "<span>Apply: false</span>",
      "<span>Blockers: " + escapeHtml(blockers.length) + "</span>",
      "</div>",
      "<p>" + escapeHtml((packet && packet.summary) || "No decision summary available.") + "</p>",
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

  window.ClaireUpdatePromotionDecisionPacket = Object.freeze({
    version: ClaireUpdatePromotionDecisionPacketVersion,
    authority: ClaireUpdatePromotionDecisionPacketAuthority,
    ensurePromotionPacketPanel,
    renderClairePromotionDecisionPacket
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", ensurePromotionPacketPanel);
  } else {
    ensurePromotionPacketPanel();
  }
})();
