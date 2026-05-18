/* BEGIN CLAIRE_S359_S365_EXPANSION_DOCK_REMOVAL */
(function () {
  "use strict";

  const selectors = [
    "#expansion-dock",
    "#expansionDock",
    ".expansion-dock",
    ".expansionDock",
    "[data-claire-panel='expansion_dock']",
    "[data-claire-panel='expansion-dock']",
    "[data-panel='expansion-dock']",
    "[data-panel='expansion_dock']",
    "[id*='expansion'][id*='dock']",
    "[class*='expansion'][class*='dock']",
    "[aria-label='Expansion Dock']",
    "[aria-label='expansion dock']"
  ];

  function removeExpansionDock() {
    const seen = new Set();
    selectors.forEach((selector) => {
      document.querySelectorAll(selector).forEach((node) => {
        if (seen.has(node)) return;
        seen.add(node);
        node.setAttribute("data-claire-expansion-dock-removed", "true");
        node.setAttribute("aria-hidden", "true");
        node.style.display = "none";
        node.style.visibility = "hidden";
        node.style.pointerEvents = "none";
      });
    });

    document.querySelectorAll("aside, section, div, nav").forEach((node) => {
      const label = `${node.getAttribute("aria-label") || ""} ${node.id || ""} ${node.className || ""} ${node.textContent || ""}`.toLowerCase();
      if (label.includes("expansion dock")) {
        node.setAttribute("data-claire-expansion-dock-removed", "true");
        node.setAttribute("aria-hidden", "true");
        node.style.display = "none";
        node.style.visibility = "hidden";
        node.style.pointerEvents = "none";
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", removeExpansionDock);
  } else {
    removeExpansionDock();
  }

  const observer = new MutationObserver(removeExpansionDock);
  observer.observe(document.documentElement, { childList: true, subtree: true });
  window.ClaireExpansionDockRemoved = true;
})();
/* END CLAIRE_S359_S365_EXPANSION_DOCK_REMOVAL */
