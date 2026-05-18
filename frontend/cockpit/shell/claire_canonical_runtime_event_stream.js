
(function () {
  "use strict";

  const VERSION = "v19.89.8-S13";

  const ROUTES = {
    payloadStatus: "/dashboard/payload/status",
    runtimeState: "/system/runtime-state/summary",
    runtimeExecution: "/system/runtime-execution/summary"
  };

  const stream = {
    version: VERSION,
    backend_owns_truth: true,
    cockpit_presentation_only: true,
    runtime_authority_expanded: false,
    safe_to_expand_runtime_authority: false,
    event_count: 0,
    last_event_at: null,
    current_state: "unknown",
    events: []
  };

  let previousSignature = null;

  async function fetchJson(route) {
    try {
      const response = await fetch(route, {
        method: "GET",
        headers: { "Accept": "application/json" },
        cache: "no-store"
      });

      let data = {};

      try {
        data = await response.json();
      } catch (err) {}

      return {
        ok: response.ok,
        status: response.status,
        data
      };

    } catch (err) {
      return {
        ok: false,
        error: String(err)
      };
    }
  }

  async function collect() {
    const out = {};

    for (const [key, route] of Object.entries(ROUTES)) {
      out[key] = await fetchJson(route);
    }

    return out;
  }

  function signature(snapshot) {
    return JSON.stringify({
      payload: snapshot.payloadStatus && snapshot.payloadStatus.status,
      runtime: snapshot.runtimeState && snapshot.runtimeState.status,
      execution: snapshot.runtimeExecution && snapshot.runtimeExecution.status
    });
  }

  function determineState(snapshot) {
    const payloadOk = snapshot.payloadStatus && snapshot.payloadStatus.ok;
    const runtimeOk = snapshot.runtimeState && snapshot.runtimeState.ok;
    const executionOk = snapshot.runtimeExecution && snapshot.runtimeExecution.ok;

    if (payloadOk && runtimeOk && executionOk) {
      return "live";
    }

    if (payloadOk || runtimeOk || executionOk) {
      return "degraded";
    }

    return "unavailable";
  }

  function pushEvent(type, detail) {
    stream.events.unshift({
      at: new Date().toISOString(),
      type,
      detail
    });

    stream.events = stream.events.slice(0, 25);

    stream.event_count += 1;
    stream.last_event_at = new Date().toISOString();
  }

  function ensurePanel() {
    let panel = document.querySelector("[data-claire-s13-event-stream-panel]");

    if (!panel) {
      panel = document.createElement("section");

      panel.setAttribute(
        "data-claire-s13-event-stream-panel",
        "true"
      );

      panel.style.marginTop = "16px";
      panel.style.padding = "12px";
      panel.style.border = "1px solid rgba(255,255,255,0.1)";
      panel.style.borderRadius = "10px";
      panel.style.background = "rgba(255,255,255,0.03)";

      const anchor =
        document.querySelector("main") ||
        document.querySelector("[class*=content]") ||
        document.body;

      anchor.appendChild(panel);
    }

    return panel;
  }

  function render() {
    const panel = ensurePanel();

    panel.innerHTML = "";

    const title = document.createElement("h3");
    title.textContent = "Canonical Runtime Event Stream";
    panel.appendChild(title);

    const pre = document.createElement("pre");

    pre.style.whiteSpace = "pre-wrap";
    pre.style.maxHeight = "320px";
    pre.style.overflow = "auto";

    pre.textContent = JSON.stringify({
      version: stream.version,
      current_state: stream.current_state,
      event_count: stream.event_count,
      last_event_at: stream.last_event_at,
      events: stream.events,
      runtime_authority_expanded: false
    }, null, 2);

    panel.appendChild(pre);

    document.documentElement.setAttribute(
      "data-claire-runtime-event-stream",
      stream.current_state
    );
  }

  async function run() {
    const snapshot = await collect();

    const currentSignature = signature(snapshot);

    const newState = determineState(snapshot);

    if (previousSignature !== null && previousSignature !== currentSignature) {
      pushEvent("runtime_transition", {
        from_signature: previousSignature,
        to_signature: currentSignature
      });
    }

    if (stream.current_state !== newState) {
      pushEvent("state_change", {
        from: stream.current_state,
        to: newState
      });
    }

    stream.current_state = newState;

    previousSignature = currentSignature;

    render();

    window.ClaireCanonicalRuntimeEventStream = stream;

    return stream;
  }

  window.ClaireCanonicalRuntimeEventStreamTools = {
    version: VERSION,
    run,
    stream
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", run);
  } else {
    run();
  }

  setInterval(run, 15000);
})();
