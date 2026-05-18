/*
Claire Syntalion v19.78
Design Route Surface Foundation

Design routes are first-class. This panel renders only backend-provided design payload truth.
*/

export function normalizeDesignRoutePayload(payload) {
  const source = payload && typeof payload === "object" ? payload : {};
  const design = source.design || source.autodesign || source.design_portal || {};
  return {
    active: Boolean(source.active_route === "breakthrough_design" || source.active_route === "existing_system_replacement" || design.active),
    autodesign: design.autodesign || source.autodesign || null,
    solution_structure: design.solution_structure || source.solution_structure || null,
    buildability: design.buildability || source.buildability || null,
    viability: design.viability || source.viability || null,
    manufacturability: design.manufacturability || source.manufacturability || null,
    feasibility: design.feasibility || source.feasibility || null,
    blueprints: design.blueprints || source.blueprints || null,
    component_map: design.component_map || source.component_map || null,
    dependency_map: design.dependency_map || source.dependency_map || null,
    implementation_phases: design.implementation_phases || source.implementation_phases || null,
  };
}

export function renderDesignRouteSurface(target, payload) {
  if (!target) return;

  const state = normalizeDesignRoutePayload(payload);
  const rows = [
    ["AutoDesign", state.autodesign],
    ["Solution Structure", state.solution_structure],
    ["Buildability", state.buildability],
    ["Viability", state.viability],
    ["Manufacturability / Deployability", state.manufacturability],
    ["Feasibility", state.feasibility],
    ["Blueprints / Specs", state.blueprints],
    ["Component Map", state.component_map],
    ["Dependency Map", state.dependency_map],
    ["Implementation Phases", state.implementation_phases],
  ];

  target.innerHTML = `
    <section class="claire-design-route-surface" data-design-active="${state.active}">
      <header>
        <h2>Design Route Engine</h2>
        <p>Stages 16-22: AutoDesign, validation, and Design Portal output.</p>
      </header>
      <div class="design-route-grid">
        ${rows.map(([label, value]) => `
          <div class="design-route-card ${value ? "available" : "unavailable"}">
            <strong>${label}</strong>
            <span>${value ? "Available from payload" : "Truthfully unavailable"}</span>
          </div>
        `).join("")}
      </div>
    </section>
  `;
}
