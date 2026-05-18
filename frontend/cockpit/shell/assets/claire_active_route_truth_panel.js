(function () {
  "use strict";

  const BUILD = "v19.83.2";

  async function getJson(url, fallback) {
    try {
      const response = await fetch(url, { cache: "no-store" });
      const payload = await response.json().catch(() => fallback);
      if (!response.ok) return fallback;
      return payload;
    } catch (_err) {
      return fallback;
    }
  }

  function ensurePanel() {
    let panel = document.getElementById("claire-active-route-truth-panel");
    if (panel) return panel;

    const main =
      document.querySelector("main") ||
      document.querySelector("[role='main']") ||
      document.getElementById("claire-cockpit-main") ||
      document.body;

    panel = document.createElement("section");
    panel.id = "claire-active-route-truth-panel";
    panel.className = "claire-active-route-truth-panel";
    panel.setAttribute("data-build", BUILD);
    panel.innerHTML = `
      <div class="claire-artp-head">
        <div>
          <p>Synchronization Proof</p>
          <h2>Active Route Truth</h2>
          <span>Verifies cockpit/backend alignment without exposing dev controls.</span>
        </div>
        <button id="claire-artp-refresh" type="button">Verify</button>
      </div>
      <div class="claire-artp-grid">
        <article><span>Required Routes</span><strong id="claire-artp-routes">checking</strong></article>
        <article><span>Payload</span><strong id="claire-artp-payload">checking</strong></article>
        <article><span>Cockpit Shell</span><strong id="claire-artp-shell">checking</strong></article>
        <article><span>Duplicates</span><strong id="claire-artp-duplicates">checking</strong></article>
      </div>
      <pre id="claire-artp-json">{ "status": "checking" }</pre>
    `;

    main.appendChild(panel);
    const button = document.getElementById("claire-artp-refresh");
    if (button) button.addEventListener("click", refresh);
    return panel;
  }

  async function refresh() {
    ensurePanel();

    const truth = await getJson("/system/cockpit-truth", {
      status: "unavailable",
      required_route_summary: { all_required_mounted: false, missing: [], duplicates: [] },
      cockpit: {}
    });

    const summary = truth.required_route_summary || {};
    const cockpit = truth.cockpit || {};
    const shell = cockpit.canonical_shell || {};
    const missing = Array.isArray(summary.missing) ? summary.missing : [];
    const duplicates = Array.isArray(summary.duplicates) ? summary.duplicates : [];

    setText("claire-artp-routes", summary.all_required_mounted ? "mounted" : `${missing.length} missing`);
    setText("claire-artp-payload", truth.status === "available" ? "available" : "unavailable");
    setText("claire-artp-shell", shell.exists && shell.contains_authored_cockpit ? "authored" : "mismatch");
    setText("claire-artp-duplicates", duplicates.length ? `${duplicates.length}` : "none");
    setText("claire-artp-json", JSON.stringify(truth, null, 2));
  }

  function setText(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = String(value);
  }

  window.ClaireActiveRouteTruthPanel = { version: BUILD, refresh };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => {
      ensurePanel();
      refresh();
    });
  } else {
    ensurePanel();
    refresh();
  }
})();
