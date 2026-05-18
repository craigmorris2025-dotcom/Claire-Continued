/*
Claire Syntalion v19.72
Runtime Render Gate

Non-invasive helper for runtime workspace panels.
It never invents lifecycle state. It only classifies loaded canonical payload.
*/

export function classifyRuntimePayloadForRendering(payload) {
  const result = {
    ok: false,
    version: "v19.72",
    render_state: "blocked",
    reason: "payload_missing",
    panels: {
      runtime_status: "blocked",
      lifecycle: "blocked",
      run_history: "blocked",
      runtime_truth: "blocked",
    },
  };

  if (!payload || typeof payload !== "object") {
    return result;
  }

  const hasLifecycle =
    Array.isArray(payload.lifecycle) ||
    Array.isArray(payload.stages) ||
    Boolean(payload.lifecycle_state) ||
    Boolean(payload.runtime_lifecycle);

  const hasRuntimeStatus =
    Boolean(payload.status) ||
    Boolean(payload.runtime_status) ||
    Boolean(payload.backend_status) ||
    Boolean(payload.system_status);

  const hasRunHistory =
    Array.isArray(payload.run_history) ||
    Array.isArray(payload.runs) ||
    Boolean(payload.history);

  const hasRuntimeTruth =
    Boolean(payload.runtime_truth) ||
    Boolean(payload.evidence) ||
    Boolean(payload.truth_state) ||
    Boolean(payload.canonical_truth);

  result.panels.runtime_status = hasRuntimeStatus ? "renderable" : "truthfully_unavailable";
  result.panels.lifecycle = hasLifecycle ? "renderable" : "truthfully_unavailable";
  result.panels.run_history = hasRunHistory ? "renderable" : "truthfully_unavailable";
  result.panels.runtime_truth = hasRuntimeTruth ? "renderable" : "truthfully_unavailable";

  result.ok = hasRuntimeStatus || hasLifecycle || hasRunHistory || hasRuntimeTruth;
  result.render_state = result.ok ? "partially_renderable" : "truthfully_empty";
  result.reason = result.ok ? "canonical_payload_contains_runtime_surfaces" : "canonical_payload_has_no_runtime_surfaces";
  return result;
}
