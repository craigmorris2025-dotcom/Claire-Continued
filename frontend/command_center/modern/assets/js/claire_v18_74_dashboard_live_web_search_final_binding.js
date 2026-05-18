(() => {
  "use strict";

  const CLAIRE_V18_74_DASHBOARD_LIVE_WEB_SEARCH_FINAL_BINDING = true;
  const VERSION = "v18.74";
  const LIVE_ENDPOINT = "/api/dashboard/search/live";
  const PROVIDER_STATUS_ENDPOINT = "/api/dashboard/search/provider/status";
  const PROVIDER_PROBE_ENDPOINT = "/api/dashboard/search/smoke/google";
  const PROBE_ENABLE_KEY = "claire_provider_probe_explicit_enable_v18_74";

  const state = {
    lastLivePayload: null,
    lastProviderStatus: null,
    lastProbePayload: null,
  };

  function qs(selectors, root = document) {
    for (const selector of selectors) {
      const found = root.querySelector(selector);
      if (found) return found;
    }
    return null;
  }

  function createElement(tag, attrs = {}, text = "") {
    const el = document.createElement(tag);
    Object.entries(attrs).forEach(([key, value]) => {
      if (value === undefined || value === null) return;
      if (key === "className") el.className = String(value);
      else if (key === "dataset") Object.assign(el.dataset, value);
      else el.setAttribute(key, String(value));
    });
    if (text) el.textContent = text;
    return el;
  }

  function hostNode() {
    return qs([
      "[data-claire-search-host]",
      "#claire-search-host",
      "#claire-dashboard-root",
      "#dashboard-root",
      "#app",
      "main",
      "body",
    ]) || document.body;
  }

  function ensureLiveSearchPanel() {
    let panel = document.getElementById("claire-v18-74-live-web-search-panel");
    if (panel) return panel;

    panel = createElement("section", {
      id: "claire-v18-74-live-web-search-panel",
      className: "claire-v18-74-panel claire-v18-74-live-web-search-panel",
      "data-claire-panel": "governed-live-web-search",
      "data-claire-version": VERSION,
      "data-claire-live-search-endpoint": LIVE_ENDPOINT,
    });

    panel.innerHTML = `
      <div class="claire-v18-74-panel-header">
        <div>
          <p class="claire-v18-74-eyebrow">Normal dashboard search</p>
          <h2>Governed Live Web Search</h2>
          <p class="claire-v18-74-muted">Uses <code>/api/dashboard/search/live</code>. Results stay evidence-visible and fail closed.</p>
        </div>
        <span class="claire-v18-74-status-pill" id="claire-v18-74-live-search-status">ready</span>
      </div>
      <form id="claire-v18-74-live-web-search-form" class="claire-v18-74-search-form" data-claire-dashboard-search-form data-claire-live-search-endpoint="/api/dashboard/search/live">
        <label class="claire-v18-74-input-label" for="claire-v18-74-live-web-search-input">Search the web</label>
        <div class="claire-v18-74-search-row">
          <input id="claire-v18-74-live-web-search-input" data-claire-dashboard-search-input type="search" autocomplete="off" placeholder="Try: google" />
          <button id="claire-v18-74-live-web-search-button" data-claire-dashboard-search-button type="submit">Search</button>
        </div>
      </form>
      <div id="claire-v18-74-live-web-search-results" class="claire-v18-74-results" data-claire-live-search-results aria-live="polite"></div>
    `;

    const host = hostNode();
    if (host.firstChild) host.insertBefore(panel, host.firstChild);
    else host.appendChild(panel);
    return panel;
  }

  function ensureProviderProbePanel() {
    let panel = document.getElementById("claire-v18-74-provider-probe-advanced-panel");
    if (panel) return panel;

    panel = createElement("section", {
      id: "claire-v18-74-provider-probe-advanced-panel",
      className: "claire-v18-74-panel claire-v18-74-provider-probe-panel",
      "data-claire-panel": "provider-probe-advanced-manual",
      "data-claire-provider-probe": "advanced-manual-explicit-enable",
    });

    panel.innerHTML = `
      <details>
        <summary>Provider Probe — Advanced / Manual</summary>
        <p class="claire-v18-74-muted">This is not normal dashboard search. It remains gated for operator proof only.</p>
        <label class="claire-v18-74-checkbox-row" for="claire-v18-74-provider-probe-enable">
          <input id="claire-v18-74-provider-probe-enable" type="checkbox" data-claire-provider-probe-explicit-enable />
          Explicitly enable one read-only provider probe
        </label>
        <div class="claire-v18-74-probe-actions">
          <button id="claire-v18-74-provider-status-button" type="button">Check provider status</button>
          <button id="claire-v18-74-provider-probe-button" type="button" disabled>Run Google provider probe</button>
        </div>
        <pre id="claire-v18-74-provider-probe-output" class="claire-v18-74-output" aria-live="polite">operator_probe_waiting_for_explicit_enable</pre>
      </details>
    `;

    const livePanel = ensureLiveSearchPanel();
    livePanel.insertAdjacentElement("afterend", panel);
    return panel;
  }

  function setLiveStatus(text, kind = "ready") {
    const status = document.getElementById("claire-v18-74-live-search-status");
    if (!status) return;
    status.textContent = text;
    status.dataset.status = kind;
  }

  function resultContainer() {
    ensureLiveSearchPanel();
    return document.getElementById("claire-v18-74-live-web-search-results");
  }

  function normalizeResults(payload) {
    if (!payload || typeof payload !== "object") return [];
    const candidates = [];
    if (Array.isArray(payload.results)) candidates.push(...payload.results);
    if (Array.isArray(payload.items)) candidates.push(...payload.items);
    if (Array.isArray(payload.cards)) candidates.push(...payload.cards);
    if (payload.result && typeof payload.result === "object") candidates.push(payload.result);
    if (payload.provider_name || payload.provider_url || payload.title || payload.url || payload.link) candidates.push(payload);

    return candidates.map((item) => {
      const title = item.title || item.name || item.provider_name || item.label || item.heading || "Untitled result";
      const url = item.url || item.link || item.href || item.provider_url || item.source_url || "";
      const snippet = item.snippet || item.description || item.summary || item.status || item.note || "";
      const source = item.source || item.provider || item.provider_name || payload.provider || "governed_web";
      return { title: String(title), url: String(url), snippet: String(snippet), source: String(source) };
    }).filter((item) => item.title || item.url || item.snippet);
  }

  function renderResultCards(payload, query) {
    state.lastLivePayload = payload;
    const container = resultContainer();
    if (!container) return;
    container.innerHTML = "";

    const results = normalizeResults(payload);
    if (!results.length) {
      const empty = createElement("article", {
        className: "claire-v18-74-live-result-card claire-v18-74-empty-result",
        "data-claire-result-card": "empty",
      });
      empty.innerHTML = `
        <h3>No governed result cards returned</h3>
        <p>Query: <strong>${escapeHtml(query || "")}</strong></p>
        <p class="claire-v18-74-muted">The live route responded but did not return a card-like result payload.</p>
      `;
      container.appendChild(empty);
      return;
    }

    results.forEach((result, index) => {
      const card = createElement("article", {
        className: "claire-v18-74-live-result-card",
        "data-claire-result-card": "governed-live-web-search",
        "data-claire-result-index": String(index),
      });
      const safeTitle = escapeHtml(result.title);
      const safeUrl = escapeHtml(result.url);
      const safeSnippet = escapeHtml(result.snippet);
      const safeSource = escapeHtml(result.source);
      const link = result.url ? `<a href="${safeUrl}" target="_blank" rel="noopener noreferrer">${safeUrl}</a>` : `<span class="claire-v18-74-muted">No URL returned</span>`;
      card.innerHTML = `
        <div class="claire-v18-74-card-topline">
          <span class="claire-v18-74-source-pill">${safeSource}</span>
          <span class="claire-v18-74-route-pill">/api/dashboard/search/live</span>
        </div>
        <h3>${safeTitle}</h3>
        <p class="claire-v18-74-url">${link}</p>
        ${safeSnippet ? `<p>${safeSnippet}</p>` : ""}
      `;
      container.appendChild(card);
    });
  }

  function renderError(message, query) {
    const container = resultContainer();
    if (!container) return;
    container.innerHTML = "";
    const card = createElement("article", {
      className: "claire-v18-74-live-result-card claire-v18-74-error-result",
      "data-claire-result-card": "fail-closed",
    });
    card.innerHTML = `
      <h3>Governed live search failed closed</h3>
      <p>Query: <strong>${escapeHtml(query || "")}</strong></p>
      <p>${escapeHtml(message)}</p>
    `;
    container.appendChild(card);
  }

  function escapeHtml(value) {
    return String(value || "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  }

  async function parseJsonResponse(response) {
    const text = await response.text();
    if (!text) return {};
    try { return JSON.parse(text); }
    catch (_) { return { raw: text, status: response.status }; }
  }

  async function fetchLiveSearch(query) {
    const payload = {
      query,
      q: query,
      source: "dashboard_search_bar",
      route: "governed_live_web_search",
      version: VERSION,
    };

    let response = await fetch(LIVE_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json", "Accept": "application/json" },
      body: JSON.stringify(payload),
    });

    if (response.status === 404 || response.status === 405 || response.status === 422) {
      const url = `${LIVE_ENDPOINT}?q=${encodeURIComponent(query)}&source=dashboard_search_bar&version=${encodeURIComponent(VERSION)}`;
      response = await fetch(url, { method: "GET", headers: { "Accept": "application/json" } });
    }

    const data = await parseJsonResponse(response);
    if (!response.ok) {
      const detail = data.detail || data.error || data.status || `HTTP ${response.status}`;
      throw new Error(String(detail));
    }
    return data;
  }

  async function runLiveDashboardSearch(query) {
    const trimmed = String(query || "").trim();
    if (!trimmed) {
      renderError("Enter a query before running governed live search.", trimmed);
      return;
    }
    setLiveStatus("searching", "busy");
    try {
      const payload = await fetchLiveSearch(trimmed);
      renderResultCards(payload, trimmed);
      setLiveStatus("result ready", "ready");
      window.dispatchEvent(new CustomEvent("claire:v18_74:live_search_result_ready", {
        detail: { query: trimmed, endpoint: LIVE_ENDPOINT, payload },
      }));
    } catch (error) {
      renderError(error && error.message ? error.message : String(error), trimmed);
      setLiveStatus("fail closed", "blocked");
    }
  }

  function bindNormalSearchForm() {
    ensureLiveSearchPanel();
    const form = document.getElementById("claire-v18-74-live-web-search-form");
    const input = document.getElementById("claire-v18-74-live-web-search-input");
    if (form && input && !form.dataset.claireV1874Bound) {
      form.dataset.claireV1874Bound = "true";
      form.dataset.claireLiveSearchEndpoint = LIVE_ENDPOINT;
      form.addEventListener("submit", (event) => {
        event.preventDefault();
        runLiveDashboardSearch(input.value);
      });
    }

    // Compatibility binding: if the existing dashboard has its own search bar, bind it to live search too.
    const legacyForm = qs([
      "form[data-dashboard-search]",
      "form[data-claire-search-form]",
      "#dashboard-search-form",
      "#claire-dashboard-search-form",
      "#searchForm",
      "form[role='search']",
    ]);
    const legacyInput = qs([
      "input[data-dashboard-search-input]",
      "input[data-claire-search-input]",
      "#dashboard-search-input",
      "#claire-dashboard-search-input",
      "#search-input",
      "input[type='search']",
    ]);
    if (legacyForm && legacyInput && !legacyForm.dataset.claireV1874Bound) {
      legacyForm.dataset.claireV1874Bound = "true";
      legacyForm.dataset.claireLiveSearchEndpoint = LIVE_ENDPOINT;
      legacyForm.addEventListener("submit", (event) => {
        event.preventDefault();
        runLiveDashboardSearch(legacyInput.value);
      });
    }
  }

  function bindProviderProbePanel() {
    ensureProviderProbePanel();
    const checkbox = document.getElementById("claire-v18-74-provider-probe-enable");
    const probeButton = document.getElementById("claire-v18-74-provider-probe-button");
    const statusButton = document.getElementById("claire-v18-74-provider-status-button");
    const output = document.getElementById("claire-v18-74-provider-probe-output");

    function syncGate() {
      const enabled = Boolean(checkbox && checkbox.checked);
      if (probeButton) probeButton.disabled = !enabled;
      if (output && !enabled) output.textContent = "operator_probe_waiting_for_explicit_enable";
      try { window.localStorage.setItem(PROBE_ENABLE_KEY, enabled ? "1" : "0"); } catch (_) {}
    }

    if (checkbox && !checkbox.dataset.claireV1874Bound) {
      checkbox.dataset.claireV1874Bound = "true";
      try { checkbox.checked = window.localStorage.getItem(PROBE_ENABLE_KEY) === "1"; } catch (_) {}
      checkbox.addEventListener("change", syncGate);
      syncGate();
    }

    if (statusButton && !statusButton.dataset.claireV1874Bound) {
      statusButton.dataset.claireV1874Bound = "true";
      statusButton.addEventListener("click", async () => {
        if (output) output.textContent = "provider_status_checking";
        try {
          const response = await fetch(PROVIDER_STATUS_ENDPOINT, { headers: { "Accept": "application/json" } });
          const payload = await parseJsonResponse(response);
          state.lastProviderStatus = payload;
          if (output) output.textContent = JSON.stringify(payload, null, 2);
        } catch (error) {
          if (output) output.textContent = `provider_status_failed_closed: ${error && error.message ? error.message : String(error)}`;
        }
      });
    }

    if (probeButton && !probeButton.dataset.claireV1874Bound) {
      probeButton.dataset.claireV1874Bound = "true";
      probeButton.addEventListener("click", async () => {
        if (!checkbox || !checkbox.checked) {
          if (output) output.textContent = "operator_probe_blocked_missing_explicit_enable";
          return;
        }
        if (output) output.textContent = "operator_probe_running_read_only_google";
        try {
          const response = await fetch(PROVIDER_PROBE_ENDPOINT, { headers: { "Accept": "application/json" } });
          const payload = await parseJsonResponse(response);
          state.lastProbePayload = payload;
          if (output) output.textContent = JSON.stringify(payload, null, 2);
          window.dispatchEvent(new CustomEvent("claire:v18_74:operator_probe_result_ready", {
            detail: { endpoint: PROVIDER_PROBE_ENDPOINT, payload },
          }));
        } catch (error) {
          if (output) output.textContent = `operator_probe_failed_closed: ${error && error.message ? error.message : String(error)}`;
        }
      });
    }
  }

  function boot() {
    ensureLiveSearchPanel();
    ensureProviderProbePanel();
    bindNormalSearchForm();
    bindProviderProbePanel();
    document.documentElement.dataset.claireV1874LiveSearchFinalBinding = "ready";
    window.CLAIRE_V18_74_DASHBOARD_LIVE_WEB_SEARCH_FINAL_BINDING = {
      version: VERSION,
      liveEndpoint: LIVE_ENDPOINT,
      providerStatusEndpoint: PROVIDER_STATUS_ENDPOINT,
      providerProbeEndpoint: PROVIDER_PROBE_ENDPOINT,
      runLiveDashboardSearch,
      normalizeResults,
      renderResultCards,
      state,
    };
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot, { once: true });
  else boot();
})();
