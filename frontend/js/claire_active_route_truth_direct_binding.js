
// Claire Syntalion v19.89.8-A12
// Active Route Truth Direct Backend Binding
// Backend owns truth. Cockpit presentation only. Runtime authority remains blocked.

(function () {
  "use strict";

  const VERSION = "v19.89.8-A12";

  const ROUTES = {
    payload_status: "/dashboard/payload/status",
    cockpit_fetch_map: "/system/cockpit-fetch-map/summary",
    route_owner_registry: "/system/route-owner-registry/summary",
    duplicate_route_fail_test: "/system/duplicate-route-fail-test/summary"
  };

  async function fetchJson(path) {
    const res = await fetch(path, {
      method: "GET",
      headers: { "Accept": "application/json" },
      cache: "no-store"
    });
    const text = await res.text();
    let data = null;
    try { data = JSON.parse(text); } catch (err) { data = { raw: text }; }
    return { ok: res.ok, status: res.status, route: path, data: data };
  }

  async function collectTruth() {
    const out = {
      version: VERSION,
      checked_at: new Date().toISOString(),
      backend_owns_truth: true,
      cockpit_presentation_only: true,
      frontend_truth_allowed: false,
      runtime_authority_expanded: false,
      safe_to_expand_runtime_authority: false,
      origin: window.location.origin,
      protocol: window.location.protocol,
      routes: {}
    };

    for (const [key, route] of Object.entries(ROUTES)) {
      try {
        out.routes[key] = await fetchJson(route);
      } catch (err) {
        out.routes[key] = {
          ok: false,
          status: null,
          route: route,
          error: String(err && err.message ? err.message : err)
        };
      }
    }

    const payloadConnected = !!(out.routes.payload_status && out.routes.payload_status.ok);
    const fetchMapConnected = !!(out.routes.cockpit_fetch_map && out.routes.cockpit_fetch_map.ok);
    const duplicateConnected = !!(out.routes.duplicate_route_fail_test && out.routes.duplicate_route_fail_test.ok);

    const fetchMap = out.routes.cockpit_fetch_map && out.routes.cockpit_fetch_map.data ? out.routes.cockpit_fetch_map.data : {};
    out.summary = {
      status: payloadConnected ? "connected" : "unavailable",
      payload: payloadConnected ? "connected" : "unavailable",
      cockpit_shell: fetchMapConnected ? "backend-bound" : "unavailable",
      duplicates: duplicateConnected ? "checked" : "unavailable",
      approved_found_count: fetchMap.approved_found_count ?? null,
      unauthorized_count: fetchMap.unauthorized_count ?? null,
      required_missing_count: fetchMap.required_missing_count ?? null,
      safe_to_expand_runtime_authority: false
    };

    window.ClaireActiveRouteTruth = out;
    return out;
  }

  function findActiveRouteTruthCard() {
    const nodes = Array.from(document.querySelectorAll("section, div, article"));
    return nodes.find(function (node) {
      const text = node.innerText || "";
      return text.indexOf("Active Route Truth") >= 0 && text.indexOf("SYNCHRONIZATION PROOF") >= 0;
    });
  }

  function renderTruth(truth) {
    const card = findActiveRouteTruthCard();
    if (!card) return false;

    const text = card.innerText || "";
    const labels = Array.from(card.querySelectorAll("*"));

    function setByLabel(labelText, value) {
      const label = labels.find(function (el) {
        return (el.innerText || "").trim().toUpperCase() === labelText.toUpperCase();
      });
      if (!label) return false;
      const parent = label.parentElement || label;
      const candidates = Array.from(parent.querySelectorAll("*")).filter(function (el) {
        return el !== label && (el.innerText || "").trim() && el.children.length === 0;
      });
      if (candidates.length) {
        candidates[candidates.length - 1].textContent = value;
        return true;
      }
      parent.appendChild(document.createTextNode(" " + value));
      return true;
    }

    setByLabel("REQUIRED ROUTES", String(truth.summary.required_missing_count ?? 0) + " missing");
    setByLabel("PAYLOAD", truth.summary.payload);
    setByLabel("COCKPIT SHELL", truth.summary.cockpit_shell);
    setByLabel("DUPLICATES", truth.summary.duplicates);

    let pre = card.querySelector("pre");
    if (!pre) {
      pre = document.createElement("pre");
      pre.style.whiteSpace = "pre-wrap";
      pre.style.marginTop = "18px";
      card.appendChild(pre);
    }

    pre.textContent = JSON.stringify({
      status: truth.summary.status,
      active_route_truth_binding: VERSION,
      backend_owns_truth: true,
      cockpit_presentation_only: true,
      runtime_authority_expanded: false,
      safe_to_expand_runtime_authority: false,
      protocol: truth.protocol,
      required_route_summary: {
        missing_count: truth.summary.required_missing_count,
        approved_found_count: truth.summary.approved_found_count,
        unauthorized_count: truth.summary.unauthorized_count
      },
      routes: {
        payload_status: truth.routes.payload_status ? truth.routes.payload_status.status : null,
        cockpit_fetch_map: truth.routes.cockpit_fetch_map ? truth.routes.cockpit_fetch_map.status : null,
        route_owner_registry: truth.routes.route_owner_registry ? truth.routes.route_owner_registry.status : null,
        duplicate_route_fail_test: truth.routes.duplicate_route_fail_test ? truth.routes.duplicate_route_fail_test.status : null
      }
    }, null, 2);

    return true;
  }

  async function run() {
    const truth = await collectTruth();
    renderTruth(truth);
    return truth;
  }

  window.ClaireActiveRouteTruthTools = {
    version: VERSION,
    collectTruth,
    renderTruth,
    run
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", run);
  } else {
    run();
  }

  setInterval(run, 30000);
})();
