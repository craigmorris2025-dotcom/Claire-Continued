(function () {
  const endpoint = "/api/cockpit/source-ingestion/payload";
  function makeCard(card) {
    const node = document.createElement("article");
    node.className = "claire-source-ingestion-card";
    node.innerHTML = `<div class="claire-source-ingestion-card__top"><strong>${card.title || "Source ingestion card"}</strong><span>${card.state || "review"}</span></div><p>${card.summary || "Review-only source ingestion card."}</p><small>${(card.badges || []).join(" · ")}</small>`;
    return node;
  }
  function findHost() {
    return document.querySelector("[data-claire-source-ingestion]") || document.querySelector("#source-ingestion-panel") || document.querySelector("#evidence-review-panel") || document.querySelector("main");
  }
  async function render() {
    const host = findHost();
    if (!host || host.dataset.claireSourceIngestionRendered === "true") return;
    host.dataset.claireSourceIngestionRendered = "true";
    const section = document.createElement("section");
    section.className = "claire-source-ingestion-panel";
    section.innerHTML = `<div class="claire-source-ingestion-panel__header"><h2>S900 Source / Update Ingestion</h2><p>Body-read, source ingestion, lineage, proposal, and promotion path are visible. Execution remains blocked.</p></div><div class="claire-source-ingestion-panel__cards" data-source-ingestion-cards></div>`;
    host.appendChild(section);
    const cardsHost = section.querySelector("[data-source-ingestion-cards]");
    try {
      const response = await fetch(endpoint, { headers: { "Accept": "application/json" } });
      if (!response.ok) throw new Error("payload unavailable");
      const payload = await response.json();
      (payload.cards || []).slice(0, 8).forEach((card) => cardsHost.appendChild(makeCard(card)));
    } catch (error) {
      cardsHost.innerHTML = `<article class="claire-source-ingestion-card"><strong>S900 source ingestion payload waiting</strong><p>${error.message}</p></article>`;
    }
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", render); else render();
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
