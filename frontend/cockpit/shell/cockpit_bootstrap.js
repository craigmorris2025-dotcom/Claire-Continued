/* Claire Syntalion v19.68 Cockpit Bootstrap */
/* Uses shared api_client + payload_adapter only. */

(function bootstrapClaireCockpit() {
  const bootState = {
    version: "v19.69",
    runtimeBehaviorChanged: false,
    fetchesEnabled: true,
    fetchOwner: "frontend/cockpit/shared/payload_adapter.js",
    launcherRewired: false,
    routesModified: false,
    truthfulState: "search-command-surface-wired"
  };

  window.ClaireCockpitBootState = bootState;

  function setStatusElement(id, entry, label) {
    const el = document.getElementById(id);
    if (!el || !window.ClaireCockpitStatusModel) return;
    el.textContent = window.ClaireCockpitStatusModel.labelFor(entry, label);
    el.className = window.ClaireCockpitStatusModel.classFor(entry);
    el.title = window.ClaireCockpitStatusModel.explain(entry);
  }

  function renderAdapterState() {
    if (!window.ClaireCockpitPayloadAdapter) return;
    const state = window.ClaireCockpitPayloadAdapter.getState();
    setStatusElement("cockpit-runtime-status", state.status, "Status");
    setStatusElement("cockpit-payload-status", state.payload, "Payload");

    const workspaceState = document.getElementById("workspace-state");
    if (workspaceState) {
      if (state.status.ok && state.payload.ok) {
        workspaceState.textContent = "canonical payload loaded through shared adapter";
      } else if (state.status.loaded && !state.status.ok) {
        workspaceState.textContent = "backend status unavailable — truthful blocked state";
      } else {
        workspaceState.textContent = "shared adapter initialized";
      }
    }
  }

  async function bootPayloadAdapter() {
    renderAdapterState();
    if (!window.ClaireCockpitPayloadAdapter) return;
    await window.ClaireCockpitPayloadAdapter.refreshAll();
    renderAdapterState();
  }

  window.addEventListener("claire:payload-adapter", renderAdapterState);

  document.addEventListener("DOMContentLoaded", () => {
    window.ClaireCockpitWorkspaceManager.bindNavigation();
    window.ClaireCockpitWorkspaceManager.render(window.ClaireCockpitRouteState.currentPanelId());
    bootPayloadAdapter();
    if (window.ClaireCommandSurface) window.ClaireCommandSurface.mountTopbar();
  });
})();

/* Claire v19.74 Runtime Payload Gate Bootstrap */
async function claireMountRuntimePayloadGateV1974() {
  const target = document.getElementById("claire-runtime-payload-gate-mount");
  if (!target) return;

  try {
    const gateModule = await import("../runtime/runtime_payload_gate.js");
    let apiClient = null;
    let payloadAdapter = null;

    try {
      apiClient = await import("../shared/api_client.js");
    } catch (error) {
      apiClient = null;
    }

    try {
      payloadAdapter = await import("../shared/payload_adapter.js");
    } catch (error) {
      payloadAdapter = null;
    }

    const client =
      apiClient && apiClient.default
        ? apiClient.default
        : apiClient && apiClient.apiClient
          ? apiClient.apiClient
          : apiClient;

    const adapter =
      payloadAdapter && payloadAdapter.default
        ? payloadAdapter.default
        : payloadAdapter;

    const state = await gateModule.buildRuntimeWorkspaceGateState({
      apiClient: client,
      payloadAdapter: adapter,
    });

    gateModule.renderRuntimeGateSummary(target, state);
  } catch (error) {
    target.innerHTML = `
      <section class="runtime-gate-summary" data-bridge-state="blocked">
        <div class="runtime-gate-header">
          <h3>Runtime Payload Gate</h3>
          <span>blocked</span>
        </div>
        <p>Runtime payload gate could not mount. ${String(error && error.message ? error.message : error)}</p>
      </section>
    `;
  }
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", claireMountRuntimePayloadGateV1974);
} else {
  claireMountRuntimePayloadGateV1974();
}

/* Claire v19.78 Autonomous Lifecycle Bootstrap */
async function claireMountAutonomousLifecycleV1978() {
  const graphTarget = document.getElementById("claire-autonomous-lifecycle-graph-mount");
  const designTarget = document.getElementById("claire-design-route-surface-mount");
  if (!graphTarget && !designTarget) return;

  let payload = null;
  try {
    const adapter = await import("../shared/payload_adapter.js");
    if (adapter && typeof adapter.loadCanonicalPayload === "function") {
      payload = await adapter.loadCanonicalPayload();
    } else if (adapter && typeof adapter.fetchCanonicalPayload === "function") {
      payload = await adapter.fetchCanonicalPayload();
    }
  } catch (error) {
    payload = null;
  }

  try {
    const graph = await import("../runtime/autonomous_lifecycle_graph.js");
    const contract = await graph.loadCockpitLifecycleContract();
    graph.renderAutonomousLifecycleGraph(graphTarget, contract, payload);
  } catch (error) {
    if (graphTarget) {
      graphTarget.innerHTML = `<section class="claire-autonomous-lifecycle-graph"><h2>Autonomous Lifecycle Runtime</h2><p>Lifecycle graph unavailable: ${String(error && error.message ? error.message : error)}</p></section>`;
    }
  }

  try {
    const design = await import("../design/design_route_surface.js");
    design.renderDesignRouteSurface(designTarget, payload);
  } catch (error) {
    if (designTarget) {
      designTarget.innerHTML = `<section class="claire-design-route-surface"><h2>Design Route Engine</h2><p>Design route surface unavailable: ${String(error && error.message ? error.message : error)}</p></section>`;
    }
  }
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", claireMountAutonomousLifecycleV1978);
} else {
  claireMountAutonomousLifecycleV1978();
}

/* Claire v19.79 Route Workspace Bootstrap */
async function claireMountRouteWorkspacesV1979() {
  const target = document.getElementById("claire-route-workspace-renderer-mount");
  if (!target) return;

  let payload = null;
  try {
    const adapter = await import("../shared/payload_adapter.js");
    if (adapter && typeof adapter.loadCanonicalPayload === "function") {
      payload = await adapter.loadCanonicalPayload();
    } else if (adapter && typeof adapter.fetchCanonicalPayload === "function") {
      payload = await adapter.fetchCanonicalPayload();
    }
  } catch (error) {
    payload = null;
  }

  try {
    const routeRenderer = await import("../runtime/route_workspace_renderer.js");
    routeRenderer.renderRouteWorkspaces(target, payload);
  } catch (error) {
    target.innerHTML = `<section class="claire-route-workspace-renderer"><h2>Route Workspaces</h2><p>Route workspace renderer unavailable: ${String(error && error.message ? error.message : error)}</p></section>`;
  }
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", claireMountRouteWorkspacesV1979);
} else {
  claireMountRouteWorkspacesV1979();
}
