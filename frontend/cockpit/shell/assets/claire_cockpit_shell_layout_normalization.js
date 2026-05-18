/*
Claire Syntalion v19.82B.12.2
Cockpit Shell Layout Normalization

Presentation-only layout detector.
No backend calls.
No runtime truth reads.
No runtime truth mutation.
*/

(function () {
  "use strict";

  const BUILD = "v19.82B.12.2";

  function hasElement(selectors) {
    return selectors.some((selector) => document.querySelector(selector));
  }

  function detectShellRelationship() {
    const shell =
      document.querySelector(".claire-cockpit-shell") ||
      document.querySelector(".cockpit-shell") ||
      document.querySelector(".enterprise-cockpit-shell") ||
      document.querySelector(".cockpit-layout") ||
      document.querySelector(".claire-cockpit-layout") ||
      document.getElementById("claire-cockpit-shell") ||
      document.getElementById("cockpit-shell") ||
      document.getElementById("cockpit-layout");

    const main =
      document.querySelector("main") ||
      document.querySelector("[role='main']") ||
      document.querySelector(".claire-cockpit-main") ||
      document.querySelector(".cockpit-main") ||
      document.querySelector(".enterprise-cockpit-main") ||
      document.getElementById("claire-cockpit-main") ||
      document.getElementById("cockpit-main");

    const rail =
      document.querySelector(".workspace-sidebar") ||
      document.querySelector(".workspace-nav") ||
      document.querySelector(".cockpit-sidebar") ||
      document.querySelector(".claire-sidebar") ||
      document.querySelector(".sidebar") ||
      document.querySelector(".side-nav") ||
      document.getElementById("claire-sidebar") ||
      document.getElementById("sidebar") ||
      document.querySelector("aside") ||
      document.querySelector("nav");

    document.body.classList.add("claire-shell-normalized");

    if (!shell || !main || !rail) {
      document.body.classList.add("claire-shell-fallback");
    } else {
      const shellContainsBoth = shell.contains(main) && shell.contains(rail);
      document.body.classList.toggle("claire-shell-fallback", !shellContainsBoth);
    }

    document.body.dataset.claireShellLayoutNormalization = BUILD;
  }

  function markLikelyWorkspaceRail() {
    const candidates = [
      ".workspace-sidebar",
      ".workspace-nav",
      ".cockpit-sidebar",
      ".claire-sidebar",
      ".sidebar",
      ".side-nav",
      "#claire-sidebar",
      "#sidebar",
      "aside",
      "nav"
    ];

    for (const selector of candidates) {
      const el = document.querySelector(selector);
      if (!el) continue;

      const text = (el.textContent || "").toLowerCase();
      if (
        text.includes("workspaces") ||
        text.includes("runtime") ||
        text.includes("portfolio") ||
        text.includes("breakthrough") ||
        text.includes("acquisition") ||
        text.includes("governance")
      ) {
        el.setAttribute("data-claire-workspace-rail", "true");
        break;
      }
    }
  }

  function normalize() {
    markLikelyWorkspaceRail();
    detectShellRelationship();
  }

  function scheduleNormalize() {
    window.requestAnimationFrame(normalize);
    window.setTimeout(normalize, 200);
    window.setTimeout(normalize, 900);
  }

  window.ClaireCockpitShellLayoutNormalization = {
    version: BUILD,
    normalize
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", scheduleNormalize);
  } else {
    scheduleNormalize();
  }

  window.addEventListener("resize", scheduleNormalize);
})();
