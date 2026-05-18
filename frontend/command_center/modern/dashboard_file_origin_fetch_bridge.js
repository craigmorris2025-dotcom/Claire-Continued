(function () {
  "use strict";

  const CONTRACT_VERSION = "v18.73.1.operator_dashboard_compat_endpoint_repair";
  const LOCAL_API_BASE = "http://localhost:8000";

  function isFileOrigin() {
    return window.location && window.location.protocol === "file:";
  }

  function apiBase() {
    if (window.CLAIRE_API_BASE) return String(window.CLAIRE_API_BASE).replace(/\/+$/, "");
    return isFileOrigin() ? LOCAL_API_BASE : "";
  }

  function normalizeUrl(input) {
    if (!input) return input;
    let text = String(input);

    if (text.indexOf("http://") === 0 || text.indexOf("https://") === 0) return text;
    if (text.indexOf("api/") === 0) text = "/" + text;
    if (text.indexOf("operator/") === 0) text = "/" + text;

    if (text.indexOf("/api/") === 0 || text.indexOf("/operator/") === 0) {
      return apiBase() + text;
    }

    return input;
  }

  const originalFetch = window.fetch ? window.fetch.bind(window) : null;

  function bridgeFetch(input, init) {
    if (!originalFetch) return Promise.reject(new Error("fetch unavailable"));

    let mapped = input;
    try {
      if (typeof input === "string") {
        mapped = normalizeUrl(input);
      } else if (input && input.url) {
        const nextUrl = normalizeUrl(input.url);
        if (nextUrl !== input.url) mapped = new Request(nextUrl, input);
      }
    } catch (error) {
      mapped = input;
    }

    return originalFetch(mapped, init);
  }

  window.fetch = bridgeFetch;

  window.ClaireDashboardWebActivationBridge = window.ClaireDashboardWebActivationBridge || {};
  window.ClaireDashboardWebActivationBridge.contractVersion = CONTRACT_VERSION;
  window.ClaireDashboardWebActivationBridge.localApiBase = LOCAL_API_BASE;
  window.ClaireDashboardWebActivationBridge.normalizeUrl = normalizeUrl;
  window.ClaireDashboardWebActivationBridge.fetch = bridgeFetch;
})();
