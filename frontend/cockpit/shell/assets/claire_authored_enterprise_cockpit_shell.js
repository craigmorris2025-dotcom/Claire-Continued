/*
Claire Syntalion v19.82B.15
Authored Enterprise Cockpit Shell

This script renders backend-owned state into an authored cockpit.
It does not fabricate discoveries, route scoring, portfolio decisions, or truth promotion.
*/

(function () {
  "use strict";

  const STATE = {
    dashboardPayload: null,
    continuous: null,
    latestRun: null,
    reviewQueue: null,
    universes: null
  };

  const WORKSPACE_COPY = {
    runtime: ["Runtime", "Operate manual and continuous intelligence runs from backend-owned state."],
    intelligence: ["Intelligence", "Review governed discovery, trend, gap, and thesis signals."],
    portfolio: ["Portfolio", "Portfolio opportunities and optimization candidates from backend artifacts."],
    breakthrough: ["Breakthrough", "Qualified breakthrough candidates and classification state."],
    design: ["Design", "AutoDesign, buildability, manufacturability, feasibility, and portal outputs."],
    sources: ["Sources", "Governed source universe registry and probe readiness."],
    review: ["Review Queue", "Operator review and promotion governance."],
    system: ["System", "Payload, runtime route, and diagnostic state."]
  };

  function byId(id) {
    return document.getElementById(id);
  }

  function setText(id, value) {
    const el = byId(id);
    if (el) el.textContent = value === undefined || value === null || value === "" ? "unavailable" : String(value);
  }

  function asArray(value) {
    return Array.isArray(value) ? value : [];
  }


  async function getFirstJson(urls, fallback) {
    for (const url of urls) {
      try {
        const res = await fetch(url, { cache: "no-store" });
        const payload = await res.json().catch(() => fallback);
        if (res.ok) return payload;
      } catch (_err) {
        // Try next route.
      }
    }
    return fallback;
  }

  async function getJson(url, fallback) {
    try {
      const res = await fetch(url, { cache: "no-store" });
      const payload = await res.json().catch(() => fallback);
      if (!res.ok) return fallback;
      return payload;
    } catch (_err) {
      return fallback;
    }
  }

  function normalizeQueue(payload) {
    if (!payload) return [];
    if (Array.isArray(payload)) return payload;
    if (Array.isArray(payload.review_queue)) return payload.review_queue;
    if (Array.isArray(payload.items)) return payload.items;
    if (Array.isArray(payload.candidates)) return payload.candidates;
    if (payload.data && Array.isArray(payload.data.review_queue)) return payload.data.review_queue;
    return [];
  }

  function candidateCounts(queueItems) {
    const textItems = asArray(queueItems).map((item) => JSON.stringify(item).toLowerCase());
    return {
      discovery: textItems.filter((x) => x.includes("discovery") || x.includes("gap") || x.includes("trend") || x.includes("signal")).length,
      breakthrough: textItems.filter((x) => x.includes("breakthrough")).length,
      portfolio: textItems.filter((x) => x.includes("portfolio")).length,
      design: textItems.filter((x) => x.includes("design") || x.includes("blueprint") || x.includes("autodesign")).length,
      package: textItems.filter((x) => x.includes("package") || x.includes("acquisition")).length
    };
  }

  function renderList(id, items, emptyText) {
    const el = byId(id);
    if (!el) return;

    if (!items || items.length === 0) {
      el.className = "claire-list-empty";
      el.textContent = emptyText;
      return;
    }

    el.className = "claire-list";
    el.innerHTML = items.slice(0, 10).map((item) => {
      const title = item.title || item.name || item.headline || item.id || "Backend item";
      const route = item.route || item.type || item.category || item.status || "pending_review";
      return `<article class="claire-list-item"><strong>${escapeHtml(title)}</strong><span>${escapeHtml(route)}</span></article>`;
    }).join("");
  }

  function renderDashboardPayload(payload) {
    const lifecycle = payload && (payload.lifecycle || payload.lifecycle_state || {});
    const latest = payload && (payload.latest_run || payload.run || {});
    const terminal = payload && (payload.terminal_state || lifecycle.terminal_state);
    const route = payload && (payload.selected_route || payload.route || lifecycle.selected_route);

    STATE.latestRun = latest;

    setText("claire-status-payload", payload && (payload.status === "available" || payload.payload_status === "available") ? "available" : "unavailable");
    setText("claire-status-run", latest && (latest.run_id || latest.id) ? "active" : "none");
    setText("claire-active-run", latest && (latest.run_id || latest.id) ? (latest.run_id || latest.id) : "no active run");
    setText("claire-route-state", route || terminal || "pending evidence");
    setText("claire-lifecycle-state", lifecycle.active_stage || lifecycle.current_stage || "30-stage runtime");
    setText("system-payload-state", payload ? "available" : "checking");
    setText("claire-system-json", JSON.stringify(payload || { status: "payload_unavailable" }, null, 2));
  }

  function renderContinuous(payload) {
    STATE.continuous = payload;
    const status = payload && (payload.status || payload.state || payload.runtime_state);
    setText("claire-status-backend", payload ? "online" : "checking");
    setText("claire-continuous-state", status || "checking");
    setText("claire-continuous-badge", status || "checking");
    setText("system-runtime-state", status || "checking");
    setText("claire-continuous-json", JSON.stringify(payload || { status: "checking_continuous_runtime" }, null, 2));
  }

  function renderQueue(payload) {
    STATE.reviewQueue = payload;
    const items = normalizeQueue(payload);
    const counts = candidateCounts(items);

    setText("claire-review-count", items.length);
    setText("review-workspace-count", items.length);
    setText("claire-candidate-counts", `${counts.discovery} D · ${counts.breakthrough} B · ${counts.portfolio} P · ${counts.design} DS · ${counts.package} PKG`);
    setText("intel-discovery-count", counts.discovery);
    setText("intel-gap-count", counts.discovery);
    setText("portfolio-count", counts.portfolio);
    setText("breakthrough-count", counts.breakthrough);
    setText("design-count", counts.design);

    renderList("claire-review-list", items, "No review items exposed yet.");
    renderList("claire-discovery-list", items.filter((item) => JSON.stringify(item).toLowerCase().includes("discovery")), "No backend discovery candidates exposed yet.");
  }

  function renderUniverses(payload) {
    STATE.universes = payload;
    const universes = Array.isArray(payload) ? payload : asArray(payload && (payload.universes || payload.source_universes));
    setText("source-universe-count", universes.length);
    renderList("claire-source-list", universes, "No source universes loaded yet.");
  }

  async function refreshAll() {
    const dashboard = await getFirstJson(["/dashboard/payload", "/api/dashboard/payload"], { status: "payload_unavailable", payload_status: "unavailable" });
    const continuous = await getJson("/runtime/continuous/status", { status: "continuous_runtime_unavailable" });
    const queue = await getJson("/runtime/continuous/review-queue", { review_queue: [] });
    const universes = await getJson("/universes", { universes: [] });

    renderDashboardPayload(dashboard);
    renderContinuous(continuous);
    renderQueue(queue);
    renderUniverses(universes);
  }

  async function postJson(url, fallback) {
    try {
      const res = await fetch(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: "{}" });
      const payload = await res.json().catch(() => fallback);
      return payload;
    } catch (_err) {
      return fallback;
    }
  }

  function activateWorkspace(name) {
    const key = WORKSPACE_COPY[name] ? name : "runtime";
    document.querySelectorAll("[data-workspace-panel]").forEach((panel) => {
      panel.classList.toggle("active", panel.getAttribute("data-workspace-panel") === key);
    });
    document.querySelectorAll("[data-workspace]").forEach((button) => {
      button.classList.toggle("active", button.getAttribute("data-workspace") === key);
    });
    const copy = WORKSPACE_COPY[key];
    setText("claire-workspace-title", copy[0]);
    setText("claire-workspace-subtitle", copy[1]);
  }

  function bindEvents() {
    document.querySelectorAll("[data-workspace]").forEach((button) => {
      button.addEventListener("click", () => activateWorkspace(button.getAttribute("data-workspace")));
    });

    const form = byId("claire-command-form");
    if (form) {
      form.addEventListener("submit", (event) => {
        event.preventDefault();
        const input = byId("claire-command-input");
        const value = input ? input.value.trim() : "";
        if (!value) return;
        setText("claire-workspace-title", "Command captured");
        setText("claire-workspace-subtitle", "Command/search capture is presentation-only here until governed command routing is connected.");
      });
    }

    const refreshRuntime = byId("claire-refresh-runtime");
    if (refreshRuntime) refreshRuntime.addEventListener("click", refreshAll);

    const refreshRun = byId("claire-refresh-run");
    if (refreshRun) refreshRun.addEventListener("click", refreshAll);

    const startContinuous = byId("claire-start-continuous");
    if (startContinuous) {
      startContinuous.addEventListener("click", async () => {
        const payload = await postJson("/runtime/continuous/start", { status: "continuous_start_unavailable" });
        renderContinuous(payload);
      });
    }

    const pauseContinuous = byId("claire-pause-continuous");
    if (pauseContinuous) {
      pauseContinuous.addEventListener("click", async () => {
        const payload = await postJson("/runtime/continuous/pause", { status: "continuous_pause_unavailable" });
        renderContinuous(payload);
      });
    }

    const startRun = byId("claire-start-run");
    if (startRun) {
      startRun.addEventListener("click", async () => {
        const payload = await postJson("/runs/start", { status: "manual_run_start_unavailable" });
        setText("claire-run-json", JSON.stringify(payload, null, 2));
        refreshAll();
      });
    }
  }

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  window.ClaireAuthoredEnterpriseCockpit = {
    version: "v19.82B.15",
    refreshAll,
    activateWorkspace
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => {
      bindEvents();
      activateWorkspace("runtime");
      refreshAll();
    });
  } else {
    bindEvents();
    activateWorkspace("runtime");
    refreshAll();
  }
})();
