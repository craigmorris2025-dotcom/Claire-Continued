(function () {
  "use strict";
  const ROOT_ID = "claire-governed-quarantine-metadata-results";
  function el(tag, attrs, text) {
    const node = document.createElement(tag);
    Object.entries(attrs || {}).forEach(([key, value]) => {
      if (key === "class") node.className = value;
      else node.setAttribute(key, value);
    });
    if (text !== undefined && text !== null) node.textContent = String(text);
    return node;
  }
  function findHost() {
    return document.querySelector("[data-panel='evidence-review']") ||
      document.querySelector("#evidence-review") ||
      document.querySelector("[data-tab='Evidence & Review']") ||
      document.querySelector("main") ||
      document.body;
  }
  function ensureRoot() {
    let root = document.getElementById(ROOT_ID);
    if (!root) {
      root = el("section", { id: ROOT_ID, class: "claire-s639-s652-panel" });
      findHost().appendChild(root);
    }
    return root;
  }
  function blockedList(blocked) {
    const items = Object.entries(blocked || {})
      .filter(([, value]) => value === false)
      .slice(0, 8)
      .map(([key]) => `<span class="claire-s639-chip">${key.replaceAll("_", " ")}</span>`)
      .join("");
    return items || "<span class='claire-s639-chip'>fail closed</span>";
  }
  function cardHtml(card) {
    const badges = (card.badges || []).map((badge) => `<span class="claire-s639-badge">${badge}</span>`).join("");
    return `<article class="claire-s639-card">
      <div class="claire-s639-card-top"><h4>${card.title || card.id || "Governed card"}</h4><span class="claire-s639-state">${card.state || card.category || "governed"}</span></div>
      <p>${card.summary || "No summary supplied."}</p>
      <div class="claire-s639-meta"><span>${card.source_family || "source family pending"}</span><span>${card.trust_tier || "trust tier pending"}</span>${card.display_url ? `<span>${card.display_url}</span>` : ""}</div>
      <div class="claire-s639-badges">${badges}</div>
    </article>`;
  }
  function actionHtml(action) {
    return `<article class="claire-s639-action"><strong>${action.label || action.id}</strong><span>${action.state || "descriptor"}</span><p>${action.description || "Governed action descriptor."}</p></article>`;
  }
  async function getJson(path) {
    const response = await fetch(path, { cache: "no-store" });
    if (!response.ok) throw new Error(`${path} returned ${response.status}`);
    return response.json();
  }
  async function render() {
    const root = ensureRoot();
    root.innerHTML = `<div class="claire-s639-header"><div><p class="claire-s639-kicker">S639-S652</p><h3>Quarantine + Metadata-Only Search Results</h3><p>Evidence can now be shown as review cards while search results remain metadata-only, quarantined, and non-authoritative.</p></div><span class="claire-s639-pill">fail-closed</span></div><div class="claire-s639-loading">Loading governed quarantine and metadata contracts...</div>`;
    try {
      const [quarantine, metadata] = await Promise.all([getJson("/api/evidence/quarantine/payload"), getJson("/api/search/metadata/payload")]);
      const qCards = quarantine.cards || [];
      const mCards = metadata.cards || [];
      const actions = [...(quarantine.actions || []), ...(metadata.actions || [])];
      const blocked = (metadata.status && metadata.status.blocked_capabilities) || (quarantine.status && quarantine.status.blocked_capabilities) || {};
      root.innerHTML = `<div class="claire-s639-header"><div><p class="claire-s639-kicker">S639-S652</p><h3>Quarantine + Metadata-Only Search Results</h3><p>${metadata.summary || quarantine.summary || "Governed source/search result surfaces are ready."}</p></div><span class="claire-s639-pill">${metadata.status ? metadata.status.status : "ready"}</span></div><div class="claire-s639-blocked">${blockedList(blocked)}</div><div class="claire-s639-grid"><section><h4>Quarantine evidence cards</h4>${qCards.length ? qCards.map(cardHtml).join("") : "<p>No quarantine cards returned.</p>"}</section><section><h4>Metadata result cards</h4>${mCards.length ? mCards.map(cardHtml).join("") : "<p>No metadata cards returned.</p>"}</section></div><section class="claire-s639-actions"><h4>Governed actions now visible</h4>${actions.length ? actions.map(actionHtml).join("") : "<p>No governed action descriptors returned.</p>"}</section>`;
    } catch (error) {
      root.innerHTML = `<div class="claire-s639-header"><div><p class="claire-s639-kicker">S639-S652</p><h3>Quarantine + Metadata-Only Search Results</h3><p class="claire-s639-error">Unable to load governed source/search payloads: ${error.message}</p></div><span class="claire-s639-pill">needs backend</span></div>`;
    }
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", render);
  else render();
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
