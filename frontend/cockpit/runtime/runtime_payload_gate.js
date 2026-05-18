/*
Claire Syntalion v19.73
Runtime Payload Gate Bridge

This module connects the cockpit runtime workspace to canonical backend payload
availability checks without fabricating data.

It expects:
- an apiClient with get(route)
- optional payloadAdapter with load/fetch canonical payload behavior

It returns truthful blocked/unavailable states when backend payload is not available.
*/

import { checkClairePayloadRoutes } from "../shared/payload_route_guard.js";
import { classifyRuntimePayloadForRendering } from "./runtime_render_gate.js";

export async function buildRuntimeWorkspaceGateState({ apiClient, payloadAdapter } = {}) {
  const gate = {
    ok: false,
    version: "v19.73",
    checked_at: new Date().toISOString(),
    bridge_state: "blocked",
    payload_routes: null,
    render_gate: null,
    payload: null,
    reason: "not_checked",
  };

  const routeState = await checkClairePayloadRoutes(apiClient);
  gate.payload_routes = routeState;

  if (!routeState.ok) {
    gate.bridge_state = "blocked";
    gate.reason = "canonical_payload_routes_unavailable";
    gate.render_gate = classifyRuntimePayloadForRendering(null);
    return gate;
  }

  let payload = null;

  try {
    if (payloadAdapter && typeof payloadAdapter.loadCanonicalPayload === "function") {
      payload = await payloadAdapter.loadCanonicalPayload();
    } else if (payloadAdapter && typeof payloadAdapter.fetchCanonicalPayload === "function") {
      payload = await payloadAdapter.fetchCanonicalPayload();
    } else if (apiClient && typeof apiClient.get === "function") {
      payload = await apiClient.get("/dashboard/payload");
    }
  } catch (error) {
    gate.bridge_state = "blocked";
    gate.reason = "canonical_payload_fetch_failed";
    gate.error = String(error && error.message ? error.message : error);
    gate.render_gate = classifyRuntimePayloadForRendering(null);
    return gate;
  }

  gate.payload = payload || null;
  gate.render_gate = classifyRuntimePayloadForRendering(payload);
  gate.ok = Boolean(routeState.ok && gate.render_gate && gate.render_gate.ok);
  gate.bridge_state = gate.ok ? "unblocked" : "truthfully_empty";
  gate.reason = gate.ok ? "runtime_payload_renderable" : "payload_available_but_runtime_surfaces_unavailable";
  return gate;
}

export function renderRuntimeGateSummary(target, state) {
  if (!target) return;

  const safeState = state || {
    ok: false,
    bridge_state: "blocked",
    reason: "state_missing",
    render_gate: null,
  };

  const panelStates = safeState.render_gate && safeState.render_gate.panels
    ? safeState.render_gate.panels
    : {
        runtime_status: "blocked",
        lifecycle: "blocked",
        run_history: "blocked",
        runtime_truth: "blocked",
      };

  target.innerHTML = `
    <section class="runtime-gate-summary" data-bridge-state="${safeState.bridge_state}">
      <div class="runtime-gate-header">
        <h3>Runtime Payload Gate</h3>
        <span>${safeState.bridge_state || "blocked"}</span>
      </div>
      <p>${safeState.reason || "No runtime payload state available."}</p>
      <div class="runtime-gate-grid">
        <div><strong>Runtime Status</strong><span>${panelStates.runtime_status}</span></div>
        <div><strong>Lifecycle</strong><span>${panelStates.lifecycle}</span></div>
        <div><strong>Run History</strong><span>${panelStates.run_history}</span></div>
        <div><strong>Runtime Truth</strong><span>${panelStates.runtime_truth}</span></div>
      </div>
    </section>
  `;
}
