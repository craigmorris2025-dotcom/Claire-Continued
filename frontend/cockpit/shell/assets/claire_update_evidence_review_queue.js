/*
Claire Update Evidence Review Queue — S527-S533
Presentation-only cockpit helper. Backend owns truth.
*/

(function () {
  "use strict";

  const ClaireUpdateEvidenceReviewQueueVersion = "v19.89.8-S527-S533";

  const ClaireUpdateEvidenceReviewQueueAuthority = Object.freeze({
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
    queuePersistentWritePerformed: false,
    operatorDecisionExecutionPerformed: false
  });

  function ensureUpdateEvidenceQueuePanel() {
    let panel = document.getElementById("claire-update-evidence-review-queue-panel");
    if (panel) return panel;

    panel = document.createElement("section");
    panel.id = "claire-update-evidence-review-queue-panel";
    panel.className = "claire-update-evidence-review-queue-panel";
    panel.setAttribute("data-version", ClaireUpdateEvidenceReviewQueueVersion);
    panel.innerHTML = [
      "<div class='claire-review-queue-header'>",
      "<span>Claire Update Evidence Review Queue</span>",
      "<small>Evidence • Packets • Queue • Recommendation</small>",
      "</div>",
      "<div id='claire-review-queue-body' class='claire-review-queue-body'>",
      "<p>Update evidence review queue is ready. Queue is in-memory and review-only.</p>",
      "</div>",
      "<footer>Presentation-only. No queue persistence, command execution, package install, promotion, or runtime mutation occurs.</footer>"
    ].join("");

    const target =
      document.getElementById("claire-controlled-update-validation-plan-panel") ||
      document.getElementById("claire-staged-update-sandbox-panel") ||
      document.querySelector("main") ||
      document.body;

    target.appendChild(panel);
    return panel;
  }

  function renderClaireUpdateReviewQueue(queue) {
    const panel = ensureUpdateEvidenceQueuePanel();
    const body = panel.querySelector("#claire-review-queue-body");
    const packets = (queue && queue.packets) || [];
    const rows = packets.slice(0, 6).map(function (packet) {
      return [
        "<article class='claire-review-packet-card'>",
        "<div class='claire-review-packet-topline'>",
        "<strong>" + escapeHtml(packet.review_packet_id || "review packet") + "</strong>",
        "<span>" + escapeHtml(packet.review_status || "queued") + "</span>",
        "</div>",
        "<p>" + escapeHtml(packet.summary || "") + "</p>",
        "<small>Recommended: " + escapeHtml(packet.recommended_action || "hold") + "</small>",
        "</article>"
      ].join("");
    }).join("");

    body.innerHTML = [
      "<div class='claire-review-queue-badges'>",
      "<span>Packets: " + escapeHtml((queue && queue.packet_count) ?? packets.length) + "</span>",
      "<span>Persistent write: false</span>",
      "<span>Decision execution: false</span>",
      "</div>",
      rows || "<p>No packets in review queue.</p>"
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

  window.ClaireUpdateEvidenceReviewQueue = Object.freeze({
    version: ClaireUpdateEvidenceReviewQueueVersion,
    authority: ClaireUpdateEvidenceReviewQueueAuthority,
    ensureUpdateEvidenceQueuePanel,
    renderClaireUpdateReviewQueue
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", ensureUpdateEvidenceQueuePanel);
  } else {
    ensureUpdateEvidenceQueuePanel();
  }
})();
