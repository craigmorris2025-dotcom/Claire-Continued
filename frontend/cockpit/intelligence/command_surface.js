
/* Claire Syntalion v19.69 Claire Command Surface */
window.ClaireCommandSurface = (() => {
  function mountTopbar() {
    const input = document.getElementById("claire-command-input");
    const status = document.querySelector(".command-status");
    if (!input) return;

    input.disabled = false;
    input.placeholder = "Search runtime/project state or preview commands. Web/research modes remain governed.";
    if (status) status.textContent = "v19.69 command surface active — no fake web results.";

    input.addEventListener("input", () => window.ClaireSearchStateModel.setQuery(input.value));
    input.addEventListener("keydown", async (event) => {
      if (event.key !== "Enter") return;
      event.preventDefault();
      const state = window.ClaireSearchStateModel.getState();
      await runSearch(state.activeMode, input.value);
    });
  }

  async function runSearch(modeId, query) {
    const response = await window.ClaireSearchModeRouter.run(modeId, query);
    const resultsContainer = document.getElementById("search-results");
    window.ClaireSearchResultsView.render(resultsContainer, response);
    if (response.ok) window.ClaireSearchStateModel.setResults(response.results || []);
    else window.ClaireSearchStateModel.setError(response.message || response.title);
    return response;
  }

  function runFromPanel() {
    const state = window.ClaireSearchStateModel.getState();
    const panelInput = document.getElementById("search-panel-input");
    const query = panelInput ? panelInput.value : state.query;
    return runSearch(state.activeMode, query);
  }

  return { mountTopbar, runSearch, runFromPanel };
})();
