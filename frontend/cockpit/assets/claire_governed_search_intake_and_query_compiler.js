(function () {
  "use strict";

  const SOURCE_INTAKE_ENDPOINT = "/api/evidence/source/intake";
  const QUERY_COMPILER_ENDPOINT = "/api/search/governed/query/payload";

  function asArray(value) {
    return Array.isArray(value) ? value : [];
  }

  function findPanel(candidates) {
    for (const selector of candidates) {
      const el = document.querySelector(selector);
      if (el) return el;
    }
    return null;
  }

  function ensurePanel(id, title) {
    let panel = document.getElementById(id);
    if (panel) return panel;

    const host =
      findPanel([
        "#governed-web",
        "[data-panel='governed-web']",
        "[data-tab='governed-web']",
        ".governed-web",
        "main",
        "#app",
        "body",
      ]) || document.body;

    panel = document.createElement("section");
    panel.id = id;
    panel.className = "claire-s611-s624-panel";
    panel.innerHTML = `
      <header class="claire-s611-s624-header">
        <div>
          <p class="claire-s611-s624-kicker">S611-S624</p>
          <h2>${title}</h2>
        </div>
        <span class="claire-s611-s624-chip">execution blocked</span>
      </header>
      <div class="claire-s611-s624-grid"></div>
    `;
    host.appendChild(panel);
    return panel;
  }

  function card(title, state, body, items) {
    const itemHtml = asArray(items)
      .slice(0, 8)
      .map((item) => {
        if (typeof item === "string") return `<li>${escapeHtml(item)}</li>`;
        const label = item.source_family || item.name || item.label || item.card_type || item.action_id || item.compiled_query_id || "item";
        const detail = item.trust_tier || item.state || item.scope_state || item.execution_state || item.description || "";
        return `<li><strong>${escapeHtml(String(label))}</strong>${detail ? ` <span>${escapeHtml(String(detail))}</span>` : ""}</li>`;
      })
      .join("");

    return `
      <article class="claire-s611-s624-card">
        <div class="claire-s611-s624-card-top">
          <h3>${escapeHtml(title)}</h3>
          <span>${escapeHtml(state || "ready")}</span>
        </div>
        <p>${escapeHtml(body || "")}</p>
        ${itemHtml ? `<ul>${itemHtml}</ul>` : ""}
      </article>
    `;
  }

  function escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  async function getJson(url) {
    const response = await fetch(url, { cache: "no-store" });
    if (!response.ok) throw new Error(`${url} ${response.status}`);
    return response.json();
  }

  function renderSourceIntake(payload) {
    const panel = ensurePanel("claire-s611-s617-source-intake", "Governed Source Evidence Intake");
    const grid = panel.querySelector(".claire-s611-s624-grid");
    if (!grid) return;

    const cards = asArray(payload.cards);
    const actions = asArray(payload.actions);
    const families = asArray(payload.policy && payload.policy.source_families);

    grid.innerHTML =
      card(
        "Intake status",
        payload.status,
        payload.summary ? payload.summary.headline : "Metadata-only source intake prepared.",
        [
          `cards: ${cards.length}`,
          "network: not performed",
          "body reads: blocked",
          "runtime mutation: blocked",
        ]
      ) +
      card("Source evidence cards", "review required", "Cards are cockpit-visible descriptors, not runtime truth.", cards) +
      card("Source families", "policy visible", "Trust tiers, quarantine state, and source-family policy are ready for review.", families) +
      card("Governed actions", "non-executing", "Actions can populate cockpit surfaces without granting execution authority.", actions);
  }

  function renderQueryCompiler(payload) {
    const panel = ensurePanel("claire-s618-s624-query-compiler", "Governed Query Builder + Search Scope Compiler");
    const grid = panel.querySelector(".claire-s611-s624-grid");
    if (!grid) return;

    const plan = payload.plan || {};
    const cards = asArray(payload.cards);
    const actions = asArray(payload.actions);
    const scope = asArray(plan.source_scope);
    const compiledQueries = asArray(plan.compiled_queries);

    grid.innerHTML =
      card(
        "Compiler status",
        payload.status,
        "Claire can compile a search plan without executing a provider or reading bodies.",
        [
          `intent: ${plan.intent ? plan.intent.primary_intent : "not detected"}`,
          `source families: ${scope.length}`,
          `compiled queries: ${compiledQueries.length}`,
          "provider execution: blocked",
        ]
      ) +
      card("Search scope", "planned only", "Source families are ordered by trust tier and route intent.", scope) +
      card("Compiled queries", "not executed", "Query strings are prepared only for operator review.", compiledQueries) +
      card("Query actions", "non-executing", "Actions describe review steps without enabling search authority.", actions.concat(cards));
  }

  async function boot() {
    try {
      const sourcePayload = await getJson(SOURCE_INTAKE_ENDPOINT);
      renderSourceIntake(sourcePayload);
    } catch (err) {
      console.warn("[Claire S611-S617] source intake unavailable", err);
    }

    try {
      const queryPayload = await getJson(QUERY_COMPILER_ENDPOINT);
      renderQueryCompiler(queryPayload);
    } catch (err) {
      console.warn("[Claire S618-S624] query compiler unavailable", err);
    }
  }

  window.ClaireGovernedSearchIntakeAndCompiler = {
    boot,
    renderSourceIntake,
    renderQueryCompiler,
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
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
