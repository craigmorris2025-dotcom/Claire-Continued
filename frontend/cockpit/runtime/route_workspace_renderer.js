/*
Claire Syntalion v19.79
Route Workspace Renderer

Renders route workspaces from canonical backend payload only.
No fabricated runtime results.
*/

export const CLAIRE_ROUTE_WORKSPACES = Object.freeze([
  "portfolio_intelligence",
  "acquisition_intelligence",
  "breakthrough_design",
  "existing_system_replacement",
  "governance_update",
  "recursive_learning",
  "evidence_traceability",
]);

export function normalizeRouteWorkspacePayload(payload) {
  const safe = payload && typeof payload === "object" ? payload : {};
  return {
    active_route: safe.active_route || safe.route || null,
    portfolio: safe.portfolio || safe.portfolio_intelligence || null,
    acquisition: safe.acquisition || safe.acquisition_intelligence || null,
    breakthrough: safe.breakthrough || safe.breakthrough_design || null,
    existing_system: safe.existing_system || safe.existing_system_replacement || null,
    governance: safe.governance || safe.update_governance || null,
    recursive: safe.recursive || safe.recursive_learning || safe.lifecycle_memory || null,
    evidence: safe.evidence || safe.evidence_traceability || safe.evidence_basis || null,
  };
}

function valueState(value) {
  return value ? "available" : "truthfully_unavailable";
}

function card(label, value, description) {
  return `
    <article class="claire-route-workspace-card ${valueState(value)}">
      <header>
        <strong>${label}</strong>
        <span>${valueState(value)}</span>
      </header>
      <p>${description}</p>
    </article>
  `;
}

export function renderRouteWorkspaces(target, payload) {
  if (!target) return;

  const state = normalizeRouteWorkspacePayload(payload);

  target.innerHTML = `
    <section class="claire-route-workspace-renderer" data-active-route="${state.active_route || "none"}">
      <header class="route-workspace-header">
        <div>
          <h2>Route Workspaces</h2>
          <p>Autonomous execution surfaces. Backend payload truth only.</p>
        </div>
        <div class="route-workspace-active">
          <strong>Active Route</strong>
          <span>${state.active_route || "Unavailable"}</span>
        </div>
      </header>
      <div class="route-workspace-grid">
        ${card("Portfolio Intelligence", state.portfolio, "Trend, thesis, weighting, risk, exposure, timing, and optimization outputs.")}
        ${card("Acquisition Intelligence", state.acquisition, "Moat, value capture, acquirer fit, deal rationale, and package readiness.")}
        ${card("Breakthrough / Design", state.breakthrough, "Breakthrough classification, advancement routing, AutoDesign, validation, and blueprints.")}
        ${card("Existing-System Replacement", state.existing_system, "Existing-system decomposition, superior-system design, component map, and replacement package.")}
        ${card("Governance / Update", state.governance, "Source trust, protected paths, risk class, migration plan, rollback, approval state.")}
        ${card("Recursive Learning", state.recursive, "Lifecycle memory, prior output comparison, and future-run strengthening.")}
        ${card("Evidence / Traceability", state.evidence, "Evidence basis, source lineage, score support, skipped-stage reasons, and proof trail.")}
      </div>
    </section>
  `;
}
