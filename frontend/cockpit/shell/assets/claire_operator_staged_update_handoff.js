/*
Claire Operator Staged Update Handoff — S555-S561
Presentation-only cockpit helper. Backend owns truth.
*/

(function () {
  "use strict";

  const ClaireOperatorStagedUpdateHandoffVersion = "v19.89.8-S555-S561";

  const ClaireOperatorStagedUpdateHandoffAuthority = Object.freeze({
    backendOwnsTruth: true,
    cockpitPresentationOnly: true,
    runtimeTruthMutationAllowed: false,
    runtimeTruthWriteAllowed: false,
    runtimeMutationEnabled: false,
    automaticUpdatesEnabled: false,
    autonomousExecutionEnabled: false,
    liveWebExecutionEnabled: false,
    packageInstallPerformed: false,
    promotionPerformed: false,
    promotionAllowedNow: false,
    updateApplyAllowed: false,
    backupCreated: false,
    restorePerformed: false,
    handoffExecutionPerformed: false,
    applicationHandoffPerformed: false
  });

  function ensureHandoffPanel() {
    let panel = document.getElementById("claire-operator-staged-update-handoff-panel");
    if (panel) return panel;

    panel = document.createElement("section");
    panel.id = "claire-operator-staged-update-handoff-panel";
    panel.className = "claire-operator-staged-update-handoff-panel";
    panel.setAttribute("data-version", ClaireOperatorStagedUpdateHandoffVersion);
    panel.innerHTML = [
      "<div class='claire-handoff-header'>",
      "<span>Claire Operator Staged Update Handoff</span>",
      "<small>Approval • Handoff • Boundary • Blockers</small>",
      "</div>",
      "<div id='claire-handoff-body' class='claire-handoff-body'>",
      "<p>Operator-approved staged update handoff is ready for review only. No application owner is enabled.</p>",
      "</div>",
      "<footer>Presentation-only. No handoff execution, install, apply, promotion, backup, restore, or runtime mutation occurs.</footer>"
    ].join("");

    const target =
      document.getElementById("claire-rollback-recovery-gate-panel") ||
      document.getElementById("claire-update-promotion-decision-packet-panel") ||
      document.querySelector("main") ||
      document.body;

    target.appendChild(panel);
    return panel;
  }

  function renderClaireOperatorStagedUpdateHandoff(packet) {
    const panel = ensureHandoffPanel();
    const body = panel.querySelector("#claire-handoff-body");
    const blockers = (packet && packet.blockers) || [];

    body.innerHTML = [
      "<article class='claire-handoff-card'>",
      "<div class='claire-handoff-topline'>",
      "<strong>" + escapeHtml((packet && packet.handoff_packet_id) || "staged handoff") + "</strong>",
      "<span>" + escapeHtml((packet && packet.packet_status) || "awaiting_operator_approval") + "</span>",
      "</div>",
      "<div class='claire-handoff-badges'>",
      "<span>Approval: " + escapeHtml(Boolean(packet && packet.operator_approval && packet.operator_approval.approval_text_matched)) + "</span>",
      "<span>Owner enabled: false</span>",
      "<span>Apply: false</span>",
      "<span>Blockers: " + escapeHtml(blockers.length) + "</span>",
      "</div>",
      "<p>" + escapeHtml((packet && packet.handoff_summary) || "No handoff summary available.") + "</p>",
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

  window.ClaireOperatorStagedUpdateHandoff = Object.freeze({
    version: ClaireOperatorStagedUpdateHandoffVersion,
    authority: ClaireOperatorStagedUpdateHandoffAuthority,
    ensureHandoffPanel,
    renderClaireOperatorStagedUpdateHandoff
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", ensureHandoffPanel);
  } else {
    ensureHandoffPanel();
  }
})();
