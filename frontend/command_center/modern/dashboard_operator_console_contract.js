(() => {
  const ROOT_ID = "claire-operator-console-contract";
  const CONTRACT_URL = "/dashboard/operator-console/contract";

  function byId(id) {
    return document.getElementById(id);
  }

  function ensureRoot() {
    let root = byId(ROOT_ID);
    if (root) return root;

    root = document.createElement("section");
    root.id = ROOT_ID;
    root.setAttribute("data-claire-operator-console-contract", "true");
    root.className = "claire-operator-console-contract";
    root.innerHTML = `
      <div class="claire-operator-console-header">
        <div>
          <p class="claire-operator-console-kicker">Operator Console</p>
          <h2>Governed Actions</h2>
          <p class="claire-operator-console-copy">Review-only controls. No web execution, body reads, crawling, updates, runtime mutation, package install, browser execution, or command execution.</p>
        </div>
        <div class="claire-operator-console-chip" data-actions-chip>Actions 0</div>
      </div>
      <div class="claire-operator-console-grid" data-actions-grid></div>
      <div class="claire-operator-console-preview" data-actions-preview>
        Select a governed action to view its review-only preview.
      </div>
    `;

    const target =
      document.querySelector("[data-panel='actions']") ||
      document.querySelector("#actions") ||
      document.querySelector("main") ||
      document.querySelector("#app") ||
      document.body;

    target.appendChild(root);
    return root;
  }

  function escapeHtml(value) {
    return String(value ?? "").replace(/[&<>"']/g, (char) => ({
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#039;"
    }[char]));
  }

  async function fetchJson(url) {
    const response = await fetch(url, { method: "GET", cache: "no-store" });
    if (!response.ok) throw new Error(`${url} returned ${response.status}`);
    return response.json();
  }

  function renderPreview(root, action) {
    const preview = root.querySelector("[data-actions-preview]");
    const title = action?.preview?.headline || action?.label || "Governed action";
    const body = action?.preview?.body || action?.description || "Review-only preview is available.";
    preview.innerHTML = `
      <p class="claire-preview-kicker">Preview only</p>
      <h3>${escapeHtml(title)}</h3>
      <p>${escapeHtml(body)}</p>
      <p class="claire-preview-locks">Execution blocked · Body reads blocked · Runtime mutation blocked</p>
    `;
  }

  function renderContract(contract) {
    const root = ensureRoot();
    const actions = Array.isArray(contract.operator_controls) ? contract.operator_controls : [];
    const chip = root.querySelector("[data-actions-chip]");
    const grid = root.querySelector("[data-actions-grid]");

    chip.textContent = `Actions ${contract.action_count || actions.length || 0}`;
    grid.innerHTML = "";

    if (!actions.length) {
      grid.innerHTML = '<div class="claire-action-empty">No governed actions registered.</div>';
      return;
    }

    actions.forEach((action) => {
      const card = document.createElement("article");
      card.className = "claire-action-card";
      card.innerHTML = `
        <div class="claire-action-card-topline">
          <span>${escapeHtml(action.status || "ready")}</span>
          <span>review-only</span>
        </div>
        <h3>${escapeHtml(action.label)}</h3>
        <p>${escapeHtml(action.description)}</p>
        <button type="button" data-action-key="${escapeHtml(action.action_key)}">${escapeHtml(action.button_label || action.label)}</button>
      `;
      card.querySelector("button").addEventListener("click", async () => {
        try {
          const preview = await fetchJson(`/dashboard/operator-console/preview/${encodeURIComponent(action.action_key)}`);
          renderPreview(root, preview.action || action);
        } catch (error) {
          renderPreview(root, action);
        }
      });
      grid.appendChild(card);
    });
  }

  async function boot() {
    try {
      const contract = await fetchJson(CONTRACT_URL);
      renderContract(contract);
    } catch (error) {
      const root = ensureRoot();
      const grid = root.querySelector("[data-actions-grid]");
      grid.innerHTML = `<div class="claire-action-empty">Operator console contract unavailable: ${escapeHtml(error.message)}</div>`;
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
