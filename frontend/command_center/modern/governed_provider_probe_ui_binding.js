(function () {
  "use strict";

  const STATUS_URL = "/api/dashboard/search/provider/status";
  const PROBE_URL = "/api/dashboard/search/provider/probe";

  function byId(id) {
    return document.getElementById(id);
  }

  function setText(id, text) {
    const node = byId(id);
    if (node) node.textContent = text;
  }

  function renderCards(cards) {
    const container = byId("claire-provider-probe-results");
    if (!container) return;
    container.innerHTML = "";

    if (!cards || !cards.length) {
      container.innerHTML = "<div class='claire-provider-probe-empty'>No provider probe results yet.</div>";
      return;
    }

    cards.forEach(function (card) {
      const item = document.createElement("div");
      item.className = "claire-provider-probe-card";

      const title = document.createElement("a");
      title.className = "claire-provider-probe-title";
      title.href = card.url || "#";
      title.target = "_blank";
      title.rel = "noopener noreferrer";
      title.textContent = card.title || "Untitled result";

      const url = document.createElement("div");
      url.className = "claire-provider-probe-url";
      url.textContent = card.url || "";

      const snippet = document.createElement("div");
      snippet.className = "claire-provider-probe-snippet";
      snippet.textContent = card.snippet || "";

      item.appendChild(title);
      item.appendChild(url);
      item.appendChild(snippet);
      container.appendChild(item);
    });
  }

  async function refreshStatus() {
    setText("claire-provider-probe-status", "Checking provider status...");
    try {
      const response = await fetch(STATUS_URL, { method: "GET" });
      const payload = await response.json();
      const status = payload.status || "unknown";
      setText("claire-provider-probe-status", "Provider status: " + status);
      window.ClaireProviderProbeUI.lastStatus = payload;
      return payload;
    } catch (error) {
      setText("claire-provider-probe-status", "Provider status error: " + error.message);
      return { status: "error", reason: error.message };
    }
  }

  async function runProbe(event) {
    if (event && event.preventDefault) event.preventDefault();

    const input = byId("claire-provider-probe-query");
    const enable = byId("claire-provider-probe-explicit-enable");
    const query = input && input.value ? input.value.trim() : "google";

    if (!enable || !enable.checked) {
      setText("claire-provider-probe-status", "Explicit real provider probe enable is required.");
      renderCards([]);
      return {
        status: "blocked",
        reason: "explicit_real_provider_probe_required",
        result_cards: []
      };
    }

    setText("claire-provider-probe-status", "Running governed provider probe...");
    try {
      const response = await fetch(PROBE_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: query,
          explicit_real_provider_probe: true,
          provider: "operator-controlled-real-provider",
          max_results: 3
        })
      });
      const payload = await response.json();
      const cards = payload.result_cards || [];
      renderCards(cards);
      setText("claire-provider-probe-status", "Probe status: " + (payload.status || "unknown"));
      window.ClaireProviderProbeUI.lastProbe = payload;
      return payload;
    } catch (error) {
      setText("claire-provider-probe-status", "Provider probe error: " + error.message);
      renderCards([]);
      return { status: "error", reason: error.message, result_cards: [] };
    }
  }

  function bind() {
    const form = byId("claire-provider-probe-form");
    if (form && !form.dataset.claireProviderProbeBound) {
      form.addEventListener("submit", runProbe);
      form.dataset.claireProviderProbeBound = "true";
    }

    const button = byId("claire-provider-probe-refresh-status");
    if (button && !button.dataset.claireProviderStatusBound) {
      button.addEventListener("click", refreshStatus);
      button.dataset.claireProviderStatusBound = "true";
    }
  }

  window.ClaireProviderProbeUI = {
    statusUrl: STATUS_URL,
    probeUrl: PROBE_URL,
    bind: bind,
    refreshStatus: refreshStatus,
    runProbe: runProbe,
    renderCards: renderCards,
    lastStatus: null,
    lastProbe: null
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bind);
  } else {
    bind();
  }
})();
