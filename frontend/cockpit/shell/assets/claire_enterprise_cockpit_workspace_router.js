/*
Claire Syntalion v19.82B.13
Enterprise Cockpit Workspace Router

Presentation-only workspace router.
No backend calls.
No runtime truth reads.
No runtime truth mutation.
*/

(function () {
  "use strict";

  const BUILD = "v19.82B.13";

  const ROUTES = [
    {
      id: "runtime",
      label: "Runtime",
      title: "Runtime",
      subtitle: "Primary operational cockpit view. Existing runtime panels remain the default surface.",
      workspaceId: null
    },
    {
      id: "sources",
      label: "Sources",
      title: "Source Universe",
      subtitle: "Governed source universe control without frontend-owned truth.",
      workspaceId: "claire-source-universe-workspace"
    },
    {
      id: "review",
      label: "Review Queue",
      title: "Operator Review",
      subtitle: "Probe-to-review governance and backend review queue visibility.",
      workspaceId: "claire-probe-review-bridge"
    },
    {
      id: "discovery",
      label: "Discovery",
      title: "Discovery Candidates",
      subtitle: "Backend-governed discovery candidate display only.",
      workspaceId: "claire-discovery-candidate-surface"
    }
  ];

  let activeRoute = "runtime";

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

    if (candidates.length > 0) return candidates[0];

    const runtimeCard =
      document.querySelector("[class*='runtime']") ||
      document.querySelector("[class*='operator']") ||
      document.querySelector("[class*='surface']");

    return runtimeCard && runtimeCard.parentElement ? runtimeCard.parentElement : document.body;
  }

  function ensureRouter() {
    let router = document.getElementById("claire-enterprise-workspace-router");
    if (router) return router;

    const main = findMainContent();

    router = document.createElement("section");
    router.id = "claire-enterprise-workspace-router";
    router.setAttribute("data-build", BUILD);
    router.innerHTML = `
      <div class="claire-router-header">
        <div>
          <p class="claire-router-kicker">Enterprise Workspace Router</p>
          <h2 id="claire-router-title">Runtime</h2>
          <p id="claire-router-subtitle" class="claire-router-subtitle">
            Primary operational cockpit view.
          </p>
        </div>
        <div class="claire-router-lock">Backend-owned truth</div>
      </div>

      <div id="claire-router-tabs" class="claire-router-tabs" role="tablist"></div>

      <div id="claire-router-stage" class="claire-router-stage">
        <div class="claire-router-empty">Select a workspace.</div>
      </div>
    `;

    const firstExistingRuntime =
      main.querySelector("[class*='runtime']") ||
      main.querySelector("[class*='operation']") ||
      main.firstElementChild;

    if (firstExistingRuntime && firstExistingRuntime.parentElement === main) {
      main.insertBefore(router, firstExistingRuntime);
    } else {
      main.prepend(router);
    }

    renderTabs();
    return router;
  }

  function renderTabs() {
    const tabs = document.getElementById("claire-router-tabs");
    if (!tabs) return;

    tabs.innerHTML = ROUTES.map((route) => `
      <button
        type="button"
        class="claire-router-tab"
        data-claire-router-tab="${route.id}"
        role="tab"
        aria-selected="${route.id === activeRoute ? "true" : "false"}"
      >
        ${escapeHtml(route.label)}
      </button>
    `).join("");

    tabs.querySelectorAll("[data-claire-router-tab]").forEach((button) => {
      button.addEventListener("click", () => activateRoute(button.getAttribute("data-claire-router-tab")));
    });
  }

  function markRoutedWorkspaces() {
    ROUTES.forEach((route) => {
      if (!route.workspaceId) return;
      const workspace = document.getElementById(route.workspaceId);
      if (!workspace) return;
      workspace.setAttribute("data-claire-routed-workspace", "true");
      workspace.setAttribute("data-claire-router-build", BUILD);
    });
  }

  function moveActiveWorkspaceToStage(route) {
    const stage = document.getElementById("claire-router-stage");
    if (!stage) return;

    stage.innerHTML = "";

    if (!route.workspaceId) {
      stage.innerHTML = `
        <div class="claire-router-empty">
          Runtime is the default cockpit surface. Existing runtime panels remain visible below this router.
        </div>
      `;
      return;
    }

    const workspace = document.getElementById(route.workspaceId);
    if (!workspace) {
      stage.innerHTML = `
        <div class="claire-router-empty">
          ${escapeHtml(route.title)} workspace is not mounted yet.
        </div>
      `;
      return;
    }

    workspace.classList.add("claire-routed-active");
    stage.appendChild(workspace);
  }

  function activateRoute(routeId) {
    const route = ROUTES.find((item) => item.id === routeId) || ROUTES[0];
    activeRoute = route.id;

    document.body.classList.toggle("claire-router-active-runtime", activeRoute === "runtime");

    ROUTES.forEach((item) => {
      if (!item.workspaceId) return;
      const workspace = document.getElementById(item.workspaceId);
      if (workspace) workspace.classList.remove("claire-routed-active");
    });

    const title = document.getElementById("claire-router-title");
    const subtitle = document.getElementById("claire-router-subtitle");

    if (title) title.textContent = route.title;
    if (subtitle) subtitle.textContent = route.subtitle;

    document.querySelectorAll("[data-claire-router-tab]").forEach((button) => {
      const selected = button.getAttribute("data-claire-router-tab") === activeRoute;
      button.classList.toggle("active", selected);
      button.setAttribute("aria-selected", selected ? "true" : "false");
    });

    moveActiveWorkspaceToStage(route);
    document.body.dataset.claireActiveWorkspace = activeRoute;
  }

  function initializeRouter() {
    ensureRouter();
    markRoutedWorkspaces();
    document.body.classList.add("claire-workspace-router-ready");
    document.body.dataset.claireEnterpriseWorkspaceRouter = BUILD;
    activateRoute(activeRoute);
  }

  function scheduleInitialize() {
    window.requestAnimationFrame(initializeRouter);
    window.setTimeout(initializeRouter, 250);
    window.setTimeout(initializeRouter, 900);
    window.setTimeout(initializeRouter, 1800);
  }

  window.ClaireEnterpriseCockpitWorkspaceRouter = {
    version: BUILD,
    activateRoute,
    initializeRouter
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", scheduleInitialize);
  } else {
    scheduleInitialize();
  }

  const observer = new MutationObserver(() => initializeRouter());

  if (document.body) {
    observer.observe(document.body, { childList: true, subtree: true });
    window.setTimeout(() => observer.disconnect(), 9000);
  } else {
    document.addEventListener("DOMContentLoaded", () => {
      observer.observe(document.body, { childList: true, subtree: true });
      window.setTimeout(() => observer.disconnect(), 9000);
    });
  }

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }
})();
