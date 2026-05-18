/* Claire Syntalion v19.68 Loading State Helpers */

window.ClaireCockpitLoadingState = (() => {
  function render(message) {
    return `
      <div class="cockpit-loading-state">
        <span class="loading-dot"></span>
        <span>${message || "Loading..."}</span>
      </div>
    `;
  }

  return { render };
})();
