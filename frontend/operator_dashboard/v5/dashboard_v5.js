"use strict";

(function () {
  const state = {
    payload: null,
    operational: null,
    selectedStage: 1,
    selectedPanel: "overview",
    selectedMode: "operate",
    filter: ""
  };

  function text(value) {
    if (Array.isArray(value)) return value.join(", ");
    if (value && typeof value === "object") return JSON.stringify(value);
    if (value === true) return "true";
    if (value === false) return "false";
    return String(value ?? "");
  }

  function label(value) {
    return String(value || "").replaceAll("_", " ");
  }

  function node(tag, attrs, value) {
    const element = document.createElement(tag);
    Object.entries(attrs || {}).forEach(([key, attrValue]) => {
      if (key === "className") element.className = attrValue;
      else element.setAttribute(key, attrValue);
    });
    if (typeof value !== "undefined") element.textContent = value;
    return element;
  }

  function stageByNumber(number) {
    return state.payload.stages.find((stage) => stage.number === number) || state.payload.stages[0];
  }

  function matchesFilter(stage) {
    const needle = state.filter.trim().toLowerCase();
    if (!needle) return true;
    return [
      stage.number,
      stage.name,
      stage.band_label,
      stage.phase,
      stage.payload_key,
      stage.route_condition,
      stage.owning_subsystem
    ].join(" ").toLowerCase().includes(needle);
  }

  function renderFields(id, fields) {
    const target = document.getElementById(id);
    target.replaceChildren();
    Object.entries(fields).forEach(([key, value]) => {
      const row = node("div");
      row.appendChild(node("dt", {}, label(key)));
      row.appendChild(node("dd", {}, text(value)));
      target.appendChild(row);
    });
  }

  function renderPanelNav() {
    const target = document.getElementById("panel-nav");
    target.replaceChildren();
    state.payload.operator_panels.forEach((panel) => {
      const button = node("button", {
        type: "button",
        "aria-current": panel.id === state.selectedPanel ? "true" : "false"
      });
      button.innerHTML = `<strong>${panel.label}</strong><span>${panel.purpose}</span>`;
      button.addEventListener("click", () => {
        state.selectedPanel = panel.id;
        renderPanelNav();
      });
      target.appendChild(button);
    });
  }

  function renderModes() {
    const target = document.getElementById("mode-switch");
    target.replaceChildren();
    state.payload.command_surface.modes.forEach((mode) => {
      const button = node("button", {
        type: "button",
        "aria-current": mode === state.selectedMode ? "true" : "false"
      }, label(mode));
      button.addEventListener("click", () => {
        state.selectedMode = mode;
        document.getElementById("active-mode").textContent = label(mode);
        renderModes();
      });
      target.appendChild(button);
    });
  }

  function renderBands() {
    const target = document.getElementById("band-strip");
    target.replaceChildren();
    state.payload.pipeline_bands.forEach((band) => {
      const card = node("article", { className: "band-card" });
      card.innerHTML = `<strong>${band.label}</strong><small>Stages ${band.stage_range[0]}-${band.stage_range[1]}</small><small>${band.purpose}</small>`;
      card.addEventListener("click", () => {
        state.filter = band.label;
        document.getElementById("stage-search").value = band.label;
        renderStageMap();
      });
      target.appendChild(card);
    });
  }

  function renderOperatorActions() {
    const target = document.getElementById("operator-actions");
    target.replaceChildren();
    const operationalActions = state.operational?.actions || [];
    const actions = operationalActions.length ? operationalActions : state.payload.operator_workflows;
    actions.forEach((workflow) => {
      const endpoint = workflow.endpoint || "/api/dashboard/v5/payload";
      const stageScope = workflow.stage_scope || [1, 30];
      const card = node("article", { className: "action-card" });
      card.innerHTML = `
        <strong>${workflow.label}</strong>
        <span>${workflow.method || "GET"} ${endpoint}</span>
        <button type="button">Run Check</button>
        <small>${workflow.execution_enabled ? "Execution enabled" : "Safe read-only control"}</small>
      `;
      card.querySelector("button").addEventListener("click", () => runControl(workflow, stageScope));
      target.appendChild(card);
    });
  }

  async function runControl(workflow, stageScope) {
    const endpoint = workflow.endpoint || "/api/dashboard/v5/payload";
    const method = workflow.method || "GET";
    const options = {
      method,
      cache: "no-store",
      headers: { "Accept": "application/json" }
    };
    if (method === "POST") {
      options.headers["Content-Type"] = "application/json";
      options.body = JSON.stringify(workflow.body || {});
    }
    const output = document.getElementById("command-output");
    if (output) output.textContent = `Running ${method} ${endpoint}...`;
    const response = await fetch(endpoint, options);
    const result = await response.json();
    state.selectedPanel = workflow.route || "diagnostics";
    state.selectedStage = (stageScope || workflow.stage_scope || [1, 30])[0];
    renderPanelNav();
    renderStageMap();
    renderSelectedStage();
    const formatted = JSON.stringify({
      control: workflow.label,
      endpoint,
      method,
      status_code: response.status,
      result
    }, null, 2);
    document.getElementById("payload-contract").textContent = formatted;
    if (output) output.textContent = formatted;
  }

  function renderPlatformConsole() {
    const operational = state.operational || state.payload.operational_control_plane || {};
    document.getElementById("route-health-metric").textContent = `Routes ${operational.route_health?.mounted_count || 0}/${operational.route_health?.required_count || 0}`;
    document.getElementById("file-health-metric").textContent = `Files ${operational.file_readiness?.present_count || 0}/${operational.file_readiness?.required_count || 0}`;
    document.getElementById("control-plane-metric").textContent = label(operational.status || "unknown");

    const target = document.getElementById("platform-action-groups");
    target.replaceChildren();
    const groups = {};
    (operational.actions || []).forEach((action) => {
      const category = action.category || "System";
      groups[category] = groups[category] || [];
      groups[category].push(action);
    });
    Object.entries(groups).forEach(([category, actions]) => {
      const group = node("article", { className: "control-group" });
      group.appendChild(node("h3", {}, category));
      const buttons = node("div", { className: "control-buttons" });
      actions.forEach((action) => {
        const button = node("button", { type: "button" });
        button.innerHTML = `<strong>${action.label}</strong><span>${action.method} ${action.endpoint}</span>`;
        button.addEventListener("click", () => runControl(action));
        buttons.appendChild(button);
      });
      group.appendChild(buttons);
      target.appendChild(group);
    });
  }

  function renderStageMap() {
    const target = document.getElementById("stage-map");
    target.replaceChildren();
    state.payload.stages.filter(matchesFilter).forEach((stage) => {
      const button = node("button", {
        type: "button",
        className: "stage-button",
        "aria-current": stage.number === state.selectedStage ? "true" : "false"
      });
      button.innerHTML = `<b>${stage.number}</b><span>${stage.name}</span><small>${label(stage.status)}</small>`;
      button.addEventListener("click", () => {
        state.selectedStage = stage.number;
        renderStageMap();
        renderSelectedStage();
      });
      target.appendChild(button);
    });
  }

  function renderSelectedStage() {
    const stage = stageByNumber(state.selectedStage);
    document.getElementById("stage-band-label").textContent = stage.band_label;
    document.getElementById("stage-title").textContent = `${stage.number}. ${stage.name}`;
    document.getElementById("stage-summary").textContent = `${stage.band_label}: ${stage.route_condition}`;
    renderFields("stage-fields", {
      status: stage.status,
      phase: stage.phase,
      requirement: stage.requirement,
      owning_subsystem: stage.owning_subsystem,
      payload_key: stage.payload_key,
      artifact_slot: stage.artifact_slot,
      required_evidence: stage.required_evidence,
      operator_next_action: stage.operator_next_action
    });

    const evidenceTarget = document.getElementById("evidence-basket");
    evidenceTarget.replaceChildren();
    stage.required_evidence.forEach((item) => evidenceTarget.appendChild(node("span", {}, label(item))));
  }

  function renderDesignRoute() {
    const target = document.getElementById("design-route");
    target.replaceChildren();
    state.payload.design_route.stages.forEach((stage) => {
      const card = node("article", { className: "design-stage" });
      card.innerHTML = `<strong>${stage.number}. ${stage.name}</strong><span>${label(stage.status)} / ${label(stage.payload_key)}</span>`;
      card.addEventListener("click", () => {
        state.selectedStage = stage.number;
        renderStageMap();
        renderSelectedStage();
      });
      target.appendChild(card);
    });
  }

  function renderSystemProcesses() {
    const target = document.getElementById("system-processes");
    target.replaceChildren();
    state.payload.system_processes.forEach((process) => {
      const row = node("article", { className: "process-row" });
      row.innerHTML = `<strong>${process.label}</strong><span>${label(process.status)} / ${process.route}</span><small>${process.operator_value}</small>`;
      target.appendChild(row);
    });
  }

  function renderAcquisitionPackage() {
    const target = document.getElementById("acquisition-package");
    target.replaceChildren();
    state.payload.stages.filter((stage) => stage.number >= 28).forEach((stage) => {
      const row = node("article", { className: "package-row" });
      row.innerHTML = `<strong>${stage.number}. ${stage.name}</strong><span>${label(stage.payload_key)}</span>`;
      target.appendChild(row);
    });
  }

  function renderProofAndSystemPanels() {
    const proof = state.payload.proof_status || {};
    renderFields("proof-status", proof);

    const pathTarget = document.getElementById("default-path");
    pathTarget.replaceChildren();
    const defaultPath = state.payload.normalized_v4.domains.signal_governance.signals.default_path || [];
    defaultPath.forEach((item) => pathTarget.appendChild(node("li", {}, label(item))));

    renderFields("governance-locks", state.payload.normalized_v4.domains.governance.signals);
    renderSystemProcesses();
    renderAcquisitionPackage();
    renderOperationalWiring();

    document.getElementById("payload-contract").textContent = JSON.stringify({
      schema_version: state.payload.schema_version,
      surface: state.payload.dashboard_identity.surface,
      stage_count: state.payload.stage_count,
      operator_workflows: state.payload.operator_workflows.length,
      operator_panels: state.payload.operator_panels.length,
      design_route: {
        required: state.payload.design_route.required,
        stage_range: state.payload.design_route.stage_range,
        stage_count: state.payload.design_route.stage_count
      },
      command_surface: state.payload.command_surface,
      operational_control_plane: {
        status: state.operational?.status || state.payload.operational_control_plane?.status,
        completion_percent: state.operational?.completion_percent || state.payload.operational_control_plane?.completion_percent,
        route_health: state.operational?.route_health?.status,
        file_readiness: state.operational?.file_readiness?.status,
        update_governance: state.operational?.update_governance?.status,
        internet_authority: state.operational?.internet_authority?.status
      },
      scores: state.payload.scores
    }, null, 2);
  }

  function renderOperationalWiring() {
    const target = document.getElementById("operational-wiring");
    target.replaceChildren();
    const operational = state.operational || state.payload.operational_control_plane || {};
    [
      ["Control plane", operational.status],
      ["Routes", `${operational.route_health?.mounted_count || 0}/${operational.route_health?.required_count || 0}`],
      ["Files", `${operational.file_readiness?.present_count || 0}/${operational.file_readiness?.required_count || 0}`],
      ["Source lineage", operational.source_lineage?.status],
      ["Update governance", operational.update_governance?.status]
    ].forEach(([name, value]) => {
      const row = node("article", { className: "process-row" });
      row.innerHTML = `<strong>${name}</strong><span>${label(value || "unknown")}</span>`;
      target.appendChild(row);
    });
    renderFields("authority-state", {
      internet: operational.internet_authority?.status || "unknown",
      live_search_enabled: operational.internet_authority?.live_search_enabled ?? false,
      automatic_updates_enabled: operational.update_governance?.automatic_updates_enabled ?? false,
      selected_provider: operational.internet_authority?.selected_provider || "none",
      missing_update_policy_files: operational.update_governance?.missing_policy_files || []
    });
  }

  function bindToolbar() {
    document.getElementById("stage-search").addEventListener("input", (event) => {
      state.filter = event.target.value;
      renderStageMap();
    });
    document.getElementById("reset-view").addEventListener("click", () => {
      state.filter = "";
      state.selectedStage = 1;
      state.selectedPanel = "overview";
      state.selectedMode = state.payload.command_surface.default_mode;
      document.getElementById("stage-search").value = "";
      document.getElementById("active-mode").textContent = label(state.selectedMode);
      render();
    });
  }

  function render() {
    document.getElementById("completion-score").textContent = `${state.payload.completion_percent}%`;
    document.getElementById("active-mode").textContent = label(state.selectedMode);
    renderPanelNav();
    renderModes();
    renderBands();
    renderPlatformConsole();
    renderOperatorActions();
    renderStageMap();
    renderSelectedStage();
    renderDesignRoute();
    renderProofAndSystemPanels();
  }

  async function boot() {
    const response = await fetch("/api/dashboard/v5/payload", {
      method: "GET",
      headers: { "Accept": "application/json" },
      cache: "no-store"
    });
    state.payload = await response.json();
    const operationalResponse = await fetch("/api/operational/control-plane", {
      method: "GET",
      headers: { "Accept": "application/json" },
      cache: "no-store"
    });
    state.operational = await operationalResponse.json();
    state.selectedMode = state.payload.command_surface.default_mode;
    bindToolbar();
    render();
  }

  window.ClaireDashboardV5 = { boot, state };
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
