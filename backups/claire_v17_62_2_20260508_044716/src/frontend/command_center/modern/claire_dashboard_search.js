(function () {
  "use strict";

  const LOCAL_JSON_PATHS = [
    "dashboard_search_index.json",
    "dashboard_architecture_map.json",
    "lifecycle_stage_registry.json",
    "runtime_surface_registry.json",
    "route_surface_registry.json",
    "runtime_truth_contract.json",
    "runtime_truth_status.json",
    "validation_authority_status.json",
    "evidence_traceability_status.json",
    "verified_memory_status.json",
    "recursive_feedback_status.json",
    "dashboard_search_contract.json",
    "intelligence_command_contract.json",
    "../../../exports/latest/dashboard_search_index.json",
    "../../../exports/latest/dashboard_runtime_truth.json",
    "../../../exports/latest/validation_authority_report.json",
    "../../../exports/latest/evidence_traceability_index.json",
    "../../../exports/latest/verified_memory_gate_report.json",
    "../../../exports/latest/recursive_feedback_gate_report.json",
    "exports/latest/dashboard_search_index.json",
    "exports/latest/dashboard_runtime_truth.json",
    "exports/latest/validation_authority_report.json",
    "exports/latest/evidence_traceability_index.json",
    "exports/latest/verified_memory_gate_report.json",
    "exports/latest/recursive_feedback_gate_report.json"
  ];

  const state = {
    documents: [],
    selectedIndex: -1,
    lastQuery: ""
  };

  function escapeHtml(value) {
    return String(value ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function normalizeText(value) {
    return String(value ?? "").replace(/\s+/g, " ").trim();
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

  function addDocument(doc) {
    const key = `${doc.type}:${doc.path}:${doc.title}`;
    if (state.documents.some((existing) => `${existing.type}:${existing.path}:${existing.title}` === key)) return;
    state.documents.push(doc);
  }

  function collectVisibleSections() {
    const selectors = [
      "section",
      "article",
      ".portal",
      ".claire-portal",
      ".surface",
      ".claire-surface",
      ".dashboard-panel",
      ".claire-panel",
      ".stage-card",
      ".route-col",
      ".validation-node",
      ".roadmap-card",
      "#claire-validation-authority-panel",
      "#claire-verified-memory-panel"
    ];

    const nodes = Array.from(document.querySelectorAll(selectors.join(",")));
    const seen = new Set();

    nodes.forEach((node, index) => {
      if (!node || seen.has(node)) return;
      seen.add(node);

      const text = normalizeText(node.innerText || node.textContent || "");
      if (!text || text.length < 16) return;

      if (!node.id) node.id = `claire-search-section-${index + 1}`;

      const titleNode = node.querySelector("h1,h2,h3,.section-title,.claire-validation-title,.claire-memory-title");
      const title = normalizeText(
        titleNode?.innerText ||
        titleNode?.textContent ||
        node.getAttribute("aria-label") ||
        node.id ||
        `Dashboard Surface ${index + 1}`
      );

      addDocument({
        type: "visible_surface",
        title,
        path: `#${node.id}`,
        text,
        targetId: node.id
      });
    });
  }

  function ingestDashboardSearchIndex(indexJson, path) {
    const docs = Array.isArray(indexJson?.documents) ? indexJson.documents : [];
    docs.forEach((doc) => {
      if (doc.status && doc.status !== "indexed") return;
      addDocument({
        type: "dashboard_index",
        title: doc.title || doc.path || path,
        path: doc.path || path,
        text: doc.text || (Array.isArray(doc.terms) ? doc.terms.join(" ") : ""),
        json: doc
      });
    });
  }

  async function collectJsonDocuments() {
    const uniquePaths = [...new Set(LOCAL_JSON_PATHS)];
    for (const path of uniquePaths) {
      const json = await fetchJson(path);
      if (!json) continue;

      if (json.schema === "claire.dashboard_intelligence_index.v1") {
        ingestDashboardSearchIndex(json, path);
      }

      const text = flattenJson(json);
      if (!text) continue;

      addDocument({
        type: "runtime_or_contract_json",
        title: path.split("/").pop() || path,
        path,
        text,
        json
      });
    }
  }

  function scoreDocument(doc, queryParts) {
    const haystack = `${doc.title}\n${doc.path}\n${doc.text}`.toLowerCase();
    let score = 0;
    for (const part of queryParts) {
      if (!part) continue;
      if (doc.title.toLowerCase().includes(part)) score += 14;
      if (doc.path.toLowerCase().includes(part)) score += 7;
      score += Math.min(haystack.split(part).length - 1, 14);
    }
    return score;
  }

  function snippet(text, queryParts) {
    const clean = normalizeText(text);
    const lower = clean.toLowerCase();
    let index = -1;
    for (const part of queryParts) {
      index = lower.indexOf(part);
      if (index >= 0) break;
    }
    if (index < 0) return clean.slice(0, 220);
    const start = Math.max(0, index - 80);
    const end = Math.min(clean.length, index + 180);
    return `${start > 0 ? "…" : ""}${clean.slice(start, end)}${end < clean.length ? "…" : ""}`;
  }

  function search(query) {
    const parts = normalizeText(query).toLowerCase().split(" ").filter(Boolean);
    if (!parts.length) return [];
    return state.documents
      .map((doc) => ({ doc, score: scoreDocument(doc, parts), snippet: snippet(doc.text, parts) }))
      .filter((item) => item.score > 0)
      .sort((a, b) => b.score - a.score)
      .slice(0, 12);
  }

  function ensureStyles() {
    if (document.getElementById("claire-dashboard-search-style")) return;
    const style = document.createElement("style");
    style.id = "claire-dashboard-search-style";
    style.textContent = `
      .claire-dashboard-search-shell {
        position: fixed;
        top: 14px;
        right: 22px;
        z-index: 10020;
        width: min(560px, calc(100vw - 470px));
        color: #e2e8f0;
        font-family: Inter, system-ui, sans-serif;
      }
      .claire-dashboard-search-box {
        display: flex;
        align-items: center;
        gap: 10px;
        border: 1px solid rgba(0, 212, 255, 0.34);
        border-radius: 16px;
        padding: 8px 12px;
        background: rgba(5, 10, 20, 0.88);
        backdrop-filter: blur(18px);
        box-shadow: 0 0 24px rgba(0, 212, 255, 0.10);
      }
      .claire-dashboard-search-label {
        font-family: Orbitron, Inter, system-ui, sans-serif;
        color: #00d4ff;
        font-size: 9px;
        font-weight: 800;
        letter-spacing: .14em;
        text-transform: uppercase;
        white-space: nowrap;
      }
      .claire-dashboard-search-input {
        flex: 1;
        min-width: 0;
        border: 0;
        outline: 0;
        background: transparent;
        color: #f8fafc;
        font-size: 13px;
        line-height: 1.4;
      }
      .claire-dashboard-search-input::placeholder { color: #64748b; }
      .claire-dashboard-search-kbd {
        border: 1px solid rgba(148, 163, 184, 0.24);
        border-radius: 8px;
        padding: 3px 7px;
        color: #94a3b8;
        font-size: 10px;
        white-space: nowrap;
      }
      .claire-dashboard-search-results {
        display: none;
        margin-top: 8px;
        border: 1px solid rgba(0, 212, 255, 0.22);
        border-radius: 18px;
        background: rgba(3, 8, 18, 0.96);
        backdrop-filter: blur(18px);
        box-shadow: 0 22px 52px rgba(0, 0, 0, 0.34);
        max-height: min(58vh, 520px);
        overflow: auto;
        padding: 8px;
      }
      .claire-dashboard-search-results.open { display: block; }
      .claire-dashboard-search-result {
        display: block;
        width: 100%;
        text-align: left;
        border: 1px solid rgba(148, 163, 184, 0.12);
        border-radius: 14px;
        padding: 10px 12px;
        margin: 6px 0;
        background: rgba(15, 23, 42, 0.52);
        color: #e2e8f0;
        cursor: pointer;
      }
      .claire-dashboard-search-result:hover,
      .claire-dashboard-search-result.active {
        border-color: rgba(0, 212, 255, 0.45);
        background: rgba(0, 212, 255, 0.08);
      }
      .claire-dashboard-search-result-title {
        color: #f8fafc;
        font-weight: 800;
        font-size: 12px;
        line-height: 1.4;
        overflow-wrap: anywhere;
      }
      .claire-dashboard-search-result-meta {
        margin-top: 2px;
        color: #7dd3fc;
        font-size: 10px;
        letter-spacing: .06em;
        text-transform: uppercase;
        overflow-wrap: anywhere;
      }
      .claire-dashboard-search-result-snippet {
        margin-top: 6px;
        color: #94a3b8;
        font-size: 12px;
        line-height: 1.5;
        overflow-wrap: anywhere;
      }
      .claire-dashboard-search-empty {
        padding: 12px;
        color: #94a3b8;
        font-size: 12px;
        line-height: 1.5;
      }
      .claire-search-highlight {
        outline: 2px solid rgba(0, 212, 255, 0.75) !important;
        box-shadow: 0 0 24px rgba(0, 212, 255, 0.22) !important;
      }
      @media (max-width: 920px) {
        .claire-dashboard-search-shell {
          position: sticky;
          top: 8px;
          right: auto;
          left: auto;
          width: calc(100% - 20px);
          margin: 8px auto 12px auto;
        }
        .claire-dashboard-search-label,
        .claire-dashboard-search-kbd {
          display: none;
        }
      }
    `;
    document.head.appendChild(style);
  }

  function renderShell() {
    if (document.getElementById("claire-dashboard-search-shell")) return;
    ensureStyles();

    const shell = document.createElement("div");
    shell.id = "claire-dashboard-search-shell";
    shell.className = "claire-dashboard-search-shell";
    shell.innerHTML = `
      <div class="claire-dashboard-search-box">
        <div class="claire-dashboard-search-label">Claire Search</div>
        <input id="claire-dashboard-search-input" class="claire-dashboard-search-input" autocomplete="off" spellcheck="false" placeholder="Search runtime, route, validation, memory…" aria-label="Claire dashboard search" />
        <div class="claire-dashboard-search-kbd">Ctrl K</div>
      </div>
      <div id="claire-dashboard-search-results" class="claire-dashboard-search-results" role="listbox"></div>
    `;
    document.body.appendChild(shell);
    document.body.classList.add("claire-search-mounted");

    const input = document.getElementById("claire-dashboard-search-input");
    const results = document.getElementById("claire-dashboard-search-results");

    input.addEventListener("input", () => {
      state.lastQuery = input.value;
      state.selectedIndex = -1;
      const query = input.value.trim();
      if (!query) {
        results.classList.remove("open");
        results.innerHTML = "";
        return;
      }
      renderResults(search(query));
    });

    input.addEventListener("focus", () => {
      if (input.value.trim()) renderResults(search(input.value));
    });

    input.addEventListener("keydown", (event) => {
      const buttons = Array.from(results.querySelectorAll(".claire-dashboard-search-result"));
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
  }

  function markActive(buttons) {
    buttons.forEach((button, index) => {
      button.classList.toggle("active", index === state.selectedIndex);
      if (index === state.selectedIndex) button.scrollIntoView({ block: "nearest" });
    });
  }

  function renderResults(items) {
    const results = document.getElementById("claire-dashboard-search-results");
    if (!results) return;
    results.classList.add("open");

    if (!items.length) {
      results.innerHTML = `
        <div class="claire-dashboard-search-empty">
          No local matches. Generate runtime truth, validation, memory, and search index reports if this data should exist.
        </div>
      `;
      return;
    }

    results.innerHTML = items.map((item, index) => `
      <button class="claire-dashboard-search-result" data-index="${index}" type="button">
        <div class="claire-dashboard-search-result-title">${escapeHtml(item.doc.title)}</div>
        <div class="claire-dashboard-search-result-meta">${escapeHtml(item.doc.type)} · ${escapeHtml(item.doc.path)}</div>
        <div class="claire-dashboard-search-result-snippet">${escapeHtml(item.snippet)}</div>
      </button>
    `).join("");

    Array.from(results.querySelectorAll(".claire-dashboard-search-result")).forEach((button, index) => {
      button.addEventListener("click", () => openResult(items[index].doc));
    });
  }

  function openResult(doc) {
    const results = document.getElementById("claire-dashboard-search-results");
    if (results) results.classList.remove("open");

    if (doc.targetId) {
      const node = document.getElementById(doc.targetId);
      if (node) {
        document.querySelectorAll(".claire-search-highlight").forEach((el) => el.classList.remove("claire-search-highlight"));
        node.classList.add("claire-search-highlight");
        node.scrollIntoView({ behavior: "smooth", block: "start" });
        window.setTimeout(() => node.classList.remove("claire-search-highlight"), 2600);
      }
      return;
    }

    const panel = ensureJsonResultPanel();
    panel.innerHTML = `
      <div class="claire-dashboard-search-result-title">Local truth file: ${escapeHtml(doc.title)}</div>
      <div class="claire-dashboard-search-result-meta">${escapeHtml(doc.path)}</div>
      <pre style="margin-top:10px; white-space:pre-wrap; overflow-wrap:anywhere; max-height:52vh; overflow:auto;">${escapeHtml(JSON.stringify(doc.json ?? doc.text, null, 2))}</pre>
    `;
    panel.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function ensureJsonResultPanel() {
    let panel = document.getElementById("claire-search-json-result-panel");
    if (!panel) {
      panel = document.createElement("section");
      panel.id = "claire-search-json-result-panel";
      panel.className = "claire-dashboard-search-results open";
      panel.style.display = "block";
      panel.style.position = "relative";
      panel.style.margin = "18px auto";
      panel.style.width = "min(100%, 1180px)";
      panel.style.transform = "none";
      const mount = document.querySelector("main") || document.getElementById("app") || document.body;
      mount.appendChild(panel);
    }
    return panel;
  }

  function installFocusToggle() {
    if (document.getElementById("claire-view-mode-toggle")) return;
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
    renderShell();
    installFocusToggle();

    window.setTimeout(async () => {
      state.documents = [];
      collectVisibleSections();
      await collectJsonDocuments();
    }, 500);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
