(function () {
  "use strict";

  const DOCK_ID = "claire-operational-expansion-dock-s31r2";
  const VERSION = "v19.89.8-S31R2";

  function text(value, fallback) {
    if (value === null || value === undefined || value === "") return fallback || "unknown";
    return String(value);
  }

  function get(payload, key) {
    return payload && typeof payload === "object" && payload[key] && typeof payload[key] === "object"
      ? payload[key]
      : {};
  }

  function compute(payload) {
    const timeline = get(payload, "governed_runtime_timeline");
    const route = get(payload, "governed_route_activity_overlay");
    const presence = get(payload, "continuous_runtime_presence");
    const evidence = get(payload, "governed_evidence_basket");
    const workflow = get(payload, "governed_operator_workflow");
    const cohesion = get(payload, "multi_panel_runtime_cohesion");
    const workspace = get(payload, "governed_runtime_workspace_continuity");
    const topology = get(payload, "governed_operational_topology_continuity");

    const routeSummary = route.summary || {};
    const evidenceSummary = evidence.summary || {};
    const workflowSummary = workflow.summary || {};
    const cohesionSummary = cohesion.summary || {};
    const workspaceSummary = workspace.summary || {};
    const topologySummary = topology.summary || {};
    const timelineSummary = timeline.summary || {};

    return {
      selectedRoute: routeSummary.selected_route || workspaceSummary.selected_route || topologySummary.selected_route || "unknown",
      timelineStatus: timeline.status || "not in payload",
      routeStatus: route.status || "not in payload",
      presenceState: presence.presence_state || "not in payload",
      evidenceTotal: evidenceSummary.evidence_total || 0,
      workflowTotal: workflowSummary.workflow_total || 0,
      cohesionState: cohesion.cohesion_state || "not in payload",
      workspaceState: workspace.workspace_state || "not in payload",
      topologyState: topology.continuity_state || "not in payload",
      payloadFreshness: timelineSummary.last_payload_freshness || workspaceSummary.payload_freshness || topologySummary.payload_propagation || "unknown"
    };
  }

  function ensureDock() {
    let dock = document.getElementById(DOCK_ID);
    if (dock) return dock;

    dock = document.createElement("aside");
    dock.id = DOCK_ID;
    dock.className = "claire-operational-expansion-dock";
    dock.innerHTML = `
      <div class="dock-head">
        <div>
          <div class="dock-kicker">Claire Governed Operational Layer</div>
          <div class="dock-title">Expansion Dock Loaded</div>
        </div>
        <div class="dock-version">${VERSION}</div>
      </div>
      <div class="dock-warning">
        Presentation-only visibility bridge. Runtime authority remains blocked.
      </div>
      <div id="claire-operational-expansion-dock-grid" class="dock-grid">
        <div class="dock-card">Waiting for /dashboard/payload...</div>
      </div>
    `;

    document.body.appendChild(dock);
    document.documentElement.classList.add("claire-operational-dock-mounted");
    return dock;
  }

  function render(payload) {
    const dock = ensureDock();
    const grid = dock.querySelector("#claire-operational-expansion-dock-grid");
    const model = compute(payload || {});

    grid.innerHTML = `
      <div class="dock-card"><span>Route</span><strong>${text(model.selectedRoute, "unknown")}</strong></div>
      <div class="dock-card"><span>Timeline</span><strong>${text(model.timelineStatus, "unknown")}</strong></div>
      <div class="dock-card"><span>Route overlay</span><strong>${text(model.routeStatus, "unknown")}</strong></div>
      <div class="dock-card"><span>Presence</span><strong>${text(model.presenceState, "unknown")}</strong></div>
      <div class="dock-card"><span>Evidence</span><strong>${text(model.evidenceTotal, "0")}</strong></div>
      <div class="dock-card"><span>Workflow</span><strong>${text(model.workflowTotal, "0")}</strong></div>
      <div class="dock-card"><span>Cohesion</span><strong>${text(model.cohesionState, "unknown")}</strong></div>
      <div class="dock-card"><span>Workspace</span><strong>${text(model.workspaceState, "unknown")}</strong></div>
      <div class="dock-card"><span>Topology</span><strong>${text(model.topologyState, "unknown")}</strong></div>
      <div class="dock-card"><span>Freshness</span><strong>${text(model.payloadFreshness, "unknown")}</strong></div>
    `;
  }

  function poll() {
    fetch("/dashboard/payload", { cache: "no-store" })
      .then((response) => response.ok ? response.json() : null)
      .then((payload) => {
        if (payload) render(payload);
        else render({});
      })
      .catch(() => {
        const dock = ensureDock();
        const grid = dock.querySelector("#claire-operational-expansion-dock-grid");
        grid.innerHTML = `<div class="dock-card dock-error">Could not reach /dashboard/payload from this page.</div>`;
      });
  }

  document.addEventListener("DOMContentLoaded", function () {
    ensureDock();
    window.addEventListener("claire:canonical-payload", function (event) { render(event.detail || {}); });
    window.addEventListener("claire:payload", function (event) { render(event.detail || {}); });
    poll();
    setInterval(poll, 8000);
  });

  window.ClaireOperationalExpansionDock = {
    version: VERSION,
    authority: "presentation_only_runtime_authority_blocked",
    render
  };
})();
