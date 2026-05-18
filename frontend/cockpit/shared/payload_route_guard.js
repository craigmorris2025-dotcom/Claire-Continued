/*
Claire Syntalion v19.72
Cockpit Payload Route Guard

Non-invasive helper. This file does not fabricate runtime truth.
It only checks whether canonical backend payload routes are reachable.

Canonical routes:
- /dashboard/payload/status
- /dashboard/payload
*/

export const CLAIRE_PAYLOAD_ROUTES = Object.freeze({
  status: "/dashboard/payload/status",
  payload: "/dashboard/payload",
});

export async function checkClairePayloadRoutes(apiClient) {
  const result = {
    ok: false,
    version: "v19.72",
    checked_at: new Date().toISOString(),
    routes: {
      status: { route: CLAIRE_PAYLOAD_ROUTES.status, ok: false, blocked: true, error: null },
      payload: { route: CLAIRE_PAYLOAD_ROUTES.payload, ok: false, blocked: true, error: null },
    },
    bridge_state: "blocked",
    reason: "not_checked",
  };

  if (!apiClient || typeof apiClient.get !== "function") {
    result.reason = "api_client_unavailable";
    return result;
  }

  try {
    const status = await apiClient.get(CLAIRE_PAYLOAD_ROUTES.status);
    result.routes.status.ok = true;
    result.routes.status.blocked = false;
    result.routes.status.response = status;
  } catch (error) {
    result.routes.status.error = String(error && error.message ? error.message : error);
  }

  try {
    const payload = await apiClient.get(CLAIRE_PAYLOAD_ROUTES.payload);
    result.routes.payload.ok = true;
    result.routes.payload.blocked = false;
    result.routes.payload.has_payload = Boolean(payload);
  } catch (error) {
    result.routes.payload.error = String(error && error.message ? error.message : error);
  }

  result.ok = result.routes.status.ok && result.routes.payload.ok;
  result.bridge_state = result.ok ? "unblocked" : "blocked";
  result.reason = result.ok ? "canonical_payload_available" : "canonical_payload_unavailable";
  return result;
}
