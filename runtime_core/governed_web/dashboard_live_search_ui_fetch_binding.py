
# Claire Syntalion v18.59
# Dashboard Live Search UI Fetch Binding
#
# This module defines the review-safe UI fetch contract used by the dashboard
# search bar. It emits frontend binding metadata and a governed JavaScript
# fetch client without auto-mutating existing dashboard HTML.

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Mapping, Optional


CONTRACT_VERSION = 'v18.59.dashboard_live_search_ui_fetch_binding'

DEFAULT_ENDPOINT = '/api/dashboard/search/live'
DEFAULT_FORM_ID = 'claire-governed-live-search-form'
DEFAULT_INPUT_ID = 'claire-governed-live-search-input'
DEFAULT_RESULTS_ID = 'claire-governed-live-search-results'
DEFAULT_STATUS_ID = 'claire-governed-live-search-status'
DEFAULT_MANUAL_ENABLE_ID = 'claire-governed-live-search-manual-enable'


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def _string(value: Any, default: str = '') -> str:
    if value is None:
        return default
    if isinstance(value, str):
        value = value.strip()
        return value if value else default
    return str(value).strip() or default


@dataclass(frozen=True)
class DashboardLiveSearchUIFetchPolicy:
    manual_enable_required: bool = True
    review_required: bool = True
    fail_closed: bool = True
    immutable_runtime_truth: bool = True
    runtime_truth_mutated: bool = False
    autonomous_execution_enabled: bool = False
    automatic_updates_enabled: bool = False
    ui_binding_only: bool = True
    html_auto_mutation: bool = False
    fetch_method: str = 'POST'
    content_type: str = 'application/json'
    max_results: int = 10

    def to_dict(self) -> Dict[str, Any]:
        return {
            'manual_enable_required': self.manual_enable_required,
            'review_required': self.review_required,
            'fail_closed': self.fail_closed,
            'immutable_runtime_truth': self.immutable_runtime_truth,
            'runtime_truth_mutated': self.runtime_truth_mutated,
            'autonomous_execution_enabled': self.autonomous_execution_enabled,
            'automatic_updates_enabled': self.automatic_updates_enabled,
            'ui_binding_only': self.ui_binding_only,
            'html_auto_mutation': self.html_auto_mutation,
            'fetch_method': self.fetch_method,
            'content_type': self.content_type,
            'max_results': self.max_results,
        }


def build_dashboard_live_search_fetch_config(
    *,
    endpoint: str = DEFAULT_ENDPOINT,
    form_id: str = DEFAULT_FORM_ID,
    input_id: str = DEFAULT_INPUT_ID,
    results_id: str = DEFAULT_RESULTS_ID,
    status_id: str = DEFAULT_STATUS_ID,
    manual_enable_id: str = DEFAULT_MANUAL_ENABLE_ID,
    provider: str = 'governed-provider',
    max_results: int = 10,
) -> Dict[str, Any]:
    policy = DashboardLiveSearchUIFetchPolicy(max_results=max(1, int(max_results or 10)))
    return {
        'contract_version': CONTRACT_VERSION,
        'status': 'ui_fetch_binding_ready',
        'created_at': _utc_now(),
        'endpoint': _string(endpoint, DEFAULT_ENDPOINT),
        'method': policy.fetch_method,
        'content_type': policy.content_type,
        'selectors': {
            'form_id': _string(form_id, DEFAULT_FORM_ID),
            'input_id': _string(input_id, DEFAULT_INPUT_ID),
            'results_id': _string(results_id, DEFAULT_RESULTS_ID),
            'status_id': _string(status_id, DEFAULT_STATUS_ID),
            'manual_enable_id': _string(manual_enable_id, DEFAULT_MANUAL_ENABLE_ID),
        },
        'request_defaults': {
            'provider': _string(provider, 'governed-provider'),
            'manual_enable_confirmed': False,
            'require_provider_env': True,
            'require_limited_body_env': True,
            'max_results': policy.max_results,
        },
        'response_contract': {
            'expects_result_cards': True,
            'result_card_fields': ['title', 'url', 'domain', 'snippet', 'trust_score', 'provider'],
            'dashboard_render_required': True,
            'visible_result_count_required': True,
        },
        'policy': policy.to_dict(),
        'governance': {
            'review_required': True,
            'runtime_truth_mutated': False,
            'autonomous_execution': False,
            'automatic_updates': False,
            'fail_closed': True,
        },
    }


def build_dashboard_live_search_request_payload(
    *,
    query: str,
    manual_enable_confirmed: bool,
    provider: str = 'governed-provider',
    session_id: str = '',
    max_results: int = 10,
    require_provider_env: bool = True,
    require_limited_body_env: bool = True,
) -> Dict[str, Any]:
    return {
        'query': _string(query),
        'session_id': _string(session_id),
        'provider': _string(provider, 'governed-provider'),
        'manual_enable_confirmed': bool(manual_enable_confirmed),
        'require_provider_env': bool(require_provider_env),
        'require_limited_body_env': bool(require_limited_body_env),
        'max_results': max(1, int(max_results or 10)),
    }


def build_review_safe_result_card_html(result: Mapping[str, Any]) -> str:
    title = _string(result.get('title'), 'Untitled result')
    url = _string(result.get('url'))
    domain = _string(result.get('domain'))
    snippet = _string(result.get('snippet'))
    trust = _string(result.get('trust_score'), '0')

    def esc(value: str) -> str:
        return (
            value.replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
            .replace("'", '&#39;')
        )

    safe_title = esc(title)
    safe_url = esc(url)
    safe_domain = esc(domain)
    safe_snippet = esc(snippet)
    safe_trust = esc(trust)

    if not (url.startswith('http://') or url.startswith('https://')):
        safe_link = f'<span class="claire-live-search-result-title">{safe_title}</span>'
    else:
        safe_link = f'<a class="claire-live-search-result-title" href="{safe_url}" target="_blank" rel="noopener noreferrer">{safe_title}</a>'

    return (
        '<article class="claire-live-search-result-card" data-review-required="true">'
        + safe_link
        + f'<div class="claire-live-search-result-domain">{safe_domain}</div>'
        + f'<p class="claire-live-search-result-snippet">{safe_snippet}</p>'
        + f'<div class="claire-live-search-result-trust">Trust: {safe_trust}</div>'
        + '</article>'
    )


def build_dashboard_live_search_javascript(config: Optional[Mapping[str, Any]] = None) -> str:
    cfg = dict(config or build_dashboard_live_search_fetch_config())
    endpoint = _string(cfg.get('endpoint'), DEFAULT_ENDPOINT)
    selectors = dict(cfg.get('selectors') or {})
    form_id = _string(selectors.get('form_id'), DEFAULT_FORM_ID)
    input_id = _string(selectors.get('input_id'), DEFAULT_INPUT_ID)
    results_id = _string(selectors.get('results_id'), DEFAULT_RESULTS_ID)
    status_id = _string(selectors.get('status_id'), DEFAULT_STATUS_ID)
    manual_enable_id = _string(selectors.get('manual_enable_id'), DEFAULT_MANUAL_ENABLE_ID)
    defaults = dict(cfg.get('request_defaults') or {})
    provider = _string(defaults.get('provider'), 'governed-provider')
    max_results = max(1, int(defaults.get('max_results') or 10))

    js_lines = [
        '(function () {',
        '  const ClaireLiveSearch = {',
        f"    contractVersion: '{CONTRACT_VERSION}',",
        f"    endpoint: '{endpoint}',",
        f"    formId: '{form_id}',",
        f"    inputId: '{input_id}',",
        f"    resultsId: '{results_id}',",
        f"    statusId: '{status_id}',",
        f"    manualEnableId: '{manual_enable_id}',",
        f"    provider: '{provider}',",
        f'    maxResults: {max_results},',
        '',
        '    escapeHtml(value) {',
        "      return String(value ?? '')",
        "        .replace(/&/g, '&amp;')",
        "        .replace(/</g, '&lt;')",
        "        .replace(/>/g, '&gt;')",
        "        .replace(/\\\"/g, '&quot;')",
        "        .replace(/'/g, '&#39;');",
        '    },',
        '',
        '    setStatus(message) {',
        '      const statusEl = document.getElementById(this.statusId);',
        '      if (statusEl) statusEl.textContent = message;',
        '    },',
        '',
        '    renderResults(payload) {',
        '      const resultsEl = document.getElementById(this.resultsId);',
        '      if (!resultsEl) return;',
        '      const cards = Array.isArray(payload.result_cards) ? payload.result_cards : [];',
        '      if (!cards.length) {',
        "        resultsEl.innerHTML = '<div class=\"claire-live-search-empty\">No governed results returned.</div>';",
        '        return;',
        '      }',
        '      resultsEl.innerHTML = cards.map((card) => {',
        "        const title = this.escapeHtml(card.title || 'Untitled result');",
        "        const url = this.escapeHtml(card.url || '');",
        "        const domain = this.escapeHtml(card.domain || '');",
        "        const snippet = this.escapeHtml(card.snippet || '');",
        "        const trust = this.escapeHtml(card.trust_score ?? '0');",
        "        const safeLink = (String(card.url || '').startsWith('http://') || String(card.url || '').startsWith('https://'))",
        "          ? `<a class=\"claire-live-search-result-title\" href=\"${url}\" target=\"_blank\" rel=\"noopener noreferrer\">${title}</a>`",
        "          : `<span class=\"claire-live-search-result-title\">${title}</span>`;",
        "        return `<article class=\"claire-live-search-result-card\" data-review-required=\"true\">${safeLink}<div class=\"claire-live-search-result-domain\">${domain}</div><p class=\"claire-live-search-result-snippet\">${snippet}</p><div class=\"claire-live-search-result-trust\">Trust: ${trust}</div></article>`;",
        '      }).join(\'\');',
        '    },',
        '',
        '    async submit(query, manualEnableConfirmed) {',
        "      const cleanQuery = String(query || '').trim();",
        '      if (!cleanQuery) {',
        "        this.setStatus('Enter a query before searching.');",
        '        return null;',
        '      }',
        '      if (!manualEnableConfirmed) {',
        "        this.setStatus('Manual governed search enable is required.');",
        '        return null;',
        '      }',
        "      this.setStatus('Running governed live search...');",
        '      const response = await fetch(this.endpoint, {',
        "        method: 'POST',",
        "        headers: { 'Content-Type': 'application/json' },",
        '        body: JSON.stringify({',
        '          query: cleanQuery,',
        '          provider: this.provider,',
        '          manual_enable_confirmed: true,',
        '          require_provider_env: true,',
        '          require_limited_body_env: true,',
        '          max_results: this.maxResults',
        '        })',
        '      });',
        '      const payload = await response.json();',
        '      this.renderResults(payload);',
        "      this.setStatus(payload.endpoint_status || payload.reason || 'Governed search complete.');",
        '      return payload;',
        '    },',
        '',
        '    attach() {',
        '      const form = document.getElementById(this.formId);',
        '      const input = document.getElementById(this.inputId);',
        '      const manualEnable = document.getElementById(this.manualEnableId);',
        '      if (!form || !input) {',
        "        this.setStatus('Governed search UI elements not found.');",
        '        return false;',
        '      }',
        "      form.addEventListener('submit', (event) => {",
        '        event.preventDefault();',
        '        this.submit(input.value, Boolean(manualEnable && manualEnable.checked));',
        '      });',
        "      this.setStatus('Governed live search UI binding ready.');",
        '      return true;',
        '    }',
        '  };',
        '',
        '  window.ClaireLiveSearch = ClaireLiveSearch;',
        "  if (document.readyState === 'loading') {",
        "    document.addEventListener('DOMContentLoaded', () => ClaireLiveSearch.attach());",
        '  } else {',
        '    ClaireLiveSearch.attach();',
        '  }',
        '})();',
    ]
    return '\n'.join(js_lines) + '\n'


__all__ = [
    'CONTRACT_VERSION',
    'DEFAULT_ENDPOINT',
    'DashboardLiveSearchUIFetchPolicy',
    'build_dashboard_live_search_fetch_config',
    'build_dashboard_live_search_javascript',
    'build_dashboard_live_search_request_payload',
    'build_review_safe_result_card_html',
]
