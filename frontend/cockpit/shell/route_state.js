/* Claire Syntalion v19.67 Route State */
/* Local route state only; no backend truth is created here. */

window.ClaireCockpitRouteState = (() => {
  const defaultPanel = "runtime";

  function currentPanelId() {
    const params = new URLSearchParams(window.location.hash.replace(/^#/, ""));
    return params.get("panel") || defaultPanel;
  }

  function setPanelId(panelId) {
    const params = new URLSearchParams(window.location.hash.replace(/^#/, ""));
    params.set("panel", panelId);
    window.location.hash = params.toString();
  }

  return { currentPanelId, setPanelId };
})();
