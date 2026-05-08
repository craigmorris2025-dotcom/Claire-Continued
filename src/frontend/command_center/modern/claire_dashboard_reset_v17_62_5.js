(function () {
  "use strict";

  const JSON_PATHS = [
    "dashboard_search_index.json",
    "dashboard_architecture_map.json",
    "lifecycle_stage_registry.json",
    "runtime_surface_registry.json",
    "route_surface_registry.json",
    "runtime_truth_status.json",
    "validation_authority_status.json",
    "evidence_traceability_status.json",
    "verified_memory_status.json",
    "recursive_feedback_status.json",
    "../../../exports/latest/dashboard_runtime_truth.json",
    "../../../exports/latest/validation_authority_report.json",
    "../../../exports/latest/evidence_traceability_index.json",
    "../../../exports/latest/verified_memory_gate_report.json",
    "../../../exports/latest/recursive_feedback_gate_report.json",
    "exports/latest/dashboard_runtime_truth.json",
    "exports/latest/validation_authority_report.json",
    "exports/latest/evidence_traceability_index.json",
    "exports/latest/verified_memory_gate_report.json",
    "exports/latest/recursive_feedback_gate_report.json"
  ];

  const state = {
    docs: [],
    selectedIndex: -1,
    listening: false,
    recognition: null
  };

  function normalize(value) {
    return String(value ?? "").replace(/\s+/g, " ").trim();
  }

  function lower(value) {
    return normalize(value).toLowerCase();
  }

  function escapeHtml(value) {
    return String(value ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function flattenJson(value, prefix = "") {
    const rows = [];
    function walk(node, path) {
      if (node === null || node === undefined) return;
      if (Array.isArray(node)) {
        node.forEach((item, index) => walk(item, `${path}[${index}]`));
        return;
      }
      if (typeof node === "object") {
        Object.entries(node).forEach(([key, item]) => walk(item, path ? `${path}.${key}` : key));
        return;
      }
      rows.push(`${path}: ${String(node)}`);
    }
    walk(value, prefix);
    return rows.join("\n");
  }

  async function fetchJson(path) {
    try {
      const response = await fetch(path, { cache: "no-store" });
      if (!response.ok) return null;
      return await response.json();
    } catch (_) {
      return null;
    }
  }

  async function fetchFirst(paths) {
    for (const path of paths) {
      const json = await fetchJson(path);
      if (json) return { path, json };
    }
    return { path: "", json: null };
  }

  function first(obj, keys, fallback = "") {
    if (!obj || typeof obj !== "object") return fallback;
    for (const key of keys) {
      const value = obj[key];
      if (value !== undefined && value !== null && value !== "") return value;
    }
    return fallback;
  }

  function section(obj, key) {
    const value = obj?.[key];
    return value && typeof value === "object" && !Array.isArray(value) ? value : {};
  }

  function compactStatus(value) {
    return lower(value || "not_generated").replace(/\s+/g, "_");
  }

  function addDoc(doc) {
    const key = `${doc.type}:${doc.path}:${doc.title}`;
    if (state.docs.some((existing) => `${existing.type}:${existing.path}:${existing.title}` === key)) return;
    state.docs.push(doc);
  }

  function collectVisibleDocs() {
    const nodes = Array.from(document.querySelectorAll(
      "section,article,.dashboard-panel,.claire-panel,.surface,.claire-surface,.portal,.claire-portal,.stage-card,.route-col,.validation-node,.roadmap-card,#claire-clean-runtime-stack"
    ));

    nodes.forEach((node, index) => {
      if (!node || node.classList.contains("claire-old-ui-hidden")) return;
      if (node.closest("#claire-clean-search-shell")) return;

      const text = normalize(node.innerText || node.textContent || "");
      if (text.length < 20) return;

      if (!node.id) node.id = `claire-clean-search-section-${index + 1}`;

      const titleNode = node.querySelector("h1,h2,h3,.section-title,.claire-clean-stack-title");
      addDoc({
        type: "visible_surface",
        title: normalize(titleNode?.innerText || titleNode?.textContent || node.id),
        path: `#${node.id}`,
        text,
        targetId: node.id
      });
    });
  }

  async function collectJsonDocs() {
    for (const path of [...new Set(JSON_PATHS)]) {
      const json = await fetchJson(path);
      if (!json) continue;

      if (json.schema === "claire.dashboard_intelligence_index.v1" && Array.isArray(json.documents)) {
        for (const doc of json.documents) {
          if (doc.status && doc.status !== "indexed") continue;
          addDoc({
            type: "dashboard_index",
            title: doc.title || doc.path || path,
            path: doc.path || path,
            text: doc.text || (Array.isArray(doc.terms) ? doc.terms.join(" ") : ""),
            json: doc
          });
        }
      }

      addDoc({
        type: "runtime_or_contract_json",
        title: path.split("/").pop() || path,
        path,
        text: flattenJson(json),
        json
      });
    }
  }

  function score(doc, parts) {
    const haystack = `${doc.title}\n${doc.path}\n${doc.text}`.toLowerCase();
    let value = 0;
    for (const part of parts) {
      if (doc.title.toLowerCase().includes(part)) value += 14;
      if (doc.path.toLowerCase().includes(part)) value += 7;
      value += Math.min(haystack.split(part).length - 1, 14);
    }
    return value;
  }

  function snippet(text, parts) {
    const clean = normalize(text);
    const hay = clean.toLowerCase();
    let idx = -1;
    for (const part of parts) {
      idx = hay.indexOf(part);
      if (idx >= 0) break;
    }
    if (idx < 0) return clean.slice(0, 220);
    const start = Math.max(0, idx - 80);
    const end = Math.min(clean.length, idx + 180);
    return `${start > 0 ? "…" : ""}${clean.slice(start, end)}${end < clean.length ? "…" : ""}`;
  }

  function search(query) {
    const parts = lower(query).split(" ").filter(Boolean);
    if (!parts.length) return [];
    return state.docs
      .map((doc) => ({ doc, score: score(doc, parts), snippet: snippet(doc.text, parts) }))
      .filter((item) => item.score > 0)
      .sort((a, b) => b.score - a.score)
      .slice(0, 12);
  }

  function findIntroText() {
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    let node;
    const patterns = [
      "operating environment aligned",
      "complete systems flow map",
      "runtime truth first",
      "no fake run data"
    ];

    while ((node = walker.nextNode())) {
      const text = lower(node.nodeValue);
      if (patterns.some((pattern) => text.includes(pattern))) {
        return node.parentElement;
      }
    }
    return null;
  }

  function findBrandMount() {
    const existing = document.getElementById("claire-clean-search-slot");
    if (existing) return existing;

    const intro = findIntroText();
    if (intro) {
      intro.classList.add("claire-clean-intro-hidden");
      const slot = document.createElement("div");
      slot.id = "claire-clean-search-slot";
      intro.insertAdjacentElement("afterend", slot);
      return slot;
    }

    const candidates = Array.from(document.querySelectorAll("aside,nav,header,.sidebar,.side-nav,.brand,.identity,div"));
    for (const node of candidates) {
      const text = lower(node.innerText || node.textContent || "");
      if (text.includes("claire syntalion") || text.includes("claire")) {
        const slot = document.createElement("div");
        slot.id = "claire-clean-search-slot";
        node.appendChild(slot);
        return slot;
      }
    }

    const slot = document.createElement("div");
    slot.id = "claire-clean-search-slot";
    document.body.prepend(slot);
    return slot;
  }

  function micIcon() {
    return `
      <svg width="17" height="17" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path d="M12 14a3 3 0 0 0 3-3V6a3 3 0 1 0-6 0v5a3 3 0 0 0 3 3Z" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        <path d="M19 11a7 7 0 0 1-14 0" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        <path d="M12 18v4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        <path d="M8 22h8" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      </svg>
    `;
  }

  function removeConflictingUi() {
    document.querySelectorAll(".claire-dashboard-search-shell,#claire-dashboard-search-shell").forEach((node) => {
      if (node.id !== "claire-clean-search-shell") node.remove();
    });

    [
      "#claire-validation-authority-panel",
      "#claire-verified-memory-panel",
      "#claire-search-json-result-panel"
    ].forEach((selector) => {
      document.querySelectorAll(selector).forEach((node) => {
        node.classList.add("claire-old-ui-hidden");
      });
    });
  }

  function renderSearch() {
    removeConflictingUi();

    const old = document.getElementById("claire-clean-search-shell");
    if (old) old.remove();

    const mount = findBrandMount();
    const shell = document.createElement("div");
    shell.id = "claire-clean-search-shell";
    shell.innerHTML = `
      <div class="claire-clean-search-box">
        <input id="claire-clean-search-input" class="claire-clean-search-input" autocomplete="off" spellcheck="false" placeholder="Search or ask Claire…" aria-label="Claire dashboard search" />
        <button id="claire-clean-mic" class="claire-clean-mic" type="button" aria-label="Use microphone">${micIcon()}</button>
      </div>
      <div id="claire-clean-search-results" class="claire-clean-search-results" role="listbox"></div>
    `;
    mount.appendChild(shell);

    const input = document.getElementById("claire-clean-search-input");
    const results = document.getElementById("claire-clean-search-results");
    const mic = document.getElementById("claire-clean-mic");

    input.addEventListener("input", () => {
      const query = input.value.trim();
      state.selectedIndex = -1;
      if (!query) {
        results.classList.remove("open");
        results.innerHTML = "";
        return;
      }
      renderSearchResults(search(query));
    });

    input.addEventListener("focus", () => {
      if (input.value.trim()) renderSearchResults(search(input.value));
    });

    input.addEventListener("keydown", (event) => {
      const buttons = Array.from(results.querySelectorAll(".claire-clean-result"));
      if (event.key === "Escape") {
        results.classList.remove("open");
        input.blur();
      } else if (event.key === "ArrowDown" && buttons.length) {
        event.preventDefault();
        state.selectedIndex = Math.min(buttons.length - 1, state.selectedIndex + 1);
        markActive(buttons);
      } else if (event.key === "ArrowUp" && buttons.length) {
        event.preventDefault();
        state.selectedIndex = Math.max(0, state.selectedIndex - 1);
        markActive(buttons);
      } else if (event.key === "Enter" && state.selectedIndex >= 0 && buttons[state.selectedIndex]) {
        event.preventDefault();
        buttons[state.selectedIndex].click();
      }
    });

    document.addEventListener("keydown", (event) => {
      const isMac = navigator.platform.toUpperCase().includes("MAC");
      if ((isMac ? event.metaKey : event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        input.focus();
        input.select();
      }
    });

    document.addEventListener("click", (event) => {
      if (!shell.contains(event.target)) results.classList.remove("open");
    });

    setupMic(input, mic);
  }

  function setupMic(input, mic) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      mic.disabled = true;
      mic.title = "Microphone search is not supported in this browser.";
      return;
    }

    const recognition = new SpeechRecognition();
    state.recognition = recognition;
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = navigator.language || "en-US";

    recognition.onstart = () => {
      state.listening = true;
      mic.classList.add("listening");
      input.placeholder = "Listening…";
    };

    recognition.onend = () => {
      state.listening = false;
      mic.classList.remove("listening");
      input.placeholder = "Search or ask Claire…";
    };

    recognition.onerror = () => {
      state.listening = false;
      mic.classList.remove("listening");
      input.placeholder = "Search or ask Claire…";
    };

    recognition.onresult = (event) => {
      const transcript = Array.from(event.results || [])
        .map((result) => result[0]?.transcript || "")
        .join(" ")
        .trim();
      if (transcript) {
        input.value = transcript;
        input.dispatchEvent(new Event("input", { bubbles: true }));
        input.focus();
      }
    };

    mic.addEventListener("click", () => {
      try {
        if (state.listening) recognition.stop();
        else recognition.start();
      } catch (_) {}
    });
  }

  function markActive(buttons) {
    buttons.forEach((button, index) => {
      button.classList.toggle("active", index === state.selectedIndex);
      if (index === state.selectedIndex) button.scrollIntoView({ block: "nearest" });
    });
  }

  function renderSearchResults(items) {
    const results = document.getElementById("claire-clean-search-results");
    if (!results) return;
    results.classList.add("open");

    if (!items.length) {
      results.innerHTML = `<div class="claire-clean-result-snippet" style="padding:12px;">No local dashboard/runtime matches. Generate truth, validation, memory, and index reports if this data should exist.</div>`;
      return;
    }

    results.innerHTML = items.map((item, index) => `
      <button class="claire-clean-result" type="button" data-index="${index}">
        <div class="claire-clean-result-title">${escapeHtml(item.doc.title)}</div>
        <div class="claire-clean-result-meta">${escapeHtml(item.doc.type)} · ${escapeHtml(item.doc.path)}</div>
        <div class="claire-clean-result-snippet">${escapeHtml(item.snippet)}</div>
      </button>
    `).join("");

    Array.from(results.querySelectorAll(".claire-clean-result")).forEach((button, index) => {
      button.addEventListener("click", () => openResult(items[index].doc));
    });
  }

  function openResult(doc) {
    const results = document.getElementById("claire-clean-search-results");
    if (results) results.classList.remove("open");

    if (doc.targetId) {
      const node = document.getElementById(doc.targetId);
      if (node) {
        node.scrollIntoView({ behavior: "smooth", block: "start" });
        node.style.outline = "2px solid rgba(0,212,255,.72)";
        node.style.boxShadow = "0 0 24px rgba(0,212,255,.22)";
        setTimeout(() => {
          node.style.outline = "";
          node.style.boxShadow = "";
        }, 2400);
      }
      return;
    }

    const stack = ensureRuntimeStack();
    const panel = document.createElement("section");
    panel.className = "claire-clean-stack-section";
    panel.innerHTML = `
      <div class="claire-clean-stack-header">
        <div>
          <div class="claire-clean-stack-kicker">Search Result</div>
          <div class="claire-clean-stack-title">${escapeHtml(doc.title)}</div>
          <div class="claire-clean-stack-subtitle">${escapeHtml(doc.path)}</div>
        </div>
      </div>
      <pre style="white-space:pre-wrap; overflow-wrap:anywhere; max-height:52vh; overflow:auto;">${escapeHtml(JSON.stringify(doc.json ?? doc.text, null, 2))}</pre>
    `;
    stack.appendChild(panel);
    panel.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function findPanelByHeading(text) {
    const wanted = lower(text);
    const headings = Array.from(document.querySelectorAll("h1,h2,h3,h4,.section-title,.surface-title,.panel-title"));
    for (const heading of headings) {
      if (!lower(heading.innerText || heading.textContent).includes(wanted)) continue;
      return heading.closest("section,article,.dashboard-panel,.claire-panel,.surface,.portal,div");
    }
    return null;
  }

  function mainMount() {
    return document.querySelector("main") || document.getElementById("app") || document.getElementById("workspace") || document.body;
  }

  function repairCommandPanel() {
    const panel = findPanelByHeading("command");
    if (!panel) return null;

    panel.classList.add("claire-clean-command-repaired");

    // Neutralize obvious clipped descendants.
    Array.from(panel.querySelectorAll("*")).forEach((node) => {
      const style = window.getComputedStyle(node);
      const clipped = ["hidden", "auto", "scroll"].includes(style.overflowY) || ["hidden", "auto", "scroll"].includes(style.overflow);
      if (clipped || style.maxHeight !== "none") {
        node.style.overflow = "visible";
        node.style.overflowY = "visible";
        node.style.maxHeight = "none";
      }
    });

    return panel;
  }

  function ensureRuntimeStack() {
    let stack = document.getElementById("claire-clean-runtime-stack");
    if (stack) return stack;

    stack = document.createElement("div");
    stack.id = "claire-clean-runtime-stack";

    const commandPanel = repairCommandPanel();
    if (commandPanel && commandPanel.parentElement) {
      commandPanel.insertAdjacentElement("afterend", stack);
    } else {
      mainMount().prepend(stack);
    }

    return stack;
  }

  function metric(label, value, note = "") {
    return `
      <div class="claire-clean-card">
        <div class="claire-clean-label">${escapeHtml(label)}</div>
        <div class="claire-clean-value">${escapeHtml(value ?? "unknown")}</div>
        ${note ? `<div class="claire-clean-note">${escapeHtml(note)}</div>` : ""}
      </div>
    `;
  }

  function pill(value) {
    const status = compactStatus(value);
    return `<span class="claire-clean-pill ${escapeHtml(status)}">${escapeHtml(value || "not_generated")}</span>`;
  }

  async function buildTruthData() {
    const runtime = await fetchFirst([
      "../../../exports/latest/dashboard_runtime_truth.json",
      "exports/latest/dashboard_runtime_truth.json",
      "runtime_truth_status.json",
      "./runtime_truth_status.json"
    ]);
    const validation = await fetchFirst([
      "../../../exports/latest/validation_authority_report.json",
      "exports/latest/validation_authority_report.json",
      "validation_authority_status.json",
      "./validation_authority_status.json"
    ]);
    const evidence = await fetchFirst([
      "../../../exports/latest/evidence_traceability_index.json",
      "exports/latest/evidence_traceability_index.json",
      "evidence_traceability_status.json",
      "./evidence_traceability_status.json"
    ]);
    const memory = await fetchFirst([
      "../../../exports/latest/verified_memory_gate_report.json",
      "exports/latest/verified_memory_gate_report.json",
      "verified_memory_status.json",
      "./verified_memory_status.json"
    ]);
    const feedback = await fetchFirst([
      "../../../exports/latest/recursive_feedback_gate_report.json",
      "exports/latest/recursive_feedback_gate_report.json",
      "recursive_feedback_status.json",
      "./recursive_feedback_status.json"
    ]);

    return { runtime, validation, evidence, memory, feedback };
  }

  function runtimeValues(data) {
    const r = data.runtime.json || {};
    const run = section(r, "run_truth");
    const route = section(r, "route_truth");
    const term = section(r, "terminal_truth");
    const stage = section(r, "stage_truth");
    const validation = data.validation.json || {};
    const memory = data.memory.json || {};

    return {
      runId: first(validation, ["run_id"], first(run, ["run_id", "id"], first(r, ["run_id"], "not_loaded"))),
      route: first(validation, ["route_selected"], first(route, ["route_selected", "selected_route"], first(run, ["selected_route"], "not_loaded"))),
      terminal: first(validation, ["terminal_state"], first(term, ["terminal_state", "state"], first(run, ["terminal_state"], "missing"))),
      stages: first(stage, ["stages_total", "total_stages"], Array.isArray(stage.stages) ? stage.stages.length : "not_loaded"),
      validationStatus: first(validation, ["validation_authority_status", "validation_status"], "not_generated"),
      validationScore: first(validation, ["validation_score"], 0),
      checks: `${first(validation, ["checks_passed"], 0)} pass / ${first(validation, ["checks_warning"], 0)} warn / ${first(validation, ["checks_failed"], 0)} fail`,
      evidenceCount: first(data.evidence.json || {}, ["evidence_count"], first(validation.evidence_summary || {}, ["evidence_count"], 0)),
      unsupported: first(data.evidence.json || {}, ["unsupported_count"], first(validation.evidence_summary || {}, ["unsupported_count"], 0)),
      memoryStatus: first(memory, ["memory_status"], "not_generated"),
      memoryEligible: first(memory, ["memory_eligible"], false) ? "eligible" : "blocked",
      feedbackStatus: first(data.feedback.json || {}, ["feedback_status"], "not_generated"),
      feedbackAllowed: first(data.feedback.json || {}, ["recursive_feedback_allowed"], false) ? "allowed" : "blocked"
    };
  }

  async function renderRuntimeStack() {
    removeConflictingUi();
    const stack = ensureRuntimeStack();
    const data = await buildTruthData();
    const v = runtimeValues(data);

    stack.innerHTML = `
      <section class="claire-clean-stack-section">
        <div class="claire-clean-stack-header">
          <div>
            <div class="claire-clean-stack-kicker">Runtime Truth Stack</div>
            <div class="claire-clean-stack-title">Run, Route, Terminal, Stage, Validation</div>
            <div class="claire-clean-stack-subtitle">
              Stable replacement for the conflicting generated panels. It reads the same local truth/status files without inventing output.
            </div>
          </div>
          ${pill(v.validationStatus)}
        </div>
        <div class="claire-clean-grid">
          ${metric("Run", v.runId, data.runtime.path || "runtime truth source")}
          ${metric("Route", v.route)}
          ${metric("Terminal", v.terminal)}
          ${metric("Stages", v.stages)}
          ${metric("Validation score", `${v.validationScore}/100`)}
          ${metric("Checks", v.checks)}
          ${metric("Evidence", `${v.evidenceCount} item(s)`)}
          ${metric("Unsupported", v.unsupported)}
        </div>
      </section>

      <section class="claire-clean-stack-section purple">
        <div class="claire-clean-stack-header">
          <div>
            <div class="claire-clean-stack-kicker">Verified Memory + Recursive Feedback</div>
            <div class="claire-clean-stack-title">Memory Gate and Recursion Gate</div>
            <div class="claire-clean-stack-subtitle">
              No validation pass means no verified memory and no recursive feedback. This panel is gated report only.
            </div>
          </div>
          ${pill(v.memoryStatus)}
        </div>
        <div class="claire-clean-grid">
          ${metric("Memory status", v.memoryStatus)}
          ${metric("Memory eligibility", v.memoryEligible)}
          ${metric("Feedback status", v.feedbackStatus)}
          ${metric("Feedback allowed", v.feedbackAllowed)}
          ${metric("Validation dependency", v.validationStatus)}
          ${metric("Storage mode", first(data.memory.json || {}, ["storage_mode"], "gated_report_only"))}
          ${metric("Memory reason", (data.memory.json?.memory_reasons || ["Run verified memory command after validation."])[0], "",)}
          ${metric("Feedback reason", (data.feedback.json?.feedback_reasons || ["Recursive feedback blocked until verified memory eligibility passes."])[0], "",)}
        </div>
      </section>
    `;

    collectVisibleDocs();
  }

  function installFocusToggle() {
    const existing = document.getElementById("claire-view-mode-toggle");
    if (existing) return;
    const button = document.createElement("button");
    button.id = "claire-view-mode-toggle";
    button.className = "claire-view-mode-toggle";
    button.type = "button";
    button.textContent = "Focus View";
    button.title = "Toggle focused dashboard view";
    button.addEventListener("click", () => {
      document.body.classList.toggle("claire-focus-mode");
      button.textContent = document.body.classList.contains("claire-focus-mode") ? "Full View" : "Focus View";
    });
    document.body.appendChild(button);
  }

  async function boot() {
    removeConflictingUi();
    renderSearch();
    installFocusToggle();
    repairCommandPanel();
    await renderRuntimeStack();

    state.docs = [];
    collectVisibleDocs();
    await collectJsonDocs();

    // Catch late-mounted conflicting panels from older bridge scripts.
    setTimeout(async () => {
      removeConflictingUi();
      repairCommandPanel();
      await renderRuntimeStack();
    }, 900);

    setTimeout(async () => {
      removeConflictingUi();
      repairCommandPanel();
    }, 2200);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
