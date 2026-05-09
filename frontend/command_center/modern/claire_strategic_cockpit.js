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
    } catch (_) { return null; }
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
      "acquisition_ready": "Acquisition ready",
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
    if (["blocked"].includes(s)) return "Blocked";
    return "Unverified";
  }

  function friendlyMemory(status) {
    const s = lower(status);
    if (["eligible", "allowed", "pass", "passed"].includes(s)) return "Ready";
    if (["blocked", "failed"].includes(s)) return "Blocked";
    return "Not ready";
  }

  function statusClass(status) {
    const s = lower(status);
    if (["verified", "ready", "eligible", "allowed", "loaded", "portfolio action ready", "acquisition package ready", "final package ready"].includes(s)) return "green";
    if (["failed", "blocked"].includes(s)) return "red";
    if (["unverified", "not ready", "awaiting mission", "awaiting signal", "no mission loaded", "not selected"].includes(s)) return "amber";
    if (s.includes("portfolio")) return "blue";
    if (s.includes("breakthrough") || s.includes("design")) return "red";
    if (s.includes("acquisition")) return "orange";
    return "cyan";
  }

  function applyPill(id, value) {
    const node = $(id);
    if (!node) return;
    node.textContent = value;
    node.className = `status-pill ${statusClass(value)}`;
  }

  function card(title, text) {
    return `<div class="operator-card"><div class="operator-card-title">${escapeHtml(title)}</div><div class="operator-card-text">${escapeHtml(text)}</div></div>`;
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
    const stage = section(r, "stage_truth");
    const output = section(r, "output_truth");
    const validationJson = validation.json || {};
    const evidenceJson = evidence.json || {};
    const memoryJson = memory.json || {};
    const feedbackJson = feedback.json || {};

    const rawRunId = first(validationJson, ["run_id"], first(run, ["run_id", "id"], first(r, ["run_id"], "")));
    const rawRoute = first(validationJson, ["route_selected"], first(route, ["route_selected", "selected_route"], first(run, ["selected_route"], "")));
    const rawTerminal = first(validationJson, ["terminal_state"], first(terminal, ["terminal_state", "state"], first(run, ["terminal_state"], "")));
    const rawTrust = first(validationJson, ["validation_authority_status", "validation_status"], "");
    const rawMemory = first(memoryJson, ["memory_status"], "");

    const mission = rawRunId || "No mission loaded";
    const path = friendlyPath(rawRoute);
    const readiness = friendlyTerminal(rawTerminal);
    const trust = friendlyTrust(rawTrust);
    const continuity = friendlyMemory(rawMemory);

    const stages = first(stage, ["stages_total", "total_stages"], Array.isArray(stage.stages) ? String(stage.stages.length) : "Not loaded");
    const trustScore = first(validationJson, ["validation_score"], 0);
    const evidenceCount = first(evidenceJson, ["evidence_count"], first(validationJson.evidence_summary || {}, ["evidence_count"], 0));
    const unsupportedCount = first(evidenceJson, ["unsupported_count"], first(validationJson.evidence_summary || {}, ["unsupported_count"], 0));
    const memoryEligible = first(memoryJson, ["memory_eligible"], false) ? "Eligible" : "Blocked";
    const feedbackAllowed = first(feedbackJson, ["recursive_feedback_allowed"], false) ? "Allowed" : "Blocked";

    const thesis = first(output, ["thesis", "strategic_thesis", "insight", "summary"], first(r, ["thesis", "strategic_thesis", "summary"], "No thesis available"));
    const signalState = runtime.json ? "Signal data loaded" : "Awaiting signal";
    const review = trust === "Verified" ? "Review package for action" : "Verify before action";

    setText("side-mission", mission);
    setText("side-path", path);
    setText("side-readiness", readiness);
    setText("side-trust", trust);

    setText("mission-title", runtime.json ? "Mission loaded" : "No active mission loaded");
    setText("mission-summary", runtime.json ? `Claire has loaded mission ${mission}. Review the path, trust gate, and strategic package before acting.` : "Claire is ready, but no completed mission output has been loaded into the cockpit yet.");

    setText("brief-objective", runtime.json ? readiness : "Load or generate a Claire mission");
    setText("brief-objective-note", runtime.json ? `Mission: ${mission}` : "The cockpit will not invent an opportunity without a run output.");
    setText("brief-thesis", thesis);
    setText("brief-signal", signalState);
    setText("brief-review", review);

    setText("acq-package", path.includes("Acquisition") || readiness.includes("Acquisition") || readiness.includes("Final") ? readiness : "No package loaded");
    setText("acq-fit", path.includes("Acquisition") ? "Review required" : "Not evaluated");
    setText("acq-rationale", path.includes("Acquisition") ? "Loaded from acquisition path when available" : "Not available");

    setText("trust-score", `${trustScore}/100`);
    setText("trust-evidence", `${evidenceCount} item(s)`);
    setText("trust-message", validationJson.blocking_failures?.[0]?.details || validationJson.message || (trust === "Verified" ? "Output passed verification." : "No verified mission output loaded."));

    setText("continuity-state", continuity);
    setText("future-use", feedbackAllowed);
    setText("continuity-reason", memoryJson.memory_reasons?.[0] || feedbackJson.feedback_reasons?.[0] || "Claire needs verified output before continuity can be enabled.");

    setText("proof-mission", mission);
    setText("proof-path", path);
    setText("proof-readiness", readiness);
    setText("proof-trust", trust);
    setText("proof-continuity", continuity);

    applyPill("brief-pill", runtime.json ? "Mission loaded" : "Awaiting mission");
    applyPill("path-pill", path);
    applyPill("acquisition-pill", path.includes("Acquisition") || readiness.includes("Acquisition") || readiness.includes("Final") ? "Package review" : "Not ready");
    applyPill("trust-pill", trust);
    applyPill("continuity-pill", continuity);

    updateRoutes(path);
    renderOperatorLists({ runtime, validation, memory, feedback, mission, path, readiness, trust, continuity, stages, evidenceCount, unsupportedCount, memoryEligible, feedbackAllowed });
    renderDiagnostics();
  }

  function updateRoutes(path) {
    const cards = ["route-portfolio", "route-breakthrough", "route-acquisition"];
    cards.forEach((id) => $(id)?.classList.remove("selected"));

    setText("route-portfolio-state", "Available");
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
    } else {
      setText("route-portfolio-state", "Default when signal qualifies");
    }
  }

  function renderOperatorLists(state) {
    const portfolio = $("portfolio-content");
    if (portfolio) {
      portfolio.innerHTML = [
        card("Portfolio recommendation", state.path.includes("Portfolio") ? state.readiness : "No portfolio action loaded yet."),
        card("Evidence basis", `${state.evidenceCount} evidence item(s), ${state.unsupportedCount} unsupported item(s).`),
        card("Operator rule", "Do not act on a portfolio recommendation until trust is verified.")
      ].join("");
    }

    const breakthrough = $("breakthrough-content");
    if (breakthrough) {
      const active = state.path.includes("Breakthrough") || state.path.includes("design");
      breakthrough.innerHTML = [
        card("Design route", active ? state.readiness : "No breakthrough/design path selected."),
        card("Stages 16–22", "Auto invention, solution structuring, buildability, viability, manufacturability, feasibility, and design portal output remain preserved for design paths."),
        card("Operator rule", "Design outputs require feasibility and trust review before packaging.")
      ].join("");
    }

    const actions = $("action-list");
    if (actions) {
      const items = [];
      if (!state.runtime.json) items.push(card("Load a mission", "Generate or expose a completed Claire output so the cockpit can display a real opportunity."));
      if (state.runtime.json && state.trust !== "Verified") items.push(card("Verify before action", "The current mission is loaded but not yet trusted. Run verification before treating it as operator-ready."));
      if (state.trust === "Verified" && state.continuity !== "Ready") items.push(card("Decide continuity", "The output is verified. Check whether it should become continuity for future Claire reasoning."));
      if (state.path.includes("Acquisition")) items.push(card("Review acquisition package", "Inspect moat, acquirer fit, strategic rationale, and final package readiness."));
      if (!items.length) items.push(card("Review final package", "The cockpit has loaded the available mission, path, trust, and continuity state."));
      actions.innerHTML = items.join("");
    }
  }

  function renderDiagnostics() {
    const node = $("diagnostic-json");
    if (node) node.textContent = JSON.stringify(latestSnapshot, null, 2);
  }

  function addDoc(doc) {
    const key = `${doc.type}:${doc.path}:${doc.title}`;
    if (searchDocs.some((d) => `${d.type}:${d.path}:${d.title}` === key)) return;
    searchDocs.push(doc);
  }

  async function buildSearchDocs() {
    searchDocs = [];
    document.querySelectorAll("section, aside, header, footer, details").forEach((node, index) => {
      const text = normalize(node.innerText || node.textContent || "");
      if (!text || text.length < 18) return;
      if (!node.id) node.id = `cockpit-search-section-${index}`;
      const title = normalize(node.querySelector("h1,h2,h3,.panel-kicker,summary")?.textContent || node.id);
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
      parts.forEach((p) => {
        if (doc.title.toLowerCase().includes(p)) score += 12;
        if (doc.path.toLowerCase().includes(p)) score += 6;
        score += Math.min(hay.split(p).length - 1, 12);
      });
      return { doc, score };
    }).filter((x) => x.score > 0).sort((a, b) => b.score - a.score).slice(0, 10);
  }

  function snippet(text, query) {
    const clean = normalize(text);
    const parts = lower(query).split(" ").filter(Boolean);
    const hay = clean.toLowerCase();
    let idx = -1;
    for (const p of parts) {
      idx = hay.indexOf(p);
      if (idx >= 0) break;
    }
    if (idx < 0) return clean.slice(0, 220);
    const start = Math.max(0, idx - 80);
    const end = Math.min(clean.length, idx + 180);
    return `${start > 0 ? "…" : ""}${clean.slice(start, end)}${end < clean.length ? "…" : ""}`;
  }

  function setupSearch() {
    const input = $("claire-search-input");
    const results = $("claire-search-results");
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
        results.innerHTML = `<div class="search-result-snippet" style="padding:12px;">No local matches. Claire is searching only loaded workspace and local mission data.</div>`;
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
        $("developer-diagnostics")?.classList.toggle("open");
      }
    });

    document.addEventListener("click", (event) => {
      if (!$("claire-search")?.contains(event.target)) results.classList.remove("open");
    });
  }

  function setupMic() {
    const button = $("claire-mic-button");
    const input = $("claire-search-input");
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

  function setupNav() {
    const links = document.querySelectorAll(".nav-item");
    links.forEach((link) => {
      link.addEventListener("click", () => {
        links.forEach((other) => other.classList.remove("active"));
        link.classList.add("active");
      });
    });
  }

  async function boot() {
    setupSearch();
    setupMic();
    setupNav();
    await loadCockpit();
    await buildSearchDocs();

    $("refresh-state")?.addEventListener("click", async () => {
      const button = $("refresh-state");
      button.textContent = "Refreshing…";
      await loadCockpit();
      await buildSearchDocs();
      button.textContent = "Refresh Cockpit";
    });

    $("diagnostics-toggle")?.addEventListener("click", () => {
      $("developer-diagnostics")?.classList.toggle("open");
      $("developer-diagnostics")?.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
