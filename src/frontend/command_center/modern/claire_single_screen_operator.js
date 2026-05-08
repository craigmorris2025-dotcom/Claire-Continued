(function () {
  "use strict";

  const PATHS = {
    runtime: [
      "../../../exports/latest/dashboard_runtime_truth.json",
      "exports/latest/dashboard_runtime_truth.json",
      "runtime_truth_status.json",
      "./runtime_truth_status.json"
    ],
    validation: [
      "../../../exports/latest/validation_authority_report.json",
      "exports/latest/validation_authority_report.json",
      "validation_authority_status.json",
      "./validation_authority_status.json"
    ],
    evidence: [
      "../../../exports/latest/evidence_traceability_index.json",
      "exports/latest/evidence_traceability_index.json",
      "evidence_traceability_status.json",
      "./evidence_traceability_status.json"
    ],
    memory: [
      "../../../exports/latest/verified_memory_gate_report.json",
      "exports/latest/verified_memory_gate_report.json",
      "verified_memory_status.json",
      "./verified_memory_status.json"
    ],
    feedback: [
      "../../../exports/latest/recursive_feedback_gate_report.json",
      "exports/latest/recursive_feedback_gate_report.json",
      "recursive_feedback_status.json",
      "./recursive_feedback_status.json"
    ],
    search: [
      "dashboard_search_index.json",
      "./dashboard_search_index.json",
      "../../../exports/latest/dashboard_search_index.json",
      "exports/latest/dashboard_search_index.json"
    ],
    registries: [
      "dashboard_architecture_map.json",
      "lifecycle_stage_registry.json",
      "runtime_surface_registry.json",
      "route_surface_registry.json",
      "dashboard_search_contract.json",
      "intelligence_command_contract.json"
    ]
  };

  const TAB_META = {
    portfolio: {
      title: "Portfolio Desk",
      subtitle: "Default path for thesis, monitoring, allocation, optimization, and practical action."
    },
    breakthrough: {
      title: "Breakthrough Studio",
      subtitle: "Conditional path for invention/design routes, preserving stages 16–22."
    },
    acquisition: {
      title: "Acquisition Room",
      subtitle: "Strategic package review for moat, acquirer fit, and final package readiness."
    },
    trust: {
      title: "Trust Gate",
      subtitle: "Verify whether the loaded mission is safe to act on."
    },
    continuity: {
      title: "Continuity Gate",
      subtitle: "Determine whether verified output can be reused in future Claire reasoning."
    },
    actions: {
      title: "Next Operator Actions",
      subtitle: "What the operator should do next based on the current mission state."
    }
  };

  let searchDocs = [];
  let latestSnapshot = {};

  function $(id) { return document.getElementById(id); }
  function normalize(value) { return String(value ?? "").replace(/\s+/g, " ").trim(); }
  function lower(value) { return normalize(value).toLowerCase(); }
  function escapeHtml(value) {
    return String(value ?? "")
      .replace(/&/g, "&amp;").replace(/</g, "&lt;")
      .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
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

  function setText(id, value) {
    const node = $(id);
    if (node) node.textContent = value ?? "";
  }

  function friendlyPath(route) {
    const r = lower(route);
    if (!r) return "Awaiting signal";
    if (r.includes("portfolio")) return "Portfolio intelligence";
    if (r.includes("breakthrough") || r.includes("design") || r.includes("autodesign") || r.includes("system")) return "Breakthrough / design";
    if (r.includes("acquisition") || r.includes("package")) return "Acquisition package";
    if (r.includes("blocked")) return "Blocked";
    if (r.includes("insufficient")) return "Insufficient data";
    return String(route).replace(/_/g, " ");
  }

  function friendlyTerminal(state) {
    const s = lower(state);
    const map = {
      "trend_thesis_ready": "Thesis ready",
      "portfolio_action_ready": "Portfolio action ready",
      "portfolio_optimization_ready": "Portfolio optimization ready",
      "discovery_ready": "Discovery ready",
      "breakthrough_classified": "Breakthrough classified",
      "advancement_path_selected": "Advancement path selected",
      "design_output_ready": "Design output ready",
      "acquisition_package_ready": "Acquisition package ready",
      "final_package_ready": "Final package ready",
      "insufficient_data": "Insufficient data",
      "blocked": "Blocked",
      "failed": "Failed",
      "max_iterations_reached": "Max iterations reached"
    };
    return map[s] || (s ? String(state).replace(/_/g, " ") : "Not ready");
  }

  function friendlyTrust(status) {
    const s = lower(status);
    if (["pass", "passed", "verified", "valid"].includes(s)) return "Verified";
    if (["fail", "failed", "invalid"].includes(s)) return "Failed";
    if (s === "blocked") return "Blocked";
    return "Unverified";
  }

  function friendlyContinuity(status) {
    const s = lower(status);
    if (["eligible", "allowed", "pass", "passed", "verified"].includes(s)) return "Ready";
    if (["blocked", "failed"].includes(s)) return "Blocked";
    return "Not ready";
  }

  function pillClass(value) {
    const v = lower(value);
    if (v.includes("verified") || v.includes("ready")) return "green";
    if (v.includes("portfolio")) return "blue";
    if (v.includes("breakthrough") || v.includes("design") || v.includes("failed")) return "red";
    if (v.includes("acquisition")) return "orange";
    if (v.includes("blocked")) return "red";
    return "amber";
  }

  function setPill(id, value) {
    const node = $(id);
    if (!node) return;
    node.textContent = value;
    node.className = `pill ${pillClass(value)}`;
  }

  function card(title, value, note, accent = "") {
    const accentClass = accent ? ` accent-${accent}` : "";
    return `
      <article class="content-card${accentClass}">
        <div class="content-title">${escapeHtml(title)}</div>
        <div class="content-value">${escapeHtml(value)}</div>
        <div class="content-note">${escapeHtml(note)}</div>
      </article>
    `;
  }

  function fullCard(title, value, note, accent = "") {
    const accentClass = accent ? ` accent-${accent}` : "";
    return `
      <article class="content-card full${accentClass}">
        <div class="content-title">${escapeHtml(title)}</div>
        <div class="content-value">${escapeHtml(value)}</div>
        <div class="content-note">${escapeHtml(note)}</div>
      </article>
    `;
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

  async function loadCockpit() {
    const runtime = await fetchFirst(PATHS.runtime);
    const validation = await fetchFirst(PATHS.validation);
    const evidence = await fetchFirst(PATHS.evidence);
    const memory = await fetchFirst(PATHS.memory);
    const feedback = await fetchFirst(PATHS.feedback);

    latestSnapshot = { runtime, validation, evidence, memory, feedback };

    const r = runtime.json || {};
    const run = section(r, "run_truth");
    const route = section(r, "route_truth");
    const terminal = section(r, "terminal_truth");
    const output = section(r, "output_truth");

    const validationJson = validation.json || {};
    const evidenceJson = evidence.json || {};
    const memoryJson = memory.json || {};
    const feedbackJson = feedback.json || {};

    const mission = first(validationJson, ["run_id"], first(run, ["run_id", "id"], first(r, ["run_id"], "No mission loaded"))) || "No mission loaded";
    const path = friendlyPath(first(validationJson, ["route_selected"], first(route, ["route_selected", "selected_route"], "")));
    const readiness = friendlyTerminal(first(validationJson, ["terminal_state"], first(terminal, ["terminal_state", "state"], "")));
    const trust = friendlyTrust(first(validationJson, ["validation_authority_status", "validation_status"], ""));
    const continuity = friendlyContinuity(first(memoryJson, ["memory_status"], ""));

    const thesis = first(output, ["thesis", "strategic_thesis", "insight", "summary"], first(r, ["thesis", "strategic_thesis", "summary"], "No thesis available"));
    const trustScore = first(validationJson, ["validation_score"], 0);
    const evidenceCount = first(evidenceJson, ["evidence_count"], first(validationJson.evidence_summary || {}, ["evidence_count"], 0));
    const unsupportedCount = first(evidenceJson, ["unsupported_count"], first(validationJson.evidence_summary || {}, ["unsupported_count"], 0));
    const memoryEligible = first(memoryJson, ["memory_eligible"], false) ? "Eligible" : "Blocked";
    const feedbackAllowed = first(feedbackJson, ["recursive_feedback_allowed"], false) ? "Allowed" : "Blocked";

    setText("side-mission", mission);
    setText("side-path", path);
    setText("side-readiness", readiness);
    setText("side-trust", trust);

    setText("proof-mission", mission);
    setText("proof-path", path);
    setText("proof-readiness", readiness);
    setText("proof-trust", trust);
    setText("proof-continuity", continuity);

    setText("brief-objective", runtime.json ? readiness : "Load or generate a mission");
    setText("brief-review", trust === "Verified" ? "Review for action" : "Verify before action");
    setText("brief-thesis", thesis);
    setText("brief-note", runtime.json ? `Mission ${mission} has been loaded honestly from local Claire output.` : "The cockpit will not invent a mission or operator recommendation.");

    setPill("brief-pill", runtime.json ? "Mission loaded" : "Awaiting mission");
    setPill("path-pill", path);

    updateRoutes(path);
    renderWorkspace({ mission, path, readiness, trust, continuity, thesis, trustScore, evidenceCount, unsupportedCount, memoryEligible, feedbackAllowed, validationJson, memoryJson, feedbackJson });
    renderDiagnostics();
  }

  function updateRoutes(path) {
    const ids = ["route-portfolio", "route-breakthrough", "route-acquisition"];
    ids.forEach((id) => $(id)?.classList.remove("selected"));

    setText("route-portfolio-state", "Default path");
    setText("route-breakthrough-state", "Not selected");
    setText("route-acquisition-state", "Not selected");

    if (path.includes("Portfolio")) {
      $("route-portfolio")?.classList.add("selected");
      setText("route-portfolio-state", "Selected");
    } else if (path.includes("Breakthrough") || path.includes("design")) {
      $("route-breakthrough")?.classList.add("selected");
      setText("route-breakthrough-state", "Selected");
    } else if (path.includes("Acquisition")) {
      $("route-acquisition")?.classList.add("selected");
      setText("route-acquisition-state", "Selected");
    }
  }

  function renderWorkspace(state) {
    const portfolio = $("portfolio-content");
    if (portfolio) {
      portfolio.innerHTML = [
        card("Current path", state.path, "Claire defaults here for actionable intelligence when full breakthrough escalation is not required.", "blue"),
        card("Readiness", state.readiness, "This is the current output state for the loaded mission.", "blue"),
        card("Operator rule", state.trust === "Verified" ? "Action may be reviewed." : "Verify before taking action.", "Portfolio outputs should be trusted only after evidence review.", "blue"),
        fullCard("Portfolio note", "Monitor, thesis update, allocation, optimization, or risk response.", "This surface is the practical default path in Claire’s governed system.", "blue")
      ].join("");
    }

    const breakthrough = $("breakthrough-content");
    if (breakthrough) {
      const active = state.path.includes("Breakthrough") || state.path.includes("design");
      breakthrough.innerHTML = [
        card("Design route", active ? state.readiness : "Not selected", "This route activates only when the signal justifies escalation.", "red"),
        card("Stages 16–22", "Preserved", "Auto invention, solution structuring, buildability, viability, manufacturability/deployability, feasibility, and design portal output stay intact.", "red"),
        card("Operator rule", active ? "Review design feasibility and trust." : "Await a qualified breakthrough signal.", "Design is conditional, not the default.", "red"),
        fullCard("Design path note", "Breakthrough / design route", "Claire should not force every run into invention. It escalates only when the route qualifies.", "red")
      ].join("");
    }

    const acquisition = $("acquisition-content");
    if (acquisition) {
      acquisition.innerHTML = [
        card("Package state", state.path.includes("Acquisition") || state.readiness.includes("Package") || state.readiness.includes("Final") ? state.readiness : "No package loaded", "Strategic package state when acquisition surfaces are active.", "orange"),
        card("Acquirer fit", state.path.includes("Acquisition") ? "Review required" : "Not evaluated", "Potential acquirer matching and rationale live here.", "orange"),
        card("Operator rule", state.trust === "Verified" ? "Review package." : "Do not treat as ready until verified.", "Acquisition outputs should remain governed.", "orange"),
        fullCard("Acquisition note", "Moat, fit, rationale, final package", "This workspace holds the strategic handoff toward acquisition intelligence.", "orange")
      ].join("");
    }

    const trust = $("trust-content");
    if (trust) {
      trust.innerHTML = [
        card("Trust state", state.trust, "Operator-facing translation of validation authority state.", "green"),
        card("Confidence", `${state.trustScore}/100`, `${state.evidenceCount} evidence item(s), ${state.unsupportedCount} unsupported item(s).`, "green"),
        card("Blocking issue", state.validationJson.blocking_failures?.[0]?.rule || "None loaded", state.validationJson.blocking_failures?.[0]?.details || "No blocking failure surfaced.", "green"),
        fullCard("Trust note", state.trust === "Verified" ? "This mission passed trust review." : "This mission is not yet trusted for operator action.", "Trust stays visible in the main cockpit instead of being buried in deep runtime surfaces.", "green")
      ].join("");
    }

    const continuity = $("continuity-content");
    if (continuity) {
      continuity.innerHTML = [
        card("Continuity", state.continuity, "Whether this mission can become future-use continuity.", "purple"),
        card("Memory eligibility", state.memoryEligible, state.memoryJson.memory_reasons?.[0] || "No verified memory reason loaded.", "purple"),
        card("Recursive feedback", state.feedbackAllowed, state.feedbackJson.feedback_reasons?.[0] || "No recursive feedback reason loaded.", "purple"),
        fullCard("Continuity note", state.continuity === "Ready" ? "This output may be reused." : "Continuity is blocked until verification and eligibility pass.", "Claire must not reuse unverified results.", "purple")
      ].join("");
    }

    const actions = $("actions-content");
    if (actions) {
      const cards = [];
      if (state.mission === "No mission loaded") {
        cards.push(card("Load a mission", "Generate or expose a completed Claire output.", "The cockpit stays honest until a mission exists.", "cyan"));
      }
      if (state.mission !== "No mission loaded" && state.trust !== "Verified") {
        cards.push(card("Verify before action", "Run trust validation.", "Do not operationalize the mission until trust passes.", "cyan"));
      }
      if (state.trust === "Verified" && state.continuity !== "Ready") {
        cards.push(card("Decide continuity", "Review whether the output should enter continuity.", "Verified output still needs eligibility for future reuse.", "cyan"));
      }
      if (state.path.includes("Acquisition")) {
        cards.push(card("Review package", "Inspect moat, fit, rationale, and package readiness.", "Acquisition route is active.", "cyan"));
      }
      if (!cards.length) {
        cards.push(card("Operator next step", "Review the current workspace and loaded mission.", "All major surfaces are consolidated into this screen.", "cyan"));
      }
      cards.push(fullCard("Cockpit rule", "One-screen operator review", "The cockpit consolidates mission, path, trust, continuity, and active workspace so core decision review does not require long scrolling.", "cyan"));
      actions.innerHTML = cards.join("");
    }
  }

  function renderDiagnostics() {
    const node = $("diagnostic-json");
    if (node) {
      node.textContent = JSON.stringify(latestSnapshot, null, 2);
    }
  }

  function setActiveTab(tabName) {
    document.querySelectorAll(".tab-button").forEach((button) => {
      button.classList.toggle("active", button.dataset.tab === tabName);
    });
    document.querySelectorAll(".nav-button").forEach((button) => {
      button.classList.toggle("active", button.dataset.tab === tabName);
    });
    document.querySelectorAll(".tab-panel").forEach((panel) => {
      panel.classList.toggle("active", panel.dataset.tabPanel === tabName);
    });

    const meta = TAB_META[tabName] || TAB_META.portfolio;
    setText("workspace-title", meta.title);
    setText("workspace-subtitle", meta.subtitle);
  }

  function addDoc(doc) {
    const key = `${doc.type}:${doc.path}:${doc.title}`;
    if (searchDocs.some((d) => `${d.type}:${d.path}:${d.title}` === key)) return;
    searchDocs.push(doc);
  }

  async function buildSearchDocs() {
    searchDocs = [];
    document.querySelectorAll(".panel, .sidebar, .topbar").forEach((node, index) => {
      const text = normalize(node.innerText || node.textContent || "");
      if (!text || text.length < 20) return;
      if (!node.id) node.id = `searchable-${index}`;
      const title = normalize(node.querySelector("h1,h2,h3,.kicker,summary")?.textContent || node.id);
      addDoc({ type: "workspace", title, path: `#${node.id}`, text, targetId: node.id });
    });

    for (const group of Object.values(PATHS)) {
      for (const path of group) {
        const json = await fetchJson(path);
        if (!json) continue;
        if (json.schema === "claire.dashboard_intelligence_index.v1" && Array.isArray(json.documents)) {
          json.documents.forEach((doc) => {
            if (doc.status && doc.status !== "indexed") return;
            addDoc({ type: "index", title: doc.title || doc.path || path, path: doc.path || path, text: doc.text || (doc.terms || []).join(" "), json: doc });
          });
        }
        addDoc({ type: "local data", title: path.split("/").pop() || path, path, text: flattenJson(json), json });
      }
    }
  }

  function search(query) {
    const parts = lower(query).split(" ").filter(Boolean);
    if (!parts.length) return [];
    return searchDocs.map((doc) => {
      const hay = `${doc.title}\n${doc.path}\n${doc.text}`.toLowerCase();
      let score = 0;
      parts.forEach((part) => {
        if (doc.title.toLowerCase().includes(part)) score += 12;
        if (doc.path.toLowerCase().includes(part)) score += 6;
        score += Math.min(hay.split(part).length - 1, 12);
      });
      return { doc, score };
    }).filter((x) => x.score > 0).sort((a, b) => b.score - a.score).slice(0, 10);
  }

  function snippet(text, query) {
    const clean = normalize(text);
    const parts = lower(query).split(" ").filter(Boolean);
    const hay = clean.toLowerCase();
    let index = -1;
    for (const part of parts) {
      index = hay.indexOf(part);
      if (index >= 0) break;
    }
    if (index < 0) return clean.slice(0, 220);
    const start = Math.max(0, index - 70);
    const end = Math.min(clean.length, index + 180);
    return `${start > 0 ? "…" : ""}${clean.slice(start, end)}${end < clean.length ? "…" : ""}`;
  }

  function setupSearch() {
    const input = $("search-input");
    const results = $("search-results");
    if (!input || !results) return;

    input.addEventListener("input", () => {
      const query = input.value.trim();
      if (!query) {
        results.classList.remove("open");
        results.innerHTML = "";
        return;
      }
      const matches = search(query);
      results.classList.add("open");
      if (!matches.length) {
        results.innerHTML = `<div class="search-result-snippet" style="padding:12px;">No local matches. Claire search only uses loaded workspace and local mission data.</div>`;
        return;
      }
      results.innerHTML = matches.map(({ doc }) => `
        <button class="search-result" type="button">
          <div class="search-result-title">${escapeHtml(doc.title)}</div>
          <div class="search-result-meta">${escapeHtml(doc.type)} · ${escapeHtml(doc.path)}</div>
          <div class="search-result-snippet">${escapeHtml(snippet(doc.text, query))}</div>
        </button>
      `).join("");

      Array.from(results.querySelectorAll(".search-result")).forEach((button, index) => {
        button.addEventListener("click", () => {
          const doc = matches[index].doc;
          results.classList.remove("open");
          if (doc.targetId) {
            const target = document.getElementById(doc.targetId);
            if (target) target.scrollIntoView({ behavior: "smooth", block: "start" });
          }
        });
      });
    });

    document.addEventListener("keydown", (event) => {
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        input.focus();
        input.select();
      }
      if ((event.ctrlKey || event.metaKey) && event.shiftKey && event.key.toLowerCase() === "d") {
        event.preventDefault();
        $("diagnostics")?.classList.toggle("open");
      }
    });

    document.addEventListener("click", (event) => {
      if (!$("claire-search")?.contains(event.target)) results.classList.remove("open");
    });
  }

  function setupMic() {
    const button = $("mic-button");
    const input = $("search-input");
    if (!button || !input) return;
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      button.disabled = true;
      button.title = "Microphone search is not supported in this browser.";
      return;
    }
    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = navigator.language || "en-US";
    recognition.onstart = () => button.classList.add("listening");
    recognition.onend = () => button.classList.remove("listening");
    recognition.onerror = () => button.classList.remove("listening");
    recognition.onresult = (event) => {
      const transcript = Array.from(event.results || []).map((r) => r[0]?.transcript || "").join(" ").trim();
      if (transcript) {
        input.value = transcript;
        input.dispatchEvent(new Event("input", { bubbles: true }));
        input.focus();
      }
    };
    button.addEventListener("click", () => {
      try { recognition.start(); } catch (_) {}
    });
  }

  function setupTabs() {
    const activate = (tabName) => setActiveTab(tabName);
    document.querySelectorAll(".tab-button, .nav-button").forEach((button) => {
      button.addEventListener("click", () => activate(button.dataset.tab));
    });
    activate("portfolio");
  }

  async function boot() {
    setupTabs();
    setupSearch();
    setupMic();
    await loadCockpit();
    await buildSearchDocs();

    $("refresh-button")?.addEventListener("click", async () => {
      const button = $("refresh-button");
      button.textContent = "Refreshing…";
      await loadCockpit();
      await buildSearchDocs();
      button.textContent = "Refresh Cockpit";
    });

    $("diagnostics-button")?.addEventListener("click", () => {
      $("diagnostics")?.classList.toggle("open");
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
