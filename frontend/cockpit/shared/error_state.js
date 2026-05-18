/* Claire Syntalion v19.68 Error State Helpers */

window.ClaireCockpitErrorState = (() => {
  function render(message) {
    return `
      <div class="cockpit-error-state">
        <strong>Unavailable</strong>
        <p>${message || "Backend data is not available yet."}</p>
      </div>
    `;
  }

  return { render };
})();
