// Claire Syntalion v19.89.8-A4
// Lightweight cockpit binding probe. Does not redesign cockpit.

(function () {
  "use strict";

  async function runProbe() {
    if (!window.ClaireCanonicalFetch) return;

    const target =
      document.querySelector("[data-claire-canonical-fetch-status]") ||
      document.getElementById("claire-canonical-fetch-status");

    if (!target) return;

    target.textContent = "Checking canonical cockpit fetch authority...";
    try {
      const results = await window.ClaireCanonicalFetch.loadRequiredSummaries();
      const okCount = Object.values(results).filter((v) => v && v.ok).length;
      target.textContent = "Canonical fetch routes reachable: " + okCount + "/" + window.ClaireCanonicalFetch.routes.length;
      target.dataset.status = okCount > 0 ? "partial" : "blocked";
    } catch (err) {
      target.textContent = "Canonical fetch check failed closed: " + String(err && err.message ? err.message : err);
      target.dataset.status = "blocked";
    }
  }

  window.addEventListener("claire:canonical-fetch-ready", runProbe);
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", runProbe);
  } else {
    runProbe();
  }
})();
