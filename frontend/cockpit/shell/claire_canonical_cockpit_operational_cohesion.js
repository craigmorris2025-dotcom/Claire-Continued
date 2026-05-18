
(function () {
  "use strict";

  const VERSION = "v19.89.8-S10";

  const state = {
    version: VERSION,
    backend_owns_truth: true,
    cockpit_presentation_only: true,
    runtime_authority_expanded: false,
    safe_to_expand_runtime_authority: false,
    canonical_operational_state: "unavailable",
    cohesion_applied: false,
    updated_nodes: 0
  };

  async function fetchJson(route) {
    try {
      const response = await fetch(route, {
        method: "GET",
        headers: { "Accept": "application/json" },
        cache: "no-store"
      });

      let data = null;

      try {
        data = await response.json();
      } catch (err) {
        data = {};
      }

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
    const payload = await fetchJson("/dashboard/payload/status");
    const runtime = await fetchJson("/system/runtime-state/summary");

    if (payload.ok && runtime.ok) {
      return "live";
    }

    if (payload.ok || runtime.ok) {
      return "degraded";
    }

    return "unavailable";
  }

  function canonicalLabel(stateValue) {
    if (stateValue === "live") return "Live";
    if (stateValue === "degraded") return "Degraded";
    return "Unavailable";
  }

  function candidateNodes() {
    return Array.from(document.querySelectorAll(
      "div, span, p, h1, h2, h3, h4, section, article"
    ));
  }

  function shouldNormalize(text) {
    const lowered = text.toLowerCase();

    return (
      lowered.includes("connected") ||
      lowered.includes("available") ||
      lowered.includes("complete") ||
      lowered.includes("active") ||
      lowered.includes("healthy") ||
      lowered.includes("live") ||
      lowered.includes("degraded") ||
      lowered.includes("offline") ||
      lowered.includes("unavailable") ||
      lowered.includes("failed") ||
      lowered.includes("backend unavailable") ||
      lowered.includes("backend connected")
    );
  }

  function applyOperationalTruth(operationalState) {
    let updated = 0;

    for (const node of candidateNodes()) {
      if (!node || node.children.length > 0) continue;

      const text = (node.innerText || "").trim();

      if (!text || text.length > 40) continue;

      if (!shouldNormalize(text)) continue;

      const label = canonicalLabel(operationalState);

      node.textContent = label;

      node.setAttribute(
        "data-claire-s10-operational-state",
        operationalState
      );

      updated += 1;
    }

    document.documentElement.setAttribute(
      "data-claire-operational-state",
      operationalState
    );

    document.documentElement.setAttribute(
      "data-claire-runtime-authority-expanded",
      "false"
    );

    state.updated_nodes = updated;
    state.cohesion_applied = true;
  }

  async function run() {
    const operationalState = await collect();

    state.canonical_operational_state = operationalState;

    applyOperationalTruth(operationalState);

    window.ClaireCanonicalCockpitOperationalCohesion = state;

    return state;
  }

  window.ClaireCanonicalCockpitOperationalCohesionTools = {
    version: VERSION,
    run,
    state
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", run);
  } else {
    run();
  }

  setInterval(run, 30000);
})();
