// Claire Syntalion v19.70 — Runtime Workspace Composer
// Consumes shared payload adapter only. Does not fetch directly unless an approved apiClient is passed through shell context.

import { createRuntimeStatusPanel } from "./runtime_status_panel.js";
import { createLifecyclePanel } from "./lifecycle_panel.js";
import { createRunHistoryPanel } from "./run_history_panel.js";
import { createRuntimeTruthPanel } from "./runtime_truth_panel.js";

export function createRuntimeWorkspace(context = {}) {
  const panels = {
    status: createRuntimeStatusPanel(context),
    lifecycle: createLifecyclePanel(context),
    history: createRunHistoryPanel(context),
    truth: createRuntimeTruthPanel(context),
  };

  async function mount(container) {
    if (!container) return;
    container.innerHTML = `
      <main class="runtime-workspace" data-claire-workspace="runtime">
        <div id="runtime-status-panel"></div>
        <div id="lifecycle-panel"></div>
        <div id="run-history-panel"></div>
        <div id="runtime-truth-panel"></div>
      </main>
    `;

    const [status, lifecycle, history, truth] = await Promise.all([
      panels.status.load(),
      panels.lifecycle.load(),
      panels.history.load(),
      panels.truth.load(),
    ]);

    panels.status.render(container.querySelector("#runtime-status-panel"), status);
    panels.lifecycle.render(container.querySelector("#lifecycle-panel"), lifecycle);
    panels.history.render(container.querySelector("#run-history-panel"), history);
    panels.truth.render(container.querySelector("#runtime-truth-panel"), truth);
  }

  return { mount, panels };
}

export default createRuntimeWorkspace;
