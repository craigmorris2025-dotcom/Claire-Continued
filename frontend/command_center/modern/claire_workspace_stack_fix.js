(function () {
  "use strict";

  function norm(value) {
    return String(value || "").replace(/\s+/g, " ").trim().toLowerCase();
  }

  function textOf(node) {
    return norm(node?.innerText || node?.textContent || "");
  }

  function findPanelByHeading(headingText) {
    const headings = Array.from(document.querySelectorAll("h1,h2,h3,h4,.section-title,.surface-title,.panel-title"));
    const wanted = headingText.toLowerCase();

    for (const heading of headings) {
      if (!textOf(heading).includes(wanted)) continue;

      const panel = heading.closest(
        "section, article, .dashboard-panel, .claire-panel, .surface, .claire-surface, .portal, .claire-portal, .command-panel, .command-surface, div"
      );

      if (panel && panel !== document.body) return panel;
    }

    return null;
  }

  function likelyMainWorkspace() {
    const selectors = [
      "#main-workspace",
      "#workspace",
      "#app",
      "main",
      ".main-workspace",
      ".workspace",
      ".workspace-column",
      ".content-column",
      ".main-column",
      ".center-column",
      ".dashboard-shell",
      ".claire-shell",
      ".operating-environment"
    ];

    for (const selector of selectors) {
      const node = document.querySelector(selector);
      if (node) return node;
    }

    return document.body;
  }

  function killScrollContainersInside(panel) {
    if (!panel) return;
    const nodes = [panel, ...Array.from(panel.querySelectorAll("*"))];

    for (const node of nodes) {
      const style = window.getComputedStyle(node);
      const hasScroll = ["auto", "scroll", "hidden"].includes(style.overflowY) || ["auto", "scroll", "hidden"].includes(style.overflow);
      const heightLimited =
        style.maxHeight !== "none" ||
        (style.height && style.height !== "auto" && node.scrollHeight > node.clientHeight + 20);

      if (hasScroll || heightLimited) {
        node.classList.add("claire-stack-scroll-kill");
        node.style.overflow = "visible";
        node.style.overflowY = "visible";
        node.style.maxHeight = "none";
        if (node !== document.body && node !== document.documentElement) {
          node.style.height = "auto";
        }
      }
    }
  }

  function applyStackFix() {
    const main = likelyMainWorkspace();
    main.classList.add("claire-main-workspace-fixed");

    const commandPanel = findPanelByHeading("command");
    if (commandPanel) {
      commandPanel.classList.add("claire-stack-panel", "claire-command-stack-panel");
      killScrollContainersInside(commandPanel);
    }

    const validationPanel =
      document.getElementById("claire-validation-authority-panel") ||
      document.querySelector(".claire-validation-authority-panel") ||
      findPanelByHeading("validation authority");

    if (validationPanel) {
      validationPanel.classList.add("claire-stack-panel", "claire-validation-stack-panel");
      validationPanel.style.position = "relative";
      validationPanel.style.height = "auto";
      validationPanel.style.maxHeight = "none";
      validationPanel.style.overflow = "visible";
    }

    const memoryPanel =
      document.getElementById("claire-verified-memory-panel") ||
      document.querySelector(".claire-memory-panel") ||
      findPanelByHeading("verified memory");

    if (memoryPanel) {
      memoryPanel.classList.add("claire-stack-panel", "claire-memory-stack-panel");
      memoryPanel.style.position = "relative";
      memoryPanel.style.height = "auto";
      memoryPanel.style.maxHeight = "none";
      memoryPanel.style.overflow = "visible";
    }

    // If validation/memory were appended inside a cramped surface, move them after
    // the command panel inside the main workspace in a stable order.
    if (commandPanel && main && validationPanel && validationPanel.parentElement !== main) {
      commandPanel.insertAdjacentElement("afterend", validationPanel);
    }

    if (validationPanel && main && memoryPanel && memoryPanel.parentElement !== main) {
      validationPanel.insertAdjacentElement("afterend", memoryPanel);
    } else if (commandPanel && main && memoryPanel && memoryPanel.parentElement !== main) {
      commandPanel.insertAdjacentElement("afterend", memoryPanel);
    }
  }

  function boot() {
    applyStackFix();

    // Prior bridge scripts mount validation/memory after DOMContentLoaded.
    // Run a few times to catch late-mounted panels.
    setTimeout(applyStackFix, 400);
    setTimeout(applyStackFix, 1200);
    setTimeout(applyStackFix, 2400);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
