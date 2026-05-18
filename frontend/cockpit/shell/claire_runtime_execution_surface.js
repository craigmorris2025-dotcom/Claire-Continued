/*
Claire Syntalion v19.89.5
Runtime Execution Contract Cockpit Surface
*/
(function () {
  const SURFACE_ID = "claire-runtime-execution-surface";
  const API_SUMMARY = "/system/runtime-execution/summary";
  const API_STAGES = "/system/runtime-execution/stages";

  function el(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined && text !== null) node.textContent = String(text);
    return node;
  }

  function findMount() {
    return document.querySelector("[data-runtime-execution-surface]")
      || document.querySelector("#operator-event-trail")
      || document.querySelector("#safe-operator-action-console")
      || document.querySelector("main")
      || document.body;
  }

  function ensureSurface() {
    let surface = document.getElementById(SURFACE_ID);
    if (surface) return surface;
    surface = el("section", "claire-runtime-execution-surface");
    surface.id = SURFACE_ID;
    surface.innerHTML = `
      <div class="runtime-execution-header">
        <div>
          <div class="runtime-execution-kicker">RUNTIME EXECUTION CONTRACT</div>
          <h2>Runtime Execution Truth</h2>
        </div>
        <div class="runtime-execution-pill" data-runtime-execution-state>Checking backend</div>
      </div>
      <div class="runtime-execution-grid">
        <div class="runtime-execution-card"><div class="runtime-execution-label">Terminal State</div><div class="runtime-execution-value" data-runtime-terminal-state>-</div></div>
        <div class="runtime-execution-card"><div class="runtime-execution-label">Route</div><div class="runtime-execution-value" data-runtime-route>-</div></div>
        <div class="runtime-execution-card"><div class="runtime-execution-label">Stages</div><div class="runtime-execution-value" data-runtime-stage-count>-</div></div>
        <div class="runtime-execution-card"><div class="runtime-execution-label">Truth Source</div><div class="runtime-execution-value" data-runtime-truth-source>Backend</div></div>
      </div>
      <div class="runtime-execution-summary" data-runtime-summary>Waiting for runtime execution contract.</div>
      <div class="runtime-execution-stage-list" data-runtime-stage-list></div>
    `;
    const mount = findMount();
    if (mount === document.body) document.body.appendChild(surface);
    else mount.insertAdjacentElement("afterend", surface);
    return surface;
  }

  async function getJson(path) {
    const response = await fetch(path, { cache: "no-store" });
    if (!response.ok) throw new Error(`${path} returned ${response.status}`);
    return response.json();
  }

  function renderSummary(surface, summary) {
    surface.querySelector("[data-runtime-execution-state]").textContent = summary.runtime_truth_available ? "Runtime truth loaded" : "Contract ready";
    surface.querySelector("[data-runtime-terminal-state]").textContent = summary.terminal_state || "unknown";
    surface.querySelector("[data-runtime-route]").textContent = summary.route || "unknown";
    surface.querySelector("[data-runtime-stage-count]").textContent = summary.stage_count ?? "-";
    surface.querySelector("[data-runtime-truth-source]").textContent = summary.runtime_truth_available ? "core_run_output.json" : "contract only";
    surface.querySelector("[data-runtime-summary]").textContent = summary.summary || "No runtime summary returned.";
  }

  function renderStages(surface, payload) {
    const list = surface.querySelector("[data-runtime-stage-list]");
    list.innerHTML = "";
    const stages = Array.isArray(payload.stages) ? payload.stages.slice(0, 30) : [];
    if (!stages.length) {
      list.appendChild(el("div", "runtime-execution-empty", "No lifecycle stage truth returned yet."));
      return;
    }
    stages.forEach((stage, idx) => {
      const row = el("div", "runtime-execution-stage-row");
      const index = stage.index || stage.stage || idx + 1;
      const name = stage.name || stage.stage_name || stage.title || `Stage ${index}`;
      const status = stage.status || stage.state || "unknown";
      row.innerHTML = `
        <div class="runtime-execution-stage-index">${index}</div>
        <div class="runtime-execution-stage-main">
          <div class="runtime-execution-stage-name"></div>
          <div class="runtime-execution-stage-reason"></div>
        </div>
        <div class="runtime-execution-stage-status"></div>
      `;
      row.querySelector(".runtime-execution-stage-name").textContent = name;
      row.querySelector(".runtime-execution-stage-status").textContent = status;
      row.querySelector(".runtime-execution-stage-reason").textContent = stage.reason || stage.route_applicability || stage.notes || "";
      list.appendChild(row);
    });
  }

  async function refreshRuntimeExecutionSurface() {
    const surface = ensureSurface();
    try {
      const [summary, stages] = await Promise.all([getJson(API_SUMMARY), getJson(API_STAGES)]);
      renderSummary(surface, summary);
      renderStages(surface, stages);
      surface.dataset.status = "ok";
    } catch (error) {
      surface.dataset.status = "error";
      surface.querySelector("[data-runtime-execution-state]").textContent = "Backend unavailable";
      surface.querySelector("[data-runtime-summary]").textContent = "Runtime execution surface failed closed: " + error.message;
    }
  }

  window.ClaireRuntimeExecutionSurface = { refresh: refreshRuntimeExecutionSurface, version: "v19.89.5" };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", refreshRuntimeExecutionSurface);
  else refreshRuntimeExecutionSurface();
})();
