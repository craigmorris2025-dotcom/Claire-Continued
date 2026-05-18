/* BEGIN CLAIRE_S422_S428_ACTION_WIRING */
(function () {
  "use strict";
  const registryEndpoint = "/dashboard/actions/registry";
  const summaryEndpoint = "/dashboard/actions/summary";

  function ensurePanel() {
    let panel = document.getElementById("claire-action-wiring-panel");
    if (!panel) {
      panel = document.createElement("section");
      panel.id = "claire-action-wiring-panel";
      panel.className = "claire-action-wiring-panel";
      const mount = document.getElementById("claire-consolidated-cockpit") || document.body;
      mount.appendChild(panel);
    }
    return panel;
  }

  function escapeHtml(value) {
    return String(value ?? "").replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;").replaceAll("'", "&#039;");
  }

  async function bootActionWiring() {
    const panel = ensurePanel();
    panel.innerHTML = "<h3>Claire Governed Actions</h3><p>Loading governed action registry...</p>";
    try {
      const [registryResponse, summaryResponse] = await Promise.all([
        fetch(registryEndpoint, { cache: "no-store" }),
        fetch(summaryEndpoint, { cache: "no-store" })
      ]);
      const registry = await registryResponse.json();
      const summary = await summaryResponse.json();
      const buttons = Object.entries(registry).map(([name, spec]) => `
        <button class="claire-action-button" data-claire-action="${escapeHtml(name)}" data-endpoint="${escapeHtml(spec.endpoint)}" ${spec.enabled ? "" : "disabled"}>
          ${escapeHtml(name.replaceAll("_", " "))}
          <small>${escapeHtml(spec.mode)} · ${escapeHtml(spec.endpoint)}</small>
        </button>
      `).join("");
      panel.innerHTML = `
        <h3>Claire Governed Actions</h3>
        <div class="claire-action-summary">
          <span>Enabled: ${escapeHtml(summary.enabled_action_count)}</span>
          <span>Runtime mutation: ${escapeHtml(summary.runtime_mutation_status)}</span>
          <span>Body read: ${escapeHtml(summary.body_read_status)}</span>
        </div>
        <div class="claire-action-grid">${buttons}</div>
      `;
    } catch (error) {
      panel.innerHTML = `<h3>Claire Governed Actions</h3><p>Action registry unavailable: ${escapeHtml(error.message)}</p>`;
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bootActionWiring);
  } else {
    bootActionWiring();
  }
})();
/* END CLAIRE_S422_S428_ACTION_WIRING */
