(function () {
  const ClaireLiveSearch = {
    contractVersion: 'v18.59.dashboard_live_search_ui_fetch_binding',
    endpoint: '/api/dashboard/search/live',
    formId: 'claire-governed-live-search-form',
    inputId: 'claire-governed-live-search-input',
    resultsId: 'claire-governed-live-search-results',
    statusId: 'claire-governed-live-search-status',
    manualEnableId: 'claire-governed-live-search-manual-enable',
    provider: 'governed-provider',
    maxResults: 10,

    escapeHtml(value) {
      return String(value ?? '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/\"/g, '&quot;')
        .replace(/'/g, '&#39;');
    },

    setStatus(message) {
      const statusEl = document.getElementById(this.statusId);
      if (statusEl) statusEl.textContent = message;
    },

    renderResults(payload) {
      const resultsEl = document.getElementById(this.resultsId);
      if (!resultsEl) return;
      const cards = Array.isArray(payload.result_cards) ? payload.result_cards : [];
      if (!cards.length) {
        resultsEl.innerHTML = '<div class="claire-live-search-empty">No governed results returned.</div>';
        return;
      }
      resultsEl.innerHTML = cards.map((card) => {
        const title = this.escapeHtml(card.title || 'Untitled result');
        const url = this.escapeHtml(card.url || '');
        const domain = this.escapeHtml(card.domain || '');
        const snippet = this.escapeHtml(card.snippet || '');
        const trust = this.escapeHtml(card.trust_score ?? '0');
        const safeLink = (String(card.url || '').startsWith('http://') || String(card.url || '').startsWith('https://'))
          ? `<a class="claire-live-search-result-title" href="${url}" target="_blank" rel="noopener noreferrer">${title}</a>`
          : `<span class="claire-live-search-result-title">${title}</span>`;
        return `<article class="claire-live-search-result-card" data-review-required="true">${safeLink}<div class="claire-live-search-result-domain">${domain}</div><p class="claire-live-search-result-snippet">${snippet}</p><div class="claire-live-search-result-trust">Trust: ${trust}</div></article>`;
      }).join('');
    },

    async submit(query, manualEnableConfirmed) {
      const cleanQuery = String(query || '').trim();
      if (!cleanQuery) {
        this.setStatus('Enter a query before searching.');
        return null;
      }
      if (!manualEnableConfirmed) {
        this.setStatus('Manual governed search enable is required.');
        return null;
      }
      this.setStatus('Running governed live search...');
      const response = await fetch(this.endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: cleanQuery,
          provider: this.provider,
          manual_enable_confirmed: true,
          require_provider_env: true,
          require_limited_body_env: true,
          max_results: this.maxResults
        })
      });
      const payload = await response.json();
      this.renderResults(payload);
      this.setStatus(payload.endpoint_status || payload.reason || 'Governed search complete.');
      return payload;
    },

    attach() {
      const form = document.getElementById(this.formId);
      const input = document.getElementById(this.inputId);
      const manualEnable = document.getElementById(this.manualEnableId);
      if (!form || !input) {
        this.setStatus('Governed search UI elements not found.');
        return false;
      }
      form.addEventListener('submit', (event) => {
        event.preventDefault();
        this.submit(input.value, Boolean(manualEnable && manualEnable.checked));
      });
      this.setStatus('Governed live search UI binding ready.');
      return true;
    }
  };

  window.ClaireLiveSearch = ClaireLiveSearch;
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => ClaireLiveSearch.attach());
  } else {
    ClaireLiveSearch.attach();
  }
})();
