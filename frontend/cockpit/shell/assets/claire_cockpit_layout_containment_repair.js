/*
Claire Syntalion v19.82B.12.1
Cockpit Layout Containment Repair

Presentation-only shell detector.
Adds CSS helper classes so containment CSS can reserve space for sidebar/nav.
Does not read or mutate runtime truth.
*/

(function () {
  "use strict";

  const BUILD = "v19.82B.12.1";

  function detectSidebarNav() {
    const selectors = [
      ".sidebar",
      ".side-nav",
      ".cockpit-sidebar",
      ".claire-sidebar",
      "#sidebar",
      "#side-nav",
      "#claire-sidebar",
      "aside",
      "nav"
    ];

    const found = selectors.some((selector) => {
      const el = document.querySelector(selector);
      if (!el) return false;

      const rect = el.getBoundingClientRect();
      const style = window.getComputedStyle(el);

      const looksLikeSidebar =
        rect.width >= 56 &&
        rect.width <= 380 &&
        rect.height >= 200 &&
        rect.left <= 40;

      const fixedOrSticky =
        style.position === "fixed" ||
        style.position === "sticky" ||
        style.position === "absolute";

      return looksLikeSidebar || fixedOrSticky;
    });

    document.body.classList.toggle("claire-has-sidebar-nav", found);

    const shell =
      document.querySelector(".claire-cockpit-shell") ||
      document.querySelector(".cockpit-shell") ||
      document.querySelector(".enterprise-cockpit-shell") ||
      document.getElementById("claire-cockpit-shell") ||
      document.getElementById("cockpit-shell");

    if (shell) {
      const style = window.getComputedStyle(shell);
      document.body.classList.toggle(
        "claire-grid-shell-detected",
        style.display === "grid" || shell.children.length >= 2
      );
    }

    document.body.setAttribute("data-claire-layout-containment", BUILD);
  }

  function scheduleDetect() {
    window.requestAnimationFrame(detectSidebarNav);
    window.setTimeout(detectSidebarNav, 250);
    window.setTimeout(detectSidebarNav, 1000);
  }

  window.ClaireCockpitLayoutContainmentRepair = {
    version: BUILD,
    detectSidebarNav
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", scheduleDetect);
  } else {
    scheduleDetect();
  }

  window.addEventListener("resize", scheduleDetect);
})();
