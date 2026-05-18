window.ClaireCockpitActions = {
  async fetchJson(path, options) {
    const response = await fetch(path, Object.assign({ cache: "no-store" }, options || {}));
    const text = await response.text();
    let body = null;
    try {
      body = text ? JSON.parse(text) : null;
    } catch (error) {
      body = { raw: text };
    }
    if (!response.ok) {
      const err = new Error(path + " returned " + response.status);
      err.status = response.status;
      err.body = body;
      throw err;
    }
    return body;
  },

  setActionState(message, detail) {
    const panel = document.getElementById("actionStatePanel");
    if (!panel) return;
    panel.textContent = JSON.stringify({
      status: message,
      detail: detail || null,
      rule: "enterprise_operator_actions_request_backend_truth_only",
      timestamp: new Date().toISOString()
    }, null, 2);
  },

  setWorkspace(workspaceId) {
    const button = document.querySelector('[data-workspace-id="' + workspaceId + '"]');
    if (button) {
      button.click();
      this.setActionState("workspace_selected", workspaceId);
      return;
    }
    this.setActionState("workspace_not_available", workspaceId);
  },

  async refreshRuntime() {
    this.setActionState("runtime_refresh_requested", "Refreshing canonical runtime payload.");
    if (window.ClaireCockpitHydration && typeof window.ClaireCockpitHydration.refresh === "function") {
      await window.ClaireCockpitHydration.refresh();
      this.setActionState("runtime_refresh_complete", "Canonical payload refresh completed.");
      return;
    }
    this.setActionState("runtime_refresh_unavailable", "Hydration bridge not exposed yet.");
  },

  async startRun() {
    this.setActionState("start_run_requested", "POST /runs/start");
    try {
      const payload = await this.fetchJson("/runs/start", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          source: "enterprise_cockpit",
          mode: "discovery_first",
          requested_by: "operator",
          contract: "endpoint_artifact_payload_cockpit_pytest"
        })
      });
      this.setActionState("start_run_backend_response", payload);
      if (window.ClaireCockpitHydration && typeof window.ClaireCockpitHydration.acceptPayload === "function") {
        window.ClaireCockpitHydration.acceptPayload(payload);
      }
    } catch (error) {
      this.setActionState("start_run_not_yet_wired", {
        message: error.message,
        status: error.status || null,
        body: error.body || null,
        required_next_layer: "Implement POST /runs/start backend endpoint + run artifacts + canonical payload exposure."
      });
    }
  },

  viewSystemStatus() {
    this.setWorkspace("system");
  },

  viewGovernance() {
    this.setWorkspace("governance");
  },

  bind() {
    const start = document.getElementById("actionStartRun");
    const refresh = document.getElementById("actionRefreshRuntime");
    const system = document.getElementById("actionViewSystemStatus");
    const governance = document.getElementById("actionViewGovernance");

    if (start) start.addEventListener("click", () => this.startRun());
    if (refresh) refresh.addEventListener("click", () => this.refreshRuntime());
    if (system) system.addEventListener("click", () => this.viewSystemStatus());
    if (governance) governance.addEventListener("click", () => this.viewGovernance());
  }
};

document.addEventListener("DOMContentLoaded", () => {
  window.ClaireCockpitActions.bind();
});

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
