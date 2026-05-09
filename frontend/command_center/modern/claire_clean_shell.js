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
  let latestTruth = {};

  function $(id) { return document.getElementById(id); }

  function normalize(value) {
    return String(value ?? "").replace(/\s+/g, " ").trim();
  }

  function lower(value) { return normalize(value).toLowerCase(); }

  function escapeHtml(value) {
    return String(value ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
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

  function setText(id, value) {
    const node = $(id);
    if (node) node.textContent = value ?? "";
  }

  function statusClass(status) {
    const s = lower(status).replace(/\s+/g, "_");
    if (["pass", "passed", "eligible", "allowed", "loaded", "valid"].includes(s)) return "green";
    if (["fail", "failed", "blocked", "invalid"].includes(s)) return "red";
    if (["not_generated", "not_loaded", "missing", "unverified", "warning"].includes(s)) return "amber";
    return "cyan";
  }

  function applyPill(id, value) {
    const node = $(id);
    if (!node) return;
    node.textContent = value;
    node.className = `status-pill ${statusClass(value)}`;
  }

  function feed(title, text, version = "") {
    const now = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
    return `
      <div class="feed-card">
        <div class="feed-title">${escapeHtml(title)}</div>
        <div class="feed-text">${escapeHtml(text)}</div>
        ${version ? `<div class="feed-time">${escapeHtml(version)}</div>` : ""}
        <div class="feed-time">${escapeHtml(now)}</div>
      </div>
    `;
  }

  async function loadTruth() {
    const runtime = await fetchFirst(PATHS.runtime);
    const validation = await fetchFirst(PATHS.validation);
    const evidence = await fetchFirst(PATHS.evidence);
    const memory = await fetchFirst(PATHS.memory);
    const feedback = await fetchFirst(PATHS.feedback);

    latestTruth = { runtime, validation, evidence, memory, feedback };

    const r = runtime.json || {};
    const run = section(r, "run_truth");
    const route = section(r, "route_truth");
    const terminal = section(r, "terminal_truth");
    const stage = section(r, "stage_truth");
    const validationJson = validation.json || {};
    const evidenceJson = evidence.json || {};
    const memoryJson = memory.json || {};
    const feedbackJson = feedback.json || {};

    const runId = first(validationJson, ["run_id"], first(run, ["run_id", "id"], first(r, ["run_id"], "not_loaded")));
    const selectedRoute = first(validationJson, ["route_selected"], first(route, ["route_selected", "selected_route"], first(run, ["selected_route"], "not_loaded")));
    const terminalState = first(validationJson, ["terminal_state"], first(terminal, ["terminal_state", "state"], first(run, ["terminal_state"], "missing")));
    const stages = first(stage, ["stages_total", "total_stages"], Array.isArray(stage.stages) ? String(stage.stages.length) : "not_loaded");
    const validationStatus = first(validationJson, ["validation_authority_status", "validation_status"], validation.path ? "not_generated" : "not_generated");
    const validationScore = first(validationJson, ["validation_score"], 0);
    const checks = `${first(validationJson, ["checks_passed"], 0)} pass / ${first(validationJson, ["checks_warning"], 0)} warn / ${first(validationJson, ["checks_failed"], 0)} fail`;
    const evidenceCount = first(evidenceJson, ["evidence_count"], first(validationJson.evidence_summary || {}, ["evidence_count"], 0));
    const unsupportedCount = first(evidenceJson, ["unsupported_count"], first(validationJson.evidence_summary || {}, ["unsupported_count"], 0));
    const memoryStatus = first(memoryJson, ["memory_status"], "not_generated");
    const memoryEligible = first(memoryJson, ["memory_eligible"], false) ? "eligible" : "blocked";
    const feedbackStatus = first(feedbackJson, ["feedback_status"], "not_generated");
    const feedbackAllowed = first(feedbackJson, ["recursive_feedback_allowed"], false) ? "allowed" : "blocked";

    setText("sidebar-route", selectedRoute);
    setText("sidebar-validation", validationStatus);
    setText("metric-run", runId);
    setText("metric-route", selectedRoute);
    setText("metric-terminal", terminalState);
    setText("metric-validation", validationStatus);

    setText("stack-run", runId);
    setText("stack-route", selectedRoute);
    setText("stack-terminal", terminalState);
    setText("stack-stages", stages);
    setText("stack-evidence", `${evidenceCount} item(s)`);
    setText("stack-unsupported", unsupportedCount);

    setText("validation-score", `${validationScore}/100`);
    setText("validation-checks", checks);
    setText("validation-message", validationJson.blocking_failures?.[0]?.details || validationJson.message || "Run validation after runtime truth exists.");

    setText("memory-status", memoryStatus);
    setText("memory-eligible", memoryEligible);
    setText("feedback-status", feedbackStatus);
    setText("feedback-allowed", feedbackAllowed);
    setText("memory-reason", memoryJson.memory_reasons?.[0] || feedbackJson.feedback_reasons?.[0] || "Run verified memory command after validation.");

    setText("proof-run", runId);
    setText("proof-route", selectedRoute);
    setText("proof-terminal", terminalState);
    setText("proof-stages", stages);
    setText("proof-validation", validationStatus);
    setText("proof-memory", memoryStatus);

    applyPill("runtime-pill", validationStatus);
    applyPill("validation-pill", validationStatus);
    applyPill("memory-pill", memoryStatus);

    const live = $("live-feed");
    if (live) {
      const items = [];
      if (!runtime.json) {
        items.push(feed("No runtime truth loaded", "Dashboard remains honest: no fake run output is displayed. Run the runtime truth builder after Claire creates output.", "v17.62.6"));
      } else {
        items.push(feed("Runtime truth loaded", `Run ${runId}; route ${selectedRoute}; terminal ${terminalState}.`, "runtime"));
      }
      if (!validation.json || validationStatus === "not_generated") {
        items.push(feed("Validation not generated", "Run tools/claire_validate_runtime_truth.py after runtime truth exists.", "validation"));
      }
      if (!memory.json || memoryStatus === "not_generated") {
        items.push(feed("Memory gate not generated", "Run tools/claire_build_verified_memory.py after validation authority reports exist.", "memory"));
      }
      items.push(feed("Dashboard clean shell active", "Old conflicting dashboard injections were removed. This shell reads local truth files only.", "v17.62.6"));
      live.innerHTML = items.join("");
    }
  }

  function addDoc(doc) {
    const key = `${doc.type}:${doc.path}:${doc.title}`;
    if (searchDocs.some((d) => `${d.type}:${d.path}:${d.title}` === key)) return;
    searchDocs.push(doc);
  }

  async function buildSearchDocs() {
    searchDocs = [];
    document.querySelectorAll("section, aside, header, footer").forEach((node, index) => {
      const text = normalize(node.innerText || node.textContent || "");
      if (!text || text.length < 18) return;
      if (!node.id) node.id = `search-section-${index}`;
      const title = normalize(node.querySelector("h1,h2,h3,.panel-kicker")?.textContent || node.id);
      addDoc({ type: "visible", title, path: `#${node.id}`, text, targetId: node.id });
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
        addDoc({ type: "json", title: path.split("/").pop() || path, path, text: flattenJson(json), json });
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
      if (!matches.length) {
        results.classList.add("open");
        results.innerHTML = `<div class="search-result-snippet" style="padding:12px;">No local matches. Generate runtime truth, validation, memory, and index reports if this should exist.</div>`;
        return;
      }
      results.classList.add("open");
      results.innerHTML = matches.map(({ doc }) => `
        <button class="search-result" type="button" data-path="${escapeHtml(doc.path)}">
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

  async function boot() {
    setupSearch();
    setupMic();
    await loadTruth();
    await buildSearchDocs();

    const refresh = $("refresh-runtime");
    if (refresh) {
      refresh.addEventListener("click", async () => {
        refresh.textContent = "Refreshing…";
        await loadTruth();
        await buildSearchDocs();
        refresh.textContent = "Refresh Runtime Truth";
      });
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
