(function () {
  "use strict";

  const CONTRACT_VERSION = "v18.73.2.dashboard_search_provider_probe_separation_repair";
  const LOCAL_API_BASE = "http://localhost:8000";
  const LIVE_SEARCH_PATH = "/api/dashboard/search/live";
  const GOOGLE_SMOKE_PATH = "/api/dashboard/search/smoke/google";

  function isFileOrigin() {
    return window.location && window.location.protocol === "file:";
  }

  function apiBase() {
    if (window.CLAIRE_API_BASE) return String(window.CLAIRE_API_BASE).replace(/\/+$/, "");
    return isFileOrigin() ? LOCAL_API_BASE : "";
  }

  function byId(id) {
    return document.getElementById(id);
  }

  function esc(value) {
    return String(value || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function endpoint(path) {
    if (String(path || "").indexOf("http") === 0) return path;
    return apiBase() + path;
  }

  function renderStatus(message, kind) {
    const node = byId("claire-primary-web-search-status");
    if (!node) return;
    node.textContent = message || "";
    node.dataset.statusKind = kind || "info";
  }

  function renderResults(payload) {
    const container = byId("claire-primary-web-search-results");
    if (!container) return;

    const cards = payload && payload.result_cards ? payload.result_cards : [];
    let html = "";

    if (!cards.length) {
      html += "<div class='claire-primary-search-empty'>";
      html += "<strong>No governed live-search results.</strong>";
      if (payload && payload.reason) html += "<p>" + esc(payload.reason) + "</p>";
      html += "</div>";
      container.innerHTML = html;
      return;
    }

    html += "<div class='claire-primary-search-card-list'>";
    cards.forEach(function (card) {
      html += "<article class='claire-primary-search-card'>";
      html += "<a class='claire-primary-search-title' href='" + esc(card.url || "#") + "' target='_blank' rel='noopener noreferrer'>" + esc(card.title || "Untitled result") + "</a>";
      html += "<div class='claire-primary-search-url'>" + esc(card.url || "") + "</div>";
      html += "<p class='claire-primary-search-snippet'>" + esc(card.snippet || "") + "</p>";
      html += "<div class='claire-primary-search-trust'>" + esc(card.trust_status || "operator_review_required") + "</div>";
      html += "</article>";
    });
    html += "</div>";

    container.innerHTML = html;
  }

  async function runPrimaryWebSearch(query) {
    const input = byId("claire-primary-web-search-query");
    const q = String(query || (input ? input.value : "") || "google").trim() || "google";
    renderStatus("Running governed live web search...", "working");

    try {
      const response = await fetch(endpoint(LIVE_SEARCH_PATH), {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
          query: q,
          manual_enable: true,
          max_results: 3
        })
      });

      if (!response.ok) throw new Error("HTTP " + response.status);

      const payload = await response.json();
      window.ClairePrimaryWebSearch.lastPayload = payload;
      renderResults(payload);

      const count = Number(payload.visible_result_count || 0);
      renderStatus(count ? "Governed live web search returned " + count + " result(s)." : "Governed live web search returned no results.", count ? "ready" : "empty");
      return payload;
    } catch (error) {
      if (q.toLowerCase() === "google") {
        try {
          const fallback = await fetch(endpoint(GOOGLE_SMOKE_PATH), {method: "GET"});
          const fallbackPayload = await fallback.json();
          window.ClairePrimaryWebSearch.lastPayload = fallbackPayload;
          renderResults(fallbackPayload);
          renderStatus("Governed live web search returned Google smoke result.", "ready");
          return fallbackPayload;
        } catch (fallbackError) {
          renderStatus("Backend search unavailable: " + fallbackError.message, "error");
          renderResults({result_cards: [], reason: fallbackError.message});
          return {status: "error", reason: fallbackError.message, result_cards: []};
        }
      }

      renderStatus("Backend search unavailable: " + error.message, "error");
      renderResults({result_cards: [], reason: error.message});
      return {status: "error", reason: error.message, result_cards: []};
    }
  }

  function bindPrimaryWebSearch() {
    const form = byId("claire-primary-web-search-form");
    const button = byId("claire-primary-web-search-button");

    if (form && !form.dataset.clairePrimaryWebSearchBound) {
      form.addEventListener("submit", function (event) {
        event.preventDefault();
        runPrimaryWebSearch();
      });
      form.dataset.clairePrimaryWebSearchBound = "true";
    }

    if (button && !button.dataset.clairePrimaryWebSearchBound) {
      button.addEventListener("click", function (event) {
        event.preventDefault();
        runPrimaryWebSearch();
      });
      button.dataset.clairePrimaryWebSearchBound = "true";
    }
  }

  window.ClairePrimaryWebSearch = {
    contractVersion: CONTRACT_VERSION,
    liveSearchPath: LIVE_SEARCH_PATH,
    googleSmokePath: GOOGLE_SMOKE_PATH,
    localApiBase: LOCAL_API_BASE,
    runPrimaryWebSearch: runPrimaryWebSearch,
    renderResults: renderResults,
    bindPrimaryWebSearch: bindPrimaryWebSearch,
    lastPayload: null
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bindPrimaryWebSearch);
  } else {
    bindPrimaryWebSearch();
  }
})();
