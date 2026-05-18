(function () {
  "use strict";
  const PANEL_ID = "governed-evidence-basket-panel";

  function text(value, fallback) {
    if (value === null || value === undefined || value === "") return fallback || "unknown";
    return String(value);
  }

  function computeBasket(payload) {
    const items = [];
    const timeline = payload && payload.governed_runtime_timeline ? payload.governed_runtime_timeline : {};
    const eventStream = payload && payload.event_stream ? payload.event_stream : {};

    if (Array.isArray(eventStream.events)) {
      eventStream.events.slice(-8).forEach((event, index) => {
        items.push({
          id: event.id || "event:" + index,
          kind: "runtime_event",
          title: event.type || "Runtime Event",
          status: event.status || "observed",
          trust_state: "runtime_observed",
          promotion_state: "review_required"
        });
      });
    }

    if (Array.isArray(timeline.events)) {
      timeline.events.slice(-8).forEach((event, index) => {
        items.push({
          id: event.id || "timeline:" + index,
          kind: "timeline_event",
          title: event.classification || event.type || "Timeline Event",
          status: event.severity || "info",
          trust_state: "timeline_observed",
          promotion_state: "review_required"
        });
      });
    }

    return {
      version: "v19.89.8-S22",
      status: "active",
      authority: {
        backend_owns_truth: true,
        cockpit_presentation_only: true,
        runtime_authority: "blocked",
        evidence_promotion: "manual_review_required",
        autonomous_execution_expansion: false
      },
      summary: {
        evidence_total: items.length,
        promotion_ready: false,
        manual_review_required: true,
        automatic_truth_mutation: false
      },
      items: items.slice(-24)
    };
  }

  function ensurePanel() {
    let panel = document.getElementById(PANEL_ID);
    if (panel) return panel;
    panel = document.createElement("section");
    panel.id = PANEL_ID;
    panel.className = "claire-card governed-evidence-basket-card";
    panel.innerHTML = `
      <div class="governed-evidence-basket-header">
        <div>
          <div class="governed-evidence-basket-kicker">Governed Evidence Basket</div>
          <h2>Evidence Review</h2>
        </div>
        <div class="governed-evidence-basket-badge">manual review required</div>
      </div>
      <div id="governed-evidence-basket-summary" class="governed-evidence-basket-summary">Waiting for canonical payload.</div>
      <div id="governed-evidence-basket-list" class="governed-evidence-basket-list"></div>
    `;
    const targets = ["#runtime-surface", "#operator-surface", "#main-content", "main", "#app", "body"];
    for (const selector of targets) {
      const target = document.querySelector(selector);
      if (target) {
        target.appendChild(panel);
        return panel;
      }
    }
    document.body.appendChild(panel);
    return panel;
  }

  function render(payload) {
    const panel = ensurePanel();
    const summaryEl = panel.querySelector("#governed-evidence-basket-summary");
    const listEl = panel.querySelector("#governed-evidence-basket-list");
    const basket = payload && payload.governed_evidence_basket ? payload.governed_evidence_basket : computeBasket(payload || {});
    const summary = basket.summary || {};
    const items = Array.isArray(basket.items) ? basket.items.slice(-12).reverse() : [];

    summaryEl.innerHTML = `
      <span><strong>Evidence:</strong> ${text(summary.evidence_total, "0")}</span>
      <span><strong>Promotion:</strong> manual review required</span>
      <span><strong>Runtime mutation:</strong> blocked</span>
      <span><strong>Authority:</strong> blocked</span>
    `;

    if (!items.length) {
      listEl.innerHTML = `<div class="governed-evidence-empty">No evidence items observed yet.</div>`;
      return;
    }

    listEl.innerHTML = items.map((item) => `
      <div class="governed-evidence-item">
        <div class="governed-evidence-kind">${text(item.kind, "evidence")}</div>
        <div class="governed-evidence-main">
          <strong>${text(item.title, "Evidence Item")}</strong>
          <span>${text(item.trust_state, "unclassified")} / ${text(item.promotion_state, "review_required")}</span>
        </div>
        <div class="governed-evidence-status">${text(item.status, "observed")}</div>
      </div>
    `).join("");
  }

  function poll() {
    fetch("/dashboard/payload", { cache: "no-store" })
      .then((response) => response.ok ? response.json() : null)
      .then((payload) => { if (payload) render(payload); })
      .catch(() => ensurePanel());
  }

  document.addEventListener("DOMContentLoaded", function () {
    ensurePanel();
    window.addEventListener("claire:canonical-payload", function (event) { render(event.detail || {}); });
    window.addEventListener("claire:payload", function (event) { render(event.detail || {}); });
    poll();
    setInterval(poll, 10000);
  });

  window.ClaireGovernedEvidenceBasket = {
    version: "v19.89.8-S22",
    render,
    authority: "presentation_only_runtime_authority_blocked"
  };
})();
