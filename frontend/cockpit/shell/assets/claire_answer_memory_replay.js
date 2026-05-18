/*
Claire Answer Memory and Replay — S499-S505
Presentation-only cockpit helper. Backend owns truth.
*/

(function () {
  "use strict";

  const ClaireAnswerMemoryReplayVersion = "v19.89.8-S499-S505";

  const ClaireAnswerMemoryReplayAuthority = Object.freeze({
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
    packageExportPerformed: false,
    persistentMemoryWritePerformed: false,
    recursiveSelfIngestionExecuted: false
  });

  function ensureMemoryPanel() {
    let panel = document.getElementById("claire-answer-memory-replay-panel");
    if (panel) return panel;

    panel = document.createElement("section");
    panel.id = "claire-answer-memory-replay-panel";
    panel.className = "claire-answer-memory-replay-panel";
    panel.setAttribute("data-version", ClaireAnswerMemoryReplayVersion);
    panel.innerHTML = [
      "<div class='claire-memory-panel-header'>",
      "<span>Claire Answer Memory & Replay</span>",
      "<small>Trace • Replay • Compare • Review-only</small>",
      "</div>",
      "<div id='claire-memory-panel-body' class='claire-memory-panel-body'>",
      "<p>Answer memory and replay contracts are ready. No persistent memory write is performed.</p>",
      "</div>",
      "<footer>Presentation-only. Replay is reference-only and does not mutate runtime truth or execute recursive self-ingestion.</footer>"
    ].join("");

    const target =
      document.getElementById("claire-useful-output-package-preview-panel") ||
      document.getElementById("claire-innovation-route-escalation-panel") ||
      document.querySelector("main") ||
      document.body;

    target.appendChild(panel);
    return panel;
  }

  function renderClaireMemoryRecord(record) {
    const panel = ensureMemoryPanel();
    const body = panel.querySelector("#claire-memory-panel-body");
    const trace = (record && record.replay_trace) || {};
    const verification = (record && record.verification_needed) || [];

    body.innerHTML = [
      "<article class='claire-memory-record-card'>",
      "<div class='claire-memory-card-topline'>",
      "<strong>" + escapeHtml((record && record.package_type) || "memory record") + "</strong>",
      "<span>" + escapeHtml((record && record.review_status) || "unknown") + "</span>",
      "</div>",
      "<div class='claire-memory-badges'>",
      "<span>Memory: " + escapeHtml((record && record.memory_id) || "n/a") + "</span>",
      "<span>Readiness: " + escapeHtml((record && record.readiness_score) ?? "n/a") + "</span>",
      "<span>Trace: " + escapeHtml(Boolean(trace.trace_available)) + "</span>",
      "<span>Verification: " + escapeHtml(verification.length) + "</span>",
      "</div>",
      "<p>" + escapeHtml((record && record.question) || "No question recorded.") + "</p>",
      "</article>"
    ].join("");
  }

  function renderClaireReplay(replay) {
    const panel = ensureMemoryPanel();
    const body = panel.querySelector("#claire-memory-panel-body");

    body.innerHTML = [
      "<article class='claire-memory-record-card'>",
      "<div class='claire-memory-card-topline'>",
      "<strong>Replay reference</strong>",
      "<span>" + escapeHtml((replay && replay.status) || "unknown") + "</span>",
      "</div>",
      "<p>" + escapeHtml((replay && replay.replay_question) || "No replay question.") + "</p>",
      "<small>Source memory: " + escapeHtml((replay && replay.source_memory_id) || "n/a") + "</small>",
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

  window.ClaireAnswerMemoryReplay = Object.freeze({
    version: ClaireAnswerMemoryReplayVersion,
    authority: ClaireAnswerMemoryReplayAuthority,
    ensureMemoryPanel,
    renderClaireMemoryRecord,
    renderClaireReplay
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", ensureMemoryPanel);
  } else {
    ensureMemoryPanel();
  }
})();
