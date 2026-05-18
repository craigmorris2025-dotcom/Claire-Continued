(function () {
  "use strict";
  const PHASE = "S957-S984";
  const ENDPOINTS = [
    "/api/cockpit/operation-visuals/payload",
    "/api/cockpit/operations/payload"
  ];
  const MOUNT_ID = "claire-operation-control-mount";
  const ACTIONS_MOUNT_ID = "claire-operation-actions-mount";
  const WEB_MOUNT_ID = "claire-operation-web-mount";
  const PREVIEW_ID = "claire-operation-preview-mount";

  const FALLBACK_BUTTONS = [
    ["readiness_audit", "Run readiness audit", "Readiness", "Audit search/web readiness without contacting providers."],
    ["provider_inspector", "Inspect providers", "Providers", "Show provider configuration and blocked authority."],
    ["source_policy", "View source policy", "Sources", "Show allowlist, denylist, quarantine, and trust tiers."],
    ["compile_query", "Compile search plan", "Search plan", "Create a governed search plan without executing search."],
    ["metadata_probe_preview", "Preview metadata search", "Metadata search", "Preview a metadata-only provider probe while execution stays blocked."],
    ["metadata_contract", "Open metadata contract", "Metadata search", "Show the metadata-only result contract."],
    ["quarantine_store", "Open quarantine store", "Evidence", "Show quarantined results before review."],
    ["evidence_cards", "Build evidence cards", "Evidence", "Normalize quarantined metadata into review cards."],
    ["source_confidence", "Score source confidence", "Evidence", "Score source trust and citation usefulness."],
    ["operator_review", "Show review queue", "Operator review", "Show non-executable review actions."],
    ["body_read_request", "Build body-read request", "Body read", "Draft a body-read request; body reads remain blocked."],
    ["body_read_preflight", "Run body-read preflight", "Body read", "Check body-read authorization and sanitizer state."],
    ["source_ingestion", "Draft source ingestion", "Source ingestion", "Draft source ingestion without runtime mutation."],
    ["truth_promotion_preview", "Preview truth promotion", "Runtime truth", "Preview promotion while mutation remains blocked."],
    ["s900_gate", "Verify S900 gate", "Stop gates", "Verify web/source ingestion stop gate."],
    ["s956_controls", "Verify operation controls", "Stop gates", "Verify operation-control registry."],
    ["s984_visual_mount", "Verify visual mount", "Stop gates", "Verify buttons are mounted into the cockpit UI."]
  ].map(function (row) {
    return {
      key: row[0], label: row[1], group: row[2], description: row[3],
      stage_range: PHASE, cockpit_tab: "Cockpit", preview_endpoint: "/api/cockpit/operation-visuals/preview/" + row[0],
      execution_enabled: false, button_visible: true, state: "preview_only"
    };
  });

  function fallbackPayload(reason) {
    const groups = {};
    FALLBACK_BUTTONS.forEach(function (button) { (groups[button.group] = groups[button.group] || []).push(button); });
    return {
      phase: PHASE,
      status: "fallback_visual_buttons_ready",
      button_count: FALLBACK_BUTTONS.length,
      action_count: FALLBACK_BUTTONS.length,
      buttons: FALLBACK_BUTTONS,
      button_groups: groups,
      actions: FALLBACK_BUTTONS.map(function (button) {
        return { key: "fallback_" + button.key, title: button.label, group: button.group, state: "preview_only", executable_now: false, reason: button.description };
      }),
      blocked_capabilities: {
        live_web_execution_enabled: false,
        search_provider_execution_enabled: false,
        body_read_allowed: false,
        runtime_mutation_enabled: false,
        package_install_performed: false,
        command_execution_enabled: false
      },
      fallback_reason: reason || "backend payload unavailable; visual controls mounted from static safe fallback"
    };
  }

  function el(tag, attrs, text) {
    const node = document.createElement(tag);
    if (attrs) Object.entries(attrs).forEach(function (entry) {
      const key = entry[0];
      const value = entry[1];
      if (key === "class") node.className = value;
      else if (key === "html") node.innerHTML = value;
      else node.setAttribute(key, value);
    });
    if (text !== undefined && text !== null) node.textContent = text;
    return node;
  }

  function mainRoot() { return document.querySelector("main") || document.querySelector("[role='main']") || document.body; }

  function findCommandAnchor() {
    const inputs = Array.from(document.querySelectorAll("input, textarea"));
    const input = inputs.find(function (node) {
      const p = (node.getAttribute("placeholder") || "").toLowerCase();
      return p.includes("ask claire") || p.includes("governed web") || p.includes("command");
    });
    if (input) return input.closest("section, form, div") || input;
    const button = Array.from(document.querySelectorAll("button")).find(function (node) { return /command/i.test(node.textContent || ""); });
    return button ? (button.closest("section, form, div") || button) : null;
  }

  function ensurePrimaryMount() {
    let mount = document.getElementById(MOUNT_ID);
    if (!mount) {
      mount = el("section", { id: MOUNT_ID, class: "claire-opv-panel claire-opv-primary" });
      const anchor = findCommandAnchor();
      if (anchor && anchor.parentNode) {
        if (anchor.nextSibling) anchor.parentNode.insertBefore(mount, anchor.nextSibling);
        else anchor.parentNode.appendChild(mount);
      } else {
        const root = mainRoot();
        if (root.firstChild) root.insertBefore(mount, root.firstChild);
        else root.appendChild(mount);
      }
    }
    return mount;
  }

  function findHeading(pattern) {
    return Array.from(document.querySelectorAll("h1,h2,h3")).find(function (h) { return pattern.test((h.textContent || "").trim()); });
  }

  function ensureMountAfterHeading(id, pattern, fallbackAfterPrimary) {
    let mount = document.getElementById(id);
    if (mount) return mount;
    mount = el("section", { id: id, class: "claire-opv-panel claire-opv-secondary" });
    const heading = findHeading(pattern);
    if (heading && heading.parentNode) {
      if (heading.nextSibling) heading.parentNode.insertBefore(mount, heading.nextSibling);
      else heading.parentNode.appendChild(mount);
    } else if (fallbackAfterPrimary) {
      const primary = ensurePrimaryMount();
      if (primary.parentNode) primary.parentNode.insertBefore(mount, primary.nextSibling);
    } else {
      mainRoot().appendChild(mount);
    }
    return mount;
  }

  function updateActionText(payload) {
    const count = Number(payload.action_count || (payload.actions || []).length || 0);
    Array.from(document.querySelectorAll("*")).forEach(function (node) {
      if (node.children && node.children.length > 0) return;
      const text = (node.textContent || "").trim();
      if (/^Actions:\s*\d+$/i.test(text)) node.textContent = "Actions: " + count;
      if (text === "No governed actions registered.") node.textContent = count + " governed operation controls registered.";
      if (text === "No action run yet.") node.textContent = "No execution run yet. Preview buttons are available below.";
    });
  }

  function showPreview(button, data) {
    let mount = document.getElementById(PREVIEW_ID);
    if (!mount) {
      mount = el("section", { id: PREVIEW_ID, class: "claire-opv-preview" });
      const primary = ensurePrimaryMount();
      if (primary.parentNode) primary.parentNode.insertBefore(mount, primary.nextSibling);
      else mainRoot().appendChild(mount);
    }
    mount.innerHTML = "";
    mount.appendChild(el("div", { class: "claire-opv-kicker" }, "LOCAL PREVIEW ONLY"));
    mount.appendChild(el("h3", {}, button.label));
    mount.appendChild(el("p", {}, "No web execution, no body read, no runtime mutation, no package install, and no command execution occurred."));
    const pre = el("pre", { class: "claire-opv-json" });
    pre.textContent = JSON.stringify(data || { status: "preview_ready", operation: button }, null, 2);
    mount.appendChild(pre);
  }

  async function previewButton(button) {
    const url = button.preview_endpoint || ("/api/cockpit/operation-visuals/preview/" + button.key);
    try {
      const response = await fetch(url, { cache: "no-store" });
      if (!response.ok) throw new Error("HTTP " + response.status);
      const data = await response.json();
      showPreview(button, data);
    } catch (error) {
      showPreview(button, {
        status: "local_static_preview_ready",
        operation: button,
        backend_preview_error: String(error && error.message ? error.message : error),
        execution_enabled: false,
        external_network_request_performed: false,
        body_read_performed: false,
        runtime_mutation_performed: false,
        command_execution_performed: false
      });
    }
  }

  function buttonNode(button) {
    const node = el("button", { class: "claire-opv-button", type: "button", "data-operation-key": button.key });
    node.appendChild(el("span", { class: "claire-opv-button-label" }, button.label));
    node.appendChild(el("small", {}, (button.group || "Operation") + " · " + (button.stage_range || PHASE)));
    node.appendChild(el("em", {}, button.description || "Preview/preflight only."));
    node.addEventListener("click", function () { previewButton(button); });
    return node;
  }

  function renderPrimary(payload) {
    const mount = ensurePrimaryMount();
    mount.innerHTML = "";
    mount.appendChild(el("div", { class: "claire-opv-kicker" }, "OPERATOR CONTROL SURFACE · " + PHASE));
    mount.appendChild(el("h2", {}, "Governed operation buttons"));
    mount.appendChild(el("p", {}, "These controls are now visually mounted. They run local preview/preflight packets only; internet execution and dangerous authority remain blocked."));
    const grid = el("div", { class: "claire-opv-button-grid" });
    (payload.buttons || FALLBACK_BUTTONS).forEach(function (button) { grid.appendChild(buttonNode(button)); });
    mount.appendChild(grid);
  }

  function renderGrouped(mount, title, payload) {
    mount.innerHTML = "";
    mount.appendChild(el("div", { class: "claire-opv-kicker" }, "VISIBLE CONTROLS"));
    mount.appendChild(el("h2", {}, title));
    const groups = payload.button_groups || {};
    const cards = el("div", { class: "claire-opv-card-grid" });
    Object.keys(groups).forEach(function (groupName) {
      const card = el("article", { class: "claire-opv-card" });
      card.appendChild(el("h3", {}, groupName));
      card.appendChild(el("p", {}, String(groups[groupName].length) + " preview-only controls."));
      const mini = el("div", { class: "claire-opv-mini-buttons" });
      groups[groupName].forEach(function (button) { mini.appendChild(buttonNode(button)); });
      card.appendChild(mini);
      cards.appendChild(card);
    });
    mount.appendChild(cards);
  }

  function renderActions(payload) {
    const mount = ensureMountAfterHeading(ACTIONS_MOUNT_ID, /Governed Actions|Actions/i, true);
    mount.innerHTML = "";
    mount.appendChild(el("div", { class: "claire-opv-kicker" }, "ACTION REGISTRY"));
    mount.appendChild(el("h2", {}, String(payload.action_count || (payload.actions || []).length || 0) + " governed visual actions"));
    const list = el("div", { class: "claire-opv-action-list" });
    (payload.actions || []).forEach(function (action) {
      const card = el("article", { class: "claire-opv-action" });
      card.appendChild(el("strong", {}, action.title || action.key));
      card.appendChild(el("span", {}, action.group || action.stage_range || "preview_only"));
      card.appendChild(el("small", {}, action.reason || "Non-executable visual action."));
      list.appendChild(card);
    });
    mount.appendChild(list);
  }

  async function loadPayload() {
    for (const endpoint of ENDPOINTS) {
      try {
        const response = await fetch(endpoint, { cache: "no-store" });
        if (!response.ok) throw new Error("HTTP " + response.status);
        const payload = await response.json();
        if (payload && (payload.buttons || payload.button_groups || payload.actions)) return payload;
      } catch (error) { /* try next */ }
    }
    return fallbackPayload("all backend operation payload endpoints unavailable");
  }

  let rendering = false;
  async function render() {
    if (rendering) return;
    rendering = true;
    try {
      const payload = await loadPayload();
      window.ClaireOperationVisualControlsPayload = payload;
      updateActionText(payload);
      renderPrimary(payload);
      renderGrouped(ensureMountAfterHeading(WEB_MOUNT_ID, /Governed Web Workflow|Governed Web/i, true), "Governed web operation controls", payload);
      renderActions(payload);
    } finally {
      rendering = false;
    }
  }

  window.ClaireOperationVisualControls = { refresh: render, phase: PHASE, mountId: MOUNT_ID };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", render); else render();
  window.setTimeout(render, 500);
  window.setTimeout(render, 1500);
  const observer = new MutationObserver(function () {
    if (!document.getElementById(MOUNT_ID) || /No governed actions registered\./.test(document.body.textContent || "")) {
      window.clearTimeout(window.__claireOpvTimer);
      window.__claireOpvTimer = window.setTimeout(render, 250);
    }
  });
  if (document.body) observer.observe(document.body, { childList: true, subtree: true });
})();

/* CLAIRE_S985_S1012_JS_FORCE_MOUNT: force visible cockpit operation controls into active JS-rendered shell. */
(function () {
  function loadClaireS985S1012ControlSurface() {
    if (window.__CLAIRE_S985_S1012_CONTROL_SURFACE_LOADING__) return;
    window.__CLAIRE_S985_S1012_CONTROL_SURFACE_LOADING__ = true;
    if (!document.querySelector('link[data-claire-s985-s1012="active-control-surface"]')) {
      var link = document.createElement('link');
      link.rel = 'stylesheet';
      link.href = '/api/cockpit/control-surface/assets/css';
      link.setAttribute('data-claire-s985-s1012', 'active-control-surface');
      document.head.appendChild(link);
    }
    if (!document.querySelector('script[data-claire-s985-s1012="active-control-surface"]')) {
      var script = document.createElement('script');
      script.src = '/api/cockpit/control-surface/assets/js';
      script.defer = true;
      script.setAttribute('data-claire-s985-s1012', 'active-control-surface');
      document.body.appendChild(script);
    }
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', loadClaireS985S1012ControlSurface);
  } else {
    loadClaireS985S1012ControlSurface();
  }
  setTimeout(loadClaireS985S1012ControlSurface, 800);
  setTimeout(loadClaireS985S1012ControlSurface, 2000);
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
