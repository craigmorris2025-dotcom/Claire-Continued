(() => {
  const WORKSPACE_REGISTRY = window.ClaireWorkspaceRegistry || {
    workspaces: [
      { id: "runtime", label: "Runtime", purpose: "Operate manual and continuous intelligence runs." },
      { id: "intelligence", label: "Intelligence", purpose: "Monitor signals, sources, trends, thesis, and discoveries." },
      { id: "portfolio", label: "Portfolio", purpose: "Review portfolio opportunities, risks, weights, and actions." },
      { id: "breakthrough", label: "Breakthrough", purpose: "Review breakthrough candidates, evidence, and route decisions." },
      { id: "design", label: "Design", purpose: "Review AutoDesign, stages 16-22, blueprints, and buildability." },
      { id: "existing_system", label: "Existing System", purpose: "Review system replacement and superior-system design routes." },
      { id: "acquisition", label: "Acquisition", purpose: "Review acquirer fit, package readiness, and strategic rationale." },
      { id: "sources", label: "Sources", purpose: "Review source universes, probes, trust, and evidence state." },
      { id: "memory", label: "Memory", purpose: "Review lifecycle memory and recursive self-ingestion." },
      { id: "governance", label: "Governance", purpose: "Review update governance, rollback, approval, and protected paths." },
      { id: "system", label: "System", purpose: "Review system health and technical diagnostics." }
    ]
  };

  const state = {
    workspaces: WORKSPACE_REGISTRY.workspaces || [],
    activeWorkspaceId: "runtime",
    payload: null,
    payloadStatus: "waiting",
    backendStatus: "checking",
    latestRun: null,
    continuous: null,
    reviewQueue: null,
    command: null
  };

  const $ = (id) => document.getElementById(id);

  function setText(id, value) {
    const node = $(id);
    if (node) node.textContent = value;
  }

  function activeWorkspace() {
    return state.workspaces.find((workspace) => workspace.id === state.activeWorkspaceId) || state.workspaces[0];
  }

  function findAny(payload, names) {
    if (!payload || typeof payload !== "object") return null;
    const queue = [payload];
    const seen = new Set();
    while (queue.length) {
      const current = queue.shift();
      if (!current || typeof current !== "object" || seen.has(current)) continue;
      seen.add(current);
      for (const name of names) {
        if (Object.prototype.hasOwnProperty.call(current, name) && current[name] !== null && current[name] !== undefined) {
          return current[name];
        }
      }
      Object.keys(current).forEach((key) => {
        const value = current[key];
        if (value && typeof value === "object") queue.push(value);
      });
    }
    return null;
  }

  function statusValue() {
    const p = state.payload || {};
    const continuousStatus = state.continuous && state.continuous.status;
    return findAny(p, ["terminal_state", "status", "payload_status"]) || continuousStatus || "awaiting runtime truth";
  }

  function routeValue() {
    const p = state.payload || {};
    return findAny(p, ["selected_route", "route", "advancement_path"]) || "pending evidence";
  }

  function runValue() {
    return (state.latestRun && (state.latestRun.active_run_id || state.latestRun.run_id)) ||
      findAny(state.payload || {}, ["active_run_id", "run_id"]) ||
      "no active run";
  }

  function reviewQueueCount() {
    const items = state.reviewQueue && Array.isArray(state.reviewQueue.items) ? state.reviewQueue.items : [];
    return items.length;
  }

  function candidateCounts() {
    const payload = state.payload || {};
    const cycle = findAny(payload, ["cycle"]) || {};
    const counts = cycle.candidate_counts || {};
    return {
      discoveries: counts.discoveries || 0,
      breakthroughs: counts.breakthroughs || 0,
      portfolios: counts.portfolios || 0,
      designs: counts.designs || 0,
      packages: counts.packages || 0
    };
  }

  function renderNav() {
    const nav = $("workspaceNav");
    if (!nav) return;
    nav.innerHTML = "";

    state.workspaces.forEach((workspace) => {
      const button = document.createElement("button");
      button.type = "button";
      button.textContent = workspace.label || workspace.id;
      button.dataset.workspaceId = workspace.id;
      button.className = workspace.id === state.activeWorkspaceId ? "active" : "";
      button.addEventListener("click", () => {
        state.activeWorkspaceId = workspace.id;
        render();
      });
      nav.appendChild(button);
    });
  }

  function makeCard(title, value, detail, tone) {
    const article = document.createElement("article");
    article.className = "operator-card " + (tone || "");
    const h3 = document.createElement("h3");
    h3.textContent = title;
    const strong = document.createElement("strong");
    strong.textContent = value;
    const p = document.createElement("p");
    p.textContent = detail;
    article.appendChild(h3);
    article.appendChild(strong);
    article.appendChild(p);
    return article;
  }

  function makeListCard(title, items, emptyText) {
    const article = document.createElement("article");
    article.className = "operator-card wide";
    const h3 = document.createElement("h3");
    h3.textContent = title;
    article.appendChild(h3);

    const list = document.createElement("div");
    list.className = "operator-list";
    const safeItems = Array.isArray(items) ? items.slice(0, 8) : [];
    if (!safeItems.length) {
      const empty = document.createElement("p");
      empty.textContent = emptyText;
      empty.className = "muted";
      article.appendChild(empty);
      return article;
    }
    safeItems.forEach((item) => {
      const row = document.createElement("div");
      row.className = "operator-list-row";
      row.textContent = typeof item === "string" ? item : (item.summary || item.type || item.id || JSON.stringify(item));
      list.appendChild(row);
    });
    article.appendChild(list);
    return article;
  }

  function workspaceOutcomeLabel(workspaceId) {
    const labels = {
      runtime: "Runtime is waiting for source universe, evidence, and lifecycle execution.",
      intelligence: "No validated discovery brief has been exposed yet.",
      portfolio: "No portfolio recommendation has been exposed yet.",
      breakthrough: "No breakthrough assessment has been exposed yet.",
      design: "No design package has been exposed yet.",
      existing_system: "No existing-system replacement package has been exposed yet.",
      acquisition: "No acquirer map or proof package has been exposed yet.",
      sources: "No governed source universe result has been promoted yet.",
      memory: "No recursive memory artifact has been exposed yet.",
      governance: "No governance update decision is pending.",
      system: "System diagnostics are available below when backend payload exposes them."
    };
    return labels[workspaceId] || "Awaiting backend truth.";
  }

  function renderWorkspace() {
    const workspace = activeWorkspace();
    if (!workspace) return;

    setText("activeWorkspaceTitle", workspace.label || workspace.id);
    setText("activeWorkspacePurpose", workspace.purpose || "Operator workspace.");

    const grid = $("workspaceGrid");
    if (!grid) return;
    grid.innerHTML = "";

    const counts = candidateCounts();
    const continuousStatus = state.continuous && state.continuous.status ? state.continuous.status : "unknown";

    if (workspace.id === "runtime") {
      grid.appendChild(makeCard("Continuous Runtime", continuousStatus, "24/7 governed monitoring for gaps, discoveries, breakthroughs, solutions, portfolios, designs, and packages.", continuousStatus === "active" ? "good" : "warn"));
      grid.appendChild(makeCard("Active Run", runValue(), "Manual operator runs remain separate from the always-on intelligence runtime.", runValue() === "no active run" ? "warn" : "good"));
      grid.appendChild(makeCard("Route State", routeValue(), "Route state is backend-owned and cannot be selected by the cockpit.", "neutral"));
      grid.appendChild(makeCard("Review Queue", String(reviewQueueCount()), "Items awaiting operator review before promotion.", reviewQueueCount() ? "good" : "neutral"));
    } else {
      grid.appendChild(makeCard("Workspace State", statusValue(), workspaceOutcomeLabel(workspace.id), "neutral"));
      grid.appendChild(makeCard("Backend Route", routeValue(), "Displayed from canonical backend truth only.", "neutral"));
      grid.appendChild(makeCard("Active Run", runValue(), "Use Runtime to start or inspect operator runs.", "neutral"));
      grid.appendChild(makeCard("Review Queue", String(reviewQueueCount()), "Operator review items related to this workspace appear here once generated.", reviewQueueCount() ? "good" : "neutral"));
    }

    grid.appendChild(makeCard("Candidate Counts", `${counts.discoveries} D · ${counts.breakthroughs} B · ${counts.portfolios} P · ${counts.designs} DS · ${counts.packages} PKG`, "Counts come from backend cycle artifacts only. Zero means no validated candidates exposed yet.", "neutral"));

    const queueItems = state.reviewQueue && Array.isArray(state.reviewQueue.items) ? state.reviewQueue.items : [];
    grid.appendChild(makeListCard("Operator Review Queue", queueItems, "No review items exposed yet. Claire should create these through continuous cycles or manual runs."));

    const payloadPanel = document.querySelector(".payload-panel");
    if (payloadPanel) {
      payloadPanel.style.display = workspace.id === "system" ? "block" : "none";
    }
  }

  function renderPayload() {
    setText("backendStatus", state.backendStatus);
    setText("payloadStatus", state.payloadStatus);
    setText("activeRunStatus", runValue());
    setText("payloadTimestamp", state.payload ? new Date().toLocaleString() : "awaiting backend");

    const preview = $("payloadPreview");
    if (preview) {
      preview.textContent = JSON.stringify({
        operator_state: {
          backend: state.backendStatus,
          payload: state.payloadStatus,
          active_run: runValue(),
          continuous_runtime: state.continuous && state.continuous.status ? state.continuous.status : "unknown",
          review_queue_count: reviewQueueCount(),
          route: routeValue(),
          rule: "system_workspace_only_diagnostics"
        },
        raw_payload_available: !!state.payload
      }, null, 2);
    }
  }

  function render() {
    renderNav();
    renderWorkspace();
    renderPayload();
  }

  async function fetchJson(path) {
    const response = await fetch(path, { cache: "no-store" });
    if (!response.ok) throw new Error(path + " returned " + response.status);
    return response.json();
  }

  async function hydrateBackendTruth() {
    try {
      const status = await fetchJson("/dashboard/payload/status");
      state.backendStatus = "online";
      state.payloadStatus = status && (status.status || status.payload_status || "status_online");
    } catch (error) {
      state.backendStatus = "offline";
      state.payloadStatus = "status_unavailable";
    }

    try {
      state.payload = await fetchJson("/dashboard/payload");
      state.backendStatus = "online";
      state.payloadStatus = "payload_online";
    } catch (error) {
      state.payload = null;
      if (state.backendStatus !== "online") state.backendStatus = "offline";
      state.payloadStatus = "waiting";
    }

    try {
      state.latestRun = await fetchJson("/runs/latest");
    } catch (error) {
      state.latestRun = null;
    }

    try {
      state.continuous = await fetchJson("/runtime/continuous/status");
    } catch (error) {
      state.continuous = null;
    }

    try {
      state.reviewQueue = await fetchJson("/runtime/continuous/review-queue");
    } catch (error) {
      state.reviewQueue = null;
    }

    render();
  }

  function bindCommandSurface() {
    const input = $("claireCommandInput");
    const button = $("claireCommandSubmit");
    const submit = () => {
      const value = (input && input.value || "").trim();
      if (!value) return;
      state.command = value;
      state.payload = {
        status: "command_captured_not_executed",
        command: value,
        rule: "operator_command_requires_backend_command_route",
        next_required_layer: "command router endpoint + artifact + canonical payload + cockpit render + pytest"
      };
      render();
    };

    if (button) button.addEventListener("click", submit);
    if (input) input.addEventListener("keydown", (event) => {
      if (event.key === "Enter") submit();
    });
  }

  window.ClaireCockpitHydration = {
    refresh: hydrateBackendTruth,
    acceptPayload(payload) {
      state.payload = payload;
      state.backendStatus = "online";
      state.payloadStatus = "operator_action_payload";
      render();
    },
    getState() {
      return {
        activeWorkspaceId: state.activeWorkspaceId,
        backendStatus: state.backendStatus,
        payloadStatus: state.payloadStatus,
        payload: state.payload,
        continuous: state.continuous,
        latestRun: state.latestRun,
        reviewQueue: state.reviewQueue
      };
    }
  };

  document.addEventListener("DOMContentLoaded", () => {
    bindCommandSurface();
    render();
    hydrateBackendTruth();
    window.setInterval(hydrateBackendTruth, 15000);
  });
})();

;(function(){
  if (window.__CLAIRE_OPERATOR_EXPERIENCE_LOADER__) return;
  window.__CLAIRE_OPERATOR_EXPERIENCE_LOADER__ = true;
  function loadOperatorExperience(){
    if (window.ClaireOperatorExperienceConsole && window.ClaireOperatorExperienceConsole.init) {
      window.ClaireOperatorExperienceConsole.init();
      return;
    }
    var existing = document.querySelector('script[data-claire-operator-experience="true"]');
    if (existing) return;
    var script = document.createElement('script');
    script.defer = true;
    script.dataset.claireOperatorExperience = 'true';
    script.src = '/api/cockpit/operator-experience/assets/js';
    script.onerror = function(){ script.src = 'assets/claire_operator_experience_console.js'; };
    document.head.appendChild(script);
    var link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = '/api/cockpit/operator-experience/assets/css';
    document.head.appendChild(link);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', loadOperatorExperience);
  else setTimeout(loadOperatorExperience, 0);
})();
