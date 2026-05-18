/*
Claire Syntalion v19.82B.14
Enterprise Cockpit Visual Frame v2

Presentation-only dashboard cleanup.
No backend calls.
No runtime truth reads.
No runtime truth mutation.
*/

(function () {
  "use strict";

  const BUILD = "v19.82B.14";

  function markRawRuntimeActions() {
    const headings = Array.from(document.querySelectorAll("h1,h2,h3,h4,h5,strong,div,span"))
      .filter((el) => (el.textContent || "").trim().toLowerCase() === "runtime actions");

    headings.forEach((heading) => {
      let container = heading.parentElement;
      for (let i = 0; i < 4 && container; i += 1) {
        const buttons = container.querySelectorAll("button, input[type='button'], input[type='submit']");
        const text = (container.textContent || "").toLowerCase();

        if (
          buttons.length >= 2 &&
          text.includes("start run") &&
          text.includes("refresh runtime") &&
          (text.includes("system status") || text.includes("governance"))
        ) {
          container.classList.add("claire-runtime-actions-raw");
          container.setAttribute("data-claire-raw-actions", "true");
          return;
        }

        container = container.parentElement;
      }
    });
  }

  function markVisualFrame() {
    document.body.classList.add("claire-visual-frame-v2");
    document.body.dataset.claireEnterpriseCockpitVisualFrame = BUILD;
    markRawRuntimeActions();
  }

  function schedule() {
    window.requestAnimationFrame(markVisualFrame);
    window.setTimeout(markVisualFrame, 250);
    window.setTimeout(markVisualFrame, 900);
    window.setTimeout(markVisualFrame, 1800);
  }

  window.ClaireEnterpriseCockpitVisualFrameV2 = {
    version: BUILD,
    markVisualFrame,
    markRawRuntimeActions
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", schedule);
  } else {
    schedule();
  }

  const observer = new MutationObserver(() => markRawRuntimeActions());

  if (document.body) {
    observer.observe(document.body, { childList: true, subtree: true });
    window.setTimeout(() => observer.disconnect(), 9000);
  } else {
    document.addEventListener("DOMContentLoaded", () => {
      observer.observe(document.body, { childList: true, subtree: true });
      window.setTimeout(() => observer.disconnect(), 9000);
    });
  }
})();
