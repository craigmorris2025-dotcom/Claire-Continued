(function () {
  const rootId = "claire-governed-body-read-gate";
  const endpoint = "/api/cockpit/body-read-gate/payload";

  function esc(value) {
    return String(value == null ? "" : value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function ensureRoot() {
    let root = document.getElementById(rootId);
    if (root) return root;
    const host = document.querySelector("[data-claire-panel='governed-web']") ||
                 document.querySelector("#governed-web") ||
                 document.querySelector("main") ||
                 document.body;
    root = document.createElement("section");
    root.id = rootId;
    root.className = "claire-governed-body-read-gate";
    host.appendChild(root);
    return root;
  }

  function cardHtml(card) {
    const badges = (card.badges || []).map(function (badge) {
      return '<span class="claire-pill claire-pill-blocked">' + esc(badge) + '</span>';
    }).join("");
    return '<article class="claire-source-card">' +
      '<p class="claire-eyebrow">' + esc(card.state || "planned") + '</p>' +
      '<h3>' + esc(card.title || "Body-read gate card") + '</h3>' +
      '<p class="claire-muted">' + esc(card.subtitle || "") + '</p>' +
      '<p>' + esc(card.summary || "") + '</p>' +
      '<div class="claire-badge-row">' + badges + '</div>' +
      '</article>';
  }

  function actionHtml(action) {
    return '<article class="claire-source-action">' +
      '<h4>' + esc(action.label || action.action_id || "Governed action") + '</h4>' +
      '<p>' + esc(action.description || "") + '</p>' +
      '<span class="claire-pill claire-pill-blocked">execution disabled</span>' +
      '</article>';
  }

  function render(payload) {
    const root = ensureRoot();
    const cards = payload.cards || [];
    const actions = payload.actions || [];
    root.innerHTML = '<div class="claire-source-panel-header">' +
      '<div><p class="claire-eyebrow">S779-S834</p><h2>Governed Body-Read Gate</h2></div>' +
      '<span class="claire-pill claire-pill-blocked">Body reads blocked</span>' +
      '</div>' +
      '<p class="claire-source-panel-summary">Authorization, extraction scope, sanitizer, and manual-gate cards are cockpit-visible. No body read, crawl, network request, update, or runtime mutation is enabled.</p>' +
      '<div class="claire-source-card-grid">' + cards.map(cardHtml).join("") + '</div>' +
      '<h3>Governed actions</h3>' +
      '<div class="claire-source-action-grid">' + actions.map(actionHtml).join("") + '</div>';
  }

  async function load() {
    const root = ensureRoot();
    root.innerHTML = '<p class="claire-muted">Loading governed body-read gate...</p>';
    try {
      const response = await fetch(endpoint, { cache: "no-store" });
      if (!response.ok) throw new Error("HTTP " + response.status);
      render(await response.json());
    } catch (error) {
      root.innerHTML = '<p class="claire-muted">Governed body-read gate unavailable: ' + esc(error.message || error) + '</p>';
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
