
/* Claire Syntalion v19.69 Search Panel */
window.ClaireSearchPanel = (() => {
  function renderInto(container) {
    if (!container) return;
    const modes = window.ClaireSearchStateModel.getModes();
    const active = window.ClaireSearchStateModel.getState().activeMode;

    container.innerHTML = `
      <article class="search-command-panel">
        <header class="search-panel-header">
          <div><div class="section-kicker">Permanent Core Surface</div><h3>Claire Command Surface</h3></div>
          <div class="search-provider-summary">${window.ClaireProviderStatusView.summarize()}</div>
        </header>
        <div class="search-mode-tabs">
          ${modes.map((mode) => `<button class="search-mode-tab ${mode.id === active ? "active" : ""}" data-search-mode="${mode.id}">${mode.label}</button>`).join("")}
        </div>
        <div class="search-input-row">
          <input id="search-panel-input" class="search-panel-input" type="search" placeholder="Search or command Claire..." />
          <button id="search-panel-run" class="search-run-button">Run</button>
        </div>
        ${window.ClaireSourceTrustBadges.renderUnavailable()}
        <div class="search-mode-note" id="search-mode-note"></div>
        <section id="search-results" class="search-results"></section>
        <footer class="search-panel-footer">Web/research/agent modes show truthful blocked states until backend wiring is enabled.</footer>
      </article>
    `;

    bind(container);
    updateModeNote();
  }

  function bind(container) {
    container.querySelectorAll("[data-search-mode]").forEach((button) => {
      button.addEventListener("click", () => {
        window.ClaireSearchStateModel.setActiveMode(button.dataset.searchMode);
        renderInto(container);
      });
    });
    const run = container.querySelector("#search-panel-run");
    if (run) run.addEventListener("click", () => window.ClaireCommandSurface.runFromPanel());
  }

  function updateModeNote() {
    const note = document.getElementById("search-mode-note");
    if (!note) return;
    const state = window.ClaireSearchStateModel.getState();
    const mode = window.ClaireSearchStateModel.getMode(state.activeMode);
    note.textContent = mode.enabled ? mode.id + " enabled." : "Blocked: " + mode.unavailableReason;
  }

  return { renderInto };
})();
