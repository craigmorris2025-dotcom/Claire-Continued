/*
Claire Syntalion v19.78
Autonomous Lifecycle Graph Foundation

This module does not fabricate runtime results.
It renders a contract-driven lifecycle graph and overlays payload truth when supplied.
*/

export const CLAIRE_AUTONOMOUS_ROUTE_TYPES = Object.freeze([
  "portfolio_intelligence",
  "acquisition_intelligence",
  "breakthrough_design",
  "existing_system_replacement",
  "governance_update",
  "recursive_learning",
]);

export async function loadCockpitLifecycleContract() {
  const response = await fetch("../cockpit_autonomous_lifecycle_contract.json", { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Failed to load cockpit lifecycle contract: ${response.status}`);
  }
  return response.json();
}

export function normalizeLifecyclePayload(payload) {
  const safe = payload && typeof payload === "object" ? payload : {};
  return {
    current_stage: safe.current_stage || safe.stage || null,
    active_route: safe.active_route || safe.route || null,
    active_gate: safe.active_gate || safe.gate || null,
    stage_scores: safe.stage_scores || safe.scores || {},
    route_confidence: safe.route_confidence || safe.confidence || null,
    evidence_basis: safe.evidence_basis || safe.evidence || [],
    selected_route_reason: safe.selected_route_reason || safe.route_reason || null,
    rejected_routes: safe.rejected_routes || [],
    skipped_stages: safe.skipped_stages || safe.skipped_stages_with_reasons || [],
    terminal_state: safe.terminal_state || null,
    next_gate: safe.next_gate || null,
  };
}

export function renderAutonomousLifecycleGraph(target, contract, payload) {
  if (!target) return;

  const runtime = normalizeLifecyclePayload(payload);
  const stages = contract && contract.lifecycle && Array.isArray(contract.lifecycle.stages)
    ? contract.lifecycle.stages
    : [];

  const stageMarkup = stages.map((stage) => {
    const isActive = Number(runtime.current_stage) === Number(stage.id) || runtime.current_stage === stage.name;
    const isDesign = [16,17,18,19,20,21,22].includes(Number(stage.id));
    const score = runtime.stage_scores && (runtime.stage_scores[stage.id] || runtime.stage_scores[stage.name]);
    return `
      <div class="claire-lifecycle-node ${isActive ? "active" : ""} ${isDesign ? "design-route" : ""}" data-stage-id="${stage.id}">
        <span class="stage-number">${stage.id}</span>
        <span class="stage-name">${stage.name}</span>
        <span class="stage-group">${stage.group}</span>
        ${score !== undefined ? `<span class="stage-score">${score}</span>` : ""}
      </div>
    `;
  }).join("");

  target.innerHTML = `
    <section class="claire-autonomous-lifecycle-graph" data-active-route="${runtime.active_route || "unknown"}">
      <header>
        <div>
          <h2>Autonomous Lifecycle Runtime</h2>
          <p>30-stage conditional routing graph. Backend payload truth only.</p>
        </div>
        <div class="route-summary">
          <strong>${runtime.active_route || "No active route"}</strong>
          <span>${runtime.active_gate || "No active gate"}</span>
        </div>
      </header>
      <div class="route-decision-bar">
        <div><strong>Selected Reason</strong><span>${runtime.selected_route_reason || "Unavailable until backend payload provides it."}</span></div>
        <div><strong>Route Confidence</strong><span>${runtime.route_confidence ?? "Unavailable"}</span></div>
        <div><strong>Terminal State</strong><span>${runtime.terminal_state || "Not reached"}</span></div>
        <div><strong>Next Gate</strong><span>${runtime.next_gate || "Unavailable"}</span></div>
      </div>
      <div class="lifecycle-node-grid">
        ${stageMarkup}
      </div>
    </section>
  `;
}
