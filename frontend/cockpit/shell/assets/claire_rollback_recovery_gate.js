/*
Claire Rollback Recovery Gate — S548-S554
Presentation-only cockpit helper. Backend owns truth.
*/

(function () {
  "use strict";

  const ClaireRollbackRecoveryGateVersion = "v19.89.8-S548-S554";

  const ClaireRollbackRecoveryGateAuthority = Object.freeze({
    backendOwnsTruth: true,
    cockpitPresentationOnly: true,
    runtimeTruthMutationAllowed: false,
    runtimeTruthWriteAllowed: false,
    runtimeMutationEnabled: false,
    automaticUpdatesEnabled: false,
    autonomousCrawlingEnabled: false,
    autonomousExecutionEnabled: false,
    liveWebExecutionEnabled: false,
    packageInstallPerformed: false,
    promotionPerformed: false,
    promotionAllowedNow: false,
    updateApplyAllowed: false,
    backupCreated: false,
    restorePerformed: false,
    rollbackExecutionPerformed: false,
    recoveryExecutionPerformed: false
  });

  function ensureRollbackRecoveryPanel() {
    let panel = document.getElementById("claire-rollback-recovery-gate-panel");
    if (panel) return panel;

    panel = document.createElement("section");
    panel.id = "claire-rollback-recovery-gate-panel";
    panel.className = "claire-rollback-recovery-gate-panel";
    panel.setAttribute("data-version", ClaireRollbackRecoveryGateVersion);
    panel.innerHTML = [
      "<div class='claire-rollback-header'>",
      "<span>Claire Rollback Proof & Recovery Gate</span>",
      "<small>Backup Map • Restore Map • Proof • Gate</small>",
      "</div>",
      "<div id='claire-rollback-body' class='claire-rollback-body'>",
      "<p>Rollback recovery gate is ready. Recovery remains blocked until proof exists.</p>",
      "</div>",
      "<footer>Presentation-only. No backup, restore, recovery, apply, promotion, install, or runtime mutation occurs.</footer>"
    ].join("");

    const target =
      document.getElementById("claire-update-promotion-decision-packet-panel") ||
      document.getElementById("claire-validation-result-intake-panel") ||
      document.querySelector("main") ||
      document.body;

    target.appendChild(panel);
    return panel;
  }

  function renderClaireRollbackRecoveryGate(gateOutput) {
    const panel = ensureRollbackRecoveryPanel();
    const body = panel.querySelector("#claire-rollback-body");
    const packet = (gateOutput && gateOutput.rollback_packet) || gateOutput || {};
    const gate = (gateOutput && gateOutput.recovery_gate) || {};
    const blockers = packet.blockers || gate.blockers || [];

    body.innerHTML = [
      "<article class='claire-rollback-card'>",
      "<div class='claire-rollback-topline'>",
      "<strong>" + escapeHtml(packet.rollback_packet_id || gate.recovery_gate_id || "rollback gate") + "</strong>",
      "<span>" + escapeHtml(packet.proof_status || gate.gate_state || "not_proven") + "</span>",
      "</div>",
      "<div class='claire-rollback-badges'>",
      "<span>Rollback proven: false</span>",
      "<span>Backup: false</span>",
      "<span>Restore: false</span>",
      "<span>Apply: false</span>",
      "<span>Blockers: " + escapeHtml(blockers.length) + "</span>",
      "</div>",
      "<p>Rollback proof must be completed in a future governed phase before application handoff.</p>",
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

  window.ClaireRollbackRecoveryGate = Object.freeze({
    version: ClaireRollbackRecoveryGateVersion,
    authority: ClaireRollbackRecoveryGateAuthority,
    ensureRollbackRecoveryPanel,
    renderClaireRollbackRecoveryGate
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", ensureRollbackRecoveryPanel);
  } else {
    ensureRollbackRecoveryPanel();
  }
})();
