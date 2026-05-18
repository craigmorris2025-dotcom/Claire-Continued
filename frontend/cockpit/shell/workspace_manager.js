/* Claire Syntalion v19.67 Workspace Manager */
/* Renders truthful empty shell states only. No live fetches in v19.67. */

window.ClaireCockpitWorkspaceManager = (() => {
  function cardTemplate(card) {
    const [id, title, description] = card;
    return `
      <article class="panel-card" data-card-id="${id}">
        <h3>${title}</h3>
        <p>${description}</p>
        <div class="panel-meta">Status: awaiting shared adapter / backend wiring</div>
      </article>
    `;
  }

  function render(panelId) {
    const panel = window.ClaireCockpitPanelRegistry.find(panelId);
    const title = document.getElementById("workspace-title");
    const grid = document.getElementById("panel-grid");
    const state = document.getElementById("workspace-state");

    if (title) title.textContent = panel.title;
    if (state) state.textContent = `${panel.module} workspace — truthful empty shell`;
    if (grid) grid.innerHTML = panel.cards.map(cardTemplate).join("");

    if (panel.id === "intelligence" && window.ClaireSearchPanel) {
      const commandCard = grid.querySelector(\'[data-card-id="command-surface"]\');
      if (commandCard) window.ClaireSearchPanel.renderInto(commandCard);
    }

    document.querySelectorAll(".nav-item").forEach((button) => {
      button.classList.toggle("active", button.dataset.panelTarget === panel.id);
    });
  }

  function bindNavigation() {
    document.querySelectorAll("[data-panel-target]").forEach((button) => {
      button.addEventListener("click", () => {
        const panelId = button.dataset.panelTarget;
        window.ClaireCockpitRouteState.setPanelId(panelId);
        render(panelId);
      });
    });

    window.addEventListener("hashchange", () => {
      render(window.ClaireCockpitRouteState.currentPanelId());
    });
  }

  return { render, bindNavigation };
})();
