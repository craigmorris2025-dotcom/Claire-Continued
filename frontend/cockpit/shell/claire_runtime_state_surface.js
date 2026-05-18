/* Claire Syntalion v19.89.6 Runtime State Cockpit Surface */
(function () {
  const SURFACE_ID = "claire-runtime-state-surface";
  const API = "/system/runtime-state/summary";

  function findMount() {
    return document.getElementById("claire-runtime-execution-surface")
      || document.querySelector("[data-runtime-state-surface]")
      || document.querySelector("main")
      || document.body;
  }

  function ensureSurface() {
    let surface = document.getElementById(SURFACE_ID);
    if (surface) return surface;

    surface = document.createElement("section");
    surface.id = SURFACE_ID;
    surface.className = "claire-runtime-state-surface";
    surface.innerHTML = `
      <div class="runtime-state-header">
        <div>
          <div class="runtime-state-kicker">RUNTIME STATE EMITTER</div>
          <h2>Backend Runtime State</h2>
        </div>
        <div class="runtime-state-pill" data-runtime-state-mode>Checking backend</div>
      </div>
      <div class="runtime-state-grid">
        <div class="runtime-state-card"><div class="runtime-state-label">Session State</div><div class="runtime-state-value" data-runtime-session-state>-</div></div>
        <div class="runtime-state-card"><div class="runtime-state-label">Execution Mode</div><div class="runtime-state-value" data-runtime-execution-mode>-</div></div>
        <div class="runtime-state-card"><div class="runtime-state-label">Route</div><div class="runtime-state-value" data-runtime-route-state>-</div></div>
        <div class="runtime-state-card"><div class="runtime-state-label">Review Queue</div><div class="runtime-state-value" data-runtime-review-state>-</div></div>
      </div>
      <div class="runtime-state-note" data-runtime-state-note>Waiting for backend runtime state.</div>
    `;

    const mount = findMount();
    if (mount === document.body) {
      document.body.appendChild(surface);
    } else {
      mount.insertAdjacentElement("afterend", surface);
    }
    return surface;
  }

  async function refreshRuntimeStateSurface() {
    const surface = ensureSurface();
    try {
      const response = await fetch(API, { cache: "no-store" });
      if (!response.ok) throw new Error(`${API} returned ${response.status}`);
      const payload = await response.json();
      const session = payload.runtime_session || {};
      const route = payload.route_state || {};
      const review = payload.review_queue_state || {};
      surface.querySelector("[data-runtime-state-mode]").textContent = payload.autonomous_loop_enabled ? "Autonomous loop enabled" : "State emission only";
      surface.querySelector("[data-runtime-session-state]").textContent = session.state || "unknown";
      surface.querySelector("[data-runtime-execution-mode]").textContent = payload.execution_mode || "unknown";
      surface.querySelector("[data-runtime-route-state]").textContent = `${route.selected_route || "unknown"} / ${route.terminal_state || "unknown"}`;
      surface.querySelector("[data-runtime-review-state]").textContent = review.enabled ? `${review.pending_items || 0} pending` : "not wired";
      surface.querySelector("[data-runtime-state-note]").textContent = route.reason || review.reason || "Runtime state emitted successfully.";
      surface.dataset.status = "ok";
    } catch (error) {
      surface.dataset.status = "error";
      surface.querySelector("[data-runtime-state-mode]").textContent = "Backend unavailable";
      surface.querySelector("[data-runtime-state-note]").textContent = "Runtime state surface failed closed: " + error.message;
    }
  }

  window.ClaireRuntimeStateSurface = { version: "v19.89.6", refresh: refreshRuntimeStateSurface };
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", refreshRuntimeStateSurface);
  } else {
    refreshRuntimeStateSurface();
  }
})();
