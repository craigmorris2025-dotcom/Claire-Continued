/* Claire Syntalion v19.68 Shared API Client */
/* All cockpit backend requests should pass through this client. */

window.ClaireCockpitApiClient = (() => {
  const DEFAULT_TIMEOUT_MS = 8000;

  function resolveBaseUrl() {
    const explicit = window.CLAIRE_API_BASE_URL;
    if (typeof explicit === "string" && explicit.trim()) {
      return explicit.replace(/\/$/, "");
    }
    return "";
  }

  function withTimeout(ms) {
    const controller = new AbortController();
    const timer = window.setTimeout(() => controller.abort(), ms);
    return { controller, timer };
  }

  async function request(path, options = {}) {
    const baseUrl = resolveBaseUrl();
    const url = `${baseUrl}${path}`;
    const timeoutMs = options.timeoutMs || DEFAULT_TIMEOUT_MS;
    const { controller, timer } = withTimeout(timeoutMs);

    try {
      const response = await fetch(url, {
        method: options.method || "GET",
        headers: {
          "Accept": "application/json",
          ...(options.headers || {})
        },
        body: options.body,
        signal: controller.signal,
        credentials: options.credentials || "same-origin"
      });

      const contentType = response.headers.get("content-type") || "";
      const body = contentType.includes("application/json")
        ? await response.json()
        : await response.text();

      return {
        ok: response.ok,
        status: response.status,
        url,
        body,
        error: response.ok ? null : `HTTP ${response.status}`
      };
    } catch (error) {
      return {
        ok: false,
        status: 0,
        url,
        body: null,
        error: error && error.name === "AbortError" ? "request_timeout" : String(error && error.message ? error.message : error)
      };
    } finally {
      window.clearTimeout(timer);
    }
  }

  return { request, resolveBaseUrl };
})();
