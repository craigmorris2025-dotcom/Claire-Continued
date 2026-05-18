(function () {
  const VERSION = "S985-S1012";
  const PAYLOAD_URL = "/api/cockpit/control-surface/payload";
  const FALLBACK = {
    stage: "S985-S1012",
    status: "fallback_control_surface_ready",
    action_count: 16,
    operator_message: "Visible cockpit controls are mounted from fallback payload. Execution remains blocked.",
    buttons: [],
    control_surface: {
      buttons: [
        ["run_readiness_audit", "Run readiness audit"],
        ["inspect_providers", "Inspect providers"],
        ["open_source_policy", "Open source policy"],
        ["compile_search_plan", "Compile search plan"],
        ["preview_metadata_search", "Preview metadata search"],
        ["view_metadata_contract", "View metadata contract"],
        ["open_quarantine_review", "Open quarantine review"],
        ["build_evidence_cards", "Build evidence cards"],
        ["score_source_confidence", "Score source confidence"],
        ["show_review_actions", "Show review actions"],
        ["build_body_read_request", "Build body-read request"],
        ["run_body_read_preflight", "Run body-read preflight"],
        ["draft_source_ingestion", "Draft source ingestion"],
        ["preview_truth_promotion", "Preview truth promotion"],
        ["verify_s900_gate", "Verify S900 gate"],
        ["verify_button_mount", "Verify button mount"]
      ].map(([key, label]) => ({ key, label, operation_mode: "preview_only", execution_enabled: false }))
    },
    blocked_flags: {
      live_web_execution_enabled: false,
      search_provider_execution_enabled: false,
      browser_execution_enabled: false,
      network_request_performed: false,
      body_read_allowed: false,
      autonomous_crawling_enabled: false,
      automatic_updates_enabled: false,
      runtime_mutation_enabled: false,
      runtime_truth_mutation_enabled: false,
      package_download_performed: false,
      package_install_performed: false,
      command_execution_enabled: false
    }
  };

  function normalizePayload(payload) {
    const buttons = (payload && payload.control_surface && payload.control_surface.buttons) || payload.buttons || FALLBACK.control_surface.buttons;
    return Object.assign({}, FALLBACK, payload || {}, {
      control_surface: Object.assign({}, FALLBACK.control_surface, (payload && payload.control_surface) || {}, { buttons })
    });
  }

  function findCommandSurface() {
    const input = Array.from(document.querySelectorAll('input, textarea')).find((el) => {
      const placeholder = (el.getAttribute('placeholder') || '').toLowerCase();
      return placeholder.includes('ask claire') || placeholder.includes('governed web') || placeholder.includes('command');
    });
    if (input) {
      return input.closest('section, div, main, article') || input.parentElement;
    }
    const headings = Array.from(document.querySelectorAll('h1, h2, h3, .title')).filter((el) => /claire operator cockpit|governed web|evidence|actions|overview/i.test(el.textContent || ''));
    if (headings.length) return headings[0].parentElement || document.body;
    return document.querySelector('main') || document.body;
  }

  function updateActionsChip(count) {
    const all = Array.from(document.querySelectorAll('body *')).filter((el) => el.children.length === 0 && /^\s*Actions\s*:\s*\d+\s*$/i.test(el.textContent || ''));
    all.forEach((el) => { el.textContent = 'Actions: ' + count; el.setAttribute('data-claire-actions-count-forced', String(count)); });
  }

  function replaceEmptyActionsText(count) {
    const nodes = [];
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    while (walker.nextNode()) nodes.push(walker.currentNode);
    nodes.forEach((node) => {
      if ((node.nodeValue || '').includes('No governed actions registered')) {
        node.nodeValue = 'Governed operation controls registered: ' + count + '. Buttons are visible and preview-only; execution remains blocked.';
      }
    });
  }

  function showPreview(key, label) {
    const output = document.getElementById('claire-s985-s1012-operation-output');
    if (!output) return;
    output.textContent = 'Loading preview for ' + label + '...';
    fetch('/api/cockpit/control-surface/preview/' + encodeURIComponent(key), { cache: 'no-store' })
      .then((res) => res.ok ? res.json() : Promise.reject(new Error('preview endpoint unavailable')))
      .then((payload) => {
        output.textContent = JSON.stringify(payload, null, 2);
      })
      .catch(() => {
        output.textContent = JSON.stringify({
          operation_key: key,
          label: label,
          status: 'local_preview_only',
          execution_enabled: false,
          network_request_performed: false,
          body_read_performed: false,
          runtime_mutation_performed: false,
          command_execution_performed: false,
          message: 'Local preview only. Execution remains blocked.'
        }, null, 2);
      });
  }

  function render(payload) {
    payload = normalizePayload(payload);
    const buttons = payload.control_surface.buttons || [];
    const count = payload.action_count || buttons.length || 0;
    let root = document.getElementById('claire-s985-s1012-control-surface');
    if (!root) {
      root = document.createElement('section');
      root.id = 'claire-s985-s1012-control-surface';
      root.className = 'claire-s985-s1012-control-surface';
      const anchor = findCommandSurface();
      if (anchor && anchor.parentElement) {
        anchor.insertAdjacentElement('afterend', root);
      } else {
        document.body.insertBefore(root, document.body.firstChild);
      }
    }
    root.innerHTML = '';

    const header = document.createElement('div');
    header.className = 'claire-s985-s1012-control-header';
    header.innerHTML = '<div><div class="claire-s985-s1012-eyebrow">OPERATOR CONTROL SURFACE</div><h2>Governed Operation Buttons</h2><p>Buttons are mounted for cockpit operation. All execution, body-read, runtime mutation, package install, and command authority remain blocked.</p></div><span class="claire-s985-s1012-badge">' + count + ' preview actions</span>';
    root.appendChild(header);

    const grid = document.createElement('div');
    grid.className = 'claire-s985-s1012-button-grid';
    buttons.forEach((button) => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'claire-s985-s1012-op-button';
      btn.setAttribute('data-operation-key', button.key);
      btn.innerHTML = '<strong>' + (button.label || button.key) + '</strong><span>' + (button.operation_mode || 'preview_only') + '</span>';
      btn.addEventListener('click', () => showPreview(button.key, button.label || button.key));
      grid.appendChild(btn);
    });
    root.appendChild(grid);

    const out = document.createElement('pre');
    out.id = 'claire-s985-s1012-operation-output';
    out.className = 'claire-s985-s1012-output';
    out.textContent = JSON.stringify({ stage: payload.stage, status: payload.status, action_count: count, blocked_flags: payload.blocked_flags }, null, 2);
    root.appendChild(out);

    updateActionsChip(count);
    replaceEmptyActionsText(count);
    document.body.setAttribute('data-claire-s985-s1012-control-surface-mounted', 'true');
  }

  function mount() {
    fetch(PAYLOAD_URL, { cache: 'no-store' })
      .then((res) => res.ok ? res.json() : FALLBACK)
      .then(render)
      .catch(() => render(FALLBACK));
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', mount);
  } else {
    mount();
  }
  setTimeout(mount, 500);
  setTimeout(mount, 1500);
  setTimeout(mount, 3500);
  try {
    const observer = new MutationObserver(() => {
      if (!document.getElementById('claire-s985-s1012-control-surface')) mount();
      const current = document.body.getAttribute('data-claire-s985-s1012-control-surface-mounted');
      if (current !== 'true') mount();
    });
    observer.observe(document.body, { childList: true, subtree: true });
  } catch (err) {}
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
