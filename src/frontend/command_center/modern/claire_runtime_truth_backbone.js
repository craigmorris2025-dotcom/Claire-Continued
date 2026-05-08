
/* Claire v17.59 — Runtime Truth Backbone dashboard bridge.
   This file is intentionally non-invasive: it updates visible shell labels if present
   and exposes the canonical runtime truth contract path for existing dashboard code. */
(function () {
  const backbone = {
    version: 'v17.59',
    contractPath: './runtime_truth_contract.json',
    statusPath: './runtime_truth_status.json',
    canonicalTruthCandidates: [
      './dashboard_runtime_truth.json',
      '/exports/latest/dashboard_runtime_truth.json',
      './runtime_truth_status.json',
      './core_run_output.json',
      '/exports/latest/core_run_output.json'
    ],
    rule: 'No validation pass -> no verified memory -> no recursive feedback.'
  };

  window.CLAIRE_RUNTIME_TRUTH_BACKBONE = backbone;

  function setText(id, value) {
    const el = document.getElementById(id);
    if (el && value) el.textContent = value;
  }

  function addRailEvent() {
    const rail = document.getElementById('event-rail');
    if (!rail || document.getElementById('v17-59-runtime-truth-event')) return;
    const card = document.createElement('div');
    card.className = 'event';
    card.id = 'v17-59-runtime-truth-event';
    card.innerHTML = '<b>Runtime Truth Backbone installed</b><p>Run, route, terminal, stage, validation, evidence, memory, and runtime health truth now have a canonical data contract. Use tools/claire_build_runtime_truth.py after an actual run output exists.</p><span class="time">v17.59</span>';
    rail.prepend(card);
  }

  document.addEventListener('DOMContentLoaded', function () {
    setText('chip-build', 'v17.59');
    setText('chip-validation', 'Truth contract ready');
    addRailEvent();
  });
})();
