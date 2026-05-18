(() => {
  const state = {
    payloadEndpoint: "/api/cockpit/web-search/payload",
    actionsEndpoint: "/api/cockpit/web-search/actions",
    cardsEndpoint: "/api/cockpit/web-search/cards"
  };

  function el(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function ensurePanel() {
    let panel = document.getElementById("claire-governed-web-search-body-read-planning");
    if (panel) return panel;
    const host = document.querySelector("main") || document.body;
    panel = el("section", "claire-card claire-governed-web-search-body-read-planning");
    panel.id = "claire-governed-web-search-body-read-planning";
    panel.innerHTML = `
      <div class="claire-source-panel-header">
        <div>
          <div class="claire-eyebrow">S737-S778</div>
          <h2>Controlled Metadata Proof + Body-Read Planning</h2>
          <p>Metadata proof and body-read governance planning remain cockpit-visible but non-executable.</p>
        </div>
        <span class="claire-pill claire-pill-blocked">Body reads blocked</span>
      </div>
      <div class="claire-source-panel-summary" data-role="summary">Loading governed web search planning payload...</div>
      <div class="claire-source-card-grid" data-role="cards"></div>
      <div class="claire-source-action-grid" data-role="actions"></div>
    `;
    host.appendChild(panel);
    return panel;
  }

  function renderSummary(panel, payload) {
    const summary = panel.querySelector('[data-role="summary"]');
    if (!summary) return;
    const data = payload.summary || {};
    summary.textContent = `terminal=${payload.terminal_state || "unknown"} | cards=${data.cards_total || 0} | actions=${data.actions_total || 0} | body_reads=${data.body_reads || 0} | network=${data.network_requests || 0}`;
  }

  function renderCards(panel, cards) {
    const target = panel.querySelector('[data-role="cards"]');
    if (!target) return;
    target.innerHTML = "";
    (cards || []).slice(0, 8).forEach((card) => {
      const node = el("article", "claire-source-card");
      const title = el("h3", "", card.title || card.card_id || "Governed card");
      const state = el("div", "claire-muted", card.state || card.subtitle || "represented");
      const summary = el("p", "", card.summary || "No summary supplied.");
      const badges = el("div", "claire-badge-row");
      (card.badges || []).slice(0, 4).forEach((badge) => badges.appendChild(el("span", "claire-pill", badge)));
      node.append(title, state, summary, badges);
      target.appendChild(node);
    });
  }

  function renderActions(panel, actions) {
    const target = panel.querySelector('[data-role="actions"]');
    if (!target) return;
    target.innerHTML = "";
    (actions || []).slice(0, 6).forEach((action) => {
      const node = el("article", "claire-source-action");
      node.append(
        el("h4", "", action.label || action.action_id || "Governed action"),
        el("p", "", action.description || "Descriptor only; execution disabled."),
        el("span", "claire-pill claire-pill-blocked", action.execution_enabled ? "enabled" : "blocked")
      );
      target.appendChild(node);
    });
  }

  async function load() {
    const panel = ensurePanel();
    try {
      const response = await fetch(state.payloadEndpoint, { headers: { "Accept": "application/json" } });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const payload = await response.json();
      renderSummary(panel, payload);
      renderCards(panel, payload.cards || []);
      renderActions(panel, payload.actions || []);
    } catch (error) {
      const summary = panel.querySelector('[data-role="summary"]');
      if (summary) summary.textContent = `Governed web search planning payload unavailable: ${error.message}`;
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", load);
  } else {
    load();
  }
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
