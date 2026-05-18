/* Claire Syntalion v19.68 Canonical Payload Adapter */
/* Single canonical cockpit fetch owner for /dashboard/payload and /dashboard/payload/status. */

window.ClaireCockpitPayloadAdapter = (() => {
  const STATUS_PATH = "/dashboard/payload/status";
  const PAYLOAD_PATH = "/dashboard/payload";

  const state = {
    status: {
      loaded: false,
      ok: false,
      httpStatus: null,
      data: null,
      error: null,
      checkedAt: null
    },
    payload: {
      loaded: false,
      ok: false,
      httpStatus: null,
      data: null,
      error: null,
      checkedAt: null
    }
  };

  function nowIso() {
    return new Date().toISOString();
  }

  function normalizeResult(result) {
    return {
      loaded: true,
      ok: Boolean(result.ok),
      httpStatus: result.status,
      data: result.ok ? result.body : null,
      error: result.ok ? null : (result.error || "request_failed"),
      checkedAt: nowIso()
    };
  }

  async function loadStatus() {
    const result = await window.ClaireCockpitApiClient.request(STATUS_PATH);
    state.status = normalizeResult(result);
    notify("status", state.status);
    return state.status;
  }

  async function loadPayload() {
    const result = await window.ClaireCockpitApiClient.request(PAYLOAD_PATH);
    state.payload = normalizeResult(result);
    notify("payload", state.payload);
    return state.payload;
  }

  async function refreshAll() {
    const status = await loadStatus();
    let payload = state.payload;

    if (status.ok) {
      payload = await loadPayload();
    } else {
      state.payload = {
        loaded: false,
        ok: false,
        httpStatus: null,
        data: null,
        error: "status_unavailable_payload_not_fetched",
        checkedAt: nowIso()
      };
      notify("payload", state.payload);
    }

    return { status, payload };
  }

  function getState() {
    return JSON.parse(JSON.stringify(state));
  }

  function notify(type, detail) {
    window.dispatchEvent(new CustomEvent("claire:payload-adapter", {
      detail: { type, state: detail }
    }));
  }

  return {
    STATUS_PATH,
    PAYLOAD_PATH,
    loadStatus,
    loadPayload,
    refreshAll,
    getState
  };
})();
