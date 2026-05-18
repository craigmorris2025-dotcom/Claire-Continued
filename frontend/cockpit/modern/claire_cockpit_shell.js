(function () {
  "use strict";

  const SAFE_FETCH_ENDPOINTS = Object.freeze({
    canonical_payload: "/dashboard/payload",
    payload_status: "/dashboard/payload/status",
    health: "/health",
    provider_status: "/api/dashboard/search/provider/status"
  });

  const BLOCKED_ACTIONS = Object.freeze({
    run_autonomous_update: "automatic_updates_blocked",
    execute_runtime_mutation: "runtime_mutation_blocked",
    start_continuous_crawl: "continuous_crawling_blocked",
    promote_without_review: "manual_promotion_mandatory"
  });

  const ACTION_INTENTS = Object.freeze({
    request_bounded_web_job: "proposal_only",
    open_review_queue: "read_only",
    approve_promotion_candidate: "manual_promotion_only",
    export_reviewed_package: "operator_approved_export",
    create_update_proposal: "proposal_only",
    run_autonomous_update: "blocked",
    execute_runtime_mutation: "blocked"
  });

  const RENDER_RULES = Object.freeze({
    current_state: ["status", "state", "overall_state"],
    selected_route: ["selected_route", "route"],
    terminal_state: ["terminal_state"],
    next_action: ["next_action"],
    confidence: ["confidence"]
  });

  function firstValue(payload, keys, fallback) {
    for (const key of keys) {
      if (payload && Object.prototype.hasOwnProperty.call(payload, key) && payload[key] !== null && payload[key] !== "") {
        return payload[key];
      }
    }
    return fallback;
  }

  function setText(cardId, value) {
    const node = document.querySelector(`[data-card-id="${cardId}"]`);
    if (node) {
      node.textContent = String(value);
    }
  }

  function setState(cardId, state) {
    const node = document.querySelector(`[data-card-id="${cardId}"]`);
    if (node) {
      node.dataset.state = state;
    }
  }

  function attachSafeActionIntentHandlers() {
    document.querySelectorAll("[data-action-id]").forEach((node) => {
      const actionId = node.dataset.actionId;
      node.dataset.authority = ACTION_INTENTS[actionId] || "unknown";
      node.addEventListener("click", (event) => {
        if (BLOCKED_ACTIONS[actionId] || node.disabled) {
          event.preventDefault();
          setText("warnings", `Blocked action: ${BLOCKED_ACTIONS[actionId] || "not enabled by backend contract"}`);
        }
      });
    });
  }

  function renderGovernanceBanners() {
    setText("governance_banner_backend_owns_truth", "Backend owns truth. Cockpit presentation only.");
    setText("governance_banner_manual_promotion", "Manual promotion mandatory.");
    setText("governance_banner_quarantine", "Quarantine mandatory.");
    setText("governance_banner_updates_blocked", "Automatic updates blocked.");
    setText("governance_banner_mutation_blocked", "Runtime mutation blocked.");
  }

  function disableBlockedButtons() {
    Object.keys(BLOCKED_ACTIONS).forEach((actionId) => {
      const node = document.querySelector(`[data-action-id="${actionId}"]`);
      if (node) {
        node.disabled = true;
        node.dataset.state = "blocked";
        node.title = BLOCKED_ACTIONS[actionId];
      }
    });
  }

  async function fetchJson(path) {
    const response = await fetch(path, { method: "GET", cache: "no-store" });
    if (!response.ok) {
      throw new Error(`${path} returned ${response.status}`);
    }
    return response.json();
  }

  function renderPayload(payload) {
    setText("current_state", `Runtime: ${firstValue(payload, RENDER_RULES.current_state, "payload available")}`);
    setText("selected_route", `Route: ${firstValue(payload, RENDER_RULES.selected_route, "not selected")}`);
    setText("terminal_state", `Terminal: ${firstValue(payload, RENDER_RULES.terminal_state, "not reached")}`);
    setText("next_action", `Next: ${firstValue(payload, RENDER_RULES.next_action, "review cockpit state")}`);
    setText("confidence", `Confidence: ${firstValue(payload, RENDER_RULES.confidence, "pending")}`);
    setText("raw_payload", JSON.stringify(payload || {}, null, 2));
  }

  async function hydrateCockpit() {
    disableBlockedButtons();
    attachSafeActionIntentHandlers();
    renderGovernanceBanners();

    try {
      const health = await fetchJson(SAFE_FETCH_ENDPOINTS.health);
      setText("payload_health", `Health: ${health.status || "available"}`);
      setState("payload_health", "ready");
    } catch (error) {
      setText("payload_health", "Health: unavailable");
      setState("payload_health", "blocked");
    }

    try {
      const status = await fetchJson(SAFE_FETCH_ENDPOINTS.payload_status);
      setText("connection_state", `Payload status: ${status.status || status.state || "available"}`);
      setState("connection_state", "ready");
    } catch (error) {
      setText("connection_state", "Payload status: unavailable");
      setState("connection_state", "blocked");
    }

    try {
      const payload = await fetchJson(SAFE_FETCH_ENDPOINTS.canonical_payload);
      renderPayload(payload);
      setState("current_state", "ready");
    } catch (error) {
      setText("current_state", "Runtime: waiting for backend payload");
      setText("warnings", "Payload unavailable. Check backend health.");
      setState("current_state", "blocked");
    }
  }

  window.ClaireCockpitShell = Object.freeze({
    SAFE_FETCH_ENDPOINTS,
    BLOCKED_ACTIONS,
    ACTION_INTENTS,
    RENDER_RULES,
    hydrateCockpit,
    renderPayload
  });

  document.addEventListener("DOMContentLoaded", hydrateCockpit);
})();
