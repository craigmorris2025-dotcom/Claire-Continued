(() => {
  const endpoints = {
    counts: "/api/workflow/counts",
    reviewQueue: "/api/workflow/review-queue",
    monitoring: "/api/workflow/monitoring",
    reviewDecision: "/api/workflow/review-decision",
    boundedJob: "/api/workflow/bounded-job",
    exportArtifact: "/api/workflow/export"
  };

  const state = {
    counts: null,
    reviewQueue: [],
    monitoring: null,
    lastError: null,
    authorityLocks: {
      runtime_truth_write_allowed: false,
      runtime_mutation_allowed: false,
      automatic_updates_allowed: false,
      autonomous_execution_allowed: false,
      continuous_crawling_allowed: false,
      workflow_actions_mode: "proposal_only"
    }
  };

  function byId(id) {
    return document.getElementById(id);
  }

  function setText(id, value) {
    const el = byId(id);
    if (el) el.textContent = String(value);
  }

  function ensurePanel() {
    let panel = byId("safe-workflow-panel");
    if (panel) return panel;

    const host = document.querySelector("main") || document.body;
    panel = document.createElement("section");
    panel.id = "safe-workflow-panel";
    panel.className = "safe-workflow-panel";
    panel.innerHTML = `
      <div class="safe-workflow-header">
        <h2>Safe Workflow Operations</h2>
        <div id="safe-workflow-status">Waiting for workflow counts...</div>
      </div>
      <div class="safe-workflow-grid">
        <div><strong>Review Queue</strong><span id="workflow-review-count">0</span></div>
        <div><strong>Pending Reviews</strong><span id="workflow-pending-count">0</span></div>
        <div><strong>Bounded Jobs</strong><span id="workflow-job-count">0</span></div>
        <div><strong>Exports</strong><span id="workflow-export-count">0</span></div>
        <div><strong>Audit Events</strong><span id="workflow-audit-count">0</span></div>
      </div>
      <div class="safe-workflow-actions">
        <button id="workflow-refresh-button" type="button">Refresh Counts</button>
        <button id="workflow-propose-job-button" type="button">Propose Bounded Job</button>
        <button id="workflow-export-button" type="button">Write Export Artifact</button>
      </div>
      <div id="workflow-lock-state" class="safe-workflow-locks"></div>
      <pre id="workflow-monitoring-state" class="safe-workflow-json"></pre>
    `;
    host.appendChild(panel);
    return panel;
  }

  async function getJson(url, options) {
    const res = await fetch(url, options || {});
    if (!res.ok) throw new Error(`${url} returned ${res.status}`);
    return await res.json();
  }

  function renderCounts(payload) {
    const counts = payload && payload.counts ? payload.counts : {};
    state.counts = counts;
    state.authorityLocks = payload.authority_locks || state.authorityLocks;

    setText("workflow-review-count", counts.review_queue_total || 0);
    setText("workflow-pending-count", counts.review_queue_pending || 0);
    setText("workflow-job-count", counts.bounded_jobs_total || 0);
    setText("workflow-export-count", counts.exports_total || 0);
    setText("workflow-audit-count", counts.audit_events_total || 0);
    setText("safe-workflow-status", `Live counts refreshed: ${payload.last_refreshed || "unknown"}`);
    setText("workflow-lock-state", `Authority locks: runtime truth write=${state.authorityLocks.runtime_truth_write_allowed}, mutation=${state.authorityLocks.runtime_mutation_allowed}, autonomous=${state.authorityLocks.autonomous_execution_allowed}, mode=${state.authorityLocks.workflow_actions_mode}`);
  }

  function renderMonitoring(payload) {
    state.monitoring = payload;
    const el = byId("workflow-monitoring-state");
    if (el) el.textContent = JSON.stringify(payload, null, 2);
  }

  async function refreshWorkflowCounts() {
    ensurePanel();
    try {
      const payload = await getJson(endpoints.counts);
      renderCounts(payload);
      const monitoring = await getJson(endpoints.monitoring);
      renderMonitoring(monitoring);
      state.lastError = null;
    } catch (err) {
      state.lastError = String(err && err.message ? err.message : err);
      setText("safe-workflow-status", `Workflow refresh failed: ${state.lastError}`);
    }
  }

  async function proposeBoundedJob() {
    ensurePanel();
    const payload = {
      job_type: "operator_ui_requested_safe_refresh",
      scope: "dashboard_ui",
      max_items: 10,
      notes: "Proposal-only bounded job request from cockpit UI."
    };
    const result = await getJson(endpoints.boundedJob, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(payload)
    });
    setText("safe-workflow-status", `Bounded job proposal recorded: ${result.job && result.job.job_id ? result.job.job_id : "ok"}`);
    await refreshWorkflowCounts();
  }

  async function writeExportArtifact() {
    ensurePanel();
    const result = await getJson(endpoints.exportArtifact, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({export_type: "dashboard_review_snapshot", include_audit_tail: true})
    });
    setText("safe-workflow-status", `Export artifact written: ${result.artifact && result.artifact.filename ? result.artifact.filename : "ok"}`);
    await refreshWorkflowCounts();
  }

  function bindActions() {
    ensurePanel();
    const refresh = byId("workflow-refresh-button");
    const job = byId("workflow-propose-job-button");
    const exp = byId("workflow-export-button");
    if (refresh && !refresh.dataset.bound) {
      refresh.dataset.bound = "true";
      refresh.addEventListener("click", refreshWorkflowCounts);
    }
    if (job && !job.dataset.bound) {
      job.dataset.bound = "true";
      job.addEventListener("click", proposeBoundedJob);
    }
    if (exp && !exp.dataset.bound) {
      exp.dataset.bound = "true";
      exp.addEventListener("click", writeExportArtifact);
    }
  }

  window.ClaireSafeWorkflow = {
    state,
    refreshWorkflowCounts,
    proposeBoundedJob,
    writeExportArtifact,
    endpoints
  };

  document.addEventListener("DOMContentLoaded", () => {
    bindActions();
    refreshWorkflowCounts();
    setInterval(refreshWorkflowCounts, 15000);
  });
})();
