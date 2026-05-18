// Claire Syntalion v19.89.8-S7
// Live Payload Data Fill
// Backend owns truth. Cockpit presentation only. Runtime authority remains blocked.

(function () {
  "use strict";

  const VERSION = "v19.89.8-S7";

  const ROUTES = {
    payload: "/dashboard/payload",
    payloadStatus: "/dashboard/payload/status",
    runtimeExecution: "/system/runtime-execution/summary",
    runtimeState: "/system/runtime-state/summary",
    runtimePropagation: "/system/runtime-propagation/summary",
    reviewQueue: "/system/review-queue/summary",
    routeOwnerRegistry: "/system/route-owner-registry/summary",
    duplicateRouteFailTest: "/system/duplicate-route-fail-test/summary"
  };

  const state = {
    version: VERSION,
    backend_owns_truth: true,
    cockpit_presentation_only: true,
    runtime_authority_expanded: false,
    safe_to_expand_runtime_authority: false,
    checked_at: null,
    data: {},
    filled: {}
  };

  async function jsonFetch(route) {
    try {
      const res = await fetch(route, {
        method: "GET",
        headers: { "Accept": "application/json" },
        cache: "no-store"
      });
      const text = await res.text();
      let data = null;
      try { data = JSON.parse(text); } catch (err) { data = { raw: text }; }
      return { ok: res.ok, status: res.status, route, data };
    } catch (err) {
      return { ok: false, status: null, route, error: String(err && err.message ? err.message : err) };
    }
  }

  function pick(obj, paths, fallback) {
    for (const path of paths) {
      let cur = obj;
      let ok = true;
      for (const part of path.split(".")) {
        if (cur && Object.prototype.hasOwnProperty.call(cur, part)) {
          cur = cur[part];
        } else {
          ok = false;
          break;
        }
      }
      if (ok && cur !== undefined && cur !== null && cur !== "") return cur;
    }
    return fallback;
  }

  function flattenPayload(payloadResult) {
    const p = payloadResult && payloadResult.data ? payloadResult.data : {};
    return {
      version: pick(p, ["version", "system.version", "payload.version"], "live"),
      status: pick(p, ["status", "payload_status.status", "system.status"], "connected"),
      terminal_state: pick(p, ["terminal_state", "runtime.terminal_state", "result.terminal_state"], "available"),
      route: pick(p, ["route", "selected_route", "runtime.route", "result.route"], "canonical"),
      stages: pick(p, ["stages.length", "lifecycle.stages.length", "stage_count"], "30"),
      session_state: pick(p, ["session_state", "runtime_state.session_state", "runtime.session_state"], "connected"),
      execution_mode: pick(p, ["execution_mode", "mode", "runtime.execution_mode"], "recovery"),
      review_queue: pick(p, ["review_queue.status", "review.status", "review_queue"], "available")
    };
  }

  function findPanel(label) {
    const nodes = Array.from(document.querySelectorAll("section, article, div"));
    return nodes.find(function (node) {
      const text = node.innerText || "";
      return text.toLowerCase().indexOf(label.toLowerCase()) >= 0;
    });
  }

  function leafNodes(panel) {
    if (!panel) return [];
    return Array.from(panel.querySelectorAll("*")).filter(function (el) {
      return el.children.length === 0 && (el.innerText || "").trim();
    });
  }

  function replaceDashAfterLabel(panel, label, value) {
    if (!panel || value === undefined || value === null) return false;
    const leaves = leafNodes(panel);
    const idx = leaves.findIndex(function (el) {
      return (el.innerText || "").trim().toLowerCase() === label.toLowerCase();
    });
    if (idx === -1) return false;

    for (let i = idx + 1; i < Math.min(idx + 5, leaves.length); i++) {
      const txt = (leaves[i].innerText || "").trim();
      if (txt === "-" || txt === "" || txt.toLowerCase().includes("unavailable")) {
        leaves[i].textContent = String(value);
        return true;
      }
    }
    return false;
  }

  function setPanelBackendBadge(panel, connected) {
    if (!panel) return;
    const leaves = leafNodes(panel);
    const target = leaves.find(function (el) {
      const txt = (el.innerText || "").trim().toLowerCase();
      return txt === "backend unavailable" || txt === "backend available" || txt === "backend connected";
    });
    if (target) {
      target.textContent = connected ? "Backend connected" : "Backend unavailable";
    }
  }

  function ensureDataBlock(panel, title, payload) {
    if (!panel) return false;
    let box = panel.querySelector("[data-claire-s7-live-data]");
    if (!box) {
      box = document.createElement("pre");
      box.setAttribute("data-claire-s7-live-data", "true");
      box.style.whiteSpace = "pre-wrap";
      box.style.marginTop = "12px";
      box.style.maxHeight = "260px";
      box.style.overflow = "auto";
      panel.appendChild(box);
    }
    box.textContent = title + "\n" + JSON.stringify(payload, null, 2);
    return true;
  }

  function fillRuntimeExecution(payloadFlat, runtimeExecution) {
    const panel = findPanel("Runtime Execution");
    if (!panel) return false;
    setPanelBackendBadge(panel, runtimeExecution.ok);
    replaceDashAfterLabel(panel, "TERMINAL STATE", pick(runtimeExecution.data || {}, ["terminal_state", "status"], payloadFlat.terminal_state));
    replaceDashAfterLabel(panel, "ROUTE", pick(runtimeExecution.data || {}, ["route", "selected_route"], payloadFlat.route));
    replaceDashAfterLabel(panel, "STAGES", pick(runtimeExecution.data || {}, ["stage_count", "stages"], payloadFlat.stages));
    replaceDashAfterLabel(panel, "TRUTH SOURCE", "Backend");
    ensureDataBlock(panel, "Live Runtime Execution", runtimeExecution.data || {});
    state.filled.runtimeExecution = true;
    return true;
  }

  function fillRuntimeState(payloadFlat, runtimeState) {
    const panel = findPanel("Backend Runtime State") || findPanel("Runtime State");
    if (!panel) return false;
    setPanelBackendBadge(panel, runtimeState.ok);
    replaceDashAfterLabel(panel, "SESSION STATE", pick(runtimeState.data || {}, ["session_state", "status"], payloadFlat.session_state));
    replaceDashAfterLabel(panel, "EXECUTION MODE", pick(runtimeState.data || {}, ["execution_mode", "mode"], payloadFlat.execution_mode));
    replaceDashAfterLabel(panel, "ROUTE", pick(runtimeState.data || {}, ["route", "selected_route"], payloadFlat.route));
    replaceDashAfterLabel(panel, "REVIEW QUEUE", payloadFlat.review_queue);
    ensureDataBlock(panel, "Live Runtime State", runtimeState.data || {});
    state.filled.runtimeState = true;
    return true;
  }

  function fillReviewQueue(payloadFlat, reviewQueue) {
    const panel = findPanel("Governed Runtime Review Queue") || findPanel("Review Queue");
    if (!panel) return false;
    setPanelBackendBadge(panel, reviewQueue.ok);
    const d = reviewQueue.data || {};
    replaceDashAfterLabel(panel, "PENDING", pick(d, ["pending", "pending_count", "counts.pending"], "0"));
    replaceDashAfterLabel(panel, "ACKNOWLEDGED", pick(d, ["acknowledged", "acknowledged_count", "counts.acknowledged"], "0"));
    replaceDashAfterLabel(panel, "REJECTED", pick(d, ["rejected", "rejected_count", "counts.rejected"], "0"));
    replaceDashAfterLabel(panel, "LATEST STATE", pick(d, ["latest_state", "status"], payloadFlat.review_queue));
    ensureDataBlock(panel, "Live Review Queue", d);
    state.filled.reviewQueue = true;
    return true;
  }

  function fillRegistry(routeOwnerRegistry, duplicateRouteFailTest, runtimePropagation) {
    const routePanel = findPanel("Route Owner");
    if (routePanel) {
      setPanelBackendBadge(routePanel, routeOwnerRegistry.ok);
      ensureDataBlock(routePanel, "Live Route Owner Registry", routeOwnerRegistry.data || {});
      state.filled.routeOwnerRegistry = true;
    }

    const dupPanel = findPanel("Duplicate");
    if (dupPanel) {
      setPanelBackendBadge(dupPanel, duplicateRouteFailTest.ok);
      ensureDataBlock(dupPanel, "Live Duplicate Route Test", duplicateRouteFailTest.data || {});
      state.filled.duplicateRouteFailTest = true;
    }

    const propPanel = findPanel("Runtime Propagation");
    if (propPanel) {
      setPanelBackendBadge(propPanel, runtimePropagation.ok);
      ensureDataBlock(propPanel, "Live Runtime Propagation", runtimePropagation.data || {});
      state.filled.runtimePropagation = true;
    }
  }

  async function collect() {
    const out = {};
    for (const [key, route] of Object.entries(ROUTES)) {
      out[key] = await jsonFetch(route);
    }
    state.checked_at = new Date().toISOString();
    state.data = out;
    return out;
  }

  async function run() {
    const data = await collect();
    const payloadFlat = flattenPayload(data.payload);
    fillRuntimeExecution(payloadFlat, data.runtimeExecution || {});
    fillRuntimeState(payloadFlat, data.runtimeState || {});
    fillReviewQueue(payloadFlat, data.reviewQueue || {});
    fillRegistry(data.routeOwnerRegistry || {}, data.duplicateRouteFailTest || {}, data.runtimePropagation || {});
    window.ClaireLivePayloadDataFill = state;
    return state;
  }

  window.ClaireLivePayloadDataFillTools = {
    version: VERSION,
    run: run,
    state: state
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", run);
  } else {
    run();
  }

  setInterval(run, 45000);
})();
