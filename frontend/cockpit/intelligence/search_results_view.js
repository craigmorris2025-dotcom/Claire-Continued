
/* Claire Syntalion v19.69 Search Results View */
window.ClaireSearchResultsView = (() => {
  function escapeHtml(value) {
    return String(value || "").replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;").replaceAll("'", "&#039;");
  }

  function renderResult(result) {
    const status = result.allowed ? "allowed preview" : "blocked/unavailable";
    return '<article class="search-result-card"><div class="search-result-type">' + escapeHtml(result.type || "result") + " · " + status + '</div><h4>' + escapeHtml(result.title || "Untitled") + '</h4><p>' + escapeHtml(result.detail || result.message || "") + '</p></article>';
  }

  function render(container, response) {
    if (!container) return;
    if (!response) {
      container.innerHTML = '<div class="search-empty-state">No search has run yet.</div>';
      return;
    }
    if (response.blocked) {
      container.innerHTML = '<div class="search-blocked-state"><strong>' + escapeHtml(response.title || "Unavailable") + '</strong><p>' + escapeHtml(response.message || "This search mode is not available yet.") + '</p></div>';
      return;
    }
    const results = response.results || [];
    if (!results.length) {
      container.innerHTML = '<div class="search-empty-state">' + escapeHtml(response.message || "No results.") + '</div>';
      return;
    }
    container.innerHTML = '<div class="search-response-summary"><strong>' + escapeHtml(response.title || "Search complete") + '</strong><span>' + escapeHtml(response.message || "") + '</span></div><div class="search-results-list">' + results.map(renderResult).join("") + '</div>';
  }

  return { render };
})();
