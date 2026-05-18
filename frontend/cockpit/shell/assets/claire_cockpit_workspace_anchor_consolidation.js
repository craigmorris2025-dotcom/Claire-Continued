/*
Claire Syntalion v19.82B.12.3
Cockpit Workspace Anchor Consolidation

Presentation-only DOM placement repair.
Moves injected cockpit workspaces into a single main-content stack so they
cannot become top-level shell/grid items.

No backend calls.
No runtime truth reads.
No runtime truth mutation.
*/

(function () {
  "use strict";

  const BUILD = "v19.82B.12.3";

  const WORKSPACE_IDS = [
    "claire-source-universe-workspace",
    "claire-probe-review-bridge",
    "claire-discovery-candidate-surface"
  ];

  function findMainContent() {
    const candidates = [
      document.querySelector("main"),
      document.querySelector("[role='main']"),
      document.querySelector(".claire-cockpit-main"),
      document.querySelector(".cockpit-main"),
      document.querySelector(".enterprise-cockpit-main"),
      document.getElementById("claire-cockpit-main"),
      document.getElementById("cockpit-main"),
      document.querySelector(".claire-main-display"),
      document.getElementById("claire-main-display")
    ].filter(Boolean);

    if (candidates.length > 0) {
      return candidates[0];
    }

    const runtimeCard =
      document.querySelector("[class*='runtime']") ||
      document.querySelector("[class*='operator']") ||
      document.querySelector("[class*='surface']");

    if (runtimeCard && runtimeCard.parentElement) {
      return runtimeCard.parentElement;
    }

    return document.body;
  }

  function ensureStack(main) {
    let stack = document.getElementById("claire-cockpit-workspace-stack");
    if (stack) return stack;

    stack = document.createElement("section");
    stack.id = "claire-cockpit-workspace-stack";
    stack.className = "claire-cockpit-workspace-stack";
    stack.setAttribute("data-build", BUILD);
    stack.setAttribute("aria-label", "Claire cockpit workspace stack");

    main.appendChild(stack);
    return stack;
  }

  function moveWorkspaceIntoStack(stack, workspace) {
    if (!workspace || workspace.parentElement === stack) return;

    workspace.setAttribute("data-claire-stack-owned", "true");
    workspace.setAttribute("data-claire-stack-build", BUILD);
    stack.appendChild(workspace);
  }

  function consolidateWorkspaces() {
    const main = findMainContent();
    const stack = ensureStack(main);

    WORKSPACE_IDS.forEach((id) => {
      const workspace = document.getElementById(id);
      if (workspace) {
        moveWorkspaceIntoStack(stack, workspace);
      }
    });

    document.body.classList.add("claire-workspace-stack-ready");
    document.body.dataset.claireWorkspaceAnchorConsolidation = BUILD;
  }

  function scheduleConsolidation() {
    window.requestAnimationFrame(consolidateWorkspaces);
    window.setTimeout(consolidateWorkspaces, 200);
    window.setTimeout(consolidateWorkspaces, 800);
    window.setTimeout(consolidateWorkspaces, 1600);
  }

  window.ClaireCockpitWorkspaceAnchorConsolidation = {
    version: BUILD,
    consolidateWorkspaces
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", scheduleConsolidation);
  } else {
    scheduleConsolidation();
  }

  window.addEventListener("resize", scheduleConsolidation);

  /*
  Existing v19.82B workspace scripts may inject after this script runs.
  Observe briefly and move late-arriving surfaces into the stack.
  */
  const observer = new MutationObserver(() => {
    consolidateWorkspaces();
  });

  if (document.body) {
    observer.observe(document.body, { childList: true, subtree: true });
    window.setTimeout(() => observer.disconnect(), 8000);
  } else {
    document.addEventListener("DOMContentLoaded", () => {
      observer.observe(document.body, { childList: true, subtree: true });
      window.setTimeout(() => observer.disconnect(), 8000);
    });
  }
})();
