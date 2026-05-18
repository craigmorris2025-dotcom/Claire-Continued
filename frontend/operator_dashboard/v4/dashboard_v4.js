"use strict";

(function () {
  const state = {
    payload: null,
    selectedDomain: "system"
  };

  const labels = {
    system: "System",
    governance: "Governance",
    lifecycle: "Lifecycle",
    signal_governance: "Signals",
    trend_discovery: "Trends",
    thesis: "Thesis",
    portfolio: "Portfolio",
    breakthrough: "Breakthrough",
    acquisition: "Acquisition",
    evidence: "Evidence",
    runtime: "Runtime",
    exports: "Exports",
    future_payloads: "Future Payloads"
  };

  function asText(value) {
    if (Array.isArray(value)) return value.join(" -> ");
    if (value && typeof value === "object") return JSON.stringify(value);
    if (value === true) return "true";
    if (value === false) return "false";
    if (value === null || typeof value === "undefined") return "";
    return String(value);
  }

  function el(tag, attrs, text) {
    const node = document.createElement(tag);
    Object.entries(attrs || {}).forEach(([key, value]) => {
      if (key === "className") node.className = value;
      else node.setAttribute(key, value);
    });
    if (typeof text !== "undefined") node.textContent = text;
    return node;
  }

  function renderNav(payload) {
    const nav = document.getElementById("domain-nav");
    nav.replaceChildren();
    payload.domain_order.forEach((key) => {
      const domain = payload.domains[key] || {};
      const button = el("button", {
        type: "button",
        "aria-current": key === state.selectedDomain ? "true" : "false"
      });
      button.innerHTML = `<strong>${labels[key] || key}</strong><br><small>${domain.status || "unknown"}</small>`;
      button.addEventListener("click", () => {
        state.selectedDomain = key;
        render();
      });
      nav.appendChild(button);
    });
  }

  function renderMetrics(payload) {
    const grid = document.getElementById("status-grid");
    grid.replaceChildren();
    const metrics = [
      ["Backend", payload.scores.backend_startup_routes],
      ["Lifecycle", payload.scores.lifecycle_contract],
      ["Payload compatibility", payload.scores.future_payload_compatibility],
      ["Dashboard", payload.scores.dashboard_functionality]
    ];
    metrics.forEach(([label, value]) => {
      const card = el("article", { className: "metric" });
      card.innerHTML = `<span class="eyebrow">${label}</span><strong>${value}%</strong>`;
      grid.appendChild(card);
    });
  }

  function renderSignals(containerId, signals) {
    const target = document.getElementById(containerId);
    target.replaceChildren();
    Object.entries(signals || {}).forEach(([key, value]) => {
      const row = el("div");
      row.appendChild(el("dt", {}, key.replaceAll("_", " ")));
      row.appendChild(el("dd", {}, asText(value)));
      target.appendChild(row);
    });
  }

  function renderSelectedDomain(payload) {
    const domain = payload.domains[state.selectedDomain] || payload.domains.system;
    document.getElementById("domain-title").textContent = labels[state.selectedDomain] || state.selectedDomain;
    document.getElementById("domain-headline").textContent = domain.headline || "";
    renderSignals("domain-signals", domain.signals || {});
  }

  function renderPath(payload) {
    const list = document.getElementById("default-path");
    list.replaceChildren();
    const path = payload.domains.signal_governance.signals.default_path || [];
    path.forEach((item) => list.appendChild(el("li", {}, item.replaceAll("_", " "))));
  }

  function renderLocks(payload) {
    renderSignals("authority-locks", payload.domains.governance.signals || {});
  }

  function render() {
    const payload = state.payload;
    if (!payload) return;
    document.getElementById("completion-score").textContent = `${payload.completion_percent}%`;
    document.getElementById("completion-label").textContent = payload.status;
    renderNav(payload);
    renderMetrics(payload);
    renderSelectedDomain(payload);
    renderPath(payload);
    renderLocks(payload);
    document.getElementById("payload-preview").textContent = JSON.stringify({
      schema_version: payload.schema_version,
      completion_percent: payload.completion_percent,
      scores: payload.scores,
      operator_next_actions: payload.operator_next_actions
    }, null, 2);
  }

  async function boot() {
    const response = await fetch("/api/dashboard/v4/payload", {
      method: "GET",
      headers: { "Accept": "application/json" },
      cache: "no-store"
    });
    state.payload = await response.json();
    render();
  }

  window.ClaireDashboardV4 = { boot, state };
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
